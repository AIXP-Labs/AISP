# Error Codes Reference

> Complete reference for AISP conformance violation codes, their severities, meanings, and fixes.
> Each code maps to a conformance rule (M / R / SE / EC) defined in the `AISP_Standard.*` files.

A validator or runtime emits these codes when a skill or runtime violates a conformance rule. **FAIL** codes mean non-conformance; **WARN** codes are flagged but non-blocking. Codes follow the form `AISP_E_<RULE>_<SHORT>` (error) or `AISP_W_<RULE>_<SHORT>` (warning).

This reference includes both codes emitted by the current reference tools and codes reserved for conforming runtimes, registries, or future reference-tool coverage. For implementation coverage, see [Validator Coverage](validator-coverage.md); for runtime-only evidence, see [Registry & Runtime Artifacts](registry-runtime-artifacts.md).

---

## Skill Violation Codes (M Series)

| Code | Rule | Severity | Meaning | Fix |
|------|------|----------|---------|-----|
| `AISP_E_M1_NOT_AISOP` | M1 | FAIL | Not a legal AISOP V1.0.0 program (bad array shape, missing required field, no `aisop.main`) | Repair to a 2-message array with all required fields and an `aisop.main` graph |
| `AISP_E_M1_JSON` | M1 | FAIL | `aisp.aisop.json` is not valid JSON | Fix JSON syntax |
| `AISP_E_M1_SHAPE` | M1 | FAIL | Skill file is not a 2-message array | Repair the AISOP message array shape |
| `AISP_E_M1_SYSTEM` | M1 | FAIL | First message content is not an object | Make `data[0].content` an object |
| `AISP_E_M1_USER` | M1 | FAIL | Second message content is not an object | Make `data[1].content` an object |
| `AISP_E_M1_AXIOM` | M1 | FAIL | `axiom_0` is missing or incorrect | Set `axiom_0` to `"Human_Sovereignty_and_Wellbeing"` |
| `AISP_E_M1_FIELD` | M1 | FAIL | Required system metadata is missing | Add the missing required field |
| `AISP_E_M1_INSTRUCTION` | M1 | FAIL | Instruction does not strongly name `aisp_contract` and `RUN aisop.main` | Use the required strong instruction |
| `AISP_E_M1_MAIN` | M1 | FAIL | `user.content.aisop.main` is missing | Add `aisop.main` |
| `AISP_E_M1_FUNCTIONS` | M1 | FAIL | `user.content.functions` is missing or empty | Add node functions |
| `AISP_E_M1_FUNCTION_SHAPE` | M1 | FAIL | A `functions.<node>` entry is not an object | Represent each function node as an object with step fields and optional node metadata |
| `AISP_E_M1_STEP_SHAPE` | M1 | FAIL | A function has no numeric execution step (`step1`, `step2`, ...) or a numeric step is not a string | Add at least one string-valued `stepN` field |
| `AISP_E_M1_GRAPH` | M1 | FAIL | Graph is malformed or empty | Fix the graph object/string |
| `AISP_E_M1_NODE_FUNCTION` | M1 | FAIL | A graph node has no corresponding `functions` entry | Add the missing function node or remove the graph node |
| `AISP_E_M1_EDGE` | M1 | FAIL | A jsonflow edge points to a missing node | Fix the `next` / `branches` / `error` target |
| `AISP_E_M1_UNREACHABLE` | M1 | FAIL | A jsonflow node is unreachable from the graph entry | Connect or remove the node |
| `AISP_E_M1_TERMINAL` | M1 | FAIL | A graph has no terminal node | Add an end node or terminal branch |
| `AISP_W_M1_MERMAID_UNPARSED` | M1 | WARN | Mermaid graph had no parseable edges | Use simple Mermaid edges or provide jsonflow for conformance-critical checks |
| `AISP_E_M1_PROTOCOL` | M1 | FAIL | `protocol` is not `"AISP V1.0.0"` | Set `system.content.protocol` to `"AISP V1.0.0"` |
| `AISP_E_M1_LOADING_MODE` | M1 | FAIL | `system.content.loading_mode` is missing or is not `"node"` | Set `system.content.loading_mode` to `"node"` |
| `AISP_E_M1_EXECUTE_MODE` | M1 | FAIL | A function declares an unsupported `execute_mode` value | Use `"inline"` or `"agent"` |
| `AISP_W_M1_EXECUTE_MODE_DEFAULT_INLINE` | M1 | WARN | A function omits `execute_mode`; runtime falls back to inline | Declare `"inline"` or `"agent"` explicitly |
| `AISP_W_M1_EXECUTE_MODE_AGENT_RECOMMENDED` | M1 | WARN | A function has more than 10 numeric execution steps (`stepN`) but is not `agent` | Review whether `execute_mode: "agent"` is appropriate; the threshold is a review heuristic, not a ban on shorter `agent` nodes |
| `AISP_W_M1_NO_LICENSE` | M1 | WARN | `license` missing | Add `system.content.license` (default `"Apache-2.0"`) |
| `AISP_W_M1_LICENSE` | M1 | WARN | Reference validator warning for missing `license` | Add `system.content.license` |
| `AISP_E_M2_SUFFIX` | M2 | FAIL | Folder name does not end with `_aisp` | Rename the folder to `<id>_aisp` |
| `AISP_E_M2_ID` | M2 | FAIL | Folder name is not lowercase snake_case ending in `_aisp` | Rename the folder |
| `AISP_E_M2_ID_MISMATCH` | M2 | FAIL | `id` does not equal the folder name | Make `id` equal the folder name |
| `AISP_E_M2_FILENAME` | M2 | FAIL | Skill file is not named `aisp.aisop.json` | Rename the entry file to `aisp.aisop.json` |
| `AISP_E_M3_NO_CONTRACT` | M3 | FAIL | `user.content.aisp_contract` missing | Add the contract as a real object in the user message |
| `AISP_E_M3_CONTRACT` | M3 | FAIL | Reference validator code for missing/non-object `aisp_contract` | Add the contract as a real object in the user message |
| `AISP_E_M3_STRING` | M3 | FAIL | Contract is a JSON-in-string or lives in `system_prompt` | Move it to `user.content.aisp_contract` as a real object |
| `AISP_E_M3_PROFILE` | M3 | FAIL | `profile` does not start with `aisp.skill.` | Set `profile` to `"aisp.skill.v1"` |
| `AISP_E_M3_INVOCATION` | M3 | FAIL | `invocation` is missing or has empty trigger arrays | Add non-empty `when_to_use` and `when_not_to_use` arrays |
| `AISP_E_M3_NON_NEGOTIABLE` | M3 | FAIL | `non_negotiable` is missing or empty | Add at least one red-line binding |
| `AISP_E_M3_RISK` | M3 | FAIL | `risk_level` is outside the allowed enum | Use `low`, `medium`, `high`, or `critical` |
| `AISP_E_M4_PHANTOM` | M4 | FAIL | `enforced_by` points to a non-existent node / numeric execution step / mechanism, or to a metadata field such as `step_note` | Point it to a real `<node>.stepN:<mechanism>`, `aisop.main` branch, or restricted `tools` |
| `AISP_E_M4_NO_MECHANISM` | M4 | FAIL | `enforced_by` of `<node>.stepN` form lacks `:<mechanism>` | Append the enforcing mechanism (e.g. `:sys.assert`) |
| `AISP_E_M4_GRAMMAR` | M4 | FAIL | `non_negotiable` entry or `enforced_by` grammar is malformed | Use one of the valid forms |
| `AISP_E_M4_TOOLS` | M4 | FAIL | `enforced_by: tools` has no restricted tools allow-list | Declare a restricted tools list or use a `sys.*` binding |
| `AISP_E_M5_PATH_ESCAPE` | M5 | FAIL | A `resources[].path` is absolute or contains `..` | Make it relative and confined to the skill folder or `_shared/` |
| `AISP_E_M5_RESOURCE` | M5 | FAIL | A resource entry is malformed or missing required fields | Add `id`, `path`, `kind`, and `mode` |
| `AISP_E_M5_RESOURCES` | M5 | FAIL | `resources` is not an array | Make it an array |
| `AISP_E_M5_MODE` | M5 | FAIL | `mode` is not in `{read_only, execute_only, read_and_execute}` | Use a valid `mode` enum value |
| `AISP_E_M5_SCOPE` | M5 | FAIL | `scope` is not in `{skill, shared}` | Use `skill` for package-local resources or `shared` for `_shared/` resources |
| `AISP_E_M5_SHA256` | M5 | FAIL | Resource `sha256` is not a 64-character hex digest | Replace it with a valid SHA-256 digest |
| `AISP_W_M5_MISSING_RESOURCE` | M5 | WARN | A declared local resource file does not exist | Add the file or remove the resource declaration |
| `AISP_W_M5_UNDECLARED_USE` | M5 | WARN | A node reads or executes a resource path not declared in `resources` | Declare the resource with correct `mode` |
| `AISP_W_M5_UNDECLARED` | M5 | WARN | A folder file is not declared in `resources` | Declare it in `resources` or remove it |
| `AISP_W_M5_UNDECLARED_FILE` | M5 | WARN | Reference validator found an undeclared file in the skill folder | Declare it in `resources` or remove it |
| `AISP_W_M5_NO_REQUIRES_TOOLS` | M5 | WARN | A `kind:script` resource has no `requires_tools` | Declare the minimal tools the script needs |
| `AISP_E_M6_SELF_TRUST` | M6 | FAIL | The skill self-declares `trusted` / `verified` / `safe` | Remove the self-asserted trust flag; let the registry judge trust |

