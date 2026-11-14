#!/usr/bin/env python3
"""Check AISP runtime conformance from an execution trace.

This checker validates runtime-observable R rules from a trace emitted by an
AISP/AISOP runtime. It does not execute a skill or authenticate event origins;
it checks the shape and selected consistency properties of supplied claims.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

try:
    from .aisp_hash import strict_json_loads
except ImportError:  # pragma: no cover - standalone script
    from aisp_hash import strict_json_loads



def _safe_load(path: Path) -> tuple[Any, str | None]:
    """Load JSON without raising. Returns (value, error_message)."""
    try:
        return strict_json_loads(path.read_text(encoding="utf-8-sig")), None
    except FileNotFoundError:
        return None, f"file not found: {path}"
    except Exception as exc:  # noqa: BLE001
        return None, f"invalid JSON: {exc}"


def _trace_report(skill_path: Path, trace_path: Path, results: list[dict[str, Any]]) -> dict[str, Any]:
    fail_count = sum(1 for r in results if r["severity"] == "FAIL" and not r["passed"])
    warning_count = sum(1 for r in results if r["severity"] == "WARN" and not r["passed"])
    return {
        "skill": str(skill_path).replace("\\", "/"),
        "trace": str(trace_path).replace("\\", "/"),
        "runtime_conformant": fail_count == 0,
        "fail_count": fail_count,
        "warning_count": warning_count,
        "results": results,
    }


def trace_shape_errors(trace: Any) -> list[str]:
    """Check the published v1 schema's bounded shape, without a schema engine."""
    if not isinstance(trace, dict):
        return ["Runtime trace must be a JSON object."]
    errors = []
    if not isinstance(trace.get("runtime"), str) or not trace["runtime"]:
        errors.append("runtime must be a non-empty string")
    if not isinstance(trace.get("skill_id"), str) or not re.fullmatch(r"[a-z0-9_]+_aisp", trace["skill_id"]):
        errors.append("skill_id must be a valid _aisp identifier")
    for key in ("contract_read", "contract_visible_to_model"):
        if key in trace and not isinstance(trace[key], bool):
            errors.append(f"{key} must be a boolean")
    if "tool_enforcement" in trace and trace["tool_enforcement"] not in ("hard", "advisory"):
        errors.append("tool_enforcement must be hard or advisory")
    raw_events = trace.get("events")
    if not isinstance(raw_events, list):
        return [*errors, "events must be an array"]
    for index, event in enumerate(raw_events):
        prefix = f"events[{index}]"
        if not isinstance(event, dict):
            errors.append(f"{prefix} must be an object")
            continue
        if not isinstance(event.get("type"), str):
            errors.append(f"{prefix}.type must be a string")
        for key in ("node", "step", "call", "mode"):
            if key in event and not isinstance(event[key], str):
                errors.append(f"{prefix}.{key} must be a string")
        if "bypassed" in event and not isinstance(event["bypassed"], bool):
            errors.append(f"{prefix}.bypassed must be a boolean")
        if "enforcement" in event and event["enforcement"] not in ("hard", "advisory", "unknown"):
            errors.append(f"{prefix}.enforcement has an invalid value")
        if "tools" in event and (not isinstance(event["tools"], list)
                                 or any(not isinstance(tool, str) for tool in event["tools"])):
            errors.append(f"{prefix}.tools must be an array of strings")
        if "dispatched_as" in event and event["dispatched_as"] not in ("inline", "agent"):
            errors.append(f"{prefix}.dispatched_as must be inline or agent")
        if event.get("type") == "execute_mode_dispatch":
            for key in ("node", "mode", "dispatched_as"):
                if key not in event:
                    errors.append(f"{prefix}.{key} is required for dispatch events")
            if event.get("mode") not in ("inline", "agent"):
                errors.append(f"{prefix}.mode must be inline or agent for dispatch events")
    return errors


def events(trace: dict[str, Any], event_type: str | None = None) -> list[dict[str, Any]]:
    raw = trace.get("events", [])
    items = [e for e in raw if isinstance(e, dict)] if isinstance(raw, list) else []
    return [e for e in items if event_type is None or e.get("type") == event_type]


def has_hard_tool_enforcement_event(trace: dict[str, Any]) -> bool:
    for event in events(trace, "tool_enforcement"):
        if event.get("enforcement", event.get("mode")) == "hard":
            return True
    return False


