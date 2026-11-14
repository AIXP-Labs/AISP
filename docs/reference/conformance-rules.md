# Conformance Rules Reference

> Master index of all AISP conformance rules, organized by series and source standard file.
> A conformant AISP skill is **first a legal AISOP V1.0.0 program**, then satisfies the skill rules (M1–M7). A conformant runtime satisfies R1–R7.

Conformance is split across three loadable standard files: `AISP_Standard.core` (M / R), `AISP_Standard.security` (SE / ST), and `AISP_Standard.ecosystem` (EC). The JSON files are authoritative for rule semantics; this page is the catalog.

---

## Conformance Summary

```
A conformant skill = legal AISOP V1.0.0 program  +  M1–M7
A conformant runtime = R1–R7
Security extension   = SE1–SE8  (threats ST1–ST6)
Ecosystem extension  = EC1–EC8
```

| Series | Count | Domain | Source |
|--------|-------|--------|--------|
| **M** (Skill) | 7 | Skill-package conformance | `AISP_Standard.core` |
| **R** (Runtime) | 7 | Runtime behavior | `AISP_Standard.core` |
| **SE** (Security) | 8 | Resource & discovery attack surface | `AISP_Standard.security` |
| **ST** (Skill threats) | 6 | Threat taxonomy | `AISP_Standard.security` |
| **EC** (Ecosystem) | 8 | Directory, index, lifecycle, bootstrap projections | `AISP_Standard.ecosystem` |

---

## M — Skill Conformance

| Rule | Name | Source | Severity | Description |
|------|------|--------|----------|-------------|
| **M1** | Legal AISOP Program | `core` | FAIL | A 2-message array; required fields present; `protocol` = `"AISP V1.0.0"`; `loading_mode` = `"node"`; `aisop.main` exists; numeric string-valued execution steps; explicit `execute_mode` is `inline` or `agent` (omission falls back inline and warns); `license` SHOULD be present |
| **M2** | Folder / File / `_aisp` Suffix | `core` | FAIL | Skill at `aisp/<id>/aisp.aisop.json`; `id` == folder name and ends with `_aisp` |
| **M3** | aisp_contract Present | `core` | FAIL | `user.content.aisp_contract` is a real object; `profile` has versioned form `aisp.skill.v<major>`; contains `invocation` + non-empty `non_negotiable` |
| **M4** | enforced_by Points to a Real Mechanism | `core` | FAIL | Every `non_negotiable[].enforced_by` resolves to an existing node/numeric `stepN`/mechanism, `aisop.main` branch, or restricted `tools`; metadata fields such as `step_note` cannot satisfy a hard binding |
| **M5** | Resource Path Safety | `core` | FAIL | `resources[].path` relative, confined to skill folder or `_shared/`, no `../`; `mode` in the enum; `scope` is `skill` or `shared`; scripts declare `requires_tools` |
| **M6** | No Self-Declared Trust | `core` | FAIL | The skill MUST NOT self-declare `trusted` / `verified` / `safe` |
| **M7** | Required Generated Compatibility Interface | `core` | FAIL | Same-folder SKILL.md exists; derived name/description/license match; fixed metadata/bootstrap match, allowing five launch strings plus a strict frozen version-policy object. Checks never execute commands, resolve latest versions, migrate or repair. |

---

## R — Runtime Conformance

| Rule | Name | Source | Severity | Description |
|------|------|--------|----------|-------------|
| **R1** | Read Contract; Don't Skip Nodes | `core` | FAIL | Read `user.content.aisp_contract`; do not skip required `aisop.main` nodes; do not bypass `sys.io.confirm` |
| **R2** | Enforce enforced_by | `core` | FAIL | Enforce each `non_negotiable` via the mechanism its `enforced_by` names |
| **R3** | Don't Hide the Contract | `core` | FAIL | Hand the user-message contract to the model unmodified; do not hide or strip it; no separate render step needed |
| **R4** | Open-World Validation (AISOP base) | `core` | FAIL | The underlying AISOP runtime tolerates unknown keys and does not gate on the `protocol` value |
| **R5** | Trust Gate; Prefer the Index | `core` | WARNING | Pass untrusted skills/resources through a trust gate; prefer reading `aisp_list.json` over executing the script |
| **R6** | Tool-Enforcement Declaration | `core` | WARNING | A runtime SHOULD declare whether its tool enforcement is hard (permissions enforced) or advisory; if advisory, `enforced_by: tools` MUST NOT be treated as a hard guarantee |
| **R7** | Honor execute_mode (Dispatch Fidelity) | `core` | FAIL | A node with `execute_mode: "agent"` MUST run in an independent sub-agent (never collapsed inline); `inline` runs in the current context; omitted values fall back inline and warn statically. `agent` may be used for short high-isolation/high-impact nodes; `>10` numeric `stepN` execution steps is only a static review heuristic for non-agent nodes. An inherited AISOP node field (AISOP §5.2.8); a dispatch attribute, not an `enforced_by` mechanism |