---

## Runtime Violation Codes (R Series)

| Code | Rule | Severity | Meaning | Fix |
|------|------|----------|---------|-----|
| `AISP_E_R1_SKIP_NODE` | R1 | FAIL | Runtime skipped a required `aisop.main` node or bypassed `sys.io.confirm` | Execute required nodes; never bypass `sys.io.confirm` |
| `AISP_E_R1_CONTRACT_NOT_READ` | R1 | FAIL | Runtime trace does not show `user.content.aisp_contract` was read | Emit contract-read evidence in the runtime trace |
| `AISP_E_R1_SKILL_MISMATCH` | R1 | FAIL | Runtime trace `skill_id` does not match the checked skill | Run the trace checker against the matching skill package |
| `AISP_E_R1_TRACE_SHAPE` | R1 | FAIL | Runtime trace is missing required execution-evidence shape | Emit a runtime name and `events` array |
| `AISP_E_R2_NOT_ENFORCED` | R2 | FAIL | A `non_negotiable`'s `enforced_by` mechanism was not enforced | Enforce the mechanism the binding names |
| `AISP_E_R3_HIDDEN` | R3 | FAIL | Runtime hid or stripped the user-message `aisp_contract` | Hand the contract to the model unmodified |
| `AISP_E_R4_CLOSED_WORLD` | R4 | FAIL | The underlying AISOP runtime rejected unknown keys or gated on the `protocol` value | Use an open-world AISOP runtime (tolerates extra keys; does not gate on `protocol`) |
| `AISP_W_R5_NO_TRUST_GATE` | R5 | WARN | Untrusted skill/resource handled without a trust gate, or script run before reading the index | Add a trust gate; prefer reading `aisp_list.json` |
| `AISP_I_R_STATIC_ONLY` | R | INFO | Static validation completed without executing runtime-only R1-R7 checks | Add runtime trace validation when runtime behavior must be proven |
| `AISP_W_R6_NO_DECLARATION` | R6 | WARN | Runtime does not declare whether its tool enforcement is hard or advisory | Declare the mode; if advisory, `enforced_by: tools` is not a hard guarantee |
| `AISP_W_R6_ADVISORY` | R6 | WARN | Runtime declares advisory tool enforcement | Do not count `enforced_by: tools` as a hard guarantee |
| `AISP_W_R6_TOOLS_CONDITIONAL` | R6 | WARN | Static validation found `enforced_by: tools`; hardness depends on runtime permission enforcement | Provide runtime tool-enforcement evidence |
| `AISP_W_R6_TOOLS_ATTESTED_NOT_VERIFIED` | R6 | WARN | Runtime/tool artifact self-attests hard enforcement but lacks the required event evidence or provenance | Add `tool_enforcement` trace events or provenance-bearing tool capabilities |
| `AISP_W_R6_TRACE_NOT_CONFORMANT` | R6 | WARN | Runtime trace failed runtime conformance checks and cannot prove hard tool enforcement | Fix the runtime trace failures |
| `AISP_I_R6_TOOLS_HARD` | R6 | INFO | `enforced_by: tools` is backed by runtime trace tool-enforcement event evidence or provenance-bearing tool capabilities | Keep the evidence artifact with the skill validation record |
| `AISP_E_R6_TOOLS_NOT_HARD` | R6 | FAIL | Strict tools mode requires event/provenance-backed hard runtime/tool capability evidence, but none was provided or evidence was advisory/unknown | Provide conformant hard `--runtime-trace` or provenance-bearing `--tool-capabilities` evidence |
| `AISP_E_R6_TRACE_NOT_CONFORMANT` | R6 | FAIL | Runtime trace failed runtime conformance checks and cannot be used as strict hard tool evidence | Fix the runtime trace failures |
| `AISP_E_R6_TRACE_SKILL_MISMATCH` | R6 | FAIL | Runtime trace `skill_id` does not match the skill being validated | Use the matching runtime trace for this skill |
| `AISP_E_R7_COLLAPSED_INLINE` | R7 | FAIL | A node with `execute_mode: "agent"` was executed inline instead of dispatched to an independent sub-agent | Dispatch `agent` nodes to a sub-agent; never collapse them inline. Omitted `execute_mode` falls back inline and is reported statically as `AISP_W_M1_EXECUTE_MODE_DEFAULT_INLINE` |

