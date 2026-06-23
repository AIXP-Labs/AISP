# Resources

A skill rarely lives on logic alone — it carries data tables, reference guides, templates, and scripts. AISP treats these as **resources**: declared once in the contract's inventory, and used on demand by the execution nodes. This document explains the resource model, its fields, and the security rules that govern it.

---

## Introduction

The governing principle is a clean split:

> **`resources` = inventory. `functions` = usage.**

The contract's `resources` array declares *what exists, where, what kind, and read-or-execute*. The `functions` nodes actually *use* a resource via `sys.io.read` (read) or `sys.run` (execute). The inventory is the single source of truth for "what is a resource"; a file present in the folder but absent from `resources` is **unknown**, and a validator SHOULD warn.

---

## Resource Fields

| Sub-field | Required | Description |
|-----------|----------|-------------|
| `id` | MUST | Resource identifier (referenced conceptually by nodes) |
| `path` | MUST | Relative path; `scope:skill` relative to the skill folder, `scope:shared` relative to `_shared/` |
| `kind` | MUST | **Open vocabulary**: data / script / reference / asset / template / … |
| `mode` | MUST | **Controlled enum**: `read_only` / `execute_only` / `read_and_execute` |
| `when` | MAY | When to load (e.g. "interpreting the hexagram") |
| `scope` | MAY | `skill` (default) / `shared` |
| `requires_tools` | MAY | Tools a script needs (least authority) |

Example:

```json
"resources": [
  { "id": "hexagrams", "path": "data/hexagrams.json", "kind": "data", "mode": "read_only" },
  { "id": "interpretation_guide", "path": "data/interpretation_guide.md", "kind": "reference", "mode": "read_only", "when": "interpreting the hexagram" },
  { "id": "fetch_quotes", "path": "scripts/fetch_quotes.py", "kind": "script", "mode": "execute_only", "requires_tools": ["shell"] },
  { "id": "finance_terms", "path": "finance_terms.md", "kind": "reference", "mode": "read_only", "scope": "shared" }
]
```

---

## Custom Layout

AISP does **not** force a fixed subfolder structure. A skill may organize resources however it likes — `data/`, `scripts/`, `assets/`, or anything else — because the layout is described by the `resources` declarations, not by convention. The only firm rule is that everything used at runtime must be declared.

---

## `_shared/` Scope

Resources common to several skills live in `aisp/_shared/`. Because `_shared/` has no `_aisp` suffix, it is not a skill folder and is naturally excluded from the discovery glob `aisp/*_aisp/aisp.aisop.json`.

| `scope` | Path resolves relative to |
|---------|---------------------------|
| `skill` (default) | The skill's own folder |
| `shared` | `aisp/_shared/` |

---

## `kind` (Open) vs `mode` (Enum)

A common mistake is to reverse these.

| Field | Vocabulary | Why |
|-------|-----------|-----|
| `kind` | **Open** — data / script / reference / asset / template / … | Descriptive; new kinds may appear over time |
| `mode` | **Closed enum** — `read_only` / `execute_only` / `read_and_execute` | The security gate; behavior depends on the exact value |

`mode` gates behavior:

- `read_only` resources are **not executed**.
- `execute_only` scripts are **not injected in full** into the model context.
- `read_and_execute` permits both.

---

## Security Rules

Resources are the attack surface. The following rules apply (see [Security Model](security-model.md)).

- **Path confinement (M5 / SE1)**: each `path` MUST be relative, confined to the skill folder or `_shared/`, with no `../` escape and no absolute paths.
- **Remote URL gate (SE2)**: remote URLs are disabled by default and require a `sys.io.confirm` gate before access.
- **Least authority (SE4)**: a `kind:script` resource SHOULD declare `requires_tools` listing only the tools it needs; dangerous commands trigger `sys.io.confirm`.
- **Undeclared-file warning (ST2)**: any file in the folder not declared in `resources` is unknown — a validator SHOULD warn.

---

## Loading on Demand (L3)

Resources are not loaded up front. In progressive disclosure, the contract's inventory is L1/L2 metadata, and the actual bytes are loaded only at **L3** — when a node reads or runs the resource, subject to `mode` and AISP's fixed `loading_mode: "node"`. This is a loading strategy, not a safety or trust proof.

```text
L1  index:        aisp_list.json knows the skill exists
L2  instructions: the full aisp.aisop.json (contract + graph + functions) is loaded
L3  resources:    a node does sys.io.read('data/hexagrams.json') only when it needs the table
```

This keeps the initial footprint small and ensures a resource is touched only when, and how, the contract declares.

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
