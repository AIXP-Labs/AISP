# enforced_by & sys.*

> AISP Protocol — Conceptual Guide
> Classification: Enforcement

A red line is only as strong as what enforces it. AISP binds each `non_negotiable` rule to a real mechanism via `enforced_by`, and draws a hard line between rules that are *read* (soft) and rules that are *enforced* (hard). This document explains the `enforced_by` grammar, the `sys.*` mechanisms behind it, and why only `sys.*` is a guarantee.

---

## Policy-as-Prompt vs Policy-as-Code

> A prose rule asks the model to comply. A `sys.*` rule makes the runtime enforce it.

| | policy-as-prompt | policy-as-code |
|---|------------------|----------------|
| Where | The NL `rule` text in the contract / nodes | `enforced_by → sys.*` |
| Who decides | The LLM, by reading | The runtime, deterministically |
| Strength | **Soft** — depends on the model attending | **Hard** — holds regardless of model memory |
| Verifiable | No | Yes (conformance rule M4) |

> **Hard guarantees come only from `sys.*`.** Whether the model "remembers" a red line does not affect a hard constraint. A rule with no `sys.*` binding is guidance, not a guarantee.

---

## The enforced_by Grammar

Every `non_negotiable[].enforced_by` MUST point to a mechanism that **actually exists** in the skill.

| Form | Meaning | Verification |
|------|---------|--------------|
| `<node>.stepN:<mechanism>` | A `sys.*` at a specific numeric execution step (most precise, recommended), e.g. `interpret.step1:sys.assert` | The node and numeric `stepN` exist, and that step begins with the mechanism |
| `aisop.main` | Enforced by graph topology (a required node/branch) | The required node/branch exists |
| `tools` | Enforced by the `tools` allow-list (a capability is not granted) | `tools` is restricted **and** the runtime truly enforces tool permissions |

---

## The sys.* Mechanisms

The mechanisms behind a hard binding are provided by AISOP and handled deterministically by the runtime — not by LLM reasoning.

| Mechanism | What it does | Typical use |
|-----------|--------------|-------------|
| `sys.assert(cond, msg)` | Deterministic hard check; aborts the step on failure | Preconditions / postconditions (e.g. "a hexagram was cast", "a disclaimer is present") |
| `sys.io.confirm(...)` | Forced-blocking human-in-the-loop gate (Axiom 0; SE7) | Dangerous or irreversible actions |
| `tools` allow-list | Capability not granted ⇒ action impossible | "never place trades" when no trading tool is declared |

Example bindings from `yijing_aisp`:

```text
"Never interpret before casting."                          → aisop.main                    (topology)
"Do not interpret without a cast hexagram."                → interpret.step1:sys.assert    (precondition)
"Reading must state it is for reflection, not prediction." → interpret.step4:sys.assert    (postcondition)
```

---

## The `tools` Caveat

`enforced_by: tools` is a hard constraint **only when the runtime truly enforces tool permissions**. If a runtime does not enforce tool permissions, `tools` is merely a declarative constraint and **MUST NOT** be counted as a hard guarantee.

```text
"never place trades", enforced_by: tools
  → hard  IF the runtime denies any non-declared tool
  → soft  IF the runtime does not enforce tool permissions
```

A skill author should prefer `<node>.stepN:sys.*` for guarantees that must hold on any conformant runtime, and reserve `tools` for capability-absence guarantees.

A runtime's top-level `tool_enforcement: "hard"` declaration is only an attestation. For strict validation or release gates, `tools` hardness needs event-backed runtime trace evidence or provenance-bearing tool capability evidence.

---

## non_negotiable, Not assert

The declarative red-line field is named `non_negotiable`, **not** `assert`. The reason is semantic:

```text
non_negotiable.rule   = a natural-language declaration (soft until bound)
sys.assert(...)       = a deterministic hard check that aborts on failure (already hard)
```

Naming the declarative field `assert` would falsely imply that the *declaration* is itself a hard check. Hardness comes from `enforced_by → sys.*`, not from the field name.

---

## Machine Verification (M4)

A validator can mechanically check every binding:

- For `<node>.stepN:<mechanism>`: assert `functions[node][stepN]` exists as a numeric execution step and begins with that mechanism.
- For `aisop.main`: assert the required node/branch exists in the graph.
- For `tools`: assert `tools` is restricted (and note the runtime caveat above).

A binding that points to a non-existent node, non-existent numeric step, metadata field such as `step_note`, or missing mechanism is a **phantom guarantee** and fails M4.

---

## Correct vs Incorrect

❌ A red line with no enforcement (prose only):

```json
{ "rule": "Always confirm before deleting." }
```

✓ Bound to a forced-blocking gate:

```json
{ "rule": "Always confirm before deleting.", "enforced_by": "delete.step2:sys.io.confirm" }
```

❌ `enforced_by` points to a step that does not exist, or to metadata such as `step_note`:

```json
{ "rule": "Validate input.", "enforced_by": "validate.step1:sys.assert" }
// but functions has no "validate" node → fails M4 (phantom guarantee)
```

✓ Points to a real step:

```json
{ "rule": "Validate input.", "enforced_by": "intake.step1:sys.assert" }
// functions.intake.step1 begins with sys.assert(...)
```

❌ Naming the declarative field `assert`:

```json
{ "assert": "Never exfiltrate data." }
```

✓ Use `non_negotiable` + a real binding:

```json
{ "rule": "Never exfiltrate data.", "enforced_by": "tools" }
```

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
