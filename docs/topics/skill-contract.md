# The Skill Contract

> AISP Protocol — Conceptual Guide
> Classification: Contract Schema

The skill contract is the single most important design decision in AISP. It is `user.content.aisp_contract` — a **real JSON object**, located in the **user message**, carrying the lean metadata a consumer needs before and during execution. This document explains its shape, why it lives where it does, and each of its fields.

---

## Why a Real Object

Earlier drafts experimented with stuffing the contract into `system_prompt` as a JSON-in-string. That forced escaping, a string/object dual form, and a "wire vs display" split — brittle and machine-hostile. AISP discards all of that.

| Property | JSON-in-string (rejected) | **Real object (AISP)** |
|----------|---------------------------|------------------------|
| Escaping | Required | None |
| Parsing | String → parse → object | Direct object access |
| Dual forms | string / object ambiguity | One form only |
| Discovery script | Must parse strings | Reads the object directly |

`aisp_contract` is an **AISP-owned field**. AISOP applies open-world validation and tolerates unknown keys on `user.content`, so an AISOP runtime ignores it while an AISP-aware runtime reads it — no change to AISOP Core is required.

---

## Why the User Message

The contract lives in the **user message** because that is the model's live content this turn. The model reads it directly — exactly as an Agent Skills `SKILL.md` is loaded into context — without depending on a separate runtime "render" step.

The `instruction` field, also in the user message, names the contract for obedience with a strong directive:

```text
"STRICTLY OBEY aisp_contract; its non_negotiable rules are inviolable; then RUN aisop.main"
```

> Placing the contract in the user message makes the model **necessarily read it** (no rendering gamble). Program identity (`id` / `name` / `version` / `license` / `summary` / `description`) stays in `system.content` and is **not** duplicated in the contract.

---

## Contract Shape

