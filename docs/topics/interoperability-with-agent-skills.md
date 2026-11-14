# Interoperability with Agent Skills

AISP is an executable, governable skill package built on AISOP and bridged to agent platforms through the Agent Skills standard.

Every conformant AISP package MUST include the generated same-folder `SKILL.md` compatibility interface (M7). The business source of truth is only `aisp.aisop.json`. The fixed interface bootstrap delegates execution to an available conforming executor, SoulRun by default; without one, stop rather than executing or continuing the skill yourself.

## Each Layer in the Stack

| Layer | Role | Domain |
|---|---|---|
| Agent Skills | Standard discovery and compatibility interface | agentskills.io |
| AISOP | Execution language: graph, functions and real `sys.*` mechanisms | aisop.dev |
| AISP | Package, contract, resources and conformance | aisp.dev |
| Executor | Runs under AISP/AISOP runtime requirements; replaceable | SoulRun by default, soulrun.dev |

AIAP and other AIXP protocols remain sibling projects, not dependencies in AISP's stack. AISP does not replace Agent Skills or turn it into the business program.

## Required Interface

M7 checks all three conditions:

1. Same-folder `SKILL.md` exists.
2. `name`, `description` and outer `license` equal the skill-derived values.
3. Metadata and fixed bootstrap match the generator; only valid launch strings and the frozen version policy may differ.

The derived name drops `_aisp`, hyphenates underscores and uses lowercase; it must be at most 64 characters and contain neither `anthropic` nor `claude`. Description derives from summary plus invocation triggers/exclusions, is injection-safe and at most 1024 characters. Outer license derives from the business skill, defaulting to Apache-2.0.

The canonical header contains `name`, `description`, `license`, `metadata`, with JSON-quoted YAML strings. Metadata fixes `generated_from_aisp: "true"`, `aisp_program: "aisp.aisop.json"`, `protocol: "AISP V1.0.0"`, and `bridge_mode: "agent_skills_bridge"`. No absolute/remote/subdirectory/traversal target or custom top-level key is allowed.

The body is titled `# AISP Skill (run with an executor)` and retains the generated/source/generator markers. Its internal `run_with_executor_aisp` program is a fixed bootstrap, not a separately distributed second skill or a copy of business functions/resources/red lines. The bootstrap's Apache-2.0 license does not override the business package license.

## Launch Configuration and Version Policy

There is one bootstrap flow and one core decision: whether the configured executor package version satisfies the frozen requirement. The five launch strings are configuration values, not five bootstrap types; different acceptance scenarios exercise this same flow.

Only `system.content.params` in the bootstrap may supply:

- `executor`: default `soulrun`.
- `executor_version`: default `soulrun --version`.
- `executor_command`: SoulRun invocation passing the skill folder, project `.soulrun_cache`, user message file and actual `--host-tool "agent=<capability>"`.
- `executor_install`: default-adapter command targeting the declared policy, such as `python -m pip install --upgrade "soulrun>=X.Y.Z"` or `python -m pip install "soulrun==X.Y.Z"`.
- `executor_help`: default `soulrun`.
- `executor_version_policy`: exactly `{"requirement": ">=X.Y.Z", "source": "latest_stable"}` or an explicit `>=X.Y.Z` / `==X.Y.Z` constraint with `source: explicit`.

The five launch values remain non-empty strings; the policy is a strict two-field object. No missing, extra or duplicate keys. SoulRun is the default adapter, not a protocol dependency. On first generation or explicit refresh of its default-managed policy, the generator resolves the latest non-yanked stable release from official PyPI and freezes a concrete lower bound. Normal regeneration, read-only checks and runtime compatibility probes do not query the index or replace the frozen bound; a consented installation may access its package source. Explicit constraints always win, including over refresh. Other executors use their own commands and an explicit requirement, with no vendor fallback. No configuration file or executor registry is added; static validation does not certify actual availability or compatibility.

