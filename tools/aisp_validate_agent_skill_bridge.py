#!/usr/bin/env python3
"""Validate Agent Skills SKILL.md sidecar bridges for native AISP skills.

The bridge is an interoperability projection, not an execution authority. This
tool checks that a SKILL.md can be discovered by Agent Skills platforms, that it
points to the native same-folder AISP program without path escape, and that the
native program passes the reference AISP validator.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from .aisp_validate import validate_skill
except ImportError:  # pragma: no cover - script execution path
    from aisp_validate import validate_skill


PROTOCOL = "AISP V1.0.0"
NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
REMOTE_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://")
INJECTION_RE = re.compile(
    r"\b(ignore|disregard|override)\s+(all\s+)?(previous|prior|system|developer)\s+instructions\b|"
    r"\bjailbreak\b|\bexfiltrat(e|ion)\b|\breveal\s+(secrets?|system\s+prompt)\b",
    re.IGNORECASE,
)
ALLOWED_FRONTMATTER_KEYS = {"allowed-tools", "description", "license", "metadata", "name"}


@dataclass
class BridgeResult:
    code: str
    rule_id: str
    severity: str
    passed: bool
    message: str
    path: str | None = None
    suggested_fix: str | None = None

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
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


class BridgeReporter:
    def __init__(self) -> None:
        self.results: list[BridgeResult] = []

    def fail(self, code: str, message: str, path: Path | str | None = None, fix: str | None = None) -> None:
        self.results.append(BridgeResult(code, "EC7", "FAIL", False, message, _path(path), fix))

    def warn(self, code: str, message: str, path: Path | str | None = None, fix: str | None = None) -> None:
        self.results.append(BridgeResult(code, "EC7", "WARN", False, message, _path(path), fix))

    def info(self, code: str, message: str, path: Path | str | None = None) -> None:
        self.results.append(BridgeResult(code, "EC7", "INFO", True, message, _path(path)))

    @property
    def has_failures(self) -> bool:
        return any(result.severity == "FAIL" for result in self.results)


def _path(path: Path | str | None) -> str | None:
    return str(path).replace("\\", "/") if path is not None else None


def _normalize_text(text: str) -> str:
    if text.startswith("\ufeff"):
        text = text[1:]
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str, str | None]:
    normalized = _normalize_text(text)
    lines = normalized.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, normalized, "SKILL.md must start with a standalone YAML frontmatter delimiter."

    close_index: int | None = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            close_index = index
            break
    if close_index is None:
        return {}, normalized, "SKILL.md frontmatter is missing a closing standalone --- delimiter."

    frontmatter_lines = lines[1:close_index]
    body = "\n".join(lines[close_index + 1 :])
    data: dict[str, Any] = {}
    current_map: dict[str, str] | None = None
    current_key: str | None = None

    for raw in frontmatter_lines:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith((" ", "\t")):
            if current_map is None or current_key is None:
                return data, body, f"Unsupported indented frontmatter line: {raw!r}."
            if ":" not in raw:
                return data, body, f"Unsupported nested frontmatter line: {raw!r}."
            key, value = raw.strip().split(":", 1)
            current_map[key.strip()] = _strip_quotes(value)
            continue
        if ":" not in raw:
            return data, body, f"Unsupported frontmatter line: {raw!r}."
        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not value:
            nested: dict[str, str] = {}
            data[key] = nested
            current_map = nested
            current_key = key
        else:
            data[key] = _strip_quotes(value)
            current_map = None
            current_key = None
    return data, body, None


def _safe_bridge_path(base: Path, rel: str) -> tuple[Path | None, str | None]:
    if not rel.strip():
        return None, "metadata.aisp_program must not be empty."
    normalized = rel.replace("\\", "/")
    if REMOTE_RE.match(normalized):
        return None, "metadata.aisp_program must be a local relative path, not a URL."
    if Path(normalized).is_absolute():
        return None, "metadata.aisp_program must be relative, not absolute."
    parts = [part for part in normalized.split("/") if part not in {"", "."}]
    if any(part == ".." for part in parts):
        return None, "metadata.aisp_program must not contain path traversal."
    resolved = (base / normalized).resolve()
    try:
        resolved.relative_to(base.resolve())
    except ValueError:
        return None, "metadata.aisp_program must stay inside the sidecar folder."
    return resolved, None


def _bridge_name_from_skill_id(skill_id: str) -> str:
    if skill_id.endswith("_aisp"):
        skill_id = skill_id[: -len("_aisp")]
    return skill_id.replace("_", "-")


def _load_native_skill_id(program: Path) -> str | None:
    try:
        doc = json.loads(program.read_text(encoding="utf-8-sig"))
    except Exception:
        return None
    if not isinstance(doc, list) or not doc:
        return None
    system = doc[0].get("content") if isinstance(doc[0], dict) else None
    if not isinstance(system, dict):
        return None
    skill_id = system.get("id")
    return skill_id if isinstance(skill_id, str) else None


def iter_bridge_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target.resolve()] if target.name == "SKILL.md" else []
    if not target.is_dir():
        return []
    direct = target / "SKILL.md"
    if direct.is_file():
        return [direct.resolve()]
    return sorted(path.resolve() for path in target.rglob("SKILL.md") if ".git" not in path.parts)


def validate_bridge(bridge: Path, strict_readme: bool = False) -> dict[str, Any]:
    bridge = bridge.resolve()
    bridge_dir = bridge.parent
    reporter = BridgeReporter()

    if not bridge.is_file():
        reporter.fail("AISP_E_EC7_BRIDGE_MISSING", "SKILL.md bridge is missing.", bridge)
        return _report(bridge, reporter)

    try:
        text = bridge.read_text(encoding="utf-8-sig")
    except Exception as exc:  # noqa: BLE001
        reporter.fail("AISP_E_EC7_BRIDGE_INPUT", f"Cannot read SKILL.md: {exc}", bridge)
        return _report(bridge, reporter)

    frontmatter, body, parse_error = _parse_frontmatter(text)
    if parse_error:
        reporter.fail("AISP_E_EC7_FRONTMATTER", parse_error, bridge, "Use standalone opening and closing --- lines with simple YAML key/value frontmatter.")
        return _report(bridge, reporter)

    unknown_keys = sorted(set(frontmatter) - ALLOWED_FRONTMATTER_KEYS)
    if unknown_keys:
        reporter.fail(
            "AISP_E_EC7_FRONTMATTER",
            "SKILL.md frontmatter contains unsupported top-level key(s): " + ", ".join(unknown_keys),
            bridge,
            "Use only name, description, license, allowed-tools, and metadata; put runtime compatibility notes in the body.",
        )

    name = frontmatter.get("name")
    if not isinstance(name, str) or not name.strip():
        reporter.fail("AISP_E_EC7_NAME", "SKILL.md frontmatter must include a non-empty name.", bridge)
    else:
        if not NAME_RE.fullmatch(name):
            reporter.fail("AISP_E_EC7_NAME", "SKILL.md name must use lowercase letters, digits, and hyphens.", bridge)
        if any(forbidden in name.lower() for forbidden in ("anthropic", "claude")):
            reporter.fail("AISP_E_EC7_NAME", "SKILL.md name must not contain anthropic or claude.", bridge)

    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip():
        reporter.fail("AISP_E_EC7_DESCRIPTION", "SKILL.md frontmatter must include a non-empty description.", bridge)
    else:
        if len(description) > 1024:
            reporter.fail("AISP_E_EC7_DESCRIPTION", "SKILL.md description must be 1024 characters or less.", bridge)
        if INJECTION_RE.search(description):
            reporter.fail("AISP_E_EC7_DESCRIPTION", "SKILL.md description contains instruction-injection wording.", bridge)

    metadata = frontmatter.get("metadata")
    if not isinstance(metadata, dict):
        reporter.fail("AISP_E_EC7_METADATA", "SKILL.md frontmatter must include metadata.generated_from_aisp and metadata.aisp_program.", bridge)
        metadata = {}
    if str(metadata.get("generated_from_aisp", "")).lower() != "true":
        reporter.fail("AISP_E_EC7_METADATA", 'metadata.generated_from_aisp must be "true".', bridge)
    program_rel = metadata.get("aisp_program")
    if not isinstance(program_rel, str):
        reporter.fail("AISP_E_EC7_PROGRAM_PATH", "metadata.aisp_program must be a relative path string.", bridge)
        program_rel = ""
    if metadata.get("protocol") != PROTOCOL:
        reporter.warn("AISP_W_EC7_PROTOCOL", f"metadata.protocol should be {PROTOCOL}.", bridge)
    if metadata.get("bridge_mode") != "native_sidecar":
        reporter.warn("AISP_W_EC7_BRIDGE_MODE", "metadata.bridge_mode should be native_sidecar.", bridge)

    if isinstance(program_rel, str) and program_rel.replace("\\", "/").strip() != "aisp.aisop.json":
        reporter.fail(
            "AISP_E_EC7_PROGRAM_PATH",
            "metadata.aisp_program must be exactly aisp.aisop.json for native sidecar bridges.",
            bridge,
        )

    program, path_error = _safe_bridge_path(bridge_dir, program_rel)
    if path_error:
        reporter.fail("AISP_E_EC7_PROGRAM_PATH", path_error, bridge)
        return _report(bridge, reporter)
    assert program is not None
    if program.name != "aisp.aisop.json":
        reporter.fail("AISP_E_EC7_PROGRAM_PATH", "metadata.aisp_program must point to an aisp.aisop.json file.", bridge)
    if not program.is_file():
        reporter.fail("AISP_E_EC7_PROGRAM_MISSING", "metadata.aisp_program points to a missing file.", program)
        return _report(bridge, reporter)

    native_id = _load_native_skill_id(program)
    if isinstance(name, str) and native_id:
        expected_name = _bridge_name_from_skill_id(native_id)
        if name != expected_name:
            reporter.fail(
                "AISP_E_EC7_NAME_DERIVATION",
                "SKILL.md name must be derived from the same-folder AISP id by removing _aisp and hyphenating underscores.",
                bridge,
                f"Set name: {expected_name}.",
            )

    normalized_body = _normalize_text(body)
    if "aisp.aisop.json" not in normalized_body:
        reporter.fail("AISP_E_EC7_BODY", "SKILL.md body must guide loading/running the same-folder aisp.aisop.json program.", bridge)
    body_lower = normalized_body.lower()
    native_sidecar = program.parent == bridge_dir and program.name == "aisp.aisop.json"
    if not native_sidecar:
        reporter.fail(
            "AISP_E_EC7_PROGRAM_PATH",
            "metadata.aisp_program must point to the same-folder native aisp.aisop.json sidecar target.",
            bridge,
            "Set metadata.aisp_program: aisp.aisop.json and place SKILL.md inside the native *_aisp skill folder.",
        )
    elif isinstance(name, str) and name != bridge_dir.name:
        reporter.info(
            "AISP_I_EC7_NATIVE_SIDECAR",
            "Native AISP sidecar mode: SKILL.md name may differ from the *_aisp folder name and is checked against the AISP id projection.",
            bridge,
        )

    if not (("thin" in body_lower and "bridge" in body_lower) or "not the source of truth" in body_lower):
        reporter.fail("AISP_E_EC7_BODY", "SKILL.md body must state that it is a thin bridge and not the source of truth.", bridge)
    if "aisp/aisop runtime" not in body_lower and "aisop runtime" not in body_lower:
        reporter.warn("AISP_W_EC7_RUNTIME_BOUNDARY", "SKILL.md should state that hard execution requires an AISP/AISOP runtime.", bridge)
    if "```json" in body_lower and '"functions"' in body_lower:
        reporter.warn("AISP_W_EC7_LOGIC_COPY", "SKILL.md appears to copy AISP function logic; keep the bridge thin.", bridge)

    native_report = validate_skill(program.parent, aisp_dir=program.parent.parent, strict_readme=strict_readme)
    if not native_report.get("conformant", False):
        codes = [
            result.get("code", "UNKNOWN")
            for result in native_report.get("results", [])
            if result.get("severity") == "FAIL"
        ]
        reporter.fail(
            "AISP_E_EC7_EMBEDDED_AISP",
            "Native same-folder AISP program failed reference validation: " + ", ".join(codes),
            program,
            "Fix the native AISP package before publishing the bridge.",
        )
    else:
        reporter.info("AISP_I_EC7_EMBEDDED_AISP", "Native same-folder AISP program passed reference validation.", program)

    return _report(bridge, reporter)


def _report(bridge: Path, reporter: BridgeReporter) -> dict[str, Any]:
    counts = {
        "fail": sum(1 for result in reporter.results if result.severity == "FAIL"),
        "warn": sum(1 for result in reporter.results if result.severity == "WARN"),
        "info": sum(1 for result in reporter.results if result.severity == "INFO"),
    }
    return {
        "path": _path(bridge),
        "conformant": counts["fail"] == 0,
        "summary": counts,
        "results": [result.as_dict() for result in reporter.results],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Agent Skills SKILL.md sidecars for native AISP skills.")
    parser.add_argument("targets", nargs="+", help="SKILL.md files, native *_aisp folders, or directories containing AISP sidecar bridges.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    parser.add_argument("--strict-readme", action="store_true", help="Require generated per-skill README conformance for native AISP programs.")
    args = parser.parse_args(argv)

    bridge_files: list[Path] = []
    for raw in args.targets:
        bridge_files.extend(iter_bridge_files(Path(raw)))
    bridge_files = sorted(dict.fromkeys(bridge_files))

    if not bridge_files:
        payload = {"reports": [], "summary": {"fail": 1, "warn": 0, "info": 0}, "conformant": False}
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print("FAIL no SKILL.md bridges found", file=sys.stderr)
        return 1

    reports = [validate_bridge(bridge, strict_readme=args.strict_readme) for bridge in bridge_files]
    summary = {
        "fail": sum(report["summary"]["fail"] for report in reports),
        "warn": sum(report["summary"]["warn"] for report in reports),
        "info": sum(report["summary"]["info"] for report in reports),
    }
    payload = {"reports": reports, "summary": summary, "conformant": summary["fail"] == 0}

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for report in reports:
            status = "PASS" if report["conformant"] else "FAIL"
            print(f"{status} {report['path']} ({report['summary']['fail']} fail, {report['summary']['warn']} warn)")
            for result in report["results"]:
                if result["severity"] in {"FAIL", "WARN"}:
                    print(f"  {result['severity']} {result['code']}: {result['message']}")
    return 0 if payload["conformant"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
