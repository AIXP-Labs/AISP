# aisp.aisop.json Field Reference

> Complete field reference for the `aisp.aisop.json` skill-file format.
> A skill file is structurally a legal AISOP V1.0.0 program: a two-message array (`system` + `user`).

An AISP skill lives at `aisp/<id>_aisp/aisp.aisop.json`. The file is a JSON array of exactly two messages. The first (`role: "system"`) carries skill identity and metadata. The second (`role: "user"`) carries the execution instruction, the skill contract, the execution graph, and the per-node functions.

---

## Field Overview

| Field | Location | Type | Required | Responsibility |
|-------|----------|------|----------|----------------|
| `protocol` | system.content | string | MUST | Protocol authorship marker — fixed `"AISP V1.0.0"` |
| `axiom_0` | system.content | string | MUST | Immutable alignment — fixed `"Human_Sovereignty_and_Wellbeing"` |
| `id` | system.content | string | MUST | Skill identity — equals folder name, ends with `_aisp` |
| `name` | system.content | string | MUST | Human-readable skill name |
| `version` | system.content | string | MUST | SemVer of this skill |
| `license` | system.content | string | SHOULD | SPDX license — default `"Apache-2.0"` |
| `summary` | system.content | string | MUST | One-sentence capability overview |
| `description` | system.content | string | SHOULD | Detailed description |
| `flow_format` | system.content | string | MUST | `"mermaid"` \| `"jsonflow"` \| `"hybrid"` |
| `loading_mode` | system.content | string | MUST | Fixed `"node"` for AISP skills |
| `tools` | system.content | array | MAY | Tool declarations (capability allow-list) |
| `params` | system.content | object | MAY | Input parameter declarations |
| `system_prompt` | system.content | string | MAY | Behavioral layer — MAY be empty `""` |
| `instruction` | user.content | string | MUST | Strong directive (immutable form, see below) |
| `user_input` | user.content | string | SHOULD | Runtime placeholder `"{user_input}"` |
| `aisp_contract` | user.content | object | MUST | The skill contract — a **real object** (see [aisp_contract Fields](aisp_contract-fields.md)) |
| `aisop` | user.content | object | MUST | Execution graph container (`main` = flow string/object) |
| `functions` | user.content | object | MUST | Per-node execution steps |

---

## system.content Field Details

### protocol

| Constraint | Value |
|------------|-------|
| Required | MUST |
| Type | string |
| Fixed value | `"AISP V1.0.0"` |
| Note | Declares AISP authorship. The file is still **structurally** an AISOP V1.0.0 program. The AISOP reference validator checks only that `protocol` exists, not its value, so it accepts `"AISP V1.0.0"` (open-world; see R4). |

### axiom_0

| Constraint | Value |
|------------|-------|
| Required | MUST |
| Type | string |
| Fixed value | `"Human_Sovereignty_and_Wellbeing"` |
| Note | Immutable. Inherited from AISOP (and ultimately HSAW); `sys.io.confirm` remains forced-blocking. |

### id

| Constraint | Value |
|------------|-------|
| Required | MUST |
| Type | string |
| Format | lowercase, `snake_case`, MUST end with `_aisp` |
| Rule | MUST equal the parent folder name (e.g. folder `yijing_aisp/` ↔ `id: "yijing_aisp"`). Enforced by conformance rule **M2**. |
| Example | `"yijing_aisp"`, `"stock_analysis_aisp"` |

### name

| Constraint | Value |
|------------|-------|
| Required | MUST |
| Type | string |
| Example | `"Yijing Divination"` |

### version

| Constraint | Value |
|------------|-------|
| Required | MUST |
| Type | string (SemVer) |
| Example | `"1.0.0"` |

### license

| Constraint | Value |
|------------|-------|
| Required | SHOULD |
| Type | string (SPDX identifier) |
| Default | `"Apache-2.0"` |
| Note | Program-identity license. The contract does NOT duplicate it. |

### summary

| Constraint | Value |
|------------|-------|
| Required | MUST |
| Type | string (one sentence) |
| Example | `"Cast and interpret an I Ching (Yijing) hexagram for a user's question."` |

### description

| Constraint | Value |
|------------|-------|
| Required | SHOULD |
| Type | string |
| Example | `"Native AISP skill: clarify the question, cast a hexagram via a deterministic toss, and interpret it for reflection (not deterministic prediction)."` |

