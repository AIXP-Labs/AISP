#!/usr/bin/env python3
"""Generate deterministic per-skill README.md files from AISP contracts."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from .aisp_hash import compute_manifest
except ImportError:  # pragma: no cover - script execution path
    from aisp_hash import compute_manifest


GENERATED_MARKER = "<!-- generated_from_aisp: true -->"
SOURCE_MARKER = "<!-- source: aisp.aisop.json -->"
GENERATOR_MARKER = "<!-- generator: tools/aisp_readme.py -->"


def normalize_text(text: str) -> str:
    """Normalize generated/check input to UTF-8 text semantics with LF endings."""
    if text.startswith("\ufeff"):
        text = text[1:]
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.rstrip("\n") + "\n"


def read_normalized(path: Path) -> str:
    return normalize_text(path.read_text(encoding="utf-8-sig"))


def write_lf(path: Path, text: str) -> None:
    path.write_text(normalize_text(text), encoding="utf-8", newline="\n")


def load_skill(skill_path: Path) -> tuple[Path, list[Any]]:
    skill_dir = skill_path if skill_path.is_dir() else skill_path.parent
    skill_file = skill_dir / "aisp.aisop.json" if skill_path.is_dir() else skill_path
    doc = json.loads(skill_file.read_text(encoding="utf-8-sig"))
    if not isinstance(doc, list) or len(doc) != 2:
        raise ValueError(f"{skill_file} must be a two-message AISP JSON array")
    return skill_dir.resolve(), doc


def _content(doc: list[Any], index: int) -> dict[str, Any]:
    if index >= len(doc) or not isinstance(doc[index], dict):
        return {}
    content = doc[index].get("content")
    return content if isinstance(content, dict) else {}


def _contract(doc: list[Any]) -> dict[str, Any]:
    user = _content(doc, 1)
    contract = user.get("aisp_contract")
    return contract if isinstance(contract, dict) else {}


def _md(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", r"\|").replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>")


def _list_lines(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [f"- {_md(item)}" for item in values if isinstance(item, (str, int, float))]


def _purpose(system: dict[str, Any], contract: dict[str, Any]) -> str:
    discovery = contract.get("discovery") if isinstance(contract.get("discovery"), dict) else {}
    if isinstance(system.get("summary"), str) and system["summary"].strip():
        return system["summary"].strip()
    if isinstance(discovery.get("summary"), str) and discovery["summary"].strip():
        return discovery["summary"].strip()
    if isinstance(system.get("name"), str) and system["name"].strip():
        return system["name"].strip()
    category = discovery.get("category")
    tags = discovery.get("tags")
    parts = []
    if isinstance(category, str) and category.strip():
        parts.append(category.strip())
    if isinstance(tags, list):
        parts.extend(str(tag).strip() for tag in tags if str(tag).strip())
    if parts:
        return "AISP skill for " + ", ".join(parts) + "."
    return str(system.get("id") or "AISP skill")


def _resources_table(resources: Any) -> list[str]:
    if not isinstance(resources, list) or not resources:
        return ["No declared resources."]
    rows = ["| ID | Path | Kind | Mode | Scope | SHA-256 |", "| --- | --- | --- | --- | --- | --- |"]
    for resource in resources:
        if not isinstance(resource, dict):
            continue
        rows.append(
            "| "
            + " | ".join(
                _md(resource.get(field, "skill" if field == "scope" else ""))
                for field in ("id", "path", "kind", "mode", "scope")
            )
            + f" | {_md(resource.get('sha256', ''))} |"
        )
    return rows if len(rows) > 2 else ["No declared resources."]


def _non_negotiable_table(items: Any) -> list[str]:
    if not isinstance(items, list) or not items:
        return ["No non-negotiable rules declared."]
    rows = ["| Rule | Enforced By |", "| --- | --- |"]
    for item in items:
        if isinstance(item, dict):
            rows.append(f"| {_md(item.get('rule', ''))} | `{_md(item.get('enforced_by', ''))}` |")
    return rows if len(rows) > 2 else ["No non-negotiable rules declared."]


def render_readme(skill_path: Path) -> str:
    skill_dir, doc = load_skill(skill_path)
    system = _content(doc, 0)
    user = _content(doc, 1)
    contract = _contract(doc)
    invocation = contract.get("invocation") if isinstance(contract.get("invocation"), dict) else {}
    discovery = contract.get("discovery") if isinstance(contract.get("discovery"), dict) else {}
    manifest = compute_manifest(skill_dir)

    lines: list[str] = [
        GENERATED_MARKER,
        SOURCE_MARKER,
        GENERATOR_MARKER,
        "",
        f"# {_md(system.get('name') or system.get('id') or skill_dir.name)}",
        "",
        "This README is a deterministic projection of `aisp.aisop.json`. The contract remains the source of truth.",
        "",
        "## Identity",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Skill ID | `{_md(system.get('id') or skill_dir.name)}` |",
        f"| Version | `{_md(system.get('version', ''))}` |",
        f"| Protocol | `{_md(system.get('protocol', ''))}` |",
        f"| License | `{_md(system.get('license', ''))}` |",
        f"| Risk Level | `{_md(contract.get('risk_level', 'unspecified'))}` |",
        f"| Category | {_md(discovery.get('category', ''))} |",
        f"| Tags | {_md(', '.join(str(tag) for tag in discovery.get('tags', []) if isinstance(discovery.get('tags'), list)))} |",
        "",
        "## Purpose",
        "",
        _md(_purpose(system, contract)),
        "",
        "## When To Use",
        "",
        *(_list_lines(invocation.get("when_to_use")) or ["- See `aisp_contract.invocation.when_to_use`."]),
        "",
        "## When Not To Use",
        "",
        *(_list_lines(invocation.get("when_not_to_use")) or ["- See `aisp_contract.invocation.when_not_to_use`."]),
        "",
        "## How To Run",
        "",
        "With an AISOP runtime:",
        "",
        "1. Load `aisp.aisop.json`.",
        "2. Read `user.content.aisp_contract` before execution.",
        "3. Run `user.content.aisop.main` exactly as declared.",
        "4. Enforce every `non_negotiable` rule and every referenced `sys.*` mechanism.",
        "5. Treat `sys.io.confirm` and other human-confirmation gates as blocking controls.",
        "",
        "With a generic AI or non-AISOP agent:",
        "",
        "- Treat this README as bootstrap guidance only.",
        "- Verify external provenance or obtain explicit human approval before executing an untrusted package.",
        "- Load the contract from `aisp.aisop.json`; do not treat this README as authoritative.",
        "- Follow `RUN aisop.main` and the non-negotiable rules on a best-effort basis.",
        "- Hard guarantees such as `sys.assert`, tool gating, and `sys.io.confirm` exist only in a conforming AISOP runtime.",
        "",
        "## Non-Negotiable Rules",
        "",
        *_non_negotiable_table(contract.get("non_negotiable")),
        "",
        "## Resources",
        "",
        *_resources_table(contract.get("resources")),
        "",
        "## Integrity",
        "",
        "| Hash | Value | Meaning |",
        "| --- | --- | --- |",
        f"| `contract_sha256` | `{manifest.get('contract_sha256')}` | Recomputable hash of `user.content.aisp_contract` |",
        f"| `resources_sha256` | `{manifest.get('resources_sha256')}` | Recomputable hash of declared resource records |",
        "",
        "`package_sha256` is intentionally not embedded here because a README is part of the distributed package and package-level hashes belong in external registry/provenance artifacts. Recompute it with `tools/aisp_hash.py` at publication time.",
        "",
        "These hashes show local integrity only. They do not prove trust, safety, or registry approval.",
        "",
        "## Source Of Truth",
        "",
        "`aisp.aisop.json` is authoritative. A successful README check proves only that this file matches the contract-derived projection; it does not prove that the skill is safe or trustworthy.",
    ]
    return normalize_text("\n".join(lines))


def check_readme(skill_path: Path) -> tuple[bool, str]:
    skill_dir, _ = load_skill(skill_path)
    readme = skill_dir / "README.md"
    if not readme.is_file():
        return False, f"missing {readme}"
    expected = render_readme(skill_dir)
    actual = read_normalized(readme)
    if actual != expected:
        return False, f"drift in {readme}"
    return True, f"ok {readme}"


def iter_skill_dirs(target: Path) -> list[Path]:
    if target.is_file() and target.name == "aisp.aisop.json":
        return [target.parent.resolve()]
    if target.is_dir() and (target / "aisp.aisop.json").is_file():
        return [target.resolve()]
    if target.is_dir():
        return sorted(path.parent.resolve() for path in target.rglob("aisp.aisop.json") if path.parent.name.endswith("_aisp"))
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic per-skill README.md files from AISP contracts.")
    parser.add_argument("target", help="Skill folder, aisp.aisop.json, or directory containing *_aisp skills.")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--write", action="store_true", help="Write README.md for one skill.")
    action.add_argument("--check", action="store_true", help="Check README.md for one skill.")
    action.add_argument("--print", action="store_true", help="Print generated README for one skill.")
    action.add_argument("--write-all", action="store_true", help="Write README.md for every *_aisp skill under target.")
    action.add_argument("--check-all", action="store_true", help="Check README.md for every *_aisp skill under target.")
    args = parser.parse_args(argv)

    target = Path(args.target)
    skill_dirs = iter_skill_dirs(target)
    if not skill_dirs:
        print(f"ERROR: no AISP skill found under {target}", file=sys.stderr)
        return 1
    wants_all = args.write_all or args.check_all
    if len(skill_dirs) != 1 and not wants_all:
        print("ERROR: target contains multiple skills; use --write-all or --check-all", file=sys.stderr)
        return 1

    try:
        if args.check or args.check_all:
            failed = False
            for skill_dir in skill_dirs:
                ok, message = check_readme(skill_dir)
                if ok:
                    print(f"PASS {message} (derivation consistency only; not a trust or safety signal)")
                else:
                    print(f"FAIL {message}")
                failed = failed or not ok
            return 1 if failed else 0
        if args.write or args.write_all:
            for skill_dir in skill_dirs:
                out = skill_dir / "README.md"
                write_lf(out, render_readme(skill_dir))
                print(f"Wrote {out}")
            return 0
        print(render_readme(skill_dirs[0]), end="")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
