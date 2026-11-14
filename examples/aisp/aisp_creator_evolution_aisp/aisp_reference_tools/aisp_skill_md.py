#!/usr/bin/env python3
"""Generate and check the required, executor-only AISP Agent Skills interface."""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable

try:
    from .aisp_hash import load_skill, write_generated_text
except ImportError:  # pragma: no cover - standalone script
    from aisp_hash import load_skill, write_generated_text


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
EXECUTOR_DEFAULTS = {
    "executor": "soulrun",
    "executor_version": "soulrun --version",
    "executor_command": 'soulrun --aisp "<the folder of this SKILL.md>" --soulrun-cache-dir "<your working folder>/.soulrun_cache" --user-message-file "<a file holding the user message>" --host-tool "agent=<true if you can start a sub-agent, otherwise false>"',
    "executor_install": "python -m pip install --upgrade soulrun",
    "executor_help": "soulrun",
}
VERSION_POLICY_KEY = "executor_version_policy"
RELEASE_RE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
REQUIREMENT_RE = re.compile(r"^(>=|==)((?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*))$")
PYPI_URL = "https://pypi.org/pypi/soulrun/json"

# Preserve the exact former bootstrap solely for explicit migration recognition.
_CALLABILITY_BOOTSTRAP_JSON = r'''[
  {
    "role": "system",
    "content": {
      "protocol": "AISP V1.0.0",
      "axiom_0": "Human_Sovereignty_and_Wellbeing",
      "id": "run_with_executor_aisp",
      "name": "Run this AISP skill with an executor",
      "version": "1.0.0",
      "license": "Apache-2.0",
      "summary": "This SKILL.md is a thin bridge, not the source of truth: the executor set in params (SoulRun by default), an AISP/AISOP runtime, runs the same-folder aisp.aisop.json. Without an executor this skill does not run.",
      "flow_format": "mermaid",
      "loading_mode": "node",
      "params": {},
      "system_prompt": "For help, run {executor_help}."
    }
  },
  {
    "role": "user",
    "content": {
      "instruction": "STRICTLY OBEY aisp_contract; its non_negotiable rules are inviolable; then RUN aisop.main",
      "user_input": "{user_input}",
      "aisp_contract": {
        "profile": "aisp.skill.v1",
        "invocation": {
          "mode": "auto_or_manual",
          "when_to_use": ["the request matches the Use when part of this skill's description"],
          "when_not_to_use": ["the request matches the Do not use when part of this skill's description"]
        },
        "non_negotiable": [
          {
            "rule": "Run every request this skill is used for in this conversation through aisop.main the same way, a repeated one too; do not answer it yourself.",
            "enforced_by": "aisop.main"
          },
          {
            "rule": "Run this skill only through the executor; never execute or continue aisp.aisop.json yourself. Reading it through the executor's commands, or reviewing it when the user asks, is not running it.",
            "enforced_by": "aisop.main"
          },
          {"rule": "Install the executor only after the user agrees.", "enforced_by": "ask.step1:sys.io.confirm"}
        ],
        "risk_level": "medium"
      },
      "aisop": {
        "main": "graph TD\n    check[Check that the executor is installed] --> run[Run this skill with the executor]\n    check -.-> ask{Ask the user to install the executor}\n    ask -->|install| install[Install the executor]\n    ask -->|do_not_install| unavailable[Tell the user this skill cannot run without the executor]\n    install --> run\n    install -.-> unavailable\n    run --> end_node((End))\n    unavailable --> end_node"
      },
      "functions": {
        "check": {
          "step1": "sys.run('{executor_version}') -> installed",
          "on_error": {"command_error": "ask"},
          "execute_mode": "inline"
        },
        "ask": {
          "step1": "sys.io.confirm('This AISP skill runs only with an executor, and {executor} is not installed. Install the latest version now ({executor_install})?', options=['install', 'do_not_install']) -> choice",
          "step2": "Return choice as the branch label",
          "constraints": ["Wait for the user's answer, even if that ends this turn; never choose for the user."],
          "execute_mode": "inline"
        },
        "install": {
          "step1": "sys.run('{executor_install}') -> install_log",
          "step2": "sys.run('{executor_version}') -> installed",
          "on_error": {"command_error": "unavailable"},
          "execute_mode": "inline"
        },
        "run": {
          "step1": "sys.run('{executor_command}') -> printed",
          "step2": "Do what printed says, to the end of this turn",
          "execute_mode": "inline"
        },
        "unavailable": {
          "step1": "sys.io.notify('This AISP skill cannot run without an executor, so this request was not run. To run it, install {executor} ({executor_install}) and ask again.')",
          "constraints": ["Do not execute aisp.aisop.json or carry out this skill's steps yourself."],
          "execute_mode": "inline"
        },
        "end_node": {"step1": "End this turn", "execute_mode": "inline"}
      }
    }
  }
]'''