### flow_format

| Constraint | Value |
|------------|-------|
| Required | MUST |
| Type | string enum |
| Values | `"mermaid"` \| `"jsonflow"` \| `"hybrid"` |

### loading_mode

| Constraint | Value |
|------------|-------|
| Required | MUST |
| Type | string enum |
| Fixed value | `"node"` |
| Reason | AISP skills use progressive disclosure: load the selected skill, then load/execute node content and resources along the actual path. This is a loading strategy, not a security or trust proof. |

### tools

| Constraint | Value |
|------------|-------|
| Required | MAY |
| Type | array of strings (or structured tool objects) |
| Role | Capability allow-list. Backs `enforced_by: tools` red lines (hard only when the runtime enforces tool permissions). |
| Example | `["filesystem", "code"]`, `["filesystem", "shell"]` |

### params

| Constraint | Value |
|------------|-------|
| Required | MAY |
| Type | object |
| Example | `{ "question": "string" }` |

### system_prompt

| Constraint | Value |
|------------|-------|
| Required | MAY |
| Type | string |
| Default | `""` (empty) |
| Note | The behavioral layer. **MAY be empty** — the contract lives in the user message, not here. It MUST NOT carry the `aisp_contract` (no JSON-in-string). |

> **Conflict rule.** `system_prompt` MAY be empty. If non-empty, it MUST NOT conflict with `aisp_contract`, `aisop.main`, or `functions`. The `aisp_contract` MUST NOT be duplicated into `system_prompt` (no dual source; no JSON-in-string).

**Must not include**

| Prohibition | Reason |
|-------------|--------|
| The `aisp_contract` as a JSON string | The contract is a real object in `user.content` |
| Anything conflicting with `aisp_contract` / `aisop.main` / `functions` | No dual source of truth |
| Triggering / red lines / resource inventory | Those belong to `aisp_contract` (Tier S) |
| Role / principles / knowledge restated | Those belong to `functions` (Tier A) |

---

## user.content Field Details

### instruction (Invariant)

| Constraint | Value |
|------------|-------|
| Required | MUST |
| Type | string |
| Immutable form | `"STRICTLY OBEY aisp_contract; its non_negotiable rules are inviolable; then RUN aisop.main"` |

The `instruction` is a strong directive: it names the contract for obedience and then asserts execution of `aisop.main`. It makes the model **necessarily read** the contract this turn (it is sitting in the same user message), without depending on a runtime render step.

### user_input

| Constraint | Value |
|------------|-------|
| Required | SHOULD |
| Type | string |
| Form | `"{user_input}"` — runtime placeholder substituted by the executor with the actual user message |

### aisp_contract

| Constraint | Value |
|------------|-------|
| Required | MUST |
| Type | **object** (a real JSON object — never a string) |
| Detection | `profile` starts with `aisp.skill.` |
| Reference | See [aisp_contract Field Reference](aisp_contract-fields.md) for the full schema |

### aisop (Execution Graph)

| Constraint | Value |
|------------|-------|
| Required | MUST |
| Type | object |
| Shape | keyed by graph name → flow string (Mermaid) or flow object (JSON). `main` is the entry graph reached by `RUN aisop.main`. |

**Example**

```json
"aisop": {
  "main": "graph TD\n    clarify[Clarify the question] --> cast[Cast hexagram]\n    cast --> interpret[Interpret]\n    interpret --> end_node((End))"
}
```

### functions Object Structure

| Constraint | Value |
|------------|-------|
| Required | MUST |
| Type | object keyed by graph node name |
| Completeness | Every node in `aisop.main` MUST have a matching `functions` entry |

**Function node fields**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `step1`, `step2`, ... | string | MUST (≥1) | Ordered execution steps. Only numeric `stepN` keys (`step1`, `step2`, ...) count as execution steps. Each step is exactly one of: a `sys.*` call, a `RUN aisop.*` sub-task, or a natural-language instruction. Metadata keys such as `step_note` do not count. |
| `constraints` | array | MAY | Per-node constraints (soft guidance) |
| `output_mapping` | string | MAY | Names the node's output for cross-node transfer |
| `on_error` | string/object | MAY | Failure routing for the node |
| `execute_mode` | string | MAY | Dispatch mode — an inherited AISOP node field (AISOP spec §5.2.8): `"inline"` (default current-context execution) or `"agent"` (independent sub-agent for isolation, source gathering, generation, complex validation, or high-impact decisions). If omitted, runtime falls back to `"inline"` and the reference validator warns. A runtime MUST honor `agent` (**R7**): an `agent` node MUST run as a sub-agent, never collapsed inline. A dispatch attribute, **not** an `enforced_by` mechanism. |

