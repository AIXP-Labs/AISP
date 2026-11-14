#!/usr/bin/env python3
"""AISP conformance validator.

Zero-dependency reference checker for AISP skill packages. It focuses on static
skill/package conformance (M1-M7) plus the static parts of the SE/EC rule sets.
Runtime-only rules (R1-R7) require execution traces and are reported as not run.
"""
from __future__ import annotations

import argparse
import ast
import getopt
import json
import re
import shlex
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

try:
    from .aisp_hash import SKILL_ID_RE, load_skill as _load_skill_document, strict_json_loads
    from .aisp_check_runtime_trace import check_trace as _check_runtime_trace
    from .aisp_check_runtime_trace import trace_shape_errors as _trace_shape_errors
    from .aisp_skill_md import validate_skill_md as _validate_skill_md
    from .aisp_readme import (
        GENERATED_MARKER,
        GENERATOR_MARKER,
        SOURCE_MARKER,
        normalize_text as _normalize_readme_text,
        render_readme as _render_readme,
    )
except ImportError:  # pragma: no cover - script execution path
    from aisp_hash import SKILL_ID_RE, load_skill as _load_skill_document, strict_json_loads
    from aisp_check_runtime_trace import check_trace as _check_runtime_trace
    from aisp_check_runtime_trace import trace_shape_errors as _trace_shape_errors
    from aisp_skill_md import validate_skill_md as _validate_skill_md
    from aisp_readme import (
        GENERATED_MARKER,
        GENERATOR_MARKER,
        SOURCE_MARKER,
        normalize_text as _normalize_readme_text,
        render_readme as _render_readme,
    )


ROOT_SKIP_NAMES = {"aisp.aisop.json", "README.md", "SKILL.md"}
READ_MODES = {"read_only", "read_and_execute"}
EXEC_MODES = {"execute_only", "read_and_execute"}
VALID_RESOURCE_MODES = {"read_only", "execute_only", "read_and_execute"}
VALID_RESOURCE_SCOPES = {"skill", "shared"}
VALID_RISK_LEVELS = {"low", "medium", "high", "critical"}
VALID_EXECUTE_MODES = {"inline", "agent"}
REQUIRED_LOADING_MODE = "node"
AGENT_STEP_RECOMMENDATION_THRESHOLD = 10
STEP_KEY_RE = re.compile(r"^step[1-9]\d*$")
TRUST_KEYS = {"trusted", "verified", "safe"}
REMOTE_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://")
PROFILE_RE = re.compile(r"^aisp\.skill\.v[0-9]+$")
ENFORCED_BY_RE = re.compile(r"^([A-Za-z0-9_]+)\.([A-Za-z0-9_]+):(sys\.[A-Za-z0-9_.]+)$")
MERMAID_EDGE_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*(?:\[[^\]]*\]|\(\([^)]*\)\)|\([^)]*\))?\s*[-.=]*>\s*([A-Za-z_][A-Za-z0-9_]*)")
_JSON_READ_ERROR = object()


@dataclass
class Result:
    code: str
    rule_id: str
    severity: str
    passed: bool
    message: str
    path: str | None = None
    suggested_fix: str | None = None

    def as_dict(self) -> dict[str, Any]:
        out = {
            "code": self.code,
            "rule_id": self.rule_id,
            "severity": self.severity,
            "passed": self.passed,
            "message": self.message,
        }
        if self.path:
            out["path"] = self.path
        if self.suggested_fix:
            out["suggested_fix"] = self.suggested_fix
        return out


@dataclass
class ToolEvidence:
    runtime_mode: str | None = None
    runtime_skill_id: str | None = None
    runtime_path: Path | None = None
    runtime_events: list[dict[str, Any]] | None = None
    capability_modes: dict[str, str] | None = None
    capability_has_provenance: bool = False
    capability_provided: bool = False


class Reporter:
    def __init__(self) -> None:
        self.results: list[Result] = []

    def fail(self, code: str, rule_id: str, message: str, path: Path | str | None = None, fix: str | None = None) -> None:
        self.results.append(Result(code, rule_id, "FAIL", False, message, _path(path), fix))

    def warn(self, code: str, rule_id: str, message: str, path: Path | str | None = None, fix: str | None = None) -> None:
        self.results.append(Result(code, rule_id, "WARN", False, message, _path(path), fix))

    def info(self, code: str, rule_id: str, message: str, path: Path | str | None = None) -> None:
        self.results.append(Result(code, rule_id, "INFO", True, message, _path(path)))

    def extend(self, other: "Reporter") -> None:
        self.results.extend(other.results)


def _path(path: Path | str | None) -> str | None:
    return str(path).replace("\\", "/") if path is not None else None


def _load_json(path: Path, reporter: Reporter, rule_id: str = "M1") -> Any:
    try:
        return strict_json_loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:  # noqa: BLE001
        reporter.fail("AISP_E_M1_JSON", rule_id, f"Invalid JSON: {exc}", path, "Fix JSON syntax.")
        return _JSON_READ_ERROR


def _edges(spec: Any) -> list[str]:
    if not isinstance(spec, dict):
        return []
    out: list[str] = []
    nxt = spec.get("next")
    if isinstance(nxt, str):
        out.append(nxt)
    elif isinstance(nxt, list):
        out.extend(x for x in nxt if isinstance(x, str))
    branches = spec.get("branches")
    if isinstance(branches, dict):
        out.extend(x for x in branches.values() if isinstance(x, str))
    err = spec.get("error")
    if isinstance(err, str):
        out.append(err)
    return out


def _parse_mermaid_graph(graph: str) -> tuple[set[str], list[tuple[str, str]]]:
    names: set[str] = set()
    edges: list[tuple[str, str]] = []
    for raw_line in graph.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("graph ", "flowchart ", "%%")):
            continue
        for left, right in MERMAID_EDGE_RE.findall(line):
            names.add(left)
            names.add(right)
            edges.append((left, right))
    return names, edges


def _walk_json(value: Any, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], Any]]:
    found = [(path, value)]
    if isinstance(value, dict):
        for key, child in value.items():
            found.extend(_walk_json(child, (*path, str(key))))
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            found.extend(_walk_json(child, (*path, str(idx))))
    return found