def agent_nodes(skill_doc: Any) -> set[str]:
    if not isinstance(skill_doc, list) or len(skill_doc) != 2:
        return set()
    user = skill_doc[1].get("content", {}) if isinstance(skill_doc[1], dict) else {}
    functions = user.get("functions", {}) if isinstance(user, dict) else {}
    if not isinstance(functions, dict):
        return set()
    return {name for name, spec in functions.items() if isinstance(spec, dict) and spec.get("execute_mode") == "agent"}


def _skill_shape_error(skill_doc: Any) -> str | None:
    if not isinstance(skill_doc, list) or len(skill_doc) != 2:
        return "skill file must be a 2-message AISP array"
    if not isinstance(skill_doc[0], dict) or not isinstance(skill_doc[1], dict):
        return "skill messages must be JSON objects"
    system = skill_doc[0].get("content")
    user = skill_doc[1].get("content")
    if not isinstance(system, dict) or not isinstance(user, dict):
        return "skill message content fields must be JSON objects"
    if not isinstance(system.get("id"), str) or not system["id"]:
        return "skill system.content.id must be a non-empty string"
    if [message.get("role") for message in skill_doc] != ["system", "user"]:
        return "skill messages must have system/user roles in order"
    if not isinstance(user.get("functions"), dict) or not isinstance(user.get("aisp_contract"), dict):
        return "skill functions and aisp_contract must be objects"
    return None


def skill_id(skill_path: Path, skill_doc: Any) -> str:
    if isinstance(skill_doc, list) and skill_doc:
        system = skill_doc[0].get("content", {}) if isinstance(skill_doc[0], dict) else {}
        if isinstance(system, dict) and isinstance(system.get("id"), str):
            return system["id"]
    skill_dir = skill_path if skill_path.is_dir() else skill_path.parent
    return skill_dir.name


