# aisp_contract Field Reference

> Complete field reference for the skill contract, `user.content.aisp_contract`.
> The contract is a **real JSON object** located in the user message — never a JSON-in-string, never in `system_prompt`.

The skill contract is the lean metadata tier (Tier S). It holds only what the execution tier cannot express, or what a consumer needs to know **before and during** invocation: when to trigger, the red lines, discovery tags, risk, and the resource inventory. Everything else — role, principles, knowledge, failure handling, structured output — lives in `functions` / `sys.*` (Tier A).

Because the contract sits in the user message, the model reads it directly this turn. The sibling `instruction` (`"STRICTLY OBEY aisp_contract; …; then RUN aisop.main"`) names it for obedience.

> **Machine-readable schema.** This contract is formally specified by [`schemas/aisp-contract-v1.schema.json`](../../schemas/aisp-contract-v1.schema.json) (JSON Schema draft 2020-12). It declares `profile` / `invocation` / `non_negotiable` as required, enforces the `profile` `aisp.skill.` prefix and the `enforced_by` grammar, and constrains the `risk_level` and resource `mode` / `scope` enums plus the optional resource `sha256` field.

---

## Top-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `profile` | string | MUST | Contract schema marker — `"aisp.skill.v1"`; detected by the `aisp.skill.` prefix |
| `invocation` | object | MUST | Triggering metadata (before-execution) |
| `non_negotiable` | array | MUST | Red lines bound to real enforcement mechanisms |
| `discovery` | object | SHOULD | Registry / routing metadata |
| `risk_level` | string | SHOULD | Single risk grade |
| `resources` | array | MAY | Resource inventory (declared, not used here) |

> **Shape rule.** `aisp_contract` is a real object. It MUST NOT appear as an escaped JSON string, and MUST NOT be carried by `system_prompt`. It is an AISP-owned key tolerated by AISOP's open-world validation (R4).

---

## profile

| Constraint | Value |
|------------|-------|
| Required | MUST |
| Type | string |
| Value | `"aisp.skill.v1"` |
| Detection | A runtime identifies an AISP skill when `profile` starts with `aisp.skill.` |
| Compatibility | Only a major change (`v1` → `v2`) is incompatible |

---

## invocation

Triggering is decided **before** execution ("should this skill start at all?"), which an AISOP flow cannot express — so it lives in the contract.

| Sub-field | Type | Required | Description |
|-----------|------|----------|-------------|
| `mode` | string | SHOULD | `"manual_only"` \| `"auto_or_manual"` \| `"auto_preferred"` \| `"internal_only"` |
| `when_to_use` | array of strings | MUST | Structured, routable trigger conditions |
| `when_not_to_use` | array of strings | MUST | Disabling boundary; **wins over `when_to_use` on conflict** |

**Routing logic**: does the request match `when_to_use`? does it hit `when_not_to_use`? On conflict, `when_not_to_use` wins; if uncertain, ask the user. `when_to_use` SHOULD NOT be over-broad.

```json
"invocation": {
  "mode": "auto_or_manual",
  "when_to_use": ["cast an I Ching reading", "interpret a hexagram"],
  "when_not_to_use": ["medical, legal, or financial decisions needing a professional", "no question provided"]
}
```

---

## non_negotiable

A red line = a natural-language declaration (`rule`) bound to a real enforcement mechanism (`enforced_by`). This declaration ↔ enforcement binding is AISP's core differentiator from prose skills.

| Sub-field | Type | Required | Description |
|-----------|------|----------|-------------|
| `rule` | string (NL) | MUST | The red line, stated in natural language (policy-as-prompt; soft) |
| `enforced_by` | string | MUST | Binding to a real mechanism (policy-as-code; hard when `sys.*`-backed) |

See the [enforced_by Grammar](enforced_by-grammar.md) reference for the full binding grammar. Each `enforced_by` MUST point to a mechanism that actually exists in the skill (conformance rule **M4**). Step bindings use numeric execution steps (`step1`, `step2`, ...); metadata keys such as `step_note` do not count.

