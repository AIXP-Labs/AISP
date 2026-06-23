# Registry & Runtime Artifacts

> Reference for machine-readable artifacts that sit around an AISP skill package: runtime traces, registry manifests, and optional tool capability declarations.

The skill folder remains the source of truth. These artifacts are evidence and metadata produced by runtimes, registries, or validation tools.

---

## Runtime Trace

Schema: [`schemas/runtime-trace-v1.schema.json`](../../schemas/runtime-trace-v1.schema.json)

A runtime trace records execution evidence for R-series checks that cannot be proven from a static `aisp.aisop.json` file.

Minimum fields:

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

---

## Registry Manifest

Schema: [`schemas/registry-manifest-v1.schema.json`](../../schemas/registry-manifest-v1.schema.json)

A registry manifest records provenance for a distributed skill folder. It is registry-side evidence; the skill must not self-declare trust.

Core fields:

| Field | Description |
|-------|-------------|
| `manifest_version` | Manifest schema version (`"1.0"`) |
| `protocol` | `"AISP V1.0.0"` |
| `skill_id` | Skill id |
| `skill_version` | Skill version from `system.content.version` |
| `source` | Optional source repository / registry URL |
| `commit` | Optional source commit |
| `skill_path` | Portable package-internal skill folder label; in v1 this is the skill id and never a host absolute path |
| `contract_sha256` | Canonical hash of `user.content.aisp_contract` |
| `resources_sha256` | Canonical hash of declared resource records |
| `package_sha256` | Canonical hash of package content evidence; excludes host-local paths and provenance fields such as `source` / `commit` |
| `resources[]` | Per-resource existence and content hash records |

`package_sha256` is content evidence, not a trust proof. It is intentionally stable when the same skill folder is copied to another local directory or when registry-side `source` / `commit` metadata changes. Trust still comes from external provenance, registry policy, signatures, or human approval.

Generate a manifest:

```bash
python -B tools/aisp_hash.py --json examples/aisp/yijing_aisp
python -B tools/aisp_hash.py examples/aisp/yijing_aisp --out yijing_aisp.manifest.json
```

---

## Tool Capabilities

Schema: [`schemas/tool-capabilities-v1.schema.json`](../../schemas/tool-capabilities-v1.schema.json)

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

---

Align Axiom 0: Human Sovereignty and Wellbeing | Protocol: AISP | Execution: AISOP | Executor: SoulBot