def check_trace(skill_path: Path, trace_path: Path) -> dict[str, Any]:
    results: list[dict[str, Any]] = []

    def add(code: str, rule_id: str, severity: str, passed: bool, message: str) -> None:
        results.append({"code": code, "rule_id": rule_id, "severity": severity, "passed": passed, "message": message})

    skill_file = skill_path if skill_path.is_file() else skill_path / "aisp.aisop.json"
    try:
        base = skill_path if skill_path.is_dir() else skill_path.parent
        if not skill_file.resolve().is_relative_to(base.resolve()):
            raise ValueError("skill entry file resolves outside its folder")
    except (OSError, ValueError, RuntimeError) as exc:
        add("AISP_E_INPUT", "INPUT", "FAIL", False, f"Cannot inspect skill entry file: {exc}.")
        return _trace_report(skill_path, trace_path, results)
    skill_doc, skill_err = _safe_load(skill_file)
    if skill_err:
        add("AISP_E_INPUT", "INPUT", "FAIL", False, f"Cannot read skill file ({skill_err}).")
    trace, trace_err = _safe_load(trace_path)
    if trace_err:
        add("AISP_E_INPUT", "INPUT", "FAIL", False, f"Cannot read trace file ({trace_err}).")
        return _trace_report(skill_path, trace_path, results)
    if not isinstance(trace, dict):
        add("AISP_E_TRACE_SHAPE", "INPUT", "FAIL", False, "Runtime trace must be a JSON object.")
        return _trace_report(skill_path, trace_path, results)
    shape_errors = trace_shape_errors(trace)
    if shape_errors:
        for message in shape_errors:
            add("AISP_E_TRACE_SHAPE", "INPUT", "FAIL", False, message)
        return _trace_report(skill_path, trace_path, results)
    if skill_err:
        return _trace_report(skill_path, trace_path, results)
    skill_shape_error = _skill_shape_error(skill_doc)
    if skill_shape_error:
        add("AISP_E_INPUT", "INPUT", "FAIL", False, f"Cannot inspect skill file ({skill_shape_error}).")
        return _trace_report(skill_path, trace_path, results)

    expected_skill_id = skill_id(skill_path, skill_doc)
    trace_skill_id = trace.get("skill_id")
    if trace_skill_id != expected_skill_id:
        add("AISP_E_R1_SKILL_MISMATCH", "R1", "FAIL", False, f"Runtime trace skill_id {trace_skill_id!r} does not match skill {expected_skill_id!r}.")
    if not trace.get("runtime"):
        add("AISP_E_R1_TRACE_SHAPE", "R1", "FAIL", False, "Runtime trace must declare a non-empty runtime name.")
    if not isinstance(trace.get("events"), list):
        add("AISP_E_R1_TRACE_SHAPE", "R1", "FAIL", False, "Runtime trace events must be an array.")

    if not trace.get("contract_read") and not events(trace, "contract_read"):
        add("AISP_E_R1_CONTRACT_NOT_READ", "R1", "FAIL", False, "Runtime trace does not show user.content.aisp_contract being read.")
    if not trace.get("contract_visible_to_model") and not events(trace, "contract_visible_to_model"):
        add("AISP_E_R3_HIDDEN", "R3", "FAIL", False, "Runtime trace does not show aisp_contract was handed to the model/user-message context.")
    for field, code, rule in (("contract_read", "AISP_E_R1_CONFLICT", "R1"),
                              ("contract_visible_to_model", "AISP_E_R3_CONFLICT", "R3")):
        if trace.get(field) is False and events(trace, field):
            add(code, rule, "FAIL", False, f"Explicit {field}: false conflicts with an affirmative event claim.")

    tool_mode = trace.get("tool_enforcement")
    if tool_mode not in {"hard", "advisory"}:
        add("AISP_W_R6_NO_DECLARATION", "R6", "WARN", False, "Runtime trace must declare tool_enforcement as hard or advisory.")
    elif tool_mode == "advisory":
        add("AISP_W_R6_ADVISORY", "R6", "WARN", False, "Runtime declares advisory tool enforcement; enforced_by: tools is not a hard guarantee.")
    elif not has_hard_tool_enforcement_event(trace):
        add("AISP_W_R6_TOOLS_ATTESTED_NOT_VERIFIED", "R6", "WARN", False, "Runtime trace top-level tool_enforcement is hard, but no tool_enforcement event records the enforcement decision.")

    if tool_mode == "hard" and any(
        event.get("enforcement", event.get("mode")) in ("advisory", "unknown")
        for event in events(trace, "tool_enforcement")
    ):
        add("AISP_E_R6_CONFLICT", "R6", "FAIL", False,
            "Hard tool-enforcement declaration conflicts with non-hard event evidence.")

    for event in events(trace, "sys_call"):
        if event.get("call") == "sys.io.confirm" and event.get("bypassed") is True:
            add("AISP_E_SE7_CONFIRM_BYPASS", "SE7", "FAIL", False, "Trace shows sys.io.confirm was bypassed.")

    for node in sorted(agent_nodes(skill_doc)):
        dispatches = [e for e in events(trace, "execute_mode_dispatch") if e.get("node") == node]
        if not dispatches:
            add("AISP_E_R7_COLLAPSED_INLINE", "R7", "FAIL", False, f"Agent node {node!r} has no dispatch evidence.")
        elif any(e.get("mode") != "agent" or e.get("dispatched_as") != "agent" for e in dispatches):
            add("AISP_E_R7_COLLAPSED_INLINE", "R7", "FAIL", False,
                f"Agent node {node!r} has a non-agent mode/dispatch claim; later events cannot hide it.")

    functions = skill_doc[1]["content"]["functions"]
    for event in events(trace, "execute_mode_dispatch"):
        spec = functions.get(event["node"])
        if isinstance(spec, dict) and spec.get("execute_mode", "inline") == "inline":
            if event["mode"] != "inline" or event["dispatched_as"] != "inline":
                add("AISP_E_R7_MODE_MISMATCH", "R7", "FAIL", False,
                    f"Inline node {event['node']!r} has a non-inline mode/dispatch claim; omitted execute_mode also defaults to inline.")

    return _trace_report(skill_path, trace_path, results)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check AISP runtime conformance from a trace JSON file.")
    parser.add_argument("skill", help="Skill folder or aisp.aisop.json path.")
    parser.add_argument("trace", help="Runtime trace JSON path.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(argv)
    report = check_trace(Path(args.skill), Path(args.trace))
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        status = "PASS" if report["runtime_conformant"] else "FAIL"
        print(f"{status} {report['trace']} ({report['fail_count']} fail, {report['warning_count']} warn)")
        for result in report["results"]:
            print(f"  {result['severity']} {result['code']}: {result['message']}")
    return 0 if report["runtime_conformant"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