---

## Security Violation Codes (SE Series)

| Code | Rule | Severity | Meaning | Fix |
|------|------|----------|---------|-----|
| `AISP_E_SE1_PATH` | SE1 | FAIL | Resource path escapes the skill folder / `_shared/` | Confine the path; no `..`, no absolute paths |
| `AISP_E_SE2_REMOTE` | SE2 | FAIL | Remote URL resource accessed without confirmation | Disable by default; gate with `sys.io.confirm` |
| `AISP_E_SE3_MODE_GATE` | SE3 | FAIL | `execute_only` injected into the model, or `read_only` executed | Respect `mode` gating |
| `AISP_W_SE4_AUTHORITY` | SE4 | WARN | Script over-requests tools or runs dangerous commands unconfirmed | Minimize `requires_tools`; add `sys.io.confirm` |
| `AISP_E_SE5_SCRIPT` | SE5 | FAIL | `aisp_list.py` has non-stdlib imports, network/subprocess calls, or side effects beyond writing `aisp_list.json` | Restore a minimal, zero-dependency script |
| `AISP_E_SE6_SELF_TRUST` | SE6 | FAIL | Self-declared trust (mirrors M6) | Remove the trust claim |
| `AISP_E_SE7_CONFIRM_BYPASS` | SE7 | FAIL | `sys.io.confirm` bypassed or downgraded | Keep `sys.io.confirm` forced-blocking |
| `AISP_W_SE8_MUTATED` | SE8 | WARN | Skill files or resources modified during normal execution (outside a deliberate evolution/edit step) | Treat the skill package as read-only at runtime; modify only through a deliberate evolution/edit step |

