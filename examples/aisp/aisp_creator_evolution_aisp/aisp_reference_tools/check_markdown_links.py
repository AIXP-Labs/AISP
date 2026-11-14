#!/usr/bin/env python3
"""Check local Markdown links and heading anchors."""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.parse
from pathlib import Path
from typing import Any


DEFAULT_TARGETS = [
    "README.md",
    "README_CN.md",
    "docs",
    "examples",
    "specification",
    "adrs",
]

EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "app://")
UNSAFE_PREFIXES = ("file:", "javascript:")


def iter_markdown_files(root: Path, targets: list[str], problems: list[dict[str, Any]] | None = None) -> list[Path]:
    root = root.resolve()
    files: list[Path] = []

    def reject(target: str, message: str) -> None:
        if problems is None:
            raise ValueError(f"{target}: {message}")
        problems.append({"path": target, "line": 0, "link": target, "message": message})

    for target in targets:
        try:
            path = (root / target).resolve()
            path.relative_to(root)
        except (OSError, ValueError, RuntimeError):
            reject(target, "scan target escapes repository root or cannot be resolved")
            continue
        if not path.exists():
            reject(target, "missing scan target")
            continue
        if path.is_file() and path.suffix.lower() == ".md":
            files.append(path)
        elif path.is_dir():
            for child in sorted(path.rglob("*.md")):
                try:
                    resolved = child.resolve()
                    resolved.relative_to(root)
                except (OSError, ValueError, RuntimeError):
                    reject(child.relative_to(root).as_posix(), "Markdown source escapes repository root")
                    continue
                files.append(resolved)
        else:
            reject(target, "scan target is not a Markdown file or directory")
    return sorted({path for path in files})


def prose_lines(text: str):
    """Yield original line numbers outside ordinary backtick/tilde fences."""
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        if fence is not None:
            char, length = fence
            if re.fullmatch(r" {0,3}" + re.escape(char) + "{" + str(length) + r",}\s*", line):
                fence = None
            continue
        opening = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if opening:
            marker = opening.group(1)
            fence = (marker[0], len(marker))
            continue
        yield number, line


def inline_text(text: str) -> str:
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    return text.replace("*", "").replace("~", "")


def github_like_anchor(text: str) -> str:
    text = inline_text(text).strip().lower()
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[^\w\u4e00-\u9fff\-\s]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text.strip("-")


def heading_anchors(path: Path) -> set[str]:
    counts: dict[str, int] = {}
    anchors: set[str] = set()
    for _, line in prose_lines(path.read_text(encoding="utf-8-sig", errors="replace")):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        base = github_like_anchor(match.group(2))
        counts[base] = counts.get(base, 0) + 1
        anchors.add(base if counts[base] == 1 else f"{base}-{counts[base] - 1}")
    return anchors


def extract_links(line: str) -> list[str]:
    # Keep non-empty labels such as [`file`](target.md), while masking syntax
    # inside a complete inline-code example like `[file](missing.md)`.
    line = re.sub(r"(?<!`)(`+)(?!`)(.*?)(?<!`)\1(?!`)", lambda match: "x" * len(match.group(0)), line)
    links: list[str] = []
    pattern = re.compile(r"(?<!!)(?:\[[^\]]+\]\(([^)]+)\)|<((?:\.?\.?/|[^:>\s]+/)[^>\s]*)>)")
    for match in pattern.finditer(line):
        if re.fullmatch(r"</[A-Za-z][A-Za-z0-9:-]*\s*>", match.group(0)):
            continue
        raw = (match.group(1) or match.group(2) or "").strip()
        if raw:
            links.append(raw)
    return links


def link_target(raw_link: str) -> str:
    target = raw_link.strip()
    if target.startswith("<") and ">" in target:
        return target[1 : target.index(">")]
    return target.split()[0].strip("<>")


def check_links(root: Path, targets: list[str]) -> list[dict[str, Any]]:
    root = root.resolve()
    problems: list[dict[str, Any]] = []
    files = iter_markdown_files(root, targets, problems)
    anchors: dict[Path, set[str]] = {}
    for file_path in files:
        try:
            text = file_path.read_text(encoding="utf-8-sig", errors="replace")
        except OSError as exc:
            problems.append(problem(root, file_path, 0, "", f"cannot read Markdown source: {exc}"))
            continue
        for line_no, line in prose_lines(text):
            for raw_link in extract_links(line):
                target = html.unescape(link_target(raw_link))
                target_lower = urllib.parse.unquote(html.unescape(target)).lower()
                if target_lower.startswith(EXTERNAL_PREFIXES):
                    continue
                if target_lower.startswith(UNSAFE_PREFIXES):
                    problems.append(problem(root, file_path, line_no, raw_link, "unsafe scheme"))
                    continue
                path_part, _, fragment = target.partition("#")
                path_part = urllib.parse.unquote(path_part)
                if re.match(r"^[A-Za-z]:", path_part):
                    problems.append(problem(root, file_path, line_no, raw_link, "host-local drive path"))
                    continue
                if re.match(r"^[a-zA-Z]+:", path_part):
                    continue
                try:
                    candidate = file_path if not path_part else (file_path.parent / path_part).resolve()
                except (OSError, ValueError, RuntimeError) as exc:
                    problems.append(problem(root, file_path, line_no, raw_link, f"cannot resolve target: {exc}"))
                    continue
                try:
                    candidate.relative_to(root)
                except ValueError:
                    problems.append(problem(root, file_path, line_no, raw_link, "escapes repository root"))
                    continue
                try:
                    if not candidate.exists():
                        problems.append(problem(root, file_path, line_no, raw_link, "missing target"))
                        continue
                    if fragment and candidate.is_file() and candidate.suffix.lower() == ".md":
                        if candidate not in anchors:
                            anchors[candidate] = heading_anchors(candidate)
                        decoded = urllib.parse.unquote(fragment).lower()
                        if decoded not in anchors[candidate]:
                            problems.append(problem(root, file_path, line_no, raw_link, f"missing anchor #{fragment}"))
                except (OSError, ValueError, RuntimeError) as exc:
                    problems.append(problem(root, file_path, line_no, raw_link, f"cannot inspect target: {exc}"))
    return problems


def problem(root: Path, path: Path, line: int, link: str, message: str) -> dict[str, Any]:
    return {
        "path": path.relative_to(root).as_posix(),
        "line": line,
        "link": link,
        "message": message,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check local Markdown links and heading anchors.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    parser.add_argument("targets", nargs="*", help="Files or directories to scan, relative to root.")
    args = parser.parse_args(argv)

    targets = args.targets or DEFAULT_TARGETS
    try:
        root = Path(args.root).resolve()
        problems = check_links(root, targets)
    except (OSError, ValueError, RuntimeError) as exc:
        problems = [{"path": args.root, "line": 0, "link": "", "message": f"cannot inspect repository: {exc}"}]
    if args.json:
        print(json.dumps({"problems": problems, "problem_count": len(problems)}, indent=2))
    elif problems:
        for item in problems:
            print(f"{item['path']}:{item['line']}: {item['message']}: {item['link']}")
        print(f"markdown link check failed: {len(problems)} problem(s)", file=sys.stderr)
    else:
        print("markdown links ok")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