```json
"non_negotiable": [
  { "rule": "Follow RUN aisop.main; never interpret before casting.", "enforced_by": "aisop.main" },
  { "rule": "Do not interpret without a cast hexagram.", "enforced_by": "interpret.step1:sys.assert" },
  { "rule": "The reading must state it is for reflection, not deterministic prediction.", "enforced_by": "interpret.step4:sys.assert" }
]
```

> Do NOT name a declarative rule field `assert` — `assert` is already `sys.assert`, a deterministic hard check (opposite semantics). Hardness comes from `enforced_by → sys.*`.

---

## discovery

| Sub-field | Type | Required | Description |
|-----------|------|----------|-------------|
| `category` | string | SHOULD | Top-level category (registry / routing) |
| `tags` | array of strings | SHOULD | Tag array (registry search) |

Used by `aisp_list.json`, the registry, and routing. May be omitted when there is no registry.

```json
"discovery": { "category": "culture", "tags": ["yijing", "iching", "divination", "hexagram"] }
```

---

## risk_level

A single risk grade for trust / registry. Fine-grained governance comes from `sys.*` + `tools`.

| Value | Meaning |
|-------|---------|
| `low` | Read-only / analysis |
| `medium` | Writes locally |
| `high` | Delete / deploy / exfiltrate |
| `critical` | Mandatory human review or no autonomy |

**Semantic definitions:**

- **low** = read-only analysis or generation.
- **medium** = local file writes, local scripts, non-destructive changes.
- **high** = deletion, deployment, external sending, credentials, production impact.
- **critical** = legal / medical / financial / physical-safety or irreversible high-impact action.

> `risk_level` is routing/governance metadata, NOT a hard enforcement mechanism — enforcement is via `sys.io.confirm` / `sys.assert` / tools / runtime policy.

---

## resources

**`resources` = inventory; `functions` = usage.** The field declares what exists, where, what kind, and whether it is read or executed; nodes actually use resources via `sys.io.read` / `sys.run`.

| Sub-field | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | MUST | Resource identifier |
| `path` | string | MUST | Relative path. `scope:skill` is relative to the skill folder; `scope:shared` is relative to `_shared/`. No `../` escape (M5 / SE1). |
| `kind` | string | MUST | **Open vocabulary**: `data` / `script` / `reference` / `asset` / `template` / … |
| `mode` | string | MUST | **Controlled enum**: `read_only` / `execute_only` / `read_and_execute` (gates behavior) |
| `when` | string | MAY | When to load |
| `scope` | string | MAY | `skill` (default) / `shared` |
| `sha256` | string | MAY | Content hash for supply-chain integrity |
| `requires_tools` | array | MAY | Tools a script needs (least authority) |

> Note the asymmetry: `kind` is an **open vocabulary** (extend freely), while `mode` is a **closed enum** (the security gate). A file present in the folder but **not** declared in `resources` is an unknown surface — a validator SHOULD warn (threat ST2).

> **Resource integrity (`sha256`).** Resource entries SHOULD include `sha256` when distributed through a registry (supply-chain integrity). It is OPTIONAL and omitted from the in-repo example skills to keep them clean; a registry records and verifies it at publication time (`resources_sha256`).

```json
"resources": [
  { "id": "hexagrams", "path": "data/hexagrams.json", "kind": "data", "mode": "read_only" },
  { "id": "interpretation_guide", "path": "data/interpretation_guide.md", "kind": "reference", "mode": "read_only", "when": "interpreting the hexagram" },
  { "id": "valuation", "path": "scripts/valuation.py", "kind": "script", "mode": "execute_only", "requires_tools": ["shell"] },
  { "id": "finance_terms", "path": "finance_terms.md", "kind": "reference", "mode": "read_only", "scope": "shared" }
]
```

---

Align Axiom 0: Human Sovereignty and Wellbeing | Protocol: AISP | Execution: AISOP | Executor: SoulBot