def _versioned_bootstrap(*, legacy_probe: bool = False) -> str:
    program = json.loads(_CALLABILITY_BOOTSTRAP_JSON)
    user = program[1]["content"]
    user["aisp_contract"]["non_negotiable"][2]["rule"] = (
        "Install, upgrade or downgrade the executor only after the user agrees."
    )
    user["aisop"]["main"] = (
        "graph TD\n"
        "    check{Check the executor package version} -->|satisfied| run[Run this skill with the executor]\n"
        "    check -->|mismatch| prepare_install[Verify the requested installation target]\n"
        "    check -.-> probe_error{Classify the failed probe}\n"
        "    probe_error -->|missing| prepare_install\n"
        "    probe_error -->|unusable| unavailable[Tell the user this request cannot run]\n"
        "    prepare_install --> ask{Ask the user to install the required executor}\n"
        "    ask -->|install| install[Install and verify the executor]\n"
        "    ask -->|do_not_install| unavailable\n"
        "    install --> run\n"
        "    install -.-> unavailable\n"
        "    run --> end_node((End))\n"
        "    unavailable --> end_node"
    )
    functions = user["functions"]
    functions["check"] = {
        "step1": "sys.run('{executor_version}') -> version_probe",
        "step2": "sys.assert('The probe unambiguously identifies the configured executor package version as three non-negative numeric components; do not use the protocol or bundled engine version, and never treat unknown output as compatible')",
        "step3": "Compare the numeric version components with executor_version_policy.requirement. Return satisfied for >= when installed is at least the bound, or for == only when equal; otherwise return mismatch. A satisfied version runs directly without asking to install or upgrade. Do not query a package index during this check.",
        "on_error": {"command_error": "probe_error", "assertion_error": "unavailable", "command_timeout": "unavailable", "default": "unavailable"},
        "execute_mode": "inline",
    }
    functions["probe_error"] = {
        "step1": (
            "Return missing only when the probe proves the configured executor executable is not installed in the current environment. A started-but-failed command, permission denial, timeout or ambiguous failure returns unusable; do not reinstall to conceal it."
            if legacy_probe else
            "Return missing only when the probe proves the configured executor package or entry point is not installed in the current environment, including a proven missing executor module behind an available launcher. A missing unrelated dependency/helper, invalid command, permission denial, timeout, other started-but-failed command or ambiguous failure returns unusable; do not reinstall to conceal it."
        ),
        "execute_mode": "inline",
    }
    functions["prepare_install"] = {
        "step1": "For >=, the installation target is the latest stable executor release satisfying the frozen lower bound. For ==, the target is exactly the declared release, even if the installed version is newer. Identify the current version, target, environment and any downgrade; use the configured executor_install command, not an invented alternative.",
        "step2": "sys.assert('The configured installation command targets the requested release: latest stable satisfying >=, or exactly the version after ==; an unpinned latest command is not an exact-version installation. If its target cannot be established, stop instead of executing or silently rewriting it')",
        "on_error": {"assertion_error": "unavailable", "default": "unavailable"},
        "execute_mode": "inline",
    }
    functions["ask"]["step1"] = "sys.io.confirm('This skill requires {executor} with the frozen executor_version_policy. State the installed version or absence, required constraint, actual target version policy, environment and any upgrade/downgrade. Install it using {executor_install}?', options=['install', 'do_not_install']) -> choice"
    functions["install"]["step3"] = "sys.assert('After installation, reparse the configured executor package version and verify executor_version_policy.requirement using numeric components; == requires equality, >= requires at least the bound. Unparseable, failed or mismatching rechecks stop without execution, retries or fallback')"
    functions["install"]["on_error"] = {"command_error": "unavailable", "command_timeout": "unavailable", "assertion_error": "unavailable", "default": "unavailable"}
    functions["unavailable"]["step1"] = "sys.io.notify('This request was not run because the required executor is missing, unusable, unverified or incompatible, or installation was declined or failed. Explain the actual reason and the declared version requirement; do not claim execution. The configured installation command is {executor_install}.')"
    functions["run"]["constraints"] = [
        "Only run after a verified matching installed version or a successful installation and matching recheck. Do not suppress the skill's own business confirmation gates. A business run failure is not permission to reinstall or upgrade."
    ]
    return json.dumps(program, ensure_ascii=False)


