# Registry & Runtime Artifacts

> Reference for machine-readable artifacts that sit around an AISP skill package: runtime traces, registry manifests, and optional tool capability declarations.

The skill folder remains the source of truth. These artifacts are evidence and metadata produced by runtimes, registries, or validation tools.

Hashing resolves resource paths before reading; the shared root itself must stay
inside the containing `aisp/` directory. A link to an external root cannot grant
additional read authority. These checks are not a hostile-filesystem concurrency
guarantee and do not authenticate the bytes or their origin.

---

## Runtime Trace

Schema: [`schemas/runtime-trace-v1.schema.json`](https://github.com/AIXP-Labs/AISP/blob/main/schemas/runtime-trace-v1.schema.json)

A runtime trace records execution evidence for R-series checks that cannot be proven from a static `aisp.aisop.json` file.

Relevant fields (the schema defines exact requiredness):

| Field | Description |
|-------|-------------|
| `runtime` | Runtime name / implementation identifier |
| `skill_id` | Skill id, ending with `_aisp` |
| `contract_read` | Whether `user.content.aisp_contract` was read |
| `contract_visible_to_model` | Whether the contract was handed to the model/user-message context |
| `tool_enforcement` | Runtime-level attestation: `"hard"` or `"advisory"` |
| `events[]` | Execution events such as `contract_read`, `tool_enforcement`, `execute_mode_dispatch`, and `sys_call` |

For `execute_mode_dispatch` events, the trace schema requires `node`, `mode`,
and `dispatched_as`. A conformant R7 trace for an `execute_mode: "agent"` node
uses `mode: "agent"` and `dispatched_as: "agent"`; `dispatched_as: "inline"`
or a missing dispatch event fails the runtime trace check.

For known inline nodes, including the default when `execute_mode` is omitted,
any recorded dispatch must use both `mode: "inline"` and
`dispatched_as: "inline"`. A contradictory event fails with
`AISP_E_R7_MODE_MISMATCH`. Inline events are not newly required for every node;
this checks supplied records, not execution completeness or event authenticity.

The zero-dependency CLI implements the published v1 trace's bounded shape,
including required fields, types, enums and dispatch-event conditionals; it is
not a generic JSON Schema engine. Agent nodes need dispatch evidence and every
matching event must declare both mode and dispatch as agent. Later valid events
cannot hide earlier non-agent records. Contradictory hard/non-hard tool evidence
fails. A reported `runtime_conformant: true` still means no implemented check
failed, not complete R-series conformance or authenticated execution.

The contract-read and visibility flags describe run-level claims, not initial
pre-event state. If explicitly false while a corresponding affirmative event
is present, the checker fails with `AISP_E_R1_CONFLICT` or
`AISP_E_R3_CONFLICT`; an absent flag can still use event evidence. Review or
regenerate a faithful record, not discard denying evidence to obtain a pass.
Consistency is not proof that any event actually occurred.

Reference check:

```bash
python -B tools/aisp_check_runtime_trace.py examples/aisp/stock_analysis_aisp examples/aisp/stock_analysis_aisp/evals/runtime-traces/hard-pass.json
```

The checker currently verifies R1/R3/R6/R7 evidence and SE7 confirm bypass evidence. A top-level `tool_enforcement: "hard"` field is only an attestation. To count as hard tool evidence, a trace must also contain a `tool_enforcement` event, for example:

```json
{ "type": "tool_enforcement", "enforcement": "hard", "tools": ["filesystem", "shell"] }
```

The static validator can also consume runtime trace evidence to resolve `enforced_by: tools`:

```bash
python -B tools/aisp_validate.py --strict-tools --runtime-trace examples/aisp/stock_analysis_aisp/evals/runtime-traces/hard-pass.json examples/aisp/stock_analysis_aisp
```

In strict tools mode, `enforced_by: tools` fails unless the trace is runtime-conformant for the same `skill_id` and contains matching hard `tool_enforcement` event evidence. A bare top-level hard declaration is reported as attested but not verified, and does not satisfy `--strict-tools`.

These are evidence-shape/consistency rules, not event authentication. A fabricated event may still satisfy them, and the checked-in traces are regression fixtures rather than independent live-run recordings. A strict PASS does not authenticate the runtime or prove that the recorded permission boundary physically held.

---

## Registry Manifest

Schema: [`schemas/registry-manifest-v1.schema.json`](https://github.com/AIXP-Labs/AISP/blob/main/schemas/registry-manifest-v1.schema.json)

A registry manifest records provenance for a distributed skill folder. It is registry-side evidence; the skill must not self-declare trust.

Core fields:

| Field | Description |
|-------|-------------|
| `manifest_version` | Artifact version: new output `"1.1"`; legacy `"1.0"` remains accepted |
| `protocol` | `"AISP V1.0.0"` |
| `skill_id` | Skill id |
| `skill_version` | Skill version from `system.content.version` |
| `source` | Optional source repository / registry URL |
| `commit` | Optional source commit |
| `skill_path` | Portable package-internal skill folder label; in v1 this is the skill id and never a host absolute path |
| `contract_sha256` | Canonical hash of `user.content.aisp_contract` |
| `program_sha256` | Canonical hash of the complete two-message program; required in manifest 1.1 |
| `resources_sha256` | Canonical hash of declared resource records |
| `package_sha256` | Canonical hash of package content evidence; excludes host-local paths and provenance fields such as `source` / `commit` |
| `resources[]` | Per-resource existence and content hash records |

`package_sha256` is content evidence, not a trust proof. It is intentionally stable when the same skill folder is copied to another local directory or when registry-side `source` / `commit` metadata changes. Trust still comes from external provenance, registry policy, signatures, or human approval.

Manifest 1.1 hashes the identity, contract/resource evidence and `program_sha256`
into `package_sha256`; 1.0 omitted the program body and therefore cannot detect
business-function-only edits. Hashes change on migration to 1.1. Neither version
automatically covers undeclared files or the generated SKILL.md executor
configuration. Canonical JSON removes formatting/key-order differences; it does
not normalize resource file bytes or authenticate an author.

The `--out` destination must not be the business-program file, a declared
resource input or a filesystem alias of either, including hardlinks. Output
uses single-file atomic UTF-8/LF replacement. This prevents overwriting hash
inputs; it is not an immutable snapshot or a hostile-filesystem concurrency
guarantee. Keep publication manifests external to their own hash inputs.

Generate a manifest:

```bash
python -B tools/aisp_hash.py --json examples/aisp/yijing_aisp
python -B tools/aisp_hash.py examples/aisp/yijing_aisp --out yijing_aisp.manifest.json
```

---

## Tool Capabilities

Schema: [`schemas/tool-capabilities-v1.schema.json`](https://github.com/AIXP-Labs/AISP/blob/main/schemas/tool-capabilities-v1.schema.json)

Tool capability declarations let a runtime or registry say whether a tool permission is hard-enforced or advisory, and what risk level it carries.

This is especially important for `enforced_by: tools`, because that binding is hard only when the runtime truly enforces tool permissions.

Example shape:

```json
{
  "tool_capabilities_version": "1.0",
  "provenance": {
    "source": "registry.example/fixtures/hard-tools",
    "generated_by": "reference-runtime"
  },
  "tools": {
    "filesystem": {
      "risk_level": "medium",
      "enforcement": "hard",
      "capabilities": ["read", "write"]
    },
    "shell": {
      "risk_level": "high",
      "enforcement": "hard",
      "capabilities": ["execute"]
    }
  }
}
```

Validator use:

```bash
python -B tools/aisp_validate.py --tool-capabilities tests/fixtures/tool_capabilities/hard_tools.json examples/aisp/stock_analysis_aisp
python -B tools/aisp_validate.py --strict-tools --tool-capabilities tests/fixtures/tool_capabilities/hard_tools.json examples/aisp/stock_analysis_aisp
```

Without `--strict-tools`, advisory, missing, or self-attested-only evidence remains a warning. With `--strict-tools`, every declared tool for a skill using `enforced_by: tools` must have event-backed runtime trace evidence or provenance-bearing hard tool capability evidence. When both runtime trace and tool capability evidence are provided, non-hard or unprovenanced capability evidence is not silently overridden by a hard runtime trace.

The CLI checks the published v1 capability shape before consuming evidence:
version `1.0`, required tool risk/enforcement fields, optional string arrays,
and known provenance-field types. Malformed input produces `AISP_E_INPUT` even
outside strict-tools mode; open extension fields remain allowed. These are
bounded standard-library checks, not a generic schema engine.

An explicitly supplied empty capability map is incomplete evidence for declared tools, not the absence of an artifact: a hard trace cannot override it. Strict tools fails; non-strict mode retains a warning. The presence of `provenance` fields is not verification of their truth, signatures or publisher identity. Consumers need an external trust policy and verification appropriate to their runtime or registry.

---

Align Axiom 0: Human Sovereignty and Wellbeing | Protocol: AISP | Execution: AISOP | Default Executor: SoulRun (replaceable)
