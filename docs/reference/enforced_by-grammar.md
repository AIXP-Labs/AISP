# enforced_by Grammar Reference

> Complete reference for the `non_negotiable[].enforced_by` binding grammar.
> `enforced_by` is what turns a declared red line into a machine-verifiable guarantee — the AISP differentiator from prose skills.

A `non_negotiable` entry pairs a natural-language `rule` (policy-as-prompt; the model reads it; soft) with an `enforced_by` binding (policy-as-code; the runtime enforces it; hard). **Only `sys.*`-backed bindings are hard guarantees.** Whether the model "remembers" a rule does not affect a `sys.*`-enforced constraint.

---

## The Three Forms

| Form | Meaning | Verification (conformance rule M4) |
|------|---------|------------------------------------|
| `<node>.stepN:<mechanism>` | A `sys.*` mechanism at a specific node and numeric execution step (most precise; recommended) | The named `functions[node][stepN]` exists AND that step begins with `<mechanism>` |
| `aisop.main` | Enforced by graph topology — a required node / branch on the main flow | The required node / branch exists in `aisop.main` |
| `tools` | Enforced by the `tools` allow-list — a capability is not granted | `tools` is restricted AND the runtime truly enforces tool permissions |

> **`tools` caveat.** `enforced_by: tools` is a hard constraint **only when the runtime truly enforces tool permissions**. On a runtime that does not enforce tool permissions, `tools` is merely a declarative constraint and MUST NOT be counted as a hard guarantee. A top-level runtime declaration is an attestation, not independent proof; strict validation requires event-backed trace evidence or provenance-bearing tool capability evidence.

Runtimes and registries MAY publish a tool capability declaration using [`schemas/tool-capabilities-v1.schema.json`](../../schemas/tool-capabilities-v1.schema.json). This lets consumers distinguish hard permission enforcement from advisory tool metadata when the declaration carries usable provenance.

---

## policy-as-prompt vs policy-as-code

| Layer | Carrier | Hardness | Enforced by |
|-------|---------|----------|-------------|
| policy-as-prompt | `rule` (NL), `functions` steps, `constraints` | Soft | The model's adherence |
| policy-as-code | `enforced_by → sys.*`, graph topology, tool allow-list | Hard | The runtime |

The two layers are complementary: the model reads the red line (so it is informed), and `sys.*` enforces it (so it cannot be skipped). Both are required — the contract in the user message makes the model **necessarily read** the rule; `sys.*` makes the rule **necessarily enforced**.

---

## Worked Examples

### Form 1 — `<node>.stepN:<mechanism>` (precise sys.* binding)

From `yijing_aisp`:

```json
{ "rule": "Do not interpret without a cast hexagram.", "enforced_by": "interpret.step1:sys.assert" }
```

Verification: `functions.interpret.step1` exists and is
`"sys.assert('hexagram != null', 'No hexagram has been cast')"` — it begins with `sys.assert`. ✓

```json
{ "rule": "The reading must state it is for reflection, not deterministic prediction.", "enforced_by": "interpret.step4:sys.assert" }
```

Verification: `functions.interpret.step4` exists and is
`"sys.assert('reading.disclaimer != null', 'Reading must state it is for reflection…')"`. ✓

From `stock_analysis_aisp`:

```json
{ "rule": "Every report must carry a not-advice disclaimer.", "enforced_by": "report.step2:sys.assert" }
```

Verification: `functions.report.step2` exists and begins with `sys.assert` (asserts the disclaimer is present). ✓

### Form 2 — `aisop.main` (topology binding)

From `yijing_aisp`:

```json
{ "rule": "Follow RUN aisop.main; never interpret before casting.", "enforced_by": "aisop.main" }
```

Verification: the required ordering exists in the graph — `clarify --> cast --> interpret` — so `interpret` cannot be reached before `cast`. ✓

### Form 3 — `tools` (allow-list binding)

From `stock_analysis_aisp`:

```json
{ "rule": "Never place trades; analysis only.", "enforced_by": "tools" }
```

Verification: the `tools` allow-list does not include any trade-execution capability (e.g. no `broker` / order-placement tool). This is hard **only if** the runtime enforces tool permissions; otherwise it is declarative. ✓ (conditional)

---

## How M4 Machine-Verifies a Binding

Conformance rule **M4** (`FAIL`) checks every `non_negotiable[].enforced_by`:

1. **Parse the form.** Match against `<node>.stepN:<mechanism>`, `aisop.main`, or `tools`.
2. **Path form** → assert `functions[node][stepN]` exists, `stepN` is a numeric execution step such as `step1`, and the step string begins with `<mechanism>`.
3. **`aisop.main` form** → assert the required node / branch exists in the main graph.
4. **`tools` form** → assert `tools` is restricted; record that hardness is conditional on runtime permission enforcement.
5. **Phantom guarantee** → if the binding points to a node / numeric execution step / mechanism that does not exist, or to metadata such as `step_note`, emit `AISP_E_M4_PHANTOM` (FAIL). A red line that claims a guarantee it cannot deliver is worse than no red line.

---

## Common Mistakes

| Mistake | Why it fails |
|---------|--------------|
| `enforced_by` points to a non-existent step, or to metadata such as `step_note` | Phantom guarantee — M4 FAIL (`AISP_E_M4_PHANTOM`) |
| `enforced_by: "interpret.step3"` (no mechanism) | Missing `:<mechanism>` — the binding is not verifiable (M4 FAIL `AISP_E_M4_NO_MECHANISM`) |
| Naming the field `assert` | `assert` is `sys.assert` (deterministic check); the declaration field is `non_negotiable` |
| Counting `enforced_by: tools` as hard on a permission-free runtime | `tools` is hard only when the runtime enforces permissions |
| Relying on the `rule` prose alone | NL rules are policy-as-prompt (soft); hardness needs `sys.*` |

---

Align Axiom 0: Human Sovereignty and Wellbeing | Protocol: AISP | Execution: AISOP | Executor: SoulBot