BOOTSTRAP_JSON = _versioned_bootstrap()
# Keep the exact preceding policy template only for explicit, offline migration.
_PREVIOUS_POLICY_BOOTSTRAP_JSON = _versioned_bootstrap(legacy_probe=True)


class SkillInterfaceError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = "AISP_E_M7_SKILL_MD_" + code


def normalize_text(text: str) -> str:
    if text.startswith("\ufeff"):
        text = text[1:]
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.rstrip("\n") + "\n"


def read_normalized(path: Path) -> str:
    return normalize_text(path.read_text(encoding="utf-8-sig"))


def write_lf(path: Path, text: str) -> None:
    write_generated_text(path, normalize_text(text))


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
    if len(name) > 64 or not NAME_RE.fullmatch(name):
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


def _render_legacy_skill_md(skill_path: Path) -> str:
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


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise SkillInterfaceError("CONFIG", f"Duplicate JSON key: {key}; no executor fallback.")
        out[key] = value
    return out


def _launch_values(values: Any) -> dict[str, str]:
    if not isinstance(values, dict) or set(values) != set(EXECUTOR_DEFAULTS):
        raise SkillInterfaceError("CONFIG", "params must contain exactly the five executor keys; no executor fallback.")
    if any(not isinstance(value, str) or not value.strip() for value in values.values()):
        raise SkillInterfaceError("CONFIG", "Every executor value must be a non-empty string; no executor fallback.")
    return {key: values[key] for key in EXECUTOR_DEFAULTS}


def _release(value: Any) -> tuple[int, int, int]:
    if not isinstance(value, str) or not RELEASE_RE.fullmatch(value):
        raise SkillInterfaceError("VERSION", "Expected a stable major.minor.patch version; no compatibility fallback.")
    return tuple(map(int, value.split(".")))


def _policy(value: Any) -> dict[str, str]:
    if not isinstance(value, dict) or set(value) != {"requirement", "source"}:
        raise SkillInterfaceError("VERSION", "Version policy must contain exactly requirement and source.")
    requirement, source = value["requirement"], value["source"]
    if not isinstance(requirement, str) or not REQUIREMENT_RE.fullmatch(requirement):
        raise SkillInterfaceError("VERSION", "Use >=major.minor.patch or ==major.minor.patch; latest must be resolved before rendering.")
    if source not in ("explicit", "latest_stable"):
        raise SkillInterfaceError("VERSION", "Version policy source must be explicit or latest_stable.")
    if source == "latest_stable" and not requirement.startswith(">="):
        raise SkillInterfaceError("VERSION", "A latest-stable snapshot is a lower bound, not an exact pin.")
    return {"requirement": requirement, "source": source}


def _params(values: Any) -> dict[str, Any]:
    if not isinstance(values, dict) or set(values) != set(EXECUTOR_DEFAULTS) | {VERSION_POLICY_KEY}:
        raise SkillInterfaceError("CONFIG", "params must contain the five launch strings and executor_version_policy; no executor fallback.")
    launch = _launch_values({key: values[key] for key in EXECUTOR_DEFAULTS})
    return {**launch, VERSION_POLICY_KEY: _policy(values[VERSION_POLICY_KEY])}


def _latest_soulrun_requirement() -> str:
    """The default adapter resolves only on generation/explicit refresh, never checks."""
    try:
        with urllib.request.urlopen(PYPI_URL, timeout=15) as response:
            raw = response.read(2_000_001)
        if len(raw) > 2_000_000:
            raise ValueError("release metadata exceeds the size limit")
        data = json.loads(raw, object_pairs_hook=_strict_object)
        info = data.get("info") if isinstance(data, dict) else None
        if not isinstance(info, dict) or not isinstance(info.get("name"), str) or info["name"].lower() != "soulrun":
            raise ValueError("release metadata does not identify the SoulRun project")
        releases = data.get("releases") if isinstance(data, dict) else None
        if not isinstance(releases, dict):
            raise ValueError("release metadata has no releases object")
        candidates = []
        prerelease = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:a|b|rc|\.dev)[0-9]+(?:\.dev[0-9]+)?$")
        for version, files in releases.items():
            if not isinstance(files, list) or any(not isinstance(item, dict) or not isinstance(item.get("yanked"), bool) for item in files):
                raise ValueError("release files or yanked flags are malformed")
            if not files or all(item["yanked"] for item in files):
                continue
            if prerelease.fullmatch(version):
                continue
            # Do not silently pick an older release when an unsupported stable form exists.
            candidates.append((_release(version), version))
        if not candidates:
            raise ValueError("no non-yanked stable release")
        return ">=" + max(candidates)[1]
    except (OSError, ValueError, TypeError, urllib.error.URLError) as exc:
        raise SkillInterfaceError("RESOLUTION", f"Cannot resolve the latest stable SoulRun release: {exc}; no stored/default-version fallback.") from exc


