# Error Codes Reference

M7 replaces the old optional-interface policy. Historical `AISP_W_EC7_BRIDGE_MISSING` / `AISP_E_EC7_BRIDGE_MISSING` map to `AISP_E_M7_SKILL_MD_MISSING`; old bridge/summary drift warnings map to M7 header/body failures. The keyword-only `AISP_W_EC7_LOGIC_COPY` heuristic is retired: the fixed bootstrap legitimately contains functions; exact M7 comparison rejects copied business logic. Historical warnings no longer grant core conformance or an opt-out. Existing EC7 frontmatter/path/native-package checks remain complementary.

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
| `AISP_E_M1_FIELD` | M1 | FAIL | Required system metadata is missing/malformed; flow_format is outside mermaid/jsonflow/hybrid; a present summary/description/license/system_prompt/user_input is not a string; params is not an object; or tools is not an array of non-blank strings | Restore the declared field type; optional fields need not be added |
| `AISP_E_M1_INSTRUCTION` | M1 | FAIL | Instruction does not strongly name `aisp_contract` and `RUN aisop.main` | Use the required strong instruction |
| `AISP_E_M1_ROLES` | M1 | FAIL | Two messages do not have system/user roles in order | Restore the required message roles |
| `AISP_E_M1_MAIN` | M1 | FAIL | `user.content.aisop.main` is missing | Add `aisop.main` |
| `AISP_E_M1_FUNCTIONS` | M1 | FAIL | `user.content.functions` is missing or empty | Add node functions |
| `AISP_E_M1_FUNCTION_SHAPE` | M1 | FAIL | A `functions.<node>` entry is not an object | Represent each function node as an object with step fields and optional node metadata |
| `AISP_E_M1_STEP_SHAPE` | M1 | FAIL | A function has no numeric execution step (`step1`, `step2`, ...) or a numeric step is not a string | Add at least one string-valued `stepN` field |
| `AISP_E_M1_ON_ERROR` | M1 | FAIL | on_error is not an object or references a missing/non-string handler function | Restore an error-type to existing-function mapping; actual dispatch still needs runtime verification |
| `AISP_E_M1_GRAPH` | M1 | FAIL | Graph is malformed or empty | Fix the graph object/string |
| `AISP_E_M1_NODE_FUNCTION` | M1 | FAIL | A graph node has no corresponding `functions` entry | Add the missing function node or remove the graph node |
| `AISP_E_M1_EDGE_SHAPE` | M1 | FAIL | JSON-flow next/branches/error fields have invalid types | Use string arrays for next, an object of string targets for branches and a string error target |
| `AISP_E_M1_EDGE` | M1 | FAIL | A jsonflow edge points to a missing node | Fix the `next` / `branches` / `error` target |
| `AISP_E_M1_UNREACHABLE` | M1 | FAIL | A jsonflow node is unreachable from the graph entry | Connect or remove the node |
| `AISP_E_M1_TERMINAL` | M1 | FAIL | A graph has no terminal node | Add an end node or terminal branch |
| `AISP_W_M1_MERMAID_UNPARSED` | M1 | WARN | Mermaid graph had no parseable edges | Use simple Mermaid edges or provide jsonflow for conformance-critical checks |
| `AISP_E_M1_PROTOCOL` | M1 | FAIL | `protocol` is not `"AISP V1.0.0"` | Set `system.content.protocol` to `"AISP V1.0.0"` |
| `AISP_E_M1_LOADING_MODE` | M1 | FAIL | `system.content.loading_mode` is missing or is not `"node"` | Set `system.content.loading_mode` to `"node"` |
| `AISP_E_M1_EXECUTE_MODE` | M1 | FAIL | A function explicitly declares an unsupported execute_mode, including null, arrays or objects; only an absent key gets the inline fallback | Use `"inline"` or `"agent"` |
| `AISP_W_M1_EXECUTE_MODE_DEFAULT_INLINE` | M1 | WARN | A function omits `execute_mode`; runtime falls back to inline | Declare `"inline"` or `"agent"` explicitly |
| `AISP_W_M1_EXECUTE_MODE_AGENT_RECOMMENDED` | M1 | WARN | A function has more than 10 numeric execution steps (`stepN`) but is not `agent` | Review whether `execute_mode: "agent"` is appropriate; the threshold is a review heuristic, not a ban on shorter `agent` nodes |
| `AISP_W_M1_NO_LICENSE` | M1 | WARN | `license` missing | Add `system.content.license` (default `"Apache-2.0"`) |
| `AISP_W_M1_LICENSE` | M1 | WARN | Reference validator warning for omitted `license` or a blank license string, not for a non-string type error | Declare a non-blank `system.content.license`; this warning does not certify its identifier |
| `AISP_E_M2_SUFFIX` | M2 | FAIL | Folder name does not end with `_aisp` | Rename the folder to `<id>_aisp` |
| `AISP_E_M2_ID` | M2 | FAIL | Folder name is not lowercase snake_case ending in `_aisp` | Rename the folder |
| `AISP_E_M2_ID_MISMATCH` | M2 | FAIL | `id` does not equal the folder name | Make `id` equal the folder name |
| `AISP_E_M2_FILENAME` | M2 | FAIL | Skill file is not named `aisp.aisop.json` | Rename the entry file to `aisp.aisop.json` |
| `AISP_E_M3_NO_CONTRACT` | M3 | FAIL | `user.content.aisp_contract` missing | Add the contract as a real object in the user message |
| `AISP_E_M3_CONTRACT` | M3 | FAIL | Missing/non-object aisp_contract or malformed discovery category/tags metadata | Add the contract as a real object in the user message |
| `AISP_E_M3_STRING` | M3 | FAIL | Contract is a JSON-in-string or lives in `system_prompt` | Move it to `user.content.aisp_contract` as a real object |
| `AISP_E_M3_PROFILE` | M3 | FAIL | `profile` does not match the versioned `aisp.skill.v<major>` form | Set `profile` to `"aisp.skill.v1"` |
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
| `AISP_W_M5_AMBIGUOUS_USE` | M5 | WARN | A literal path names distinct skill/shared targets and at least one declaration permits the operation; the actual scoped target remains unknown | Resolve scope and review runtime evidence or use distinct paths; do not merge permissions. If all declarations forbid the operation, SE3 fails instead; this warning is not proof of safety |
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
| `AISP_E_R1_CONFLICT` | R1 | FAIL | Explicit contract_read: false conflicts with a contract_read event | Review/regenerate a faithful runtime summary; do not drop denying evidence merely to pass |
| `AISP_E_R1_TRACE_SHAPE` | R1 | FAIL | Runtime trace is missing required execution-evidence shape | Emit a runtime name and `events` array |
| `AISP_E_R2_NOT_ENFORCED` | R2 | FAIL | A `non_negotiable`'s `enforced_by` mechanism was not enforced | Enforce the mechanism the binding names |
| `AISP_E_R3_CONFLICT` | R3 | FAIL | Explicit contract_visible_to_model: false conflicts with a visibility event | Review the contradictory record without treating self-report as authentication |
| `AISP_E_R3_HIDDEN` | R3 | FAIL | Runtime hid or stripped the user-message `aisp_contract` | Hand the contract to the model unmodified |
| `AISP_E_R4_CLOSED_WORLD` | R4 | FAIL | The underlying AISOP runtime rejected unknown keys or gated on the `protocol` value | Use an open-world AISOP runtime (tolerates extra keys; does not gate on `protocol`) |
| `AISP_W_R5_NO_TRUST_GATE` | R5 | WARN | Untrusted skill/resource handled without a trust gate, or script run before reading the index | Add a trust gate; prefer reading `aisp_list.json` |
| `AISP_I_R_STATIC_ONLY` | R | INFO | Static validation completed without executing runtime-only R1-R7 checks | Add runtime trace validation when runtime behavior must be proven |
| `AISP_W_R6_NO_DECLARATION` | R6 | WARN | Runtime does not declare whether its tool enforcement is hard or advisory | Declare the mode; if advisory, `enforced_by: tools` is not a hard guarantee |
| `AISP_W_R6_ADVISORY` | R6 | WARN | Runtime declares advisory tool enforcement | Do not count `enforced_by: tools` as a hard guarantee |
| `AISP_W_R6_TOOLS_CONDITIONAL` | R6 | WARN | Static validation found `enforced_by: tools`; hardness depends on runtime permission enforcement | Provide runtime tool-enforcement evidence |
| `AISP_W_R6_TOOLS_ATTESTED_NOT_VERIFIED` | R6 | WARN | Runtime/tool artifact self-attests hard enforcement but lacks the required event evidence or provenance | Add `tool_enforcement` trace events or provenance-bearing tool capabilities |
| `AISP_W_R6_TRACE_NOT_CONFORMANT` | R6 | WARN | Runtime trace failed runtime conformance checks and cannot prove hard tool enforcement | Fix the runtime trace failures |
| `AISP_I_R6_TOOLS_HARD` | R6 | INFO | Artifact meets event/capability evidence criteria; provenance and recorded events are not independently authenticated | Keep the evidence artifact with the skill validation record |
| `AISP_E_R6_CONFLICT` | R6 | FAIL | Top-level hard declaration conflicts with advisory/unknown tool events | Review contradictory evidence; do not conceal non-hard records |
| `AISP_E_R6_TOOLS_NOT_HARD` | R6 | FAIL | Strict tools mode requires event/provenance-backed hard runtime/tool capability evidence, but none was provided or evidence was advisory/unknown | Provide conformant hard `--runtime-trace` or provenance-bearing `--tool-capabilities` evidence |
| `AISP_E_R6_TRACE_NOT_CONFORMANT` | R6 | FAIL | Runtime trace failed runtime conformance checks and cannot be used as strict hard tool evidence | Fix the runtime trace failures |
| `AISP_E_R6_TRACE_SKILL_MISMATCH` | R6 | FAIL | Runtime trace `skill_id` does not match the skill being validated | Use the matching runtime trace for this skill |
| `AISP_E_R7_COLLAPSED_INLINE` | R7 | FAIL | An agent node lacks dispatch evidence or any matching event claims non-agent mode/dispatch | Dispatch `agent` nodes to a sub-agent; never collapse them inline. Omitted `execute_mode` falls back inline and is reported statically as `AISP_W_M1_EXECUTE_MODE_DEFAULT_INLINE` |
| `AISP_E_R7_MODE_MISMATCH` | R7 | FAIL | A recorded dispatch for a known inline node (including the omitted-mode default) claims a non-inline mode or dispatch | Honor the declared/default inline mode; this check adds no mandatory inline-event coverage and does not authenticate events |