def _truthy_trust(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in TRUST_KEYS | {"true", "yes"}
    return False


def _is_step_key(key: Any) -> bool:
    return isinstance(key, str) and STEP_KEY_RE.fullmatch(key) is not None


def _step_strings(functions: dict[str, Any]) -> list[tuple[str, str, str]]:
    steps: list[tuple[str, str, str]] = []
    for node, spec in functions.items():
        if not isinstance(spec, dict):
            continue
        for key, value in spec.items():
            if _is_step_key(key) and isinstance(value, str):
                steps.append((str(node), str(key), value))
    return steps


def _numeric_step_items(spec: dict[str, Any]) -> list[tuple[str, Any]]:
    return [(key, value) for key, value in spec.items() if _is_step_key(key)]


def _step_count(spec: dict[str, Any]) -> int:
    return sum(1 for _key, value in _numeric_step_items(spec) if isinstance(value, str))


def _extract_call_paths(step: str, call_name: str) -> list[str]:
    paths: list[str] = []
    marker = re.compile(r"(?<![\w.])" + re.escape(call_name) + r"\s*\(")
    for match in marker.finditer(step):
        arg_start = match.end()
        while arg_start < len(step) and step[arg_start].isspace():
            arg_start += 1
        if arg_start < len(step) and step[arg_start] in {"'", '"'}:
            quote = step[arg_start]
            arg_end = arg_start + 1
            escaped = False
            while arg_end < len(step):
                ch = step[arg_end]
                if ch == quote and not escaped:
                    literal = step[arg_start : arg_end + 1]
                    try:
                        paths.append(ast.literal_eval(literal))
                    except Exception:
                        pass
                    break
                escaped = ch == "\\" and not escaped
                if ch != "\\":
                    escaped = False
                arg_end += 1
    return paths


def _command_script(parts: list[str]) -> str | None:
    if not parts:
        return None
    executable = PurePosixPath(parts[0].replace("\\", "/")).name.lower()
    if not re.fullmatch(r"python(?:\d+(?:\.\d+)*)?(?:\.exe)?|py(?:\.exe)?", executable):
        if executable in {"bash", "sh"} and len(parts) > 1 and not parts[1].startswith("-"):
            return parts[1]
        # An arbitrary tool's .py argument can be data, not executed code.
        return parts[0] if "/" in parts[0] or "\\" in parts[0] or parts[0].endswith(".py") else None
    arguments = parts[1:]
    if executable in {"py", "py.exe"} and arguments and re.fullmatch(r"-3(?:\.\d+)?(?:-(?:32|64))?", arguments[0]):
        arguments = arguments[1:]
    try:
        options, operands = getopt.getopt(arguments, "bBdEhiIOPqRsSuvVx?c:m:W:X:", [
            "check-hash-based-pycs=", "help", "help-env", "help-xoptions", "help-all", "version",
        ])
    except getopt.GetoptError:
        return None  # Unsupported command syntax is not certified by this check.
    if any(option in {"-c", "-m", "-h", "-?", "-V", "--help", "--help-env", "--help-xoptions", "--help-all", "--version"}
           for option, _value in options):
        return None
    return operands[0] if operands and operands[0] != "-" else None


def _extract_sys_run_scripts(step: str) -> list[str]:
    scripts: list[str] = []
    for call in ("sys.run", "sys.run.bg"):
        for command in _extract_call_paths(step, call):
            try:
                # Non-POSIX tokenization preserves Windows path separators.
                parts = shlex.split(command, posix=False)
            except ValueError:
                continue  # Unsupported/malformed commands still need runtime checks.
            parts = [
                part[1:-1] if len(part) >= 2 and part[0] == part[-1] and part[0] in "\"'" else part
                for part in parts
            ]
            script = _command_script(parts)
            if script is not None:
                scripts.append(script.replace("\\", "/"))
    return scripts


def _normalize_rel(path: str) -> str:
    return PurePosixPath(path.replace("\\", "/")).as_posix()


def _safe_resolve(base: Path, rel: str) -> Path:
    return (base / rel).resolve()


def _is_inside(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def validate_skill(
    skill_dir: Path,
    aisp_dir: Path | None = None,
    tool_evidence: ToolEvidence | None = None,
    strict_tools: bool = False,
    strict_readme: bool = False,
) -> dict[str, Any]:
    skill_dir = skill_dir.resolve()
    aisp_dir = (aisp_dir or skill_dir.parent).resolve()
    reporter = Reporter()
    skill_file = skill_dir / "aisp.aisop.json"

    if not skill_dir.name.endswith("_aisp"):
        reporter.fail("AISP_E_M2_SUFFIX", "M2", "Skill folder name must end with _aisp.", skill_dir)
    if not re.match(r"^[a-z0-9_]+_aisp$", skill_dir.name):
        reporter.fail("AISP_E_M2_ID", "M2", "Skill folder name must be lowercase snake_case and end with _aisp.", skill_dir)
    if not skill_file.is_file():
        reporter.fail("AISP_E_M2_FILENAME", "M2", "Missing fixed skill file aisp.aisop.json.", skill_dir)
        return _report(skill_dir, reporter)
    if not _is_inside(skill_file.resolve(), skill_dir):
        reporter.fail("AISP_E_SE1_PATH", "SE1", "Skill entry file resolves outside its folder.", skill_file)
        return _report(skill_dir, reporter)

    doc = _load_json(skill_file, reporter)
    if doc is _JSON_READ_ERROR:
        return _report(skill_dir, reporter)
    if not isinstance(doc, list) or len(doc) != 2:
        reporter.fail("AISP_E_M1_SHAPE", "M1", "AISP skill file must be a 2-message array.", skill_file)
        return _report(skill_dir, reporter)
    if any(not isinstance(message, dict) for message in doc) or [message.get("role") for message in doc] != ["system", "user"]:
        reporter.fail("AISP_E_M1_ROLES", "M1", "Skill messages must have system/user roles in that order.", skill_file)
    _check_skill_readme(skill_dir, strict_readme, reporter)
    _check_bridge_file(skill_dir / "SKILL.md", skill_dir, reporter)

    system = doc[0].get("content") if isinstance(doc[0], dict) else None
    user = doc[1].get("content") if isinstance(doc[1], dict) else None
    if not isinstance(system, dict):
        reporter.fail("AISP_E_M1_SYSTEM", "M1", "First message content must be an object.", skill_file)
        system = {}
    if not isinstance(user, dict):
        reporter.fail("AISP_E_M1_USER", "M1", "Second message content must be an object.", skill_file)
        user = {}

    if system.get("protocol") != "AISP V1.0.0":
        reporter.fail("AISP_E_M1_PROTOCOL", "M1", 'system.content.protocol must be "AISP V1.0.0".', skill_file)
    if system.get("axiom_0") != "Human_Sovereignty_and_Wellbeing":
        reporter.fail("AISP_E_M1_AXIOM", "M1", 'system.content.axiom_0 must be "Human_Sovereignty_and_Wellbeing".', skill_file)
    for field in ("id", "name", "version", "flow_format"):
        if not isinstance(system.get(field), str) or not system[field].strip():
            reporter.fail("AISP_E_M1_FIELD", "M1", f"Missing required system.content.{field}.", skill_file)
    if isinstance(system.get("flow_format"), str) and system["flow_format"] not in ("mermaid", "jsonflow", "hybrid"):
        reporter.fail("AISP_E_M1_FIELD", "M1", "flow_format must be mermaid, jsonflow or hybrid.", skill_file)
    for field in ("summary", "description", "license", "system_prompt"):
        if field in system and not isinstance(system[field], str):
            reporter.fail("AISP_E_M1_FIELD", "M1", f"system.content.{field} must be a string when present.", skill_file)
    if "params" in system and not isinstance(system["params"], dict):
        reporter.fail("AISP_E_M1_FIELD", "M1", "system.content.params must be an object when present.", skill_file)
    if "user_input" in user and not isinstance(user["user_input"], str):
        reporter.fail("AISP_E_M1_FIELD", "M1", "user.content.user_input must be a string when present.", skill_file)
    if system.get("loading_mode") != REQUIRED_LOADING_MODE:
        reporter.fail(
            "AISP_E_M1_LOADING_MODE",
            "M1",
            'AISP skills MUST set system.content.loading_mode to "node".',
            skill_file,
            'Set system.content.loading_mode to "node".',
        )
    license_value = system.get("license")
    if "license" not in system or (isinstance(license_value, str) and not license_value.strip()):
        reporter.warn("AISP_W_M1_LICENSE", "M1", "license SHOULD be present and non-blank; default is Apache-2.0.", skill_file)
    if "tools" in system and (not isinstance(system["tools"], list) or any(
        not isinstance(tool, str) or not tool.strip() for tool in system["tools"]
    )):
        reporter.fail("AISP_E_M1_FIELD", "M1", "system.content.tools must be an array of non-empty strings.", skill_file)

    if system.get("id") != skill_dir.name:
        reporter.fail("AISP_E_M2_ID_MISMATCH", "M2", "system.content.id must equal the skill folder name.", skill_file)

    instruction = user.get("instruction", "")
    if not isinstance(instruction, str) or "aisp_contract" not in instruction or "RUN aisop.main" not in instruction:
        reporter.fail("AISP_E_M1_INSTRUCTION", "M1", "instruction must strongly name aisp_contract and RUN aisop.main.", skill_file)

    aisop = user.get("aisop")
    functions = user.get("functions")
    if not isinstance(aisop, dict) or "main" not in aisop:
        reporter.fail("AISP_E_M1_MAIN", "M1", "user.content.aisop.main is required.", skill_file)
        aisop = {}
    if not isinstance(functions, dict) or not functions:
        reporter.fail("AISP_E_M1_FUNCTIONS", "M1", "user.content.functions must be a non-empty object.", skill_file)
        functions = {}

    _check_function_execute_modes(functions, reporter, skill_file)
    _check_graphs(aisop, functions, reporter, skill_file)

    contract = user.get("aisp_contract")
    if isinstance(contract, str):
        reporter.fail("AISP_E_M3_STRING", "M3", "aisp_contract must be a real object, not JSON-in-string.", skill_file)
        contract = {}
    if not isinstance(contract, dict):
        reporter.fail("AISP_E_M3_CONTRACT", "M3", "user.content.aisp_contract must be present as an object.", skill_file)
        contract = {}
    if not PROFILE_RE.fullmatch(str(contract.get("profile", ""))):
        reporter.fail("AISP_E_M3_PROFILE", "M3", "aisp_contract.profile must match aisp.skill.v<major>.", skill_file)
    invocation = contract.get("invocation")
    if not isinstance(invocation, dict):
        reporter.fail("AISP_E_M3_INVOCATION", "M3", "aisp_contract.invocation is required.", skill_file)
    else:
        for field in ("when_to_use", "when_not_to_use"):
            values = invocation.get(field)
            if not isinstance(values, list) or not values or any(not isinstance(value, str) for value in values):
                reporter.fail("AISP_E_M3_INVOCATION", "M3", f"invocation.{field} must be a non-empty array.", skill_file)
        if "mode" in invocation and invocation["mode"] not in ("manual_only", "auto_or_manual", "auto_preferred", "internal_only"):
            reporter.fail("AISP_E_M3_INVOCATION", "M3", "invocation.mode has an invalid value.", skill_file)
    if "discovery" in contract and not isinstance(contract["discovery"], dict):
        reporter.fail("AISP_E_M3_CONTRACT", "M3", "discovery must be an object when present.", skill_file)
    discovery = contract.get("discovery")
    if isinstance(discovery, dict) and (
        ("category" in discovery and not isinstance(discovery["category"], str))
        or ("tags" in discovery and (not isinstance(discovery["tags"], list)
                                    or any(not isinstance(tag, str) for tag in discovery["tags"])))
    ):
        reporter.fail("AISP_E_M3_CONTRACT", "M3", "discovery.category must be a string and tags an array of strings.", skill_file)
    nn_list = contract.get("non_negotiable")
    if not isinstance(nn_list, list) or not nn_list:
        reporter.fail("AISP_E_M3_NON_NEGOTIABLE", "M3", "aisp_contract.non_negotiable must be a non-empty array.", skill_file)
        nn_list = []
    if "risk_level" in contract and (not isinstance(contract["risk_level"], str) or contract["risk_level"] not in VALID_RISK_LEVELS):
        reporter.fail("AISP_E_M3_RISK", "M3", "risk_level must be low, medium, high, or critical.", skill_file)

    _check_enforced_by(nn_list, functions, aisop, system, reporter, skill_file, tool_evidence, strict_tools)
    resources = _check_resources(contract, functions, skill_dir, aisp_dir, reporter, skill_file)
    _check_resource_usage(resources, functions, reporter, skill_file)
    _check_self_trust(system, contract, reporter, skill_file)
    _check_undeclared_files(resources, skill_dir, reporter)

    reporter.info("AISP_I_R_STATIC_ONLY", "R", "R1-R7 require runtime traces and were not executed by the static validator.", skill_file)
    return _report(skill_dir, reporter)


def _check_function_execute_modes(functions: dict[str, Any], reporter: Reporter, skill_file: Path) -> None:
    for node, spec in functions.items():
        if not isinstance(spec, dict):
            reporter.fail(
                "AISP_E_M1_FUNCTION_SHAPE",
                "M1",
                f"Function {node!r} must be an object.",
                skill_file,
                "Represent each function node as an object containing step fields and optional node metadata.",
            )
            continue
        step_items = _numeric_step_items(spec)
        if not step_items:
            reporter.fail(
                "AISP_E_M1_STEP_SHAPE",
                "M1",
                f"Function {node!r} must contain at least one numeric step field such as step1.",
                skill_file,
                "Add at least one string-valued step field named step1, step2, and so on.",
            )
        for step_key, step_value in step_items:
            if not isinstance(step_value, str):
                reporter.fail(
                    "AISP_E_M1_STEP_SHAPE",
                    "M1",
                    f"Function {node!r}.{step_key} must be a string.",
                    skill_file,
                    "Represent every execution step as a string instruction.",
                )
        if "on_error" in spec:
            routing = spec["on_error"]
            if not isinstance(routing, dict) or any(
                not isinstance(target, str) or not target or target not in functions
                for target in routing.values()
            ):
                reporter.fail("AISP_E_M1_ON_ERROR", "M1", f"Function {node!r} on_error must map error types to existing function nodes.", skill_file)
        mode = spec.get("execute_mode")
        valid_dispatch_intent = True
        if "execute_mode" not in spec:
            reporter.warn(
                "AISP_W_M1_EXECUTE_MODE_DEFAULT_INLINE",
                "M1",
                f"Function {node!r} omits execute_mode; runtime falls back to inline.",
                skill_file,
                'Declare execute_mode as "inline" or "agent" for auditable dispatch intent.',
            )
            effective_mode = "inline"
        elif not isinstance(mode, str) or mode not in VALID_EXECUTE_MODES:
            reporter.fail(
                "AISP_E_M1_EXECUTE_MODE",
                "M1",
                f"Function {node!r} execute_mode {mode!r} is invalid; use inline or agent.",
                skill_file,
                'Set execute_mode to "inline" or "agent".',
            )
            effective_mode = "inline"
            valid_dispatch_intent = False
        else:
            effective_mode = mode
        count = _step_count(spec)
        if valid_dispatch_intent and count > AGENT_STEP_RECOMMENDATION_THRESHOLD and effective_mode != "agent":
            reporter.warn(
                "AISP_W_M1_EXECUTE_MODE_AGENT_RECOMMENDED",
                "M1",
                f"Function {node!r} has {count} steps and is not agent; review whether execute_mode: agent is appropriate.",
                skill_file,
                'The 10-step threshold is a review heuristic, not a restriction on using agent for shorter high-isolation nodes.',
            )


def _readme_issue(
    reporter: Reporter,
    strict_readme: bool,
    short_code: str,
    message: str,
    path: Path,
    fix: str,
) -> None:
    if strict_readme:
        reporter.fail(f"AISP_E_EC8_SKILL_README_{short_code}", "EC8", message, path, fix)
    else:
        reporter.warn(f"AISP_W_EC8_SKILL_README_{short_code}", "EC8", message, path, fix)


def _check_skill_readme(skill_dir: Path, strict_readme: bool, reporter: Reporter) -> None:
    readme = skill_dir / "README.md"
    if readme.is_symlink():
        _readme_issue(reporter, strict_readme, "DRIFT", "Per-skill README.md must not be a symbolic link.", readme, "Restore a regular generated README.md inside the skill folder.")
        return
    if not readme.is_file():
        _readme_issue(
            reporter,
            strict_readme,
            "MISSING",
            "Per-skill README.md is SHOULD by default and MUST in strict/release profiles.",
            readme,
            "Run python -B tools/aisp_readme.py <skill> --write.",
        )
        return
    try:
        actual_raw = readme.read_text(encoding="utf-8-sig")
        actual = _normalize_readme_text(actual_raw)
        expected = _render_readme(skill_dir)
    except Exception as exc:  # noqa: BLE001
        _readme_issue(
            reporter,
            strict_readme,
            "DRIFT",
            f"Per-skill README.md could not be checked against aisp.aisop.json: {exc}.",
            readme,
            "Regenerate README.md from the contract after fixing the skill package.",
        )
        return
    if GENERATED_MARKER not in actual_raw:
        _readme_issue(
            reporter,
            strict_readme,
            "MANUAL",
            "Per-skill README.md lacks the generated_from_aisp marker.",
            readme,
            "Regenerate README.md with tools/aisp_readme.py or keep manual docs outside the generated README.",
        )
    else:
        if SOURCE_MARKER not in actual_raw:
            _readme_issue(
                reporter,
                strict_readme,
                "BAD_SOURCE",
                "Per-skill README.md generated marker source must be aisp.aisop.json.",
                readme,
                "Regenerate README.md with tools/aisp_readme.py.",
            )
        if GENERATOR_MARKER not in actual_raw:
            _readme_issue(
                reporter,
                strict_readme,
                "UNSUPPORTED_GENERATOR",
                "Per-skill README.md generator marker is missing or unsupported.",
                readme,
                "Regenerate README.md with tools/aisp_readme.py.",
            )
    if actual != _normalize_readme_text(expected):
        _readme_issue(
            reporter,
            strict_readme,
            "DRIFT",
            "Per-skill README.md differs from the deterministic contract-derived projection.",
            readme,
            "Run python -B tools/aisp_readme.py <skill> --write.",
        )


def _frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    out: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            out[key.strip()] = value.strip().strip("\"'")
    return out


def _check_bridge_file(bridge: Path, skill_dir: Path, reporter: Reporter) -> None:
    issues = _validate_skill_md(skill_dir)
    for issue in issues:
        reporter.fail(issue["code"], "M7", issue["message"], bridge)
    if not issues:
        reporter.info("AISP_I_M7_SKILL_MD", "M7", "Bootstrap unchanged and format valid; executor not certified. No execution, safety or external trust is proved.", bridge)


def _check_graphs(aisop: dict[str, Any], functions: dict[str, Any], reporter: Reporter, skill_file: Path) -> None:
    for graph_name, graph in aisop.items():
        if isinstance(graph, str):
            names, edges = _parse_mermaid_graph(graph)
            if not names:
                reporter.warn("AISP_W_M1_MERMAID_UNPARSED", "M1", f"Mermaid graph aisop.{graph_name} had no parseable edges.", skill_file)
                continue
            for node in sorted(names):
                if node not in functions:
                    reporter.fail("AISP_E_M1_NODE_FUNCTION", "M1", f"Mermaid node {graph_name}.{node} has no matching functions entry.", skill_file)
            outgoing = {left for left, _ in edges}
            if not (names - outgoing):
                reporter.fail("AISP_E_M1_TERMINAL", "M1", f"Mermaid graph {graph_name} has no terminal node.", skill_file)
            continue
        if not isinstance(graph, dict):
            reporter.fail("AISP_E_M1_GRAPH", "M1", f"aisop.{graph_name} must be a jsonflow object or mermaid string.", skill_file)
            continue
        if not graph:
            reporter.fail("AISP_E_M1_GRAPH", "M1", f"aisop.{graph_name} is empty.", skill_file)
            continue
        names = set(graph)
        seen: set[str] = set()
        stack = [next(iter(graph))]
        terminals = set()
        for node, spec in graph.items():
            if not isinstance(spec, dict):
                reporter.fail("AISP_E_M1_GRAPH", "M1", f"Graph node {graph_name}.{node} must be an object.", skill_file)
                continue
            malformed = (
                "next" in spec and (not isinstance(spec["next"], list) or any(not isinstance(target, str) for target in spec["next"]))
            ) or (
                "branches" in spec and (not isinstance(spec["branches"], dict) or any(not isinstance(target, str) for target in spec["branches"].values()))
            ) or ("error" in spec and not isinstance(spec["error"], str))
            if malformed:
                reporter.fail("AISP_E_M1_EDGE_SHAPE", "M1", f"Graph node {graph_name}.{node} has malformed next/branches/error fields.", skill_file)
            if node not in functions:
                reporter.fail("AISP_E_M1_NODE_FUNCTION", "M1", f"Graph node {graph_name}.{node} has no matching functions entry.", skill_file)
            edges = _edges(spec)
            if not edges:
                terminals.add(node)
            for target in edges:
                if target not in names:
                    reporter.fail("AISP_E_M1_EDGE", "M1", f"Broken edge {graph_name}.{node} -> {target}.", skill_file)
        while stack:
            node = stack.pop()
            if node in seen or node not in graph:
                continue
            seen.add(node)
            stack.extend(_edges(graph[node]))
        for node in sorted(names - seen):
            reporter.fail("AISP_E_M1_UNREACHABLE", "M1", f"Unreachable graph node {graph_name}.{node}.", skill_file)
        if not terminals:
            reporter.fail("AISP_E_M1_TERMINAL", "M1", f"Graph {graph_name} has no terminal node.", skill_file)


def _check_enforced_by(
    nn_list: list[Any],
    functions: dict[str, Any],
    aisop: dict[str, Any],
    system: dict[str, Any],
    reporter: Reporter,
    skill_file: Path,
    tool_evidence: ToolEvidence | None = None,
    strict_tools: bool = False,
) -> None:
    tools = system.get("tools", [])
    for idx, item in enumerate(nn_list):
        if not isinstance(item, dict):
            reporter.fail("AISP_E_M4_GRAMMAR", "M4", f"non_negotiable[{idx}] must be an object.", skill_file)
            continue
        if not isinstance(item.get("rule"), str) or not item["rule"]:
            reporter.fail("AISP_E_M4_GRAMMAR", "M4", f"non_negotiable[{idx}].rule must be a non-empty string.", skill_file)
        eb = item.get("enforced_by")
        if eb == "aisop.main":
            if "main" not in aisop:
                reporter.fail("AISP_E_M4_PHANTOM", "M4", "enforced_by aisop.main but aisop.main is missing.", skill_file)
            continue
        if eb == "tools":
            if not isinstance(tools, list) or not tools:
                reporter.fail("AISP_E_M4_TOOLS", "M4", "enforced_by tools requires a non-empty restricted tools allow-list.", skill_file)
            else:
                _check_tools_hardness(system, tools, tool_evidence, strict_tools, reporter, skill_file)
            continue
        match = ENFORCED_BY_RE.match(str(eb or ""))
        if not match:
            reporter.fail("AISP_E_M4_NO_MECHANISM", "M4", f"Invalid enforced_by binding: {eb!r}.", skill_file)
            continue
        node, step, mechanism = match.groups()
        if not _is_step_key(step):
            reporter.fail("AISP_E_M4_PHANTOM", "M4", f"enforced_by points to non-execution field {node}.{step}.", skill_file)
            continue
        value = functions.get(node, {}).get(step) if isinstance(functions.get(node), dict) else None
        if value is None:
            reporter.fail("AISP_E_M4_PHANTOM", "M4", f"enforced_by points to missing function step {node}.{step}.", skill_file)
        elif not isinstance(value, str) or not re.match(re.escape(mechanism) + r"\s*\(", value.strip()):
            reporter.fail("AISP_E_M4_NO_MECHANISM", "M4", f"{node}.{step} does not begin with {mechanism}.", skill_file)


def _check_tools_hardness(
    system: dict[str, Any],
    tools: list[Any],
    evidence: ToolEvidence | None,
    strict_tools: bool,
    reporter: Reporter,
    skill_file: Path,
) -> None:
    skill_id = system.get("id")
    if evidence and evidence.runtime_skill_id and evidence.runtime_skill_id != skill_id:
        reporter.fail("AISP_E_R6_TRACE_SKILL_MISMATCH", "R6", f"Runtime trace skill_id {evidence.runtime_skill_id!r} does not match skill {skill_id!r}.", skill_file)
        return

    runtime_trace_conformant = True
    if evidence and evidence.runtime_path:
        trace_report = _check_runtime_trace(skill_file.parent, evidence.runtime_path)
        runtime_trace_conformant = trace_report["fail_count"] == 0
        if not runtime_trace_conformant:
            message = "Runtime trace cannot be used as hard tool evidence because runtime conformance checks failed."
            if strict_tools:
                reporter.fail("AISP_E_R6_TRACE_NOT_CONFORMANT", "R6", message, skill_file)
            else:
                reporter.warn("AISP_W_R6_TRACE_NOT_CONFORMANT", "R6", message, skill_file)
            return

    if evidence and evidence.runtime_mode == "advisory":
        if strict_tools:
            reporter.fail("AISP_E_R6_TOOLS_NOT_HARD", "R6", "Strict tools mode requires hard runtime tool enforcement; trace declares advisory.", skill_file)
        else:
            reporter.warn("AISP_W_R6_ADVISORY", "R6", "Runtime declares advisory tool enforcement; enforced_by: tools is not a hard guarantee.", skill_file)
        return
    if evidence and evidence.runtime_mode == "unknown" and not evidence.capability_modes:
        if strict_tools:
            reporter.fail("AISP_E_R6_TOOLS_NOT_HARD", "R6", "Strict tools mode requires hard runtime tool enforcement; trace does not declare hard enforcement.", skill_file)
        else:
            reporter.warn("AISP_W_R6_NO_DECLARATION", "R6", "Runtime trace does not declare hard or advisory tool enforcement.", skill_file)
        return

    capability_modes = evidence.capability_modes if evidence and evidence.capability_modes else {}
    if capability_modes or (evidence and evidence.capability_provided):
        tool_names = [str(tool) for tool in tools]
        missing = [tool for tool in tool_names if tool not in capability_modes]
        non_hard = [tool for tool in tool_names if capability_modes.get(tool) != "hard"]
        if not missing and not non_hard:
            if evidence and evidence.capability_has_provenance:
                reporter.info("AISP_I_R6_TOOLS_HARD", "R6", "Capability artifact meets the hard-evidence structure; provenance claims are not independently authenticated.", skill_file)
            elif strict_tools:
                reporter.fail("AISP_E_R6_TOOLS_NOT_HARD", "R6", "Hard tool capability evidence lacks provenance; it is an unverified attestation.", skill_file)
            else:
                reporter.warn("AISP_W_R6_TOOLS_ATTESTED_NOT_VERIFIED", "R6", "Tool capabilities attest hard enforcement but lack provenance; not independently verified.", skill_file)
            return
        detail = []
        if missing:
            detail.append(f"missing capabilities for {missing}")
        if non_hard:
            detail.append(f"non-hard capabilities for {non_hard}")
        message = "Tool capability evidence is not hard for all declared tools: " + "; ".join(detail) + "."
        if strict_tools:
            reporter.fail("AISP_E_R6_TOOLS_NOT_HARD", "R6", message, skill_file)
        elif any(capability_modes.get(tool) == "advisory" for tool in non_hard):
            reporter.warn("AISP_W_R6_ADVISORY", "R6", message, skill_file)
        else:
            reporter.warn("AISP_W_R6_NO_DECLARATION", "R6", message, skill_file)
        return

    if evidence and evidence.runtime_mode == "hard":
        if runtime_trace_conformant and _has_hard_tool_enforcement_event(evidence.runtime_events or [], tools):
            reporter.info("AISP_I_R6_TOOLS_HARD", "R6", "Trace meets the tool-enforcement event criteria; recorded events are not independently authenticated.", skill_file)
        elif strict_tools:
            reporter.fail("AISP_E_R6_TOOLS_NOT_HARD", "R6", "Runtime trace only attests hard tool enforcement at the top level; missing matching tool_enforcement event evidence.", skill_file)
        else:
            reporter.warn("AISP_W_R6_TOOLS_ATTESTED_NOT_VERIFIED", "R6", "Runtime trace attests hard tool enforcement but lacks matching event evidence; not independently verified.", skill_file)
        return

    if strict_tools:
        reporter.fail("AISP_E_R6_TOOLS_NOT_HARD", "R6", "Strict tools mode requires hard runtime/tool capability evidence for enforced_by: tools.", skill_file)
    else:
        reporter.warn("AISP_W_R6_TOOLS_CONDITIONAL", "R6", "enforced_by: tools is hard only when the runtime enforces tool permissions.", skill_file)


def _has_hard_tool_enforcement_event(events: list[dict[str, Any]], tools: list[Any]) -> bool:
    tool_names = {str(tool) for tool in tools}
    for event in events:
        if event.get("type") != "tool_enforcement":
            continue
        mode = event.get("enforcement", event.get("mode"))
        if mode != "hard":
            continue
        event_tools = event.get("tools")
        if event_tools is None:
            return True
        if isinstance(event_tools, list) and tool_names.issubset({str(tool) for tool in event_tools}):
            return True
    return False


def _has_capability_provenance(doc: dict[str, Any]) -> bool:
    provenance = doc.get("provenance")
    if not isinstance(provenance, dict):
        return False
    for field in ("source", "generated_by", "runtime", "registry", "signature"):
        if isinstance(provenance.get(field), str) and provenance[field].strip():
            return True
    return False


def _check_resources(contract: dict[str, Any], functions: dict[str, Any], skill_dir: Path, aisp_dir: Path, reporter: Reporter, skill_file: Path) -> dict[str, dict[str, Any]]:
    resources = contract.get("resources", [])
    if not isinstance(resources, list):
        reporter.fail("AISP_E_M5_RESOURCES", "M5", "resources must be an array when present.", skill_file)
        return {}

    by_path: dict[str, dict[str, Any]] = {}
    binding_modes: dict[tuple[str, Path], str] = {}
    shared_root = aisp_dir / "_shared"
    for idx, resource in enumerate(resources):
        if not isinstance(resource, dict):
            reporter.fail("AISP_E_M5_RESOURCE", "M5", f"resources[{idx}] must be an object.", skill_file)
            continue
        for field in ("id", "path", "kind", "mode"):
            if not isinstance(resource.get(field), str) or not resource[field]:
                reporter.fail("AISP_E_M5_RESOURCE", "M5", f"resources[{idx}] missing required field {field}.", skill_file)
        if not isinstance(resource.get("path"), str) or not resource["path"]:
            continue
        raw_path = str(resource.get("path", ""))
        mode = resource.get("mode")
        scope = resource.get("scope", "skill")
        if not isinstance(mode, str) or mode not in VALID_RESOURCE_MODES:
            reporter.fail("AISP_E_M5_MODE", "M5", f"Resource {raw_path!r} has invalid mode {mode!r}.", skill_file)
            continue
        if not isinstance(scope, str) or scope not in VALID_RESOURCE_SCOPES:
            reporter.fail("AISP_E_M5_SCOPE", "M5", f"Resource {raw_path!r} has invalid scope {scope!r}.", skill_file)
            continue
        if resource.get("kind") == "script" and not resource.get("requires_tools"):
            reporter.warn("AISP_W_M5_NO_REQUIRES_TOOLS", "M5", f"Script resource {raw_path!r} should declare requires_tools.", skill_file)
        if "sha256" in resource and (not isinstance(resource["sha256"], str) or not re.fullmatch(r"[a-fA-F0-9]{64}", resource["sha256"])):
            reporter.fail("AISP_E_M5_SHA256", "M5", f"Resource {raw_path!r} has invalid sha256.", skill_file)
        if "requires_tools" in resource and (not isinstance(resource["requires_tools"], list) or any(
            not isinstance(tool, str) for tool in resource["requires_tools"]
        )):
            reporter.fail("AISP_E_M5_RESOURCE", "M5", f"Resource {raw_path!r} requires_tools must be an array of strings.", skill_file)
        if REMOTE_RE.match(raw_path):
            reporter.fail("AISP_E_SE2_REMOTE", "SE2", f"Remote resource {raw_path!r} is disabled by default and must be confirmation-gated.", skill_file)
            continue
        rel = Path(raw_path.replace("\\", "/"))
        if raw_path.startswith(("\\", "/")) or rel.is_absolute() or re.match(r"^[A-Za-z]:", raw_path) or ".." in rel.parts:
            reporter.fail("AISP_E_M5_PATH_ESCAPE", "M5", f"Resource path {raw_path!r} is absolute or escapes the package.", skill_file)
            continue
        try:
            base = shared_root.resolve() if scope == "shared" else skill_dir
            if scope == "shared" and not _is_inside(base, aisp_dir):
                raise ValueError("_shared root resolves outside the aisp directory")
            resolved = _safe_resolve(base, str(rel))
            if not _is_inside(resolved, base):
                raise ValueError("resource resolves outside its declared scope")
            if not resolved.exists():
                reporter.warn("AISP_W_M5_MISSING_RESOURCE", "M5", f"Declared resource {raw_path!r} does not exist.", skill_file)
        except (OSError, ValueError, RuntimeError) as exc:
            reporter.fail("AISP_E_SE1_PATH", "SE1", f"Cannot confine resource {raw_path!r}: {exc}.", skill_file)
            continue
        entry = dict(resource)
        entry["_resolved"] = resolved
        key = _normalize_rel(raw_path)
        binding = (key, resolved)
        previous_mode = binding_modes.get(binding)
        if previous_mode is not None and previous_mode != mode:
            reporter.fail("AISP_E_SE3_MODE_GATE", "SE3", f"Conflicting modes for the same normalized resource path {key!r}; aliases must not broaden permissions.", skill_file)
            continue
        binding_modes[binding] = mode
        previous = by_path.get(key)
        entry["_resolved_paths"] = {resolved, *previous["_resolved_paths"]} if previous else {resolved}
        entry["_declared_modes"] = {mode, *previous["_declared_modes"]} if previous else {mode}
        by_path[key] = entry
    return by_path


def _check_resource_usage(resources: dict[str, dict[str, Any]], functions: dict[str, Any], reporter: Reporter, skill_file: Path) -> None:
    for node, step_key, step in _step_strings(functions):
        for read_path in _extract_call_paths(step, "sys.io.read"):
            norm = _normalize_rel(read_path)
            resource = resources.get(norm)
            if not resource:
                reporter.warn("AISP_W_M5_UNDECLARED_USE", "M5", f"{node}.{step_key} reads undeclared resource {read_path!r}.", skill_file)
                continue
            if len(resource.get("_resolved_paths", ())) > 1:
                if READ_MODES.isdisjoint(resource.get("_declared_modes", (resource.get("mode"),))):
                    reporter.fail("AISP_E_SE3_MODE_GATE", "SE3", f"Every scoped declaration for {read_path!r} forbids reading; target ambiguity cannot waive the mode gate.", skill_file)
                else:
                    reporter.warn("AISP_W_M5_AMBIGUOUS_USE", "M5", f"{node}.{step_key} reads {read_path!r}, which names distinct skill/shared resources; static mode matching cannot disambiguate the scope.", skill_file)
                continue
            if resource.get("mode") not in READ_MODES:
                reporter.fail("AISP_E_SE3_MODE_GATE", "SE3", f"{node}.{step_key} reads execute_only resource {read_path!r}.", skill_file)
        for script_path in _extract_sys_run_scripts(step):
            norm = _normalize_rel(script_path)
            resource = resources.get(norm)
            if not resource:
                reporter.warn("AISP_W_M5_UNDECLARED_USE", "M5", f"{node}.{step_key} executes undeclared resource {script_path!r}.", skill_file)
                continue
            if len(resource.get("_resolved_paths", ())) > 1:
                if EXEC_MODES.isdisjoint(resource.get("_declared_modes", (resource.get("mode"),))):
                    reporter.fail("AISP_E_SE3_MODE_GATE", "SE3", f"Every scoped declaration for {script_path!r} forbids execution; target ambiguity cannot waive the mode gate.", skill_file)
                else:
                    reporter.warn("AISP_W_M5_AMBIGUOUS_USE", "M5", f"{node}.{step_key} executes {script_path!r}, which names distinct skill/shared resources; static mode matching cannot disambiguate the scope.", skill_file)
                continue
            if resource.get("mode") not in EXEC_MODES:
                reporter.fail("AISP_E_SE3_MODE_GATE", "SE3", f"{node}.{step_key} executes non-executable resource {script_path!r}.", skill_file)


def _check_self_trust(system: dict[str, Any], contract: dict[str, Any], reporter: Reporter, skill_file: Path) -> None:
    for path, value in _walk_json({"system": system, "contract": contract}):
        if path and path[-1].lower() in TRUST_KEYS and _truthy_trust(value):
            reporter.fail("AISP_E_M6_SELF_TRUST", "M6", f"Self-declared trust field {'.'.join(path)} is forbidden.", skill_file)


def _check_undeclared_files(resources: dict[str, dict[str, Any]], skill_dir: Path, reporter: Reporter) -> None:
    declared = {Path(path).resolve() for entry in resources.values() if entry.get("_resolved")
                for path in entry.get("_resolved_paths", (entry["_resolved"],))}
    for path in skill_dir.rglob("*"):
        if not path.is_file() or path.name in ROOT_SKIP_NAMES:
            continue
        if path.resolve() not in declared:
            reporter.warn("AISP_W_M5_UNDECLARED_FILE", "M5", f"File is present but not declared in aisp_contract.resources: {_path(path.relative_to(skill_dir))}.", path)


def tool_capabilities_shape_errors(doc: Any) -> list[str]:
    """Check the bounded published v1 capability shape, not provenance truth."""
    if not isinstance(doc, dict):
        return ["tool capabilities must be an object"]
    errors = []
    if doc.get("tool_capabilities_version") != "1.0":
        errors.append("tool_capabilities_version must be 1.0")
    if "provenance" in doc:
        provenance = doc["provenance"]
        if not isinstance(provenance, dict):
            errors.append("provenance must be an object")
        else:
            for field in ("source", "generated_by", "runtime", "registry", "signature"):
                if field in provenance and (not isinstance(provenance[field], str) or not provenance[field]):
                    errors.append(f"provenance.{field} must be a non-empty string")
    tools = doc.get("tools")
    if not isinstance(tools, dict):
        return [*errors, "tools must be an object"]
    for name, spec in tools.items():
        if not isinstance(spec, dict):
            errors.append(f"tools.{name} must be an object")
            continue
        if spec.get("risk_level") not in ("low", "medium", "high", "critical"):
            errors.append(f"tools.{name}.risk_level has an invalid or missing value")
        if spec.get("enforcement") not in ("hard", "advisory", "unknown"):
            errors.append(f"tools.{name}.enforcement has an invalid or missing value")
        for field in ("capabilities", "forbidden_capabilities"):
            if field in spec and (not isinstance(spec[field], list) or any(not isinstance(value, str) for value in spec[field])):
                errors.append(f"tools.{name}.{field} must be an array of strings")
    return errors


def _load_tool_evidence(runtime_trace: Path | None = None, tool_capabilities: Path | None = None) -> ToolEvidence | None:
    if not runtime_trace and not tool_capabilities:
        return None
    evidence = ToolEvidence(capability_modes={})
    if runtime_trace:
        doc = strict_json_loads(runtime_trace.read_text(encoding="utf-8-sig"))
        errors = _trace_shape_errors(doc)
        if errors:
            raise ValueError("Invalid runtime trace shape: " + "; ".join(errors))
        evidence.runtime_path = runtime_trace
        mode = doc.get("tool_enforcement")
        if mode in {"hard", "advisory"}:
            evidence.runtime_mode = mode
        else:
            evidence.runtime_mode = "unknown"
        evidence.runtime_skill_id = doc.get("skill_id") if isinstance(doc.get("skill_id"), str) else None
        evidence.runtime_events = [event for event in doc.get("events", []) if isinstance(event, dict)]
    if tool_capabilities:
        doc = strict_json_loads(tool_capabilities.read_text(encoding="utf-8-sig"))
        errors = tool_capabilities_shape_errors(doc)
        if errors:
            raise ValueError("Invalid tool capabilities shape: " + "; ".join(errors))
        evidence.capability_provided = True
        evidence.capability_has_provenance = _has_capability_provenance(doc)
        evidence.capability_modes = {
            name: spec["enforcement"] for name, spec in doc["tools"].items()
        }
    return evidence


def validate_aisp_dir(
    aisp_dir: Path,
    tool_evidence: ToolEvidence | None = None,
    strict_tools: bool = False,
    strict_readme: bool = False,
) -> dict[str, Any]:
    aisp_dir = aisp_dir.resolve()
    reporter = Reporter()
    if not (aisp_dir / "README.md").is_file():
        reporter.fail("AISP_E_EC1_README", "EC1", "aisp/ directory must contain README.md.", aisp_dir)
    if (aisp_dir / "_shared" / "aisp.aisop.json").exists():
        reporter.warn("AISP_W_EC3_SHARED", "EC3", "_shared/ must not be a skill folder.", aisp_dir / "_shared")
    _check_discovery_script(aisp_dir / "aisp_list.py", reporter)

    skill_paths = []
    for path in sorted(aisp_dir.glob("*_aisp")):
        if not path.is_dir():
            continue
        if not _is_inside(path.resolve(), aisp_dir):
            reporter.fail("AISP_E_EC2_INDEX", "EC2", "Skill folder resolves outside aisp/.", path)
            continue
        skill_paths.append(path)
    skill_reports = [
        validate_skill(path, aisp_dir, tool_evidence, strict_tools, strict_readme)
        for path in skill_paths
    ]
    _check_index(aisp_dir, skill_reports, reporter)

    all_results = list(reporter.results)
    for report in skill_reports:
        all_results.extend(Result(**_result_from_dict(item)) for item in report["results"])

    return _summary_report(aisp_dir, all_results, {"skill_reports": skill_reports})


def _result_from_dict(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "code": item["code"],
        "rule_id": item["rule_id"],
        "severity": item["severity"],
        "passed": item["passed"],
        "message": item["message"],
        "path": item.get("path"),
        "suggested_fix": item.get("suggested_fix"),
    }


def _check_discovery_script(script: Path, reporter: Reporter) -> None:
    if not script.exists() and not script.is_symlink():
        reporter.warn("AISP_W_EC1_NO_SCRIPT", "EC1", "aisp_list.py is SHOULD but missing.", script.parent)
        return
    try:
        if not script.is_file() or not _is_inside(script.resolve(), script.parent.resolve()):
            raise ValueError("discovery script must be a file confined to the aisp directory")
        text = script.read_text(encoding="utf-8-sig")
        tree = ast.parse(text)
    except (OSError, ValueError, RuntimeError, SyntaxError) as exc:
        reporter.fail("AISP_E_SE5_SCRIPT", "SE5", f"Cannot inspect aisp_list.py: {exc}.", script)
        return
    bad_imports: list[str] = []
    bad_calls: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            bad_imports.extend(alias.name for alias in node.names if alias.name.split(".")[0] not in {"json", "sys", "pathlib", "re"})
        elif isinstance(node, ast.ImportFrom):
            mod = (node.module or "").split(".")[0]
            if mod not in {"pathlib"}:
                bad_imports.append(node.module or "")
        elif isinstance(node, ast.Call):
            name = _call_name(node.func)
            if name in {"subprocess.run", "subprocess.Popen", "os.system", "requests.get", "urllib.request.urlopen"}:
                bad_calls.append(name)
            if name.endswith(".open") or name == "open":
                bad_calls.append(name)
            if name.endswith(".unlink") or name.endswith(".rmdir") or name.endswith(".remove"):
                bad_calls.append(name)
            if name.endswith(".write_text"):
                if not _write_target_looks_like_index(node.func):
                    bad_calls.append(name)
    if bad_imports:
        reporter.fail("AISP_E_SE5_SCRIPT", "SE5", f"aisp_list.py imports disallowed modules: {sorted(set(bad_imports))}.", script)
    if bad_calls:
        reporter.fail("AISP_E_SE5_SCRIPT", "SE5", f"aisp_list.py uses disallowed calls: {sorted(set(bad_calls))}.", script)


def _call_name(func: ast.AST) -> str:
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return _call_name(func.value) + "." + func.attr
    return ""


def _write_target_looks_like_index(func: ast.AST) -> bool:
    if not isinstance(func, ast.Attribute):
        return False
    text = ast.unparse(func.value) if hasattr(ast, "unparse") else ""
    return "aisp_list.json" in text or text == "out"


def _check_index(aisp_dir: Path, skill_reports: list[dict[str, Any]], reporter: Reporter) -> None:
    index_path = aisp_dir / "aisp_list.json"
    if not index_path.exists() and not index_path.is_symlink():
        reporter.warn("AISP_W_EC1_NO_INDEX", "EC1", "aisp_list.json is SHOULD but missing.", aisp_dir)
        return
    if index_path.is_symlink() or not index_path.is_file():
        reporter.fail("AISP_E_EC2_INDEX", "EC2", "aisp_list.json must be a regular non-symlink file.", index_path)
        return
    doc = _load_json(index_path, reporter, "EC2")
    if not isinstance(doc, dict):
        reporter.fail("AISP_E_EC2_INDEX", "EC2", "aisp_list.json must be an object.", index_path)
        return
    entries = doc.get("skills")
    if not isinstance(entries, list) or any(
        not isinstance(row, dict) or not isinstance(row.get("id"), str)
        or not SKILL_ID_RE.fullmatch(row["id"]) for row in entries
    ):
        reporter.fail("AISP_E_EC2_INDEX", "EC2", "Index skills must be an array of objects with valid skill ids.", index_path)
        return
    rows = {row["id"]: row for row in entries}
    if len(rows) != len(entries):
        reporter.fail("AISP_E_EC2_INDEX", "EC2", "Index contains duplicate skill ids.", index_path)
    actual = {report["id"]: report for report in skill_reports if report.get("id")}
    for skill_id in sorted(set(actual) - set(rows)):
        reporter.warn("AISP_W_EC2_INDEX_DRIFT", "EC2", f"Skill {skill_id} is missing from aisp_list.json.", index_path)
    for skill_id in sorted(set(rows) - set(actual)):
        reporter.warn("AISP_W_EC2_INDEX_DRIFT", "EC2", f"Index row {skill_id} has no matching skill folder.", index_path)
    for skill_id in sorted(set(actual) & set(rows)):
        program = Path(actual[skill_id]["target"]) / "aisp.aisop.json"
        expected = program.relative_to(aisp_dir.parent).as_posix()
        if rows[skill_id].get("path") != expected:
            reporter.warn("AISP_W_EC2_INDEX_DRIFT", "EC2", f"Index path for {skill_id} differs from folder truth.", index_path)
        if not actual[skill_id].get("conformant"):
            continue
        try:
            _, skill_doc = _load_skill_document(program)
        except (OSError, ValueError, RuntimeError) as exc:
            reporter.fail("AISP_E_EC2_INDEX", "EC2", f"Cannot inspect index source for {skill_id}: {exc}", index_path)
            continue
        system = skill_doc[0]["content"]
        contract = skill_doc[1]["content"]["aisp_contract"]
        discovery = contract.get("discovery", {})
        invocation = contract.get("invocation", {})
        if not isinstance(discovery, dict) or not isinstance(invocation, dict):
            reporter.fail("AISP_E_EC2_INDEX", "EC2", f"Index source for {skill_id} changed to a malformed contract.", index_path)
            continue
        metadata = {
            "name": system.get("name"),
            "summary": system.get("summary") or system.get("description", ""),
            "category": discovery.get("category"),
            "tags": discovery.get("tags", []),
            "when_to_use": invocation.get("when_to_use", []),
            "risk_level": contract.get("risk_level"),
        }
        drift = [key for key, value in metadata.items() if rows[skill_id].get(key) != value]
        if drift:
            reporter.warn("AISP_W_EC2_INDEX_DRIFT", "EC2", f"Index metadata for {skill_id} differs from folder truth: {', '.join(drift)}.", index_path)


def _report(skill_dir: Path, reporter: Reporter) -> dict[str, Any]:
    fails = [r for r in reporter.results if r.severity == "FAIL" and not r.passed]
    warnings = [r for r in reporter.results if r.severity == "WARN" and not r.passed]
    skill_id = skill_dir.name
    return {
        "target": _path(skill_dir),
        "id": skill_id,
        "conformant": not fails,
        "fail_count": len(fails),
        "warning_count": len(warnings),
        "results": [r.as_dict() for r in reporter.results],
    }


def _summary_report(target: Path, results: list[Result], extra: dict[str, Any] | None = None) -> dict[str, Any]:
    fails = [r for r in results if r.severity == "FAIL" and not r.passed]
    warnings = [r for r in results if r.severity == "WARN" and not r.passed]
    out = {
        "target": _path(target),
        "conformant": not fails,
        "fail_count": len(fails),
        "warning_count": len(warnings),
        "results": [r.as_dict() for r in results],
    }
    if extra:
        out.update(extra)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate AISP skills and aisp/ directories.")
    parser.add_argument("paths", nargs="+", help="Skill folder, aisp.aisop.json, or aisp/ directory paths.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--warnings-fail", action="store_true", help="Return exit code 1 when warnings remain; keep report severity and conformance unchanged.")
    parser.add_argument("--runtime-trace", help="Optional runtime trace JSON checked against tool-enforcement evidence criteria; event origins are not authenticated.")
    parser.add_argument("--tool-capabilities", help="Optional tool capability JSON checked against tool-enforcement evidence criteria; provenance is not authenticated.")
    parser.add_argument("--strict-tools", action="store_true", help="Fail enforced_by: tools unless hard runtime/tool capability evidence is provided.")
    parser.add_argument("--strict-readme", action="store_true", help="Fail missing/manual/drifted/bad-marker per-skill README.md instead of warning.")
    args = parser.parse_args(argv)

    try:
        tool_evidence = _load_tool_evidence(
            Path(args.runtime_trace) if args.runtime_trace else None,
            Path(args.tool_capabilities) if args.tool_capabilities else None,
        )
    except Exception as exc:  # noqa: BLE001
        result = Result("AISP_E_INPUT", "INPUT", "FAIL", False, f"Cannot read tool enforcement evidence: {exc}")
        report = _summary_report(Path("."), [result])
        if args.json:
            print(json.dumps({"reports": [report]}, ensure_ascii=False, indent=2))
        else:
            print(f"FAIL . ({report['fail_count']} fail, {report['warning_count']} warn)")
            print(f"  FAIL {result.code}: {result.message}")
        return 1

    reports = []
    for raw in args.paths:
        path = Path(raw)
        try:
            if path.is_file() and path.name == "aisp.aisop.json":
                reports.append(validate_skill(path.parent, tool_evidence=tool_evidence, strict_tools=args.strict_tools, strict_readme=args.strict_readme))
            elif path.is_dir() and (path / "aisp.aisop.json").is_file():
                reports.append(validate_skill(path, tool_evidence=tool_evidence, strict_tools=args.strict_tools, strict_readme=args.strict_readme))
            elif path.is_dir():
                reports.append(validate_aisp_dir(path, tool_evidence, args.strict_tools, args.strict_readme))
            else:
                reports.append(_summary_report(path, [Result("AISP_E_INPUT", "INPUT", "FAIL", False, "Path does not exist or is not an AISP target.", _path(path))]))
        except (OSError, ValueError, RuntimeError) as exc:
            reports.append(_summary_report(path, [Result("AISP_E_INPUT", "INPUT", "FAIL", False, f"Cannot inspect target: {exc}", _path(path))]))

    failed = any(not report["conformant"] for report in reports)
    warned = any(report.get("warning_count", 0) for report in reports)
    if args.json:
        print(json.dumps({"reports": reports}, ensure_ascii=False, indent=2))
    else:
        for report in reports:
            status = "PASS" if report["conformant"] else "FAIL"
            print(f"{status} {report['target']} ({report['fail_count']} fail, {report['warning_count']} warn)")
            for result in report["results"]:
                if result["severity"] != "INFO":
                    print(f"  {result['severity']} {result['code']}: {result['message']}")
    return 1 if failed or (args.warnings_fail and warned) else 0


if __name__ == "__main__":
    raise SystemExit(main())