def _soulrun_install(requirement: str) -> str:
    if requirement.startswith("=="):
        return f'python -m pip install "soulrun{requirement}"'
    return f'python -m pip install --upgrade "soulrun{requirement}"'


def _managed_soulrun_install(command: str) -> bool:
    if command == EXECUTOR_DEFAULTS["executor_install"]:
        return True
    match = re.fullmatch(r'python -m pip install(?: --upgrade)? "soulrun((?:>=|==)[0-9]+\.[0-9]+\.[0-9]+)"', command)
    return bool(match and REQUIREMENT_RE.fullmatch(match[1]) and command == _soulrun_install(match[1]))


def _select_values(values: dict[str, Any], *, requirement: str | None = None,
                   refresh: bool = False, resolver: Callable[[], str] | None = None) -> dict[str, Any]:
    current = values.get(VERSION_POLICY_KEY)
    if requirement is not None:
        policy = _policy({"requirement": requirement, "source": "explicit"})
    elif current is not None and (current["source"] == "explicit" or not refresh):
        return _params(values)
    else:
        if values["executor"] != "soulrun":
            raise SkillInterfaceError("VERSION", "This tool has a latest-release resolver only for the default SoulRun adapter; specify another executor's requirement explicitly. No vendor fallback.")
        policy = _policy({"requirement": (resolver or _latest_soulrun_requirement)(), "source": "latest_stable"})
    result = dict(values)
    if result["executor"] == "soulrun" and _managed_soulrun_install(result["executor_install"]):
        result["executor_install"] = _soulrun_install(policy["requirement"])
    result[VERSION_POLICY_KEY] = policy
    return _params(result)


def _render_interface(skill_path: Path, values: dict[str, Any], *, callability_legacy: bool = False,
                      version_policy_legacy: bool = False) -> str:
    skill_dir, doc = load_skill(skill_path)
    system = _content(doc, 0)
    name = _bridge_name(_one_line(system.get("id") or skill_dir.name))
    bootstrap = (_CALLABILITY_BOOTSTRAP_JSON if callability_legacy else
                 _PREVIOUS_POLICY_BOOTSTRAP_JSON if version_policy_legacy else BOOTSTRAP_JSON)
    program = json.loads(bootstrap)
    program[0]["content"]["params"] = _launch_values(values) if callability_legacy else _params(values)
    lines = [
        "---",
        f"name: {_yaml_string(name)}",
        f"description: {_yaml_string(_description(system, _contract(doc)))}",
        f"license: {_yaml_string(_one_line(system.get('license') or 'Apache-2.0'))}",
        "metadata:",
        '  generated_from_aisp: "true"',
        '  aisp_program: "aisp.aisop.json"',
        f"  protocol: {_yaml_string(PROTOCOL)}",
        '  bridge_mode: "agent_skills_bridge"',
        "---", "", "# AISP Skill (run with an executor)", "",
        GENERATED_MARKER, SOURCE_MARKER, GENERATOR_MARKER, "", "```json",
        json.dumps(program, ensure_ascii=False, indent=2), "```", "",
        "Align Axiom 0: Human Sovereignty and Wellbeing. AISP - AI Skill Protocol V1.0.0. www.aisp.dev",
    ]
    return normalize_text("\n".join(lines))


def _split_header(text: str) -> tuple[str, str]:
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise SkillInterfaceError("HEADER", "Expected standalone generated YAML frontmatter delimiters.")
    header, body = text[4:].split("\n---\n", 1)
    return header, body