Runtime conformance requires execution evidence. The format is defined by [`runtime-trace-v1.schema.json`](https://github.com/AIXP-Labs/AISP/blob/main/schemas/runtime-trace-v1.schema.json); the zero-dependency reference checker validates the published v1 trace shape plus selected runtime rules; it is not a generic JSON Schema engine or evidence authenticator:

```bash
python -B tools/aisp_check_runtime_trace.py examples/aisp/stock_analysis_aisp examples/aisp/stock_analysis_aisp/evals/runtime-traces/hard-pass.json
```

The static validator can consume the same trace claims to assess its `enforced_by: tools` evidence criteria in strict mode:

```bash
python -B tools/aisp_validate.py --strict-tools --runtime-trace examples/aisp/stock_analysis_aisp/evals/runtime-traces/hard-pass.json examples/aisp/stock_analysis_aisp
```

For R6, a top-level `tool_enforcement: "hard"` field is only a runtime attestation. Strict validation requires the trace to pass runtime checks and include matching `tool_enforcement` event evidence, or to use provenance-bearing tool capability evidence.

These criteria do not authenticate events or provenance fields. Checked-in traces are fixtures; accepting their recorded claims does not independently prove live runtime enforcement. See [Validator Coverage](validator-coverage.md) for the exact partial R-series coverage.

---

## Open-World AISOP Compatibility

> AISP requires the underlying AISOP runtime to (a) tolerate unknown keys in `system.content` (e.g. `license`) and `user.content` (e.g. `aisp_contract`), and (b) not gate on the `protocol` value (accept `AISP V1.0.0`). Closed-world validators that reject unknown keys or require `protocol == "AISOP V1.0.0"` are NOT AISP-compatible. AISP files are structurally AISOP V1.0.0 programs; the AISP `protocol` marker declares package semantics and protocol ownership, not a different execution grammar.

This is the operational restatement of **R4**. AISP does not fork the AISOP language — it rides on AISOP's open-world validation. A validator that is closed-world, or that hard-checks the `protocol` literal, cannot consume AISP files; this is a declared compatibility boundary, not a defect in either protocol.

---

## SE — Security Conformance

| Rule | Name | Source | Severity | Description |
|------|------|--------|----------|-------------|
| **SE1** | Path Confinement | `security` | FAIL | Resource paths relative and confined to the skill folder or `_shared/`; no `../`, no absolute paths |
| **SE2** | Remote Resource Gate | `security` | FAIL | Remote URLs disabled by default; require user confirmation |
| **SE3** | mode Gating | `security` | FAIL | `execute_only` scripts not injected in full into the model; `read_only` not executed; `mode` is a closed enum |
| **SE4** | Least-Authority Scripts | `security` | WARNING | Scripts declare `requires_tools` minimally; dangerous commands trigger `sys.io.confirm` |
| **SE5** | Discovery Script Safety | `security` | FAIL | `aisp_list.py` minimal, auditable, zero-dependency, only writes `aisp_list.json` |
| **SE6** | Trust Not Self-Declared | `security` | FAIL | Trust judged by runtime / registry / user / scanner; provenance recorded by registry |
| **SE7** | Axiom 0 Confirm Invariant | `security` | FAIL | `sys.io.confirm` is forced-blocking; MUST NOT be bypassed regardless of mode or `risk_level` |
| **SE8** | Read-Only During Execution | `security` | WARNING | Skill files and resources are read-only during normal execution; modifications happen only through a deliberate evolution/edit step |

---

## ST — Skill Threat Taxonomy

| Threat | Name | Vector | Mitigation |
|--------|------|--------|------------|
| **ST1** | Skill Discovery Poisoning | Malicious `aisp_list.py` / tampered `aisp_list.json` executes code or misrepresents skills | SE5 |
| **ST2** | Undeclared Resource | A folder file not declared in `resources` (unknown surface) | M5 (validator warns) |
| **ST3** | Indirect Injection via Remote Content | A resource references remote content carrying an injected payload | SE2 |
| **ST4** | Path Traversal / Resource Escape | A `resources[].path` uses `../` or an absolute path | SE1 / M5 |
| **ST5** | Excessive Authority | A script requests/uses more tools than needed; dangerous commands unconfirmed | SE4 |
| **ST6** | Trust Spoofing | A skill claims to be verified/trusted/safe | SE6 / M6 |

See the [Threat Taxonomy](threat-taxonomy.md) reference for per-threat detail.

---

## EC — Ecosystem Conformance

| Rule | Name | Source | Severity | Description |
|------|------|--------|----------|-------------|
| **EC1** | `aisp/` Directory Contract | `ecosystem` | WARNING | `aisp/README.md` MUST exist; `aisp_list.py` / `aisp_list.json` SHOULD exist |
| **EC2** | Index ↔ Folder Consistency | `ecosystem` | WARNING | `aisp_list.json` is a cache derived from folders; the folder is the source of truth |
| **EC3** | `_shared/` Scope | `ecosystem` | WARNING | `_shared/` holds shared resources, is not a skill folder, has no `_aisp` suffix |
| **EC4** | Registry Provenance | `ecosystem` | WARNING | Registry records provenance (source / commit / `contract_sha256` / `resources_sha256`) |
| **EC5** | Generation | `ecosystem` | ADVISORY | Generated skills still satisfy M1–M7 (generation is AISP-native and tool-agnostic) |
| **EC6** | Evolution Safety | `ecosystem` | WARNING | An evolution MUST NOT remove a safety constraint, lower `risk_level`, or expand `tools` without justification |
| **EC7** | Compatibility Mapping to M7 | `ecosystem` | FAIL | Required same-folder generated executor-only interface; no opt-out. Keep frontmatter, injection, same-folder path and native package checks. `bridge_mode` is `agent_skills_bridge`; fixed bootstrap functions are not copied business logic. |
| **EC8** | Generated Per-Skill README | `ecosystem` | WARNING / strict FAIL | Each `*_aisp/README.md` SHOULD be generated from `aisp.aisop.json`; strict/release profiles treat missing/manual/drifted README, bad source markers, and unsupported generator markers as FAIL |

Validate Agent Skills bridges with:

```bash
python -B tools/aisp_skill_md.py examples --check-all
python -B tools/aisp_validate_agent_skill_bridge.py examples/aisp --strict-readme
```

The shared M7 check proves unchanged bootstrap text and valid format, including derived header consistency; five strings do not certify an executor. The bridge validator additionally checks same-folder path safety and native package conformance. Neither proves trust, safety, runtime behavior or completion. Execution MUST use a conforming AISP/AISOP executor (SoulRun by default); without one, stop rather than improvise execution.

Generate and check per-skill README projections with:

```bash
python -B tools/aisp_readme.py examples/aisp/yijing_aisp --write
python -B tools/aisp_skill_md.py examples/aisp/yijing_aisp --write
python -B tools/aisp_readme.py examples --check-all
python -B tools/aisp_skill_md.py examples --check-all
python -B tools/aisp_validate.py --strict-readme examples/aisp
```

EC8 checks derivation consistency only. A passing README check does not prove the skill is safe or trustworthy; trust still comes from external provenance, registry/scanner output, and human approval. A generic non-AISOP agent can use a generated README as bootstrap guidance only; hard guarantees (`sys.assert`, tool gates, `sys.io.confirm`) require a conforming AISOP runtime. README-integrity hashes are local integrity hints, not trust claims; publication-time `package_sha256` is computed by the registry/provenance workflow instead of embedded in the README. See [Generated Skill README](generated-readme.md).

Registry provenance can be generated with:

```bash
python -B tools/aisp_hash.py --json examples/aisp/yijing_aisp
```

See [Registry & Runtime Artifacts](registry-runtime-artifacts.md).

---

## Severity Semantics

| Severity | Meaning | Effect |
|----------|---------|--------|
| **FAIL** | MUST violation | The skill / runtime is non-conformant |
| **WARNING** | SHOULD violation | Conformant but flagged; fix recommended |
| **ADVISORY** | Informative | Reference / lifecycle guidance, not a gate |

---

Align Axiom 0: Human Sovereignty and Wellbeing | Protocol: AISP | Execution: AISOP | Default Executor: SoulRun (replaceable)
