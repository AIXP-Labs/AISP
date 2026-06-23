#!/usr/bin/env python3
"""Check local Markdown links and heading anchors."""
from __future__ import annotations

import argparse
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


def iter_markdown_files(root: Path, targets: list[str]) -> list[Path]:
    files: list[Path] = []
    for target in targets:
        path = (root / target).resolve()
        if not path.exists():
            continue
        if path.is_file() and path.suffix.lower() == ".md":
            files.append(path)
        elif path.is_dir():
            files.extend(sorted(path.rglob("*.md")))
    return sorted({path for path in files})


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
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        base = github_like_anchor(match.group(2))
        counts[base] = counts.get(base, 0) + 1
        anchors.add(base if counts[base] == 1 else f"{base}-{counts[base] - 1}")
    return anchors


def extract_links(line: str) -> list[str]:
    links: list[str] = []
    pattern = re.compile(r"(?<!!)(?:\[[^\]]+\]\(([^)]+)\)|<((?:\.?\.?/|[^:>\s]+/)[^>\s]*)>)")
    for match in pattern.finditer(line):
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
    files = iter_markdown_files(root, targets)
    anchors: dict[Path, set[str]] = {}
    problems: list[dict[str, Any]] = []
    for file_path in files:
        text = file_path.read_text(encoding="utf-8-sig", errors="replace")
        for line_no, line in enumerate(text.splitlines(), 1):
            for raw_link in extract_links(line):
                target = link_target(raw_link)
                target_lower = target.lower()
                if target_lower.startswith(EXTERNAL_PREFIXES):
                    continue
                if target_lower.startswith(UNSAFE_PREFIXES):
                    problems.append(problem(root, file_path, line_no, raw_link, "unsafe scheme"))
                    continue
                path_part, _, fragment = target.partition("#")
                path_part = urllib.parse.unquote(path_part)
                if re.match(r"^[a-zA-Z]+:", path_part):
                    continue
                candidate = file_path if not path_part else (file_path.parent / path_part).resolve()
                try:
                    candidate.relative_to(root)
                except ValueError:
                    problems.append(problem(root, file_path, line_no, raw_link, "escapes repository root"))
                    continue
                if not candidate.exists():
                    problems.append(problem(root, file_path, line_no, raw_link, "missing target"))
                    continue
                if fragment and candidate.is_file() and candidate.suffix.lower() == ".md":
                    if candidate not in anchors:
                        anchors[candidate] = heading_anchors(candidate)
                    decoded = urllib.parse.unquote(fragment).lower()
                    if decoded not in anchors[candidate]:
                        problems.append(problem(root, file_path, line_no, raw_link, f"missing anchor #{fragment}"))
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

    root = Path(args.root).resolve()
    targets = args.targets or DEFAULT_TARGETS
    problems = check_links(root, targets)
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
