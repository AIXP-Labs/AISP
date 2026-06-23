#!/usr/bin/env python3
"""Read-only release gate for generated AISP candidate packages.

This checker complements static M1-M6 validation with checks that were exposed
by real candidate generation:

* default output path semantics: absent output_path means sibling of this
  creator skill, not cwd/repo/home
* deterministic README and SKILL.md projections
* no candidate-internal aisp/ wrapper; any parent-level aisp/ registry is fixed
  external infrastructure outside creator scope
* default same-folder SKILL.md sidecar strictness, including missing-sidecar
  release blocking unless the author explicitly opted out, plus EC7 WARNs that
  are release-blocking for generated candidates
* replayable behavior evidence for executable script resources
* reviewable behavior cases for non-script / model-mediated skills
* parseable schema resources and behavior-case input parameter alignment
* neutral candidate id / folder / SKILL.md name for known third-party source identity terms

Read-only, stdlib-only, no network. Exit code 0 = pass, 1 = fail.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


RELEASE_BLOCKING_EC7_WARNS = {
    "AISP_W_EC7_PROTOCOL",
    "AISP_W_EC7_BRIDGE_MODE",
    "AISP_W_EC7_RUNTIME_BOUNDARY",
    "AISP_W_EC7_LOGIC_COPY",
}
SCRIPT_MODES = {"execute_only", "read_and_execute"}
SCRIPT_CASE_KINDS = {"positive", "boundary", "failure"}
BEHAVIOR_CASE_KINDS = {"positive", "boundary", "failure"}
CACHE_DIR_NAMES = {"__pycache__", ".evolution_snapshot", ".version_history"}
CACHE_FILE_SUFFIXES = {".pyc", ".pyo"}
RESERVED_SOURCE_NAME_TERMS = {"anthropic", "claude"}


def add(report: dict[str, Any], severity: str, code: str, message: str, path: Path | None = None) -> None:
    item: dict[str, Any] = {"severity": severity, "code": code, "message": message}
    if path is not None:
        item["path"] = str(path).replace("\\", "/")
    report["results"].append(item)


def load_skill(candidate_root: Path, report: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    skill_file = candidate_root / "aisp.aisop.json"
    if not skill_file.is_file():
        add(report, "FAIL", "AISP_E_CANDIDATE_MISSING", "candidate root has no aisp.aisop.json", skill_file)
        return {}, {}
    try:
        doc = json.loads(skill_file.read_text(encoding="utf-8-sig"))
    except Exception as exc:  # noqa: BLE001
        add(report, "FAIL", "AISP_E_CANDIDATE_JSON", f"cannot parse aisp.aisop.json: {exc}", skill_file)
        return {}, {}
    if not isinstance(doc, list) or len(doc) != 2:
        add(report, "FAIL", "AISP_E_CANDIDATE_SHAPE", "aisp.aisop.json must be a two-message array", skill_file)
        return {}, {}
    system = doc[0].get("content") if isinstance(doc[0], dict) else {}
    user = doc[1].get("content") if isinstance(doc[1], dict) else {}
    return (system if isinstance(system, dict) else {}, user if isinstance(user, dict) else {})


def run_process(argv: list[str], cwd: Path, stdin: str | None = None, timeout: int = 30) -> dict[str, Any]:
    proc = subprocess.run(
        argv,
        cwd=str(cwd),
        input=stdin,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )
    return {
        "argv": argv,
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def check_location(candidate_root: Path, creator_root: Path, output_path: str | None, report: dict[str, Any]) -> None:
    expected_parent = Path(output_path).resolve() if output_path else creator_root.parent.resolve()
    actual_parent = candidate_root.parent.resolve()
    if actual_parent != expected_parent:
        add(
            report,
            "FAIL",
            "AISP_E_CANDIDATE_LOCATION",
            f"candidate parent {actual_parent} does not match expected parent {expected_parent}",
            candidate_root,
        )


def check_reference_tools(candidate_root: Path, creator_root: Path, allow_missing_sidecar: bool, report: dict[str, Any]) -> None:
    validator = creator_root / "aisp_reference_tools" / "aisp_validate.py"
    readme = creator_root / "aisp_reference_tools" / "aisp_readme.py"
    skill_md = creator_root / "aisp_reference_tools" / "aisp_skill_md.py"
    for script in (validator, readme, skill_md):
        if not script.is_file():
            add(report, "FAIL", "AISP_E_CANDIDATE_TOOL_MISSING", f"missing checker {script}", script)
            return

    proc = run_process([sys.executable, "-B", str(validator), "--strict-readme", str(candidate_root)], creator_root)
    report["artifacts"]["reference_validator"] = {
        "exit_code": proc["exit_code"],
        "stdout": proc["stdout"].strip(),
        "stderr": proc["stderr"].strip(),
    }
    if proc["exit_code"] != 0:
        add(report, "FAIL", "AISP_E_CANDIDATE_REFERENCE_VALIDATION", "reference validator failed", candidate_root)

    proc = run_process([sys.executable, "-B", str(readme), str(candidate_root), "--check"], creator_root)
    report["artifacts"]["readme_check"] = {
        "exit_code": proc["exit_code"],
        "stdout": proc["stdout"].strip(),
        "stderr": proc["stderr"].strip(),
    }
    if proc["exit_code"] != 0:
        add(report, "FAIL", "AISP_E_CANDIDATE_README_DRIFT", "README.md is not the deterministic AISP projection", candidate_root / "README.md")

    if (candidate_root / "SKILL.md").is_file() or not allow_missing_sidecar:
        proc = run_process([sys.executable, "-B", str(skill_md), str(candidate_root), "--check"], creator_root)
        report["artifacts"]["skill_md_check"] = {
            "exit_code": proc["exit_code"],
            "stdout": proc["stdout"].strip(),
            "stderr": proc["stderr"].strip(),
        }
        if proc["exit_code"] != 0:
            add(report, "FAIL", "AISP_E_CANDIDATE_SKILL_MD_DRIFT", "SKILL.md is not the deterministic AISP sidecar projection", candidate_root / "SKILL.md")
    else:
        report["artifacts"]["skill_md_check"] = {"skipped": "explicit Agent Skills sidecar opt-out"}


def check_no_internal_aisp_wrapper(candidate_root: Path, report: dict[str, Any]) -> None:
    internal = candidate_root / "aisp"
    if internal.exists():
        add(
            report,
            "FAIL",
            "AISP_E_CANDIDATE_INTERNAL_AISP_WRAPPER",
            "candidate packages must not contain an internal aisp/ wrapper; parent-level aisp/ infrastructure is external to this creator",
            internal,
        )


def iter_skill_md(candidate_root: Path) -> list[Path]:
    return sorted(path for path in candidate_root.rglob("SKILL.md") if ".git" not in path.parts)


def _blocked_source_terms(value: str) -> list[str]:
    text = value.lower().replace("_", "-")
    return sorted(term for term in RESERVED_SOURCE_NAME_TERMS if term in text)


def _read_sidecar_name(sidecar: Path) -> str:
    for line in sidecar.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if stripped.startswith("name:"):
            return stripped.split(":", 1)[1].strip().strip('"\'')
        if stripped == "---" and line != sidecar.read_text(encoding="utf-8-sig").splitlines()[0]:
            break
    return ""


def check_source_name_neutrality(candidate_root: Path, system: dict[str, Any], report: dict[str, Any]) -> None:
    """Keep source/platform identity out of distributable package identifiers.

    Attribution belongs in resources/references, not in package id, folder name,
    or Agent Skills sidecar trigger name. This prevents converted third-party
    skills from looking like official platform/vendor skills.
    """
    checks = {
        "folder": candidate_root.name,
        "system.id": str(system.get("id", "")),
    }
    sidecar = candidate_root / "SKILL.md"
    if sidecar.is_file():
        checks["SKILL.md name"] = _read_sidecar_name(sidecar)
    for label, value in checks.items():
        blocked = _blocked_source_terms(value)
        if blocked:
            add(
                report,
                "FAIL",
                "AISP_E_CANDIDATE_SOURCE_NAME_LEAK",
                f"{label} contains reserved third-party source identity term(s) {blocked}; use a neutral adapter id/name and keep source attribution in resources/references",
                candidate_root if label != "SKILL.md name" else sidecar,
            )


def check_sidecar(
    candidate_root: Path,
    creator_root: Path,
    system: dict[str, Any],
    allow_missing_sidecar: bool,
    report: dict[str, Any],
) -> None:
    sidecars = iter_skill_md(candidate_root)
    for sidecar in sidecars:
        rel_parts = sidecar.relative_to(candidate_root).parts
        rel_text = "/".join(rel_parts)
        if sidecar.parent != candidate_root:
            add(report, "FAIL", "AISP_E_CANDIDATE_SIDECAR_LOCATION", "SKILL.md must be same-folder with aisp.aisop.json", sidecar)
        if "examples" in rel_parts and "agent_skills_examples" in rel_parts:
            add(report, "FAIL", "AISP_E_CANDIDATE_EXTERNAL_BRIDGE", "old examples/agent_skills_examples bridge layout is forbidden", sidecar)
        if "/aisp/" in f"/{rel_text}/":
            add(report, "FAIL", "AISP_E_CANDIDATE_NESTED_BRIDGE", "nested aisp/<id>_aisp bridge package layout is forbidden", sidecar)
    if not (candidate_root / "SKILL.md").is_file():
        if allow_missing_sidecar:
            add(
                report,
                "WARN",
                "AISP_W_CANDIDATE_SIDECAR_OPT_OUT",
                "same-folder SKILL.md sidecar is missing under an explicit opt-out; core AISP conformance may still pass",
                candidate_root,
            )
        else:
            add(
                report,
                "FAIL",
                "AISP_E_CANDIDATE_SIDECAR_MISSING_DEFAULT",
                "generated/distributed candidates must include a same-folder SKILL.md sidecar by default unless the author explicitly opts out",
                candidate_root / "SKILL.md",
            )
        return

    bridge_validator = creator_root / "aisp_reference_tools" / "aisp_validate_agent_skill_bridge.py"
    proc = run_process([sys.executable, "-B", str(bridge_validator), "--json", str(candidate_root)], creator_root)
    try:
        payload = json.loads(proc["stdout"])
    except Exception:
        payload = {"conformant": False, "summary": {"fail": 1}, "reports": []}
    report["artifacts"]["bridge_validator"] = payload
    if proc["exit_code"] != 0 or not payload.get("conformant", False):
        add(report, "FAIL", "AISP_E_CANDIDATE_BRIDGE_VALIDATION", "Agent Skills sidecar validation failed", candidate_root / "SKILL.md")
    for bridge_report in payload.get("reports", []):
        for result in bridge_report.get("results", []):
            if result.get("code") in RELEASE_BLOCKING_EC7_WARNS:
                add(
                    report,
                    "FAIL",
                    "AISP_E_CANDIDATE_BRIDGE_WARN_RELEASE_BLOCK",
                    f"release-blocking EC7 warning: {result.get('code')}",
                    candidate_root / "SKILL.md",
                )
    summary = system.get("summary")
    text = (candidate_root / "SKILL.md").read_text(encoding="utf-8-sig")
    if isinstance(summary, str) and summary.strip() and summary.strip() not in text:
        add(report, "FAIL", "AISP_E_CANDIDATE_BRIDGE_SUMMARY_DRIFT", "SKILL.md must include system.summary exactly as a single line", candidate_root / "SKILL.md")


def script_resources(user: dict[str, Any]) -> list[dict[str, Any]]:
    contract = user.get("aisp_contract") if isinstance(user.get("aisp_contract"), dict) else {}
    resources = contract.get("resources") if isinstance(contract.get("resources"), list) else []
    return [
        resource
        for resource in resources
        if isinstance(resource, dict)
        and resource.get("kind") == "script"
        and resource.get("mode") in SCRIPT_MODES
        and isinstance(resource.get("path"), str)
    ]


def resource_paths(user: dict[str, Any]) -> set[str]:
    contract = user.get("aisp_contract") if isinstance(user.get("aisp_contract"), dict) else {}
    resources = contract.get("resources") if isinstance(contract.get("resources"), list) else []
    return {
        resource.get("path", "").replace("\\", "/")
        for resource in resources
        if isinstance(resource, dict) and isinstance(resource.get("path"), str)
    }


def contract_resources(user: dict[str, Any]) -> list[dict[str, Any]]:
    contract = user.get("aisp_contract") if isinstance(user.get("aisp_contract"), dict) else {}
    resources = contract.get("resources") if isinstance(contract.get("resources"), list) else []
    return [resource for resource in resources if isinstance(resource, dict)]


def schema_resources(user: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        resource
        for resource in contract_resources(user)
        if resource.get("kind") == "schema" and isinstance(resource.get("path"), str)
    ]


def check_schema_resources(candidate_root: Path, user: dict[str, Any], report: dict[str, Any]) -> None:
    schemas = schema_resources(user)
    report["artifacts"]["schema_resources"] = [schema.get("path") for schema in schemas]
    for resource in schemas:
        rel = resource["path"].replace("\\", "/")
        path = candidate_root / rel
        if not path.is_file():
            add(report, "FAIL", "AISP_E_CANDIDATE_SCHEMA_MISSING", f"schema resource does not exist: {rel}", path)
            continue
        try:
            doc = json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception as exc:  # noqa: BLE001
            add(report, "FAIL", "AISP_E_CANDIDATE_SCHEMA_JSON", f"schema resource is not valid JSON: {exc}", path)
            continue
        if not isinstance(doc, dict):
            add(report, "FAIL", "AISP_E_CANDIDATE_SCHEMA_SHAPE", "schema resource must be a JSON object", path)
            continue
        if "$schema" not in doc:
            add(report, "FAIL", "AISP_E_CANDIDATE_SCHEMA_DIALECT", "schema resource must declare $schema", path)
        if not any(key in doc for key in ("type", "properties", "oneOf", "anyOf", "allOf", "$ref")):
            add(report, "FAIL", "AISP_E_CANDIDATE_SCHEMA_SHAPE", "schema resource lacks recognizable JSON Schema constraint keywords", path)


def load_script_evidence(candidate_root: Path, report: dict[str, Any]) -> dict[str, Any] | None:
    path = candidate_root / "evals" / "script-behavior.json"
    if not path.is_file():
        add(report, "FAIL", "AISP_E_CANDIDATE_SCRIPT_EVIDENCE_MISSING", "script resources require evals/script-behavior.json", path)
        return None
    try:
        doc = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:  # noqa: BLE001
        add(report, "FAIL", "AISP_E_CANDIDATE_SCRIPT_EVIDENCE_JSON", f"script behavior evidence is not valid JSON: {exc}", path)
        return None
    if not isinstance(doc, dict):
        add(report, "FAIL", "AISP_E_CANDIDATE_SCRIPT_EVIDENCE_JSON", "script behavior evidence must be an object", path)
        return None
    return doc


def normalize_argv(argv: list[Any]) -> list[str] | None:
    if not argv or not all(isinstance(item, str) for item in argv):
        return None
    out = list(argv)
    if out[0] in {"python", "python3", "py"}:
        out[0] = sys.executable
    return out


def case_matches(proc: dict[str, Any], case: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    expected_exit = case.get("expected_exit", 0)
    if proc["exit_code"] != expected_exit:
        failures.append(f"exit {proc['exit_code']} != expected {expected_exit}")
    stdout = proc["stdout"]
    for needle in case.get("expect_stdout_contains", []) or []:
        if isinstance(needle, str) and needle not in stdout:
            failures.append(f"stdout missing {needle!r}")
    for needle in case.get("forbid_stdout_contains", []) or []:
        if isinstance(needle, str) and needle in stdout:
            failures.append(f"stdout contains forbidden {needle!r}")
    return failures


def check_script_behavior(candidate_root: Path, user: dict[str, Any], report: dict[str, Any]) -> None:
    scripts = script_resources(user)
    report["artifacts"]["script_resources"] = [script.get("path") for script in scripts]
    if not scripts:
        return
    if "evals/script-behavior.json" not in resource_paths(user):
        add(
            report,
            "FAIL",
            "AISP_E_CANDIDATE_SCRIPT_EVIDENCE_UNDECLARED",
            "evals/script-behavior.json must be declared in aisp_contract.resources when executable scripts exist",
            candidate_root / "evals" / "script-behavior.json",
        )
    evidence = load_script_evidence(candidate_root, report)
    if evidence is None:
        return
    entries = evidence.get("scripts")
    if not isinstance(entries, list):
        add(report, "FAIL", "AISP_E_CANDIDATE_SCRIPT_EVIDENCE_SHAPE", "script behavior evidence must have scripts[]", candidate_root / "evals" / "script-behavior.json")
        return
    by_path = {entry.get("path"): entry for entry in entries if isinstance(entry, dict)}
    for resource in scripts:
        rel = resource["path"].replace("\\", "/")
        entry = by_path.get(rel)
        if not isinstance(entry, dict):
            add(report, "FAIL", "AISP_E_CANDIDATE_SCRIPT_EVIDENCE_MISSING", f"missing behavior evidence for script {rel}", candidate_root / rel)
            continue
        cases = entry.get("cases")
        if not isinstance(cases, list):
            add(report, "FAIL", "AISP_E_CANDIDATE_SCRIPT_EVIDENCE_SHAPE", f"script {rel} evidence must have cases[]", candidate_root / rel)
            continue
        kinds = {case.get("kind") for case in cases if isinstance(case, dict)}
        missing = SCRIPT_CASE_KINDS - kinds
        if missing:
            add(report, "FAIL", "AISP_E_CANDIDATE_SCRIPT_CASE_COVERAGE", f"script {rel} lacks case kinds {sorted(missing)}", candidate_root / rel)
        for case in cases:
            if not isinstance(case, dict):
                continue
            argv = normalize_argv(case.get("argv", []))
            if argv is None or rel not in [arg.replace("\\", "/") for arg in argv]:
                add(report, "FAIL", "AISP_E_CANDIDATE_SCRIPT_CASE_ARGV", f"case for {rel} must run the declared script path without shell", candidate_root / rel)
                continue
            try:
                proc = run_process(argv, candidate_root, stdin=case.get("stdin", ""), timeout=int(case.get("timeout_seconds", 10)))
            except Exception as exc:  # noqa: BLE001
                add(report, "FAIL", "AISP_E_CANDIDATE_SCRIPT_CASE_RUN", f"case {case.get('name')} could not run: {exc}", candidate_root / rel)
                continue
            report["artifacts"].setdefault("script_cases", []).append(
                {
                    "script": rel,
                    "name": case.get("name"),
                    "kind": case.get("kind"),
                    "exit_code": proc["exit_code"],
                }
            )
            failures = case_matches(proc, case)
            if failures:
                add(report, "FAIL", "AISP_E_CANDIDATE_SCRIPT_CASE_FAIL", f"case {case.get('name')} failed: {'; '.join(failures)}", candidate_root / rel)


def check_behavior_cases(candidate_root: Path, system: dict[str, Any], user: dict[str, Any], report: dict[str, Any]) -> None:
    """Validate optional non-executable behavior evidence.

    These cases are review/runtime guidance only. Passing this shape check does
    not prove that a model or runtime will produce correct semantic output.
    """
    rel = "evals/behavior-cases.json"
    path = candidate_root / rel
    scripts = script_resources(user)
    if not path.is_file():
        if not scripts:
            add(
                report,
                "WARN",
                "AISP_W_CANDIDATE_BEHAVIOR_EVIDENCE_MISSING",
                "non-script candidates should include evals/behavior-cases.json with positive, boundary, and failure review cases",
                path,
            )
        return

    if rel not in resource_paths(user):
        add(
            report,
            "FAIL",
            "AISP_E_CANDIDATE_BEHAVIOR_EVIDENCE_UNDECLARED",
            "evals/behavior-cases.json must be declared in aisp_contract.resources when present",
            path,
        )
    try:
        doc = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:  # noqa: BLE001
        add(report, "FAIL", "AISP_E_CANDIDATE_BEHAVIOR_EVIDENCE_JSON", f"behavior cases are not valid JSON: {exc}", path)
        return
    if not isinstance(doc, dict):
        add(report, "FAIL", "AISP_E_CANDIDATE_BEHAVIOR_EVIDENCE_JSON", "behavior cases must be an object", path)
        return
    cases = doc.get("cases")
    if not isinstance(cases, list):
        add(report, "FAIL", "AISP_E_CANDIDATE_BEHAVIOR_EVIDENCE_SHAPE", "behavior cases must have cases[]", path)
        return
    kinds = {case.get("kind") for case in cases if isinstance(case, dict)}
    missing = BEHAVIOR_CASE_KINDS - kinds
    if not scripts and missing:
        add(report, "FAIL", "AISP_E_CANDIDATE_BEHAVIOR_CASE_COVERAGE", f"non-script behavior evidence lacks case kinds {sorted(missing)}", path)
    checked = 0
    declared_params = set(system.get("params", {})) if isinstance(system.get("params"), dict) else set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            add(report, "FAIL", "AISP_E_CANDIDATE_BEHAVIOR_CASE_SHAPE", f"cases[{index}] must be an object", path)
            continue
        checked += 1
        if case.get("kind") not in BEHAVIOR_CASE_KINDS:
            add(report, "FAIL", "AISP_E_CANDIDATE_BEHAVIOR_CASE_KIND", f"cases[{index}] has unsupported kind {case.get('kind')!r}", path)
        if not isinstance(case.get("name"), str) or not case["name"].strip():
            add(report, "FAIL", "AISP_E_CANDIDATE_BEHAVIOR_CASE_NAME", f"cases[{index}] must have a non-empty name", path)
        input_params = case.get("input_params")
        if not isinstance(input_params, dict):
            add(report, "FAIL", "AISP_E_CANDIDATE_BEHAVIOR_CASE_INPUT", f"cases[{index}] must have input_params object", path)
        elif declared_params:
            unknown = sorted(set(input_params) - declared_params)
            if unknown:
                add(report, "FAIL", "AISP_E_CANDIDATE_BEHAVIOR_CASE_PARAM", f"cases[{index}] references undeclared params {unknown}", path)
        expected = case.get("expected_behavior")
        if not isinstance(expected, list) or not all(isinstance(item, str) and item.strip() for item in expected):
            add(report, "FAIL", "AISP_E_CANDIDATE_BEHAVIOR_CASE_EXPECTED", f"cases[{index}] must have non-empty expected_behavior[] strings", path)
        forbidden = case.get("forbidden_behavior", [])
        if forbidden is not None and (
            not isinstance(forbidden, list)
            or not all(isinstance(item, str) and item.strip() for item in forbidden)
        ):
            add(report, "FAIL", "AISP_E_CANDIDATE_BEHAVIOR_CASE_FORBIDDEN", f"cases[{index}] forbidden_behavior must be a string array when present", path)
    report["artifacts"]["behavior_cases"] = {"path": rel, "cases_checked": checked}


def check_cache(candidate_root: Path, report: dict[str, Any]) -> None:
    bad: list[str] = []
    for path in candidate_root.rglob("*"):
        rel = path.relative_to(candidate_root).as_posix()
        if path.is_dir() and path.name in CACHE_DIR_NAMES:
            bad.append(rel)
        elif path.is_file() and path.suffix in CACHE_FILE_SUFFIXES:
            bad.append(rel)
    if bad:
        add(report, "FAIL", "AISP_E_CANDIDATE_CACHE_RESIDUE", f"cache/build residue present: {bad}", candidate_root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only release gate for generated AISP candidates.")
    parser.add_argument("candidate_root", help="Generated <id>_aisp candidate folder.")
    parser.add_argument("--creator-root", default=".", help="Creator skill root containing aisp_reference_tools/.")
    parser.add_argument("--output-path", default="", help="User-provided output_path. Omit/empty means default sibling mode.")
    parser.add_argument(
        "--allow-missing-sidecar",
        action="store_true",
        help="Allow a missing default SKILL.md sidecar only when the author explicitly opted out of Agent Skills interop.",
    )
    args = parser.parse_args(argv)

    candidate_root = Path(args.candidate_root).resolve()
    creator_root = Path(args.creator_root).resolve()
    output_path = args.output_path.strip() or None
    report: dict[str, Any] = {
        "candidate_root": str(candidate_root).replace("\\", "/"),
        "creator_root": str(creator_root).replace("\\", "/"),
        "results": [],
        "artifacts": {"sidecar_policy": {"allow_missing_sidecar": bool(args.allow_missing_sidecar)}},
        "pass": False,
    }

    system, user = load_skill(candidate_root, report)
    if system:
        check_location(candidate_root, creator_root, output_path, report)
        if candidate_root.name != system.get("id"):
            add(report, "FAIL", "AISP_E_CANDIDATE_ID_MISMATCH", "candidate folder name must equal system.content.id", candidate_root)
        check_source_name_neutrality(candidate_root, system, report)
    check_reference_tools(candidate_root, creator_root, args.allow_missing_sidecar, report)
    if system:
        check_no_internal_aisp_wrapper(candidate_root, report)
        check_sidecar(candidate_root, creator_root, system, args.allow_missing_sidecar, report)
    if user:
        check_script_behavior(candidate_root, user, report)
        check_schema_resources(candidate_root, user, report)
        check_behavior_cases(candidate_root, system, user, report)
    check_cache(candidate_root, report)

    report["pass"] = not any(item["severity"] == "FAIL" for item in report["results"])
    report["summary"] = {
        "fail": sum(1 for item in report["results"] if item["severity"] == "FAIL"),
        "warn": sum(1 for item in report["results"] if item["severity"] == "WARN"),
        "info": sum(1 for item in report["results"] if item["severity"] == "INFO"),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