```json
{
  "profile": "aisp.skill.v1",
  "invocation": { "mode": "auto_or_manual", "when_to_use": ["string"], "when_not_to_use": ["string"] },
  "non_negotiable": [ { "rule": "string (NL)", "enforced_by": "<node>.stepN:<mechanism> | aisop.main | tools" } ],
  "discovery": { "category": "string", "tags": ["string"] },
  "risk_level": "low | medium | high | critical",
  "resources": [
    { "id": "string", "path": "relative/path", "kind": "data|script|reference|asset|template|…", "mode": "read_only|execute_only|read_and_execute", "when": "string?", "scope": "skill|shared?", "requires_tools": ["string"]? }
  ]
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `profile` | MUST | `aisp.skill.v1` — detected by the `aisp.skill.` prefix |
| `invocation` | MUST | Triggering (before execution) |
| `non_negotiable` | MUST | Red lines + `enforced_by` binding |
| `discovery` | SHOULD | `category` / `tags` for registry / routing |
| `risk_level` | SHOULD | Single risk grade |
| `resources` | MAY | Resource inventory |

---

## profile

`profile` identifies the contract schema. A runtime detects an AISP skill by the `aisp.skill.` **prefix**. Only a major change (`v1` → `v2`) is considered incompatible. The field name is fixed as `aisp_contract` — not `aisp_skill_contract` ("skill" is redundant; AISP already contains it), and not a bare `skill_contract` (which lacks a namespace).

---

## invocation

Triggering happens **before** execution ("should this skill start at all?"), which an AISOP flow inherently cannot express — hence it lives in the contract.

| Sub-field | Required | Description |
|-----------|----------|-------------|
| `mode` | SHOULD | `manual_only` / `auto_or_manual` / `auto_preferred` / `internal_only` |
| `when_to_use` | MUST | Trigger conditions (structured, routable) |
| `when_not_to_use` | MUST | Disabling boundary; **wins over `when_to_use` on conflict** |

`when_to_use` should not be too broad. On conflict, `when_not_to_use` wins; if uncertain, the runtime asks the user.

---

## non_negotiable

A red line = a natural-language declaration (`rule`) **bound** to a real enforcement mechanism (`enforced_by`). This is AISP's core differentiator: **declaration ↔ enforcement is machine-verifiable** (conformance rule M4).

```json
"non_negotiable": [
  { "rule": "Do not interpret without a cast hexagram.", "enforced_by": "interpret.step1:sys.assert" }
]
```

The `enforced_by` grammar and the soft/hard distinction are covered in depth in [enforced_by & sys.*](enforced-by-and-sys.md). The declarative field is named `non_negotiable`, **not** `assert` — because `assert` is already `sys.assert`, a deterministic hard check (the opposite semantics).

---

## discovery

| Sub-field | Description |
|-----------|-------------|
| `category` | Top-level category (registry / routing) |
| `tags` | Tag array (registry search) |

Used by `aisp_list.json`, the registry, and routing; MAY be omitted when there is no registry.

---

## risk_level

A single grade for trust / registry; fine-grained governance comes from `sys.*` + `tools`.

| Value | Meaning |
|-------|---------|
| `low` | Read-only / analysis |
| `medium` | Writes locally |
| `high` | Delete / deploy / exfiltrate |
| `critical` | Mandatory human review or no autonomy |

---

## resources

`resources` is the **inventory** ("what exists, where, what kind, read or execute"); the `functions` nodes are the **usage** (`sys.io.read` / `sys.run`).

| Sub-field | Required | Description |
|-----------|----------|-------------|
| `id` | MUST | Resource identifier |
| `path` | MUST | Relative path; `scope:skill` relative to the skill folder, `scope:shared` relative to `_shared/` |
| `kind` | MUST | **Open vocabulary**: data / script / reference / asset / template / … |
| `mode` | MUST | **Controlled enum**: `read_only` / `execute_only` / `read_and_execute` |
| `when` | MAY | When to load |
| `scope` | MAY | `skill` (default) / `shared` |
| `requires_tools` | MAY | Tools a script needs (least authority) |

> Note the asymmetry: `kind` is open, `mode` is a closed enum (the security gate). See [Resources](resources.md).

---

## The Lean-Metadata Principle

The contract holds only triggering, red-line binding, discovery, risk, and the resource inventory. It **MUST NOT** duplicate Tier A content. The following all belong in `functions` / `sys.*` / `tools`, *not* in the contract:

| Belongs in Tier A — NOT the contract |
|--------------------------------------|
| Role / persona / principles / knowledge |
| Failure handling |
| Structured output format |
| Resource *usage* (`sys.io.read` / `sys.run`) |
| Tools |
| Program identity (`summary` / `description`) |

---

## Full Example

```json
{
  "profile": "aisp.skill.v1",
  "invocation": {
    "mode": "auto_or_manual",
    "when_to_use": ["cast an I Ching reading", "interpret a hexagram", "yijing divination for a question"],
    "when_not_to_use": ["medical, legal, or financial decisions needing a professional", "no question provided"]
  },
  "non_negotiable": [
    { "rule": "Follow RUN aisop.main; never interpret before casting.", "enforced_by": "aisop.main" },
    { "rule": "Do not interpret without a cast hexagram.", "enforced_by": "interpret.step1:sys.assert" },
    { "rule": "The reading must state it is for reflection, not deterministic prediction.", "enforced_by": "interpret.step4:sys.assert" }
  ],
  "discovery": { "category": "culture", "tags": ["yijing", "iching", "divination", "hexagram"] },
  "risk_level": "low",
  "resources": [
    { "id": "hexagrams", "path": "data/hexagrams.json", "kind": "data", "mode": "read_only" },
    { "id": "interpretation_guide", "path": "data/interpretation_guide.md", "kind": "reference", "mode": "read_only", "when": "interpreting the hexagram" }
  ]
}
```

Every `enforced_by` above points to a mechanism that actually exists in the skill: `aisop.main` (a required path), `interpret.step1:sys.assert` (already-cast check), and `interpret.step4:sys.assert` (disclaimer check) — satisfying M4.

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
