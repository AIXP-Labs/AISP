#!/usr/bin/env python3
"""Generate deterministic SKILL.md sidecar bridges from AISP contracts."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


PROTOCOL = "AISP V1.0.0"
GENERATED_MARKER = "<!-- generated_from_aisp: true -->"
SOURCE_MARKER = "<!-- source: aisp.aisop.json -->"
GENERATOR_MARKER = "<!-- generator: tools/aisp_skill_md.py -->"
NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
INJECTION_RE = re.compile(
    r"\b(ignore|disregard|override)\s+(all\s+)?(previous|prior|system|developer)\s+instructions\b|"
    r"\bjailbreak\b|\bexfiltrat(e|ion)\b|\breveal\s+(secrets?|system\s+prompt)\b",
    re.IGNORECASE,
)


def normalize_text(text: str) -> str:
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


def _one_line(value: Any) -> str:
    text = "" if value is None else str(value)
    return " ".join(text.replace("\r\n", "\n").replace("\r", "\n").split())


def _yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _bridge_name(skill_id: str) -> str:
    if skill_id.endswith("_aisp"):
        skill_id = skill_id[: -len("_aisp")]
    name = skill_id.replace("_", "-").lower()
    if not NAME_RE.fullmatch(name):
        raise ValueError(f"cannot derive valid Agent Skills name from AISP id: {skill_id}")
    if any(forbidden in name for forbidden in ("anthropic", "claude")):
        raise ValueError("derived SKILL.md name must not contain anthropic or claude")
    return name


def _summary(system: dict[str, Any]) -> str:
    for field in ("summary", "description", "name", "id"):
        value = _one_line(system.get(field))
        if value:
            return value
    return "Native AISP skill package."


def _list_text(values: Any, limit: int = 2) -> str:
    if not isinstance(values, list):
        return ""
    items = [_one_line(item) for item in values if _one_line(item)]
    return "; ".join(items[:limit])


def _description(system: dict[str, Any], contract: dict[str, Any]) -> str:
    invocation = contract.get("invocation") if isinstance(contract.get("invocation"), dict) else {}
    parts = [f"AISP-backed bridge for {_summary(system)}"]
    use_text = _list_text(invocation.get("when_to_use"), limit=2)
    avoid_text = _list_text(invocation.get("when_not_to_use"), limit=2)
    if use_text:
        parts.append(f"Use when {use_text}")
    if avoid_text:
        parts.append(f"Do not use when {avoid_text}")
    description = ". ".join(part.rstrip(".") for part in parts if part) + "."
    if INJECTION_RE.search(description):
        raise ValueError("derived SKILL.md description contains instruction-injection wording")
    if len(description) > 1024:
        description = description[:1021].rstrip() + "..."
    return description


def _title(system: dict[str, Any], skill_id: str) -> str:
    name = _one_line(system.get("name"))
    if name:
        return name
    return skill_id.replace("_", " ").title()


def _resources(resources: Any) -> list[str]:
    if not isinstance(resources, list) or not resources:
        return ["- No declared resources."]
    lines: list[str] = []
    for resource in resources:
        if not isinstance(resource, dict):
            continue
        path = _one_line(resource.get("path"))
        mode = _one_line(resource.get("mode"))
        kind = _one_line(resource.get("kind"))
        if path:
            suffix = ", ".join(part for part in (kind, mode) if part)
            lines.append(f"- `{path}`" + (f" ({suffix})" if suffix else ""))
    return lines or ["- No declared resources."]


def _non_negotiable(items: Any) -> list[str]:
    if not isinstance(items, list) or not items:
        return ["- Follow the non-negotiable rules declared in `user.content.aisp_contract`."]
    lines: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        rule = _one_line(item.get("rule"))
        enforced_by = _one_line(item.get("enforced_by"))
        if rule and enforced_by:
            lines.append(f"- {rule} (`{enforced_by}`)")
        elif rule:
            lines.append(f"- {rule}")
    return lines or ["- Follow the non-negotiable rules declared in `user.content.aisp_contract`."]


def render_skill_md(skill_path: Path) -> str:
    skill_dir, doc = load_skill(skill_path)
    system = _content(doc, 0)
    user = _content(doc, 1)
    contract = _contract(doc)
    skill_id = _one_line(system.get("id") or skill_dir.name)
    if not skill_id:
        raise ValueError("AISP system.content.id is required to generate SKILL.md")
    name = _bridge_name(skill_id)
    title = _title(system, skill_id)
    instruction = _one_line(user.get("instruction"))
    license_value = _one_line(system.get("license") or "Apache-2.0")
    description = _description(system, contract)

    lines = [
        "---",
        f"name: {_yaml_string(name)}",
        f"description: {_yaml_string(description)}",
        f"license: {_yaml_string(license_value)}",
        "metadata:",
        '  generated_from_aisp: "true"',
        f"  aisp_program: {_yaml_string('aisp.aisop.json')}",
        f"  protocol: {_yaml_string(PROTOCOL)}",
        f"  bridge_mode: {_yaml_string('native_sidecar')}",
        "---",
        "",
        f"# {title} (AISP-backed Agent Skill)",
        "",
        GENERATED_MARKER,
        SOURCE_MARKER,
        GENERATOR_MARKER,
        "",
        "This `SKILL.md` is a thin Agent Skills discovery bridge, not the source of truth. The executable source of truth is the same-folder `aisp.aisop.json` AISP program.",
        "",
        "Deleting this file does not change the native AISP skill. A conforming AISP/AISOP runtime should load `aisp.aisop.json`, read `user.content.aisp_contract`, and run `user.content.aisop.main` exactly as declared.",
        "",
        "## How to use",
        "",
        "1. Load `aisp.aisop.json` from this folder.",
        "2. Read `user.content.aisp_contract` before following any workflow.",
    ]
    if instruction:
        lines.append(f"3. Follow `user.content.instruction`: `{instruction}`.")
    else:
        lines.append("3. Follow `user.content.instruction` from the AISP program.")
    lines.extend(
        [
            "4. Load declared resources only when the AISP graph reaches the node that needs them.",
            "5. Enforce every non-negotiable rule through the mechanism named by `enforced_by`.",
            "",
            "## Declared resources",
            "",
            *_resources(contract.get("resources")),
            "",
            "## Non-negotiable boundaries",
            "",
            *_non_negotiable(contract.get("non_negotiable")),
            "",
            "## Runtime boundary",
            "",
            "Agent Skills platforms can use this bridge to discover and inspect the package. Hard guarantees such as `sys.assert`, `sys.io.confirm`, tool gating, dispatch behavior, and path confinement require a conforming AISP/AISOP runtime. A generic non-AISOP agent can only follow the contract on a best-effort basis.",
            "",
            "Passing `SKILL.md` generation or bridge validation proves only projection consistency and bridge shape. It does not prove external trust, safety, registry approval, or hard execution on a non-AISOP platform.",
            "",
            "Align Axiom 0: Human Sovereignty and Wellbeing. AISP - AI Skill Protocol V1.0.0. www.aisp.dev",
        ]
    )
    return normalize_text("\n".join(lines))


def check_skill_md(skill_path: Path) -> tuple[bool, str]:
    skill_dir, _ = load_skill(skill_path)
    sidecar = skill_dir / "SKILL.md"
    if not sidecar.is_file():
        return False, f"missing {sidecar}"
    expected = render_skill_md(skill_dir)
    actual = read_normalized(sidecar)
    if actual != expected:
        return False, f"drift in {sidecar}"
    return True, f"ok {sidecar}"


def iter_skill_dirs(target: Path) -> list[Path]:
    if target.is_file() and target.name == "aisp.aisop.json":
        return [target.parent.resolve()]
    if target.is_dir() and (target / "aisp.aisop.json").is_file():
        return [target.resolve()]
    if target.is_dir():
        return sorted(path.parent.resolve() for path in target.rglob("aisp.aisop.json") if path.parent.name.endswith("_aisp"))
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic SKILL.md sidecar bridges from AISP contracts.")
    parser.add_argument("target", help="Skill folder, aisp.aisop.json, or directory containing *_aisp skills.")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--write", action="store_true", help="Write SKILL.md for one skill.")
    action.add_argument("--check", action="store_true", help="Check SKILL.md for one skill.")
    action.add_argument("--print", action="store_true", help="Print generated SKILL.md for one skill.")
    action.add_argument("--write-all", action="store_true", help="Write SKILL.md for every *_aisp skill under target.")
    action.add_argument("--check-all", action="store_true", help="Check SKILL.md for every *_aisp skill under target.")
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
                ok, message = check_skill_md(skill_dir)
                if ok:
                    print(f"PASS {message} (projection consistency only; not a trust or safety signal)")
                else:
                    print(f"FAIL {message}")
                failed = failed or not ok
            return 1 if failed else 0
        if args.write or args.write_all:
            for skill_dir in skill_dirs:
                out = skill_dir / "SKILL.md"
                write_lf(out, render_skill_md(skill_dir))
                print(f"Wrote {out}")
            return 0
        print(render_skill_md(skill_dirs[0]), end="")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