**Rules for functions**

- A step referenced by an `enforced_by` of the form `<node>.stepN:<mechanism>` MUST be a numeric execution step, MUST exist, and MUST begin with that mechanism (conformance rule **M4**). Metadata keys such as `step_note` cannot satisfy `enforced_by`.
- Role, principles, knowledge, failure handling, and structured output (`sys.llm.json` schema) all live here (Tier A) — never in the contract.
- `execute_mode` omitted means fallback `"inline"` and `AISP_W_M1_EXECUTE_MODE_DEFAULT_INLINE`; generated/distributed skills SHOULD declare it explicitly for auditability.
- Explicit `execute_mode` values MUST be `"inline"` or `"agent"`; anything else fails static conformance.
- `inline` is appropriate for short routing, classification, confirmation, and simple summarization nodes.
- `agent` MAY be used for high-isolation, high-complexity, or high-impact nodes; step count is not the sole criterion.
- Nodes with more than 10 numeric `stepN` execution steps SHOULD be reviewed for `execute_mode: "agent"`; the reference validator warns when such a non-agent node remains inline. Metadata keys such as `step_note` are ignored by this heuristic. This threshold is a review heuristic, not a restriction on using `agent` for shorter nodes.
- AISP does not redefine `execute_mode` — it inherits it from AISOP and requires runtimes to honor it (R7). Other inherited AISOP node keys (`join`, `map`, `retry_policy`, `context_filter`) are likewise available per the AISOP spec.
- The graph MUST have an end node.

---

## Complete File Structure

```json
[
  {
    "role": "system",
    "content": {
      "protocol": "AISP V1.0.0",
      "axiom_0": "Human_Sovereignty_and_Wellbeing",
      "id": "yijing_aisp",
      "name": "Yijing Divination",
      "version": "1.0.0",
      "license": "Apache-2.0",
      "summary": "Cast and interpret an I Ching (Yijing) hexagram for a user's question.",
      "description": "Native AISP skill: clarify, cast, and interpret a hexagram for reflection.",
      "flow_format": "mermaid",
      "loading_mode": "node",
      "tools": ["filesystem", "code"],
      "params": { "question": "string" },
      "system_prompt": ""
    }
  },
  {
    "role": "user",
    "content": {
      "instruction": "STRICTLY OBEY aisp_contract; its non_negotiable rules are inviolable; then RUN aisop.main",
      "user_input": "{user_input}",
      "aisp_contract": {
        "profile": "aisp.skill.v1",
        "invocation": { "mode": "auto_or_manual", "when_to_use": ["..."], "when_not_to_use": ["..."] },
        "non_negotiable": [ { "rule": "...", "enforced_by": "interpret.step1:sys.assert" } ],
        "discovery": { "category": "culture", "tags": ["yijing"] },
        "risk_level": "low",
        "resources": [ { "id": "hexagrams", "path": "data/hexagrams.json", "kind": "data", "mode": "read_only" } ]
      },
      "aisop": {
        "main": "graph TD\n    clarify --> cast\n    cast --> interpret\n    interpret --> end_node((End))"
      },
      "functions": {
        "clarify": { "step1": "Identify the user's question and intent.", "output_mapping": "question" },
        "cast": { "step1": "sys.code.exec('python', '...') -> lines", "step2": "sys.io.read('data/hexagrams.json') -> table" },
        "interpret": {
          "step1": "sys.assert('hexagram != null', 'No hexagram has been cast')",
          "step2": "sys.llm.json('Interpret the hexagram', schema={summary:'string', disclaimer:'string'}) -> reading",
          "constraints": ["Ground the interpretation in the cast hexagram."]
        },
        "end_node": { "step1": "Return the final Markdown reading." }
      }
    }
  }
]
```

---

Align Axiom 0: Human Sovereignty and Wellbeing | Protocol: AISP | Execution: AISOP | Executor: SoulBot