---

## Ecosystem Violation Codes (EC Series)

| Code | Rule | Severity | Meaning | Fix |
|------|------|----------|---------|-----|
| `AISP_E_EC1_NO_README` | EC1 | FAIL | `aisp/README.md` missing | Add `aisp/README.md` |
| `AISP_E_EC1_README` | EC1 | FAIL | Reference validator code for missing `aisp/README.md` | Add `aisp/README.md` |
| `AISP_W_EC1_NO_INDEX` | EC1 | WARN | `aisp_list.py` / `aisp_list.json` missing | Add the discovery toolkit |
| `AISP_W_EC1_NO_SCRIPT` | EC1 | WARN | `aisp_list.py` is missing | Add the discovery script or document why it is omitted |
| `AISP_W_EC2_DRIFT` | EC2 | WARN | `aisp_list.json` disagrees with the skill folders | Re-run `python -B aisp_list.py --json` |
| `AISP_E_EC2_INDEX` | EC2 | FAIL | `aisp_list.json` is malformed | Fix the index JSON object |
| `AISP_W_EC2_INDEX_DRIFT` | EC2 | WARN | Reference validator detected index drift | Re-run the discovery script or update `aisp_list.json` |
| `AISP_W_EC3_SHARED` | EC3 | WARN | `_shared/` contains an `aisp.aisop.json` or has an `_aisp` suffix | `_shared/` is not a skill folder |
| `AISP_W_EC4_PROVENANCE` | EC4 | WARN | Registry entry lacks provenance (source / commit / `contract_sha256`) | Record provenance in the registry entry (registry-side) |
| `AISP_W_EC6_EVOLUTION` | EC6 | WARN | Evolution removed a safety constraint, lowered `risk_level`, or expanded `tools` without justification | Restore the constraint or record justification |
| `AISP_W_EC7_BRIDGE` | EC7 | WARN | `SKILL.md` copies logic or its `name` contains `anthropic` / `claude` | Make the bridge thin; fix the `name` |
| `AISP_W_EC7_BRIDGE_DRIFT` | EC7 | WARN | `SKILL.md` bridge summary differs from `aisp.aisop.json` | Regenerate the bridge from the AISP contract or update its summary |
| `AISP_W_EC7_BRIDGE_MISSING` | EC7 | WARN | Default generated/distributed Agent Skills `SKILL.md` sidecar is missing, but core AISP conformance is still valid | Add a same-folder `SKILL.md` sidecar or document the opt-out |
| `AISP_E_EC7_BRIDGE_MISSING` | EC7 | FAIL | Expected Agent Skills `SKILL.md` bridge is missing | Add `SKILL.md` or point the bridge validator at the correct folder |
| `AISP_E_EC7_BRIDGE_INPUT` | EC7 | FAIL | `SKILL.md` could not be read | Fix file permissions/encoding |
| `AISP_E_EC7_FRONTMATTER` | EC7 | FAIL | `SKILL.md` frontmatter is missing, compressed, unclosed, contains unsupported top-level keys, or is outside the supported simple YAML shape | Use standalone `---` delimiters and only supported top-level keys: `name`, `description`, `license`, `allowed-tools`, `metadata` |
| `AISP_E_EC7_NAME` | EC7 | FAIL | Bridge `name` is missing, not lowercase hyphenated, too long, or contains forbidden vendor branding | Set `name` to the same-folder AISP id minus `_aisp` with underscores hyphenated |
| `AISP_E_EC7_NAME_DERIVATION` | EC7 | FAIL | Bridge `name` does not match the same-folder AISP id minus `_aisp` with underscores hyphenated | Update the sidecar frontmatter or the native AISP id |
| `AISP_E_EC7_DESCRIPTION` | EC7 | FAIL | Bridge `description` is missing, too long, or contains instruction-injection wording | Keep the description concise, routing-focused, and injection-safe |
| `AISP_E_EC7_METADATA` | EC7 | FAIL | Bridge metadata is missing or `metadata.generated_from_aisp` is not `"true"` | Add `metadata.generated_from_aisp: "true"` |
| `AISP_E_EC7_PROGRAM_PATH` | EC7 | FAIL | `metadata.aisp_program` is missing, absolute, remote, path-traversing, points outside the sidecar folder, or is not `aisp.aisop.json` | Put `SKILL.md` in the native `*_aisp` folder and set `metadata.aisp_program: aisp.aisop.json` |
| `AISP_E_EC7_PROGRAM_MISSING` | EC7 | FAIL | `metadata.aisp_program` points to a missing native AISP file | Add `aisp.aisop.json` to the same folder or fix the path |
| `AISP_E_EC7_BODY` | EC7 | FAIL | Bridge body does not guide loading `aisp.aisop.json` or does not state the bridge/source-of-truth boundary | Keep `SKILL.md` as a thin discovery bridge and name `aisp.aisop.json` |
| `AISP_E_EC7_EMBEDDED_AISP` | EC7 | FAIL | Native same-folder AISP package failed reference validation | Fix the native `aisp.aisop.json` package |
| `AISP_W_EC7_PROTOCOL` | EC7 | WARN | Bridge metadata protocol is missing or not `AISP V1.0.0` | Set `metadata.protocol: AISP V1.0.0` |
| `AISP_W_EC7_BRIDGE_MODE` | EC7 | WARN | Bridge metadata mode is missing or not `native_sidecar` | Set `metadata.bridge_mode: native_sidecar` |
| `AISP_W_EC7_RUNTIME_BOUNDARY` | EC7 | WARN | Bridge does not state that hard execution requires an AISP/AISOP runtime | Add the runtime boundary to the bridge body |
| `AISP_W_EC7_LOGIC_COPY` | EC7 | WARN | Bridge appears to copy AISP function logic | Keep logic in `aisp.aisop.json`; keep `SKILL.md` thin |
| `AISP_I_EC7_EMBEDDED_AISP` | EC7 | INFO | Native same-folder AISP program passed reference validation | Keep this validation record with release evidence |
| `AISP_W_EC8_SKILL_README_MISSING` | EC8 | WARN | Per-skill `README.md` is missing in the default profile | Run `python -B tools/aisp_readme.py <skill> --write` |
| `AISP_E_EC8_SKILL_README_MISSING` | EC8 | FAIL | Per-skill `README.md` is missing in strict/release mode | Run `python -B tools/aisp_readme.py <skill> --write` |
| `AISP_W_EC8_SKILL_README_MANUAL` | EC8 | WARN | Per-skill `README.md` lacks the generated marker | Regenerate it from `aisp.aisop.json` |
| `AISP_E_EC8_SKILL_README_MANUAL` | EC8 | FAIL | Strict/release mode found a per-skill `README.md` without the generated marker | Regenerate it from `aisp.aisop.json` |
| `AISP_W_EC8_SKILL_README_DRIFT` | EC8 | WARN | Per-skill `README.md` differs from the deterministic contract-derived projection | Run `python -B tools/aisp_readme.py <skill> --write` |
| `AISP_E_EC8_SKILL_README_DRIFT` | EC8 | FAIL | Strict/release mode found README drift from `aisp.aisop.json` | Run `python -B tools/aisp_readme.py <skill> --write` |
| `AISP_W_EC8_SKILL_README_BAD_SOURCE` | EC8 | WARN | Generated README source marker is missing or not `aisp.aisop.json` | Regenerate it from `aisp.aisop.json` |
| `AISP_E_EC8_SKILL_README_BAD_SOURCE` | EC8 | FAIL | Strict/release mode found a bad generated README source marker | Regenerate it from `aisp.aisop.json` |
| `AISP_W_EC8_SKILL_README_UNSUPPORTED_GENERATOR` | EC8 | WARN | Generated README generator marker is missing or unsupported | Regenerate it with `tools/aisp_readme.py` |
| `AISP_E_EC8_SKILL_README_UNSUPPORTED_GENERATOR` | EC8 | FAIL | Strict/release mode found a missing or unsupported README generator marker | Regenerate it with `tools/aisp_readme.py` |