def _executor_input(skill_dir: Path) -> tuple[dict[str, Any], str]:
    path = skill_dir / "SKILL.md"
    if path.is_symlink():
        raise SkillInterfaceError("INPUT", "SKILL.md must be a same-folder regular file, not a symbolic link.")
    if not path.exists():
        return dict(EXECUTOR_DEFAULTS), "first generation"
    if path.resolve().parent != skill_dir.resolve():
        raise SkillInterfaceError("INPUT", "SKILL.md must stay in the same skill directory.")
    text = read_normalized(path)
    # Full old projection matching prevents a damaged new file being mistaken for a migration.
    if text == _render_legacy_skill_md(skill_dir):
        return dict(EXECUTOR_DEFAULTS), "legacy migration"
    header, body = _split_header(text)
    blocks = re.findall(r"(?m)^```json\n(.*?)\n```$", body, re.DOTALL)
    if len(blocks) != 1:
        raise SkillInterfaceError("CONFIG", "Expected exactly one two-message bootstrap JSON block; unknown content is not automatically migrated.")
    try:
        program = json.loads(blocks[0], object_pairs_hook=_strict_object)
    except json.JSONDecodeError as exc:
        raise SkillInterfaceError("CONFIG", f"Invalid bootstrap JSON: {exc}; no executor fallback.") from exc
    if (not isinstance(program, list) or len(program) != 2
            or any(not isinstance(message, dict) for message in program)
            or [message.get("role") for message in program] != ["system", "user"]
            or not isinstance(program[0].get("content"), dict)
            or not isinstance(program[1].get("content"), dict)):
        raise SkillInterfaceError("CONFIG", "Bootstrap must have the fixed system/user two-message structure.")
    raw_values = program[0]["content"].get("params")
    old_shape = isinstance(raw_values, dict) and set(raw_values) == set(EXECUTOR_DEFAULTS)
    values = _launch_values(raw_values) if old_shape else _params(raw_values)
    expected_header, expected_body = _split_header(_render_interface(skill_dir, values, callability_legacy=old_shape))
    actual_lines, expected_lines = header.splitlines(), expected_header.splitlines()
    if len(actual_lines) != len(expected_lines) or actual_lines[3:] != expected_lines[3:]:
        raise SkillInterfaceError("HEADER", "Fixed interface metadata differs; repair explicitly, not through silent regeneration.")
    for key, line in zip(("name", "description", "license"), actual_lines[:3]):
        try:
            value = json.loads(line.removeprefix(key + ": ")) if line.startswith(key + ": ") else None
        except json.JSONDecodeError as exc:
            raise SkillInterfaceError("HEADER", "Derived YAML fields must use generated JSON string escaping.") from exc
        if not isinstance(value, str):
            raise SkillInterfaceError("HEADER", f"Expected the generated {key} string field.")
    if body != expected_body:
        if not old_shape:
            _, previous_body = _split_header(_render_interface(skill_dir, values, version_policy_legacy=True))
            if body == previous_body:
                return values, "version policy migration"
        raise SkillInterfaceError("BODY", "Fixed bootstrap body drift; only launch strings and version policy may change. Restore the fixed text explicitly before regenerating.")
    return values, "callability migration" if old_shape else "current configuration preserved"


def render_skill_md(skill_path: Path, *, executor_version_requirement: str | None = None,
                    refresh_executor_version: bool = False) -> str:
    """Never write; resolve a default only for new/migrated or explicitly refreshed output."""
    skill_dir, _ = load_skill(skill_path)
    values, _ = _executor_input(skill_dir)
    return _render_interface(skill_dir, _select_values(values, requirement=executor_version_requirement, refresh=refresh_executor_version))


def validate_skill_md(skill_path: Path) -> list[dict[str, str]]:
    """Pure shared M7 check. Does not call core validation or execute any command."""
    skill_dir = skill_path if skill_path.is_dir() else skill_path.parent
    path = skill_dir / "SKILL.md"
    if not path.is_file():
        return [{"code": "AISP_E_M7_SKILL_MD_MISSING", "message": "Required same-folder SKILL.md is missing; generate it before validation."}]
    try:
        skill_dir, _ = load_skill(skill_path)
        values, state = _executor_input(skill_dir)
        if state in {"legacy migration", "callability migration", "version policy migration"}:
            raise SkillInterfaceError("LEGACY", "Recognized legacy interface; preview or explicitly --write its migration. A check never migrates it.")
        if read_normalized(path) != _render_interface(skill_dir, values):
            raise SkillInterfaceError("HEADER", "Derived name, description or license differs from the skill; regenerate the derived header.")
    except SkillInterfaceError as exc:
        return [{"code": exc.code, "message": str(exc)}]
    except (OSError, ValueError, TypeError) as exc:
        return [{"code": "AISP_E_M7_SKILL_MD_INPUT", "message": f"Cannot check interface: {exc}"}]
    return []