---

## Security Violation Codes (SE Series)

| Code | Rule | Severity | Meaning | Fix |
|------|------|----------|---------|-----|
| `AISP_E_SE1_PATH` | SE1 | FAIL | Entry/resource path is invalid or escapes its scope, or the resolved shared root leaves its containing aisp directory | Confine both the root and file before reading; no parent/absolute escapes |
| `AISP_E_SE2_REMOTE` | SE2 | FAIL | Remote URL resource accessed without confirmation | Disable by default; gate with `sys.io.confirm` |
| `AISP_E_SE3_MODE_GATE` | SE3 | FAIL | `execute_only` read into the model, `read_only` executed, or conflicting modes on normalized aliases of the same resolved file | Respect mode gating and resolve inconsistent inventory explicitly; do not merge permissions automatically |
| `AISP_W_SE4_AUTHORITY` | SE4 | WARN | Script over-requests tools or runs dangerous commands unconfirmed | Minimize `requires_tools`; add `sys.io.confirm` |
| `AISP_E_SE5_SCRIPT` | SE5 | FAIL | `aisp_list.py` cannot be safely inspected (path/type/encoding/syntax), or matches a disallowed import/call pattern | Restore a confined minimal script; passing the bounded AST scan is not a safety proof |
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
| `AISP_E_M7_SKILL_MD_MISSING` | M7 | FAIL | Required same-folder interface is absent | Explicitly generate it; no opt-out |
| `AISP_E_M7_SKILL_MD_INPUT` | M7 | FAIL | Interface/native input cannot be read or derived, or interface is an escaping/nonregular link | Repair input/path explicitly |
| `AISP_E_M7_SKILL_MD_HEADER` | M7 | FAIL | Derived name/description/license differ or fixed header/metadata drifted | Regenerate derived fields with `--write`; if fixed metadata changed, back up, note launch strings and version policy, delete and regenerate |
| `AISP_E_M7_SKILL_MD_CONFIG` | M7 | FAIL | Damaged/duplicate-key JSON, wrong two-message structure, missing/extra fields, empty/non-string launch value, or unknown content | Repair a damaged current interface explicitly, or back up, note launch strings and version policy, delete and regenerate; no defaults fallback |
| `AISP_E_M7_SKILL_MD_BODY` | M7 | FAIL | Fixed bootstrap, markers or other body text changed | Back up, note launch strings and version policy, delete and regenerate; write does not silently repair |
| `AISP_E_M7_SKILL_MD_LEGACY` | M7 | Retired | No longer emitted from the 2026-11-14 revision; old interfaces fail CONFIG, HEADER or BODY checks | Back up, note launch strings and version policy, delete and regenerate; checks never migrate |
| `AISP_E_M7_SKILL_MD_VERSION` | M7 | FAIL | Invalid/unresolved version policy, unsupported constraint/source, or another executor lacks an explicit requirement | Use a concrete `>=X.Y.Z` or `==X.Y.Z` and valid source; do not substitute SoulRun |
| `AISP_E_M7_SKILL_MD_RESOLUTION` | Generation | FAIL | Default SoulRun stable-release metadata is unavailable, malformed or unsupported | Stop without cached/default fallback; checks never invoke this resolver |
| `AISP_I_M7_SKILL_MD` | M7 | INFO | Bootstrap unchanged and format valid; executor not certified | Does not prove execution, safety or external trust; keep runtime acceptance separate |
| `AISP_E_EC7_BRIDGE_MODE` | EC7 / M7 | FAIL | Interface marker is not `agent_skills_bridge` | Back up, delete and regenerate |
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
| `AISP_E_EC7_PROTOCOL` (formerly `AISP_W_EC7_PROTOCOL`) | EC7 / M7 | FAIL | Required interface protocol marker is not `AISP V1.0.0` | Back up, delete and regenerate; cannot pass as a warning |
| Historical `AISP_W_EC7_BRIDGE_MODE` | EC7 → M7 | Retired | Old `native_sidecar` marker is no longer a current interface | Regenerate; current wrong markers FAIL `AISP_E_EC7_BRIDGE_MODE` and M7 |
| Historical `AISP_W_EC7_RUNTIME_BOUNDARY` | EC7 → M7 | Retired | Runtime-boundary keyword heuristic is replaced by fixed-bootstrap checking | Changed fixed text fails M7; do not add free-form repair prose |
| Historical `AISP_W_EC7_LOGIC_COPY` | EC7 → M7 | Retired | Functions in the fixed bootstrap are legitimate, not copied business logic | Exact M7 comparison rejects drift; the keyword-only warning is no longer emitted |
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
| `AISP_E_TRACE_SHAPE` | INPUT | FAIL | Runtime trace violates the bounded published v1 shape (types, required fields or enums) | Emit a runtime trace object that follows `schemas/runtime-trace-v1.schema.json` |

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

Align Axiom 0: Human Sovereignty and Wellbeing | Protocol: AISP | Execution: AISOP | Default Executor: SoulRun (replaceable)