---

## Input and Trace Shape Codes

| Code | Rule | Severity | Meaning | Fix |
|------|------|----------|---------|-----|
| `AISP_E_INPUT` | INPUT | FAIL | Validator/checker input file is missing, unreadable, invalid JSON, or cannot be inspected as the required artifact | Pass an existing valid `aisp.aisop.json`, skill folder, `aisp/` directory, or trace JSON file |
| `AISP_E_TRACE_SHAPE` | INPUT | FAIL | Runtime trace JSON is not an object | Emit a runtime trace object that follows `schemas/runtime-trace-v1.schema.json` |

---

## Standard Freshness Warning

| Code | Severity | Meaning | Fix |
|------|----------|---------|-----|
| `STANDARD_STALE` | WARN | `today > last_verified_date + 180 days` for a loaded `AISP_Standard.*` file | Re-verify the standard against current AISOP / Agent Skills references and bump `last_verified_date` |

---

## Violation vs Correct Examples

**M2 — `_aisp` suffix**

| Violation | Correct |
|-----------|---------|
| folder `yijing/` with `id: "yijing"` | folder `yijing_aisp/` with `id: "yijing_aisp"` |

**M3 — contract shape**

| Violation | Correct |
|-----------|---------|
| `system_prompt: "{\"profile\": \"aisp.skill.v1\", ...}"` | `user.content.aisp_contract: { "profile": "aisp.skill.v1", ... }` |

**M4 — phantom enforcement**

| Violation | Correct |
|-----------|---------|
| `"enforced_by": "interpret.step9:sys.assert"` (no `step9`) or `"interpret.step_note:sys.assert"` (metadata, not an execution step) | `"enforced_by": "interpret.step1:sys.assert"` (numeric execution step exists, begins with `sys.assert`) |

**M5 — path escape**

| Violation | Correct |
|-----------|---------|
| `"path": "../../etc/passwd"` | `"path": "data/hexagrams.json"` |

---

Align Axiom 0: Human Sovereignty and Wellbeing | Protocol: AISP | Execution: AISOP | Executor: SoulBot