def check_skill_md(skill_path: Path) -> tuple[bool, str]:
    issues = validate_skill_md(skill_path)
    if issues:
        return False, "; ".join(item["code"] + ": " + item["message"] for item in issues)
    return True, f"ok {skill_path} (bootstrap unchanged and format valid; executor not certified)"


def iter_skill_dirs(target: Path) -> list[Path]:
    if target.is_file() and target.name == "aisp.aisop.json":
        return [target.parent.resolve()]
    if target.is_dir() and (target / "aisp.aisop.json").is_file():
        return [target.resolve()]
    if target.is_dir():
        folders = set()
        for path in target.rglob("aisp.aisop.json"):
            if not path.parent.name.endswith("_aisp"):
                continue
            folder = path.parent.resolve()
            if not folder.is_relative_to(target.resolve()):
                raise ValueError("Discovered skill folder resolves outside the selected directory")
            folders.add(folder)
        return sorted(folders)
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate/check the required AISP executor-only SKILL.md interface.")
    parser.add_argument("target", help="Skill folder, aisp.aisop.json, or directory containing *_aisp skills.")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--write", action="store_true", help="Write SKILL.md for one skill.")
    action.add_argument("--check", action="store_true", help="Check SKILL.md for one skill.")
    action.add_argument("--print", action="store_true", help="Print generated SKILL.md for one skill.")
    action.add_argument("--write-all", action="store_true", help="Write SKILL.md for every *_aisp skill under target.")
    action.add_argument("--check-all", action="store_true", help="Check SKILL.md for every *_aisp skill under target.")
    parser.add_argument("--executor-version-requirement", help="Explicit >=X.Y.Z or ==X.Y.Z; takes precedence over stored/default policy and latest refresh.")
    parser.add_argument("--refresh-executor-version", action="store_true", help="Refresh only a default-managed latest-stable lower bound; preserve explicit constraints.")
    args = parser.parse_args(argv)
    if (args.check or args.check_all) and (args.executor_version_requirement is not None or args.refresh_executor_version):
        parser.error("check modes are offline/read-only; generation options cannot be combined with checks")

    target = Path(args.target)
    try:
        skill_dirs = iter_skill_dirs(target)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"ERROR: cannot discover skills: {exc}", file=sys.stderr)
        return 1
    if not skill_dirs:
        print(f"ERROR: no AISP skill found under {target}", file=sys.stderr)
        return 1
    wants_all = args.write_all or args.check_all
    if len(skill_dirs) != 1 and not wants_all:
        print("ERROR: target contains multiple skills; use --write-all or --check-all", file=sys.stderr)
        return 1

    try:
        resolved_requirement = None
        def resolve_once() -> str:
            nonlocal resolved_requirement
            if resolved_requirement is None:
                resolved_requirement = _latest_soulrun_requirement()
            return resolved_requirement
        def prepare(skill_dir: Path, values: dict[str, Any]) -> str:
            selected = _select_values(values, requirement=args.executor_version_requirement,
                                      refresh=args.refresh_executor_version, resolver=resolve_once)
            return _render_interface(skill_dir, selected)
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
            inputs = [(skill_dir, *_executor_input(skill_dir)) for skill_dir in skill_dirs]
            prepared = [(skill_dir / "SKILL.md", prepare(skill_dir, values), state) for skill_dir, values, state in inputs]
            written = []
            for out, text, state in prepared:
                try:
                    write_lf(out, text)
                except OSError:
                    print(f"ERROR: I/O failure; completed: {[str(path) for path in written]}; failed/possibly partial: {out}; not attempted: {[str(path) for path, _, _ in prepared[len(written) + 1:]]}", file=sys.stderr)
                    raise
                written.append(out)
                print(f"Wrote {out} ({state})")
            return 0
        values, _ = _executor_input(skill_dirs[0])
        print(prepare(skill_dirs[0], values), end="")
        return 0
    except Exception as exc:  # noqa: BLE001
        code = f"{exc.code}: " if isinstance(exc, SkillInterfaceError) else ""
        print(f"ERROR: {code}{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
