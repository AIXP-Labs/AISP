#!/usr/bin/env python3
"""Lightweight documentation synchronization checks."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


COMMANDS = [
    "python -B tools/aisp_validate.py examples/aisp",
    "python -B tools/aisp_validate.py --json examples/aisp/yijing_aisp",
    "python -B tools/aisp_validate.py --strict-tools --runtime-trace examples/aisp/stock_analysis_aisp/evals/runtime-traces/hard-pass.json examples/aisp/stock_analysis_aisp",
    "python -B tools/aisp_validate.py --strict-tools --runtime-trace examples/aisp/aisp_creator_evolution_aisp/evals/runtime-traces/hard-pass.json examples/aisp/aisp_creator_evolution_aisp",
    "python -B tools/aisp_check_runtime_trace.py examples/aisp/stock_analysis_aisp examples/aisp/stock_analysis_aisp/evals/runtime-traces/hard-pass.json",
    "python -B tools/aisp_hash.py --json examples/aisp/yijing_aisp",
    "python -B examples/aisp/aisp_list.py --check",
    "python -B tools/aisp_readme.py examples --check-all",
    "python -B tools/aisp_skill_md.py examples --check-all",
    "python -B tools/aisp_validate.py --strict-readme examples/aisp",
    "python -B tools/aisp_validate_agent_skill_bridge.py examples/aisp --strict-readme",
    "python -B tools/check_doc_sync.py --root .",
    "python -B tools/check_markdown_links.py --root .",
    "git diff --check",
    "git diff --exit-code",
    "python -B -m unittest discover -s tests",
]

DERIVED_FILE_COMMANDS = [
    "python -B examples/aisp/aisp_list.py --json",
    "python -B tools/aisp_readme.py examples/aisp/yijing_aisp --write",
    "python -B tools/aisp_skill_md.py examples/aisp/yijing_aisp --write",
]

SPEC_COMMANDS = [
    "python -B tools/aisp_validate_agent_skill_bridge.py examples/aisp --strict-readme",
]

WORKFLOW_COMMANDS = [command for command in COMMANDS if command != "git diff --check"] + [
    "git diff-tree --check --root -r HEAD",
]

FORBIDDEN_PATTERNS = [
    (re.compile(r"python tools/aisp_validate_agent_skill_bridge\.py"), "use `python -B tools/aisp_validate_agent_skill_bridge.py`"),
    (re.compile(r"`python aisp_list\.py"), "use `python -B aisp_list.py`"),
    (re.compile(r"^python aisp_list\.py", re.MULTILINE), "use `python -B aisp_list.py`"),
    (re.compile(r"`python aisp/aisp_list\.py"), "use `python -B aisp/aisp_list.py`"),
    (re.compile(r"python -m json\.tool examples/aisp/aisp_list\.json"), "use `python -B -m json.tool examples/aisp/aisp_list.json`"),
]

EMBEDDED_SPEC_FORBIDDEN_LINKS = [
    "](../adrs/",
    "](../docs/",
    "](../schemas/",
]

SNAPSHOT_DIRS = [
    Path("examples/aisp/aisp_creator_evolution_aisp/aisp_specification"),
    Path("examples/aisp/aisp_creator_evolution_aisp/aisp_protocol_schemas"),
    Path("examples/aisp/aisp_creator_evolution_aisp/aisp_reference_tools"),
    Path("examples/aisp/aisp_creator_evolution_aisp/aisop_specification"),
]


def check_file_contains(path: Path, needles: list[str]) -> list[str]:
    text = path.read_text(encoding="utf-8-sig")
    return [needle for needle in needles if needle not in text]


def check_forbidden_patterns(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8-sig")
    failures: list[str] = []
    for pattern, replacement in FORBIDDEN_PATTERNS:
        if pattern.search(text):
            failures.append(f"{path}: old command form matched `{pattern.pattern}`; {replacement}")
    return failures


def _readme_field(text: str, name: str) -> str | None:
    match = re.search(rf"^- {re.escape(name)}: `([^`]+)`", text, flags=re.MULTILINE)
    return match.group(1) if match else None


def check_snapshot_metadata(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_dir in SNAPSHOT_DIRS:
        directory = root / rel_dir
        readme_path = directory / "README.md"
        manifest_path = directory / "MANIFEST.sha256.json"
        if not readme_path.exists() or not manifest_path.exists():
            failures.append(f"{directory}: missing README.md or MANIFEST.sha256.json")
            continue
        readme = readme_path.read_text(encoding="utf-8-sig")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        readme_commit = _readme_field(readme, "source commit")
        readme_date = _readme_field(readme, "snapshot date")
        if readme_commit != manifest.get("source_commit"):
            failures.append(f"{readme_path}: source commit differs from manifest")
        if readme_date != manifest.get("snapshot_date"):
            failures.append(f"{readme_path}: snapshot date differs from manifest")
        manifest_state = manifest.get("snapshot_state")
        if manifest_state and _readme_field(readme, "snapshot state") != manifest_state:
            failures.append(f"{readme_path}: snapshot state differs from manifest")
    return failures


def check_snapshot_manifest_integrity(root: Path) -> list[str]:
    failures: list[str] = []
    metadata_names = {"README.md", "MANIFEST.sha256.json"}
    for rel_dir in SNAPSHOT_DIRS:
        directory = root / rel_dir
        manifest_path = directory / "MANIFEST.sha256.json"
        if not manifest_path.exists():
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            failures.append(f"{manifest_path}: cannot read manifest: {exc}")
            continue
        seen: set[str] = set()
        files = manifest.get("files")
        if not isinstance(files, list):
            failures.append(f"{manifest_path}: files must be a list")
            continue
        for item in files:
            if not isinstance(item, dict) or not isinstance(item.get("path"), str):
                failures.append(f"{manifest_path}: each files[] entry must contain a string path")
                continue
            rel_path = item["path"]
            if rel_path in seen:
                failures.append(f"{manifest_path}: duplicate manifest path {rel_path}")
                continue
            seen.add(rel_path)
            file_path = directory / rel_path
            if not file_path.is_file():
                failures.append(f"{manifest_path}: listed file is missing: {rel_path}")
                continue
            data = file_path.read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            if item.get("bytes") != len(data):
                failures.append(f"{manifest_path}: byte count mismatch for {rel_path}")
            if item.get("sha256") != digest:
                failures.append(f"{manifest_path}: sha256 mismatch for {rel_path}")
        actual = {
            path.relative_to(directory).as_posix()
            for path in directory.rglob("*")
            if path.is_file() and path.name not in metadata_names
        }
        unlisted = sorted(actual - seen)
        if unlisted:
            failures.append(f"{manifest_path}: unlisted snapshot source files: {', '.join(unlisted)}")
    return failures


def check_embedded_spec_links(root: Path) -> list[str]:
    failures: list[str] = []
    spec_dir = root / "examples" / "aisp" / "aisp_creator_evolution_aisp" / "aisp_specification"
    for path in [spec_dir / "AISP_Protocol.md", spec_dir / "AISP_Protocol_cn.md"]:
        text = path.read_text(encoding="utf-8-sig")
        for forbidden in EMBEDDED_SPEC_FORBIDDEN_LINKS:
            if forbidden in text:
                failures.append(f"{path}: embedded snapshot contains repo-relative companion link `{forbidden}`")
    return failures


def check_adr_mirrors(root: Path) -> list[str]:
    failures: list[str] = []
    adr_root = root / "adrs"
    docs_adr_root = root / "docs" / "adrs"
    for source in sorted(adr_root.glob("adr-*.md")):
        if source.name == "adr-template.md":
            continue
        mirror = docs_adr_root / source.name
        if not mirror.exists():
            failures.append(f"{mirror}: missing ADR mirror for {source}")
            continue
        source_text = source.read_text(encoding="utf-8-sig")
        mirror_text = mirror.read_text(encoding="utf-8-sig")
        if source_text != mirror_text:
            failures.append(f"{mirror}: differs from {source}")
    return failures


def check_workflow(root: Path) -> list[str]:
    workflow = root / ".github" / "workflows" / "validate.yml"
    if not workflow.exists():
        return [f"{workflow}: missing validation workflow"]
    text = workflow.read_text(encoding="utf-8-sig")
    failures = [f"{workflow}: missing `{command}`" for command in WORKFLOW_COMMANDS if command not in text]
    if "examples/agent_skills_examples" in text:
        failures.append(f"{workflow}: old external Agent Skills bridge path is forbidden; use examples/aisp")
    if re.search(r"run:\s+python (?!-B|-m pip)", text):
        failures.append(f"{workflow}: repository tool commands should use `python -B`")
    return failures


def check_retired_external_bridge_layout(root: Path) -> list[str]:
    retired = root / "examples" / "agent_skills_examples"
    if retired.exists():
        return [f"{retired}: retired external Agent Skills bridge layout must not exist; use same-folder SKILL.md sidecars under examples/aisp"]
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check AISP documentation synchronization.")
    parser.add_argument("--root", default=".", help="Repository root.")
    args = parser.parse_args(argv)
    root = Path(args.root)
    targets = [
        root / "README.md",
        root / "README_CN.md",
        root / "docs" / "guides" / "conformance-walkthrough.md",
        root / "docs" / "guides" / "conformance-walkthrough_CN.md",
        root / "docs" / "reference" / "validator-coverage.md",
        root / "docs" / "reference" / "release-evidence-matrix.md",
        root / "docs" / "reference" / "release-evidence-matrix_CN.md",
    ]
    spec_targets = [
        root / "specification" / "AISP_Protocol.md",
        root / "specification" / "AISP_Protocol_cn.md",
        root / "examples" / "aisp" / "aisp_creator_evolution_aisp" / "aisp_specification" / "AISP_Protocol.md",
        root / "examples" / "aisp" / "aisp_creator_evolution_aisp" / "aisp_specification" / "AISP_Protocol_cn.md",
    ]
    forbidden_targets = [
        root / "examples" / "README.md",
        root / "examples" / "aisp" / "README.md",
        root / "docs" / "guides" / "discovering-skills.md",
        root / "docs" / "guides" / "first-aisp-skill.md",
        root / "docs" / "topics" / "discovery-and-registry.md",
        root / "docs" / "reference" / "error-codes.md",
        root / "specification" / "AISP_Protocol.md",
        root / "specification" / "AISP_Protocol_cn.md",
        root / "specification" / "standards" / "AISP_Standard.core.aisop.json",
        root / "examples" / "aisp" / "aisp_list.py",
        root / "examples" / "aisp" / "aisp_creator_evolution_aisp" / "aisp_specification" / "AISP_Protocol.md",
        root / "examples" / "aisp" / "aisp_creator_evolution_aisp" / "aisp_specification" / "AISP_Protocol_cn.md",
        root / "examples" / "aisp" / "aisp_creator_evolution_aisp" / "aisp_specification" / "standards" / "AISP_Standard.core.aisop.json",
    ]
    failures: list[str] = []
    for target in targets:
        expected = list(COMMANDS)
        if target.name in {"README.md", "README_CN.md"}:
            expected.extend(DERIVED_FILE_COMMANDS)
        missing = check_file_contains(target, expected)
        for command in missing:
            failures.append(f"{target}: missing `{command}`")
    for target in spec_targets:
        missing = check_file_contains(target, SPEC_COMMANDS)
        for command in missing:
            failures.append(f"{target}: missing `{command}`")
    for target in forbidden_targets:
        failures.extend(check_forbidden_patterns(target))
    failures.extend(check_snapshot_metadata(root))
    failures.extend(check_snapshot_manifest_integrity(root))
    failures.extend(check_embedded_spec_links(root))
    failures.extend(check_adr_mirrors(root))
    failures.extend(check_workflow(root))
    failures.extend(check_retired_external_bridge_layout(root))
    if failures:
        print("\n".join(failures))
        return 1
    print("doc sync ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