With `>=1.0.0`, installed 1.0.0 or newer runs without asking to upgrade; missing/older versions require consent to install the latest stable release satisfying the bound. With `==1.0.0`, only exactly 1.0.0 runs; every other version requires consent to install exactly 1.0.0, explicitly disclosing any downgrade. Unknown output stops, and every installation must be followed by a matching version recheck. Installation refusal/failure/mismatch means no execution or automatic retry. Business confirmation gates remain mandatory. See [specification §20](https://github.com/AIXP-Labs/AISP/blob/main/specification/AISP_Protocol.md#20-interoperability) for the full bounded version syntax and failure rules.

## Generate and Check

```bash
python -B tools/aisp_skill_md.py examples/aisp/yijing_aisp --print
python -B tools/aisp_skill_md.py examples/aisp/yijing_aisp --write
python -B tools/aisp_skill_md.py examples --check-all
python -B tools/aisp_validate_agent_skill_bridge.py examples/aisp --strict-readme
```

Use `--executor-version-requirement '>=1.0.0'` or `'==1.0.0'` on generation to supply an explicit constraint. `--refresh-executor-version` refreshes only a default-managed bound; stored explicit constraints are preserved. Check modes reject these generation options and stay offline. Default resolution failure stops without a cached-version fallback.

Generation uses the business program, five launch strings plus the frozen version policy and actual generator revision/digest. A missing interface uses defaults on explicit generation. Only the current generated interface is accepted. Older generated or edited interfaces fail both checking and writing, with their files unchanged; they are not migrated. Back up the interface, note its five launch strings and frozen version policy, delete it, regenerate, then restore non-default values and check again. Current valid configuration is preserved while derived header values are updated. Default metadata must identify SoulRun; this is an input consistency check, not independent provenance verification. Selecting or refreshing a policy updates either exact generated SoulRun install-command form even if its previous constraint disagrees; custom commands remain unchanged.

Damaged JSON, bad launch configuration and version policy, unknown handwritten content or changed fixed bootstrap fails: no silent defaults, automatic repair or overwrite. For an older or edited interface, back it up, record its configuration, delete it and regenerate before restoring non-default values. Print/check never write; batch writes preflight all targets, and any later I/O error reports completed, failed/possibly partial and not-attempted files.

Writing is UTF-8 without BOM, LF, one trailing newline. Comparison normalizes a leading BOM, CRLF/CR and trailing newlines; other fixed bytes remain canonical. Core and bridge checks share one read-only M7 function that never calls back into core validation. EC7 is the legacy interoperability mapping, not permission to omit the interface.

## Host and Runtime Boundaries

The host must not bypass the executor to execute or continue `aisp.aisop.json`. Executor-mediated reads, such as its normal program interface, and user-requested code review are permitted.

Before installation, the consent gate and version-report interpretation rely on host controls, not a nonexistent executor. Distinguish missing, unusable, incompatible/unverified version and runtime failure. The fixed bootstrap requires the configured executor package version to satisfy the frozen policy; command exit 0 alone is insufficient, and runtime failure must not trigger an automatic reinstall/upgrade. Static checks prove policy format, not true compatibility.

A proven missing executor package/module behind an available launcher is still missing; the executable need not be absent. Missing unrelated dependencies/helpers, invalid commands, permission denial, timeout and ambiguous failures remain unusable and must not be concealed by reinstalling.

Command exit 0 may indicate turn preparation or a waiting gate. Waiting is not consent; completion needs the run record's terminal status and corresponding output within the verified scope. Executors must preserve blocking human gates, red lines and independent dispatch for `execute_mode: "agent"`.

No `--session-id` is added. The same default project/runtime scope supports one active session, including waits. Alternating windows does not isolate conversations; use stable host isolation or different project/runtime directories for concurrency.

## What Passing Means

M7 proves only unchanged bootstrap text and valid format, including derived header consistency. Even `echo available`/`echo done` substitutes can satisfy string format. Bridge validation also checks safe same-folder paths and native package conformance. None proves executor certification, external trust, safety or completed execution.

Verify external provenance or obtain a user trust decision before running an untrusted package. Package-contained generated markers and hashes are not trust roots. Full executor compatibility and real-host tests are separate work; no platform success is inferred from static checks.

AISP still relies on AISOP open-world validation: tolerate the extra contract/license fields and do not gate execution on a literal `protocol == "AISOP V1.0.0"`. See [the specification map](../specification.md) for normative details.

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
