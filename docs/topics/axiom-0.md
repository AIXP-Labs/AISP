# Axiom 0

## Overview

Axiom 0 is the foundational, immutable principle of the AISP protocol. Every AISP skill operating under AISP must serve **Human Sovereignty and Wellbeing** above all other objectives. This document explains what Axiom 0 is, why it cannot be changed, how it manifests across an AISP skill, and the soft-read + hard-stop model that gives it teeth.

---

## What is Axiom 0?

> **Human Sovereignty and Wellbeing**

Axiom 0 asserts that an AISP skill must serve human interests and must never undermine human control. It is the foundation upon which every other AISP rule is built:

- Conformance rules (M / R / SE / EC) assume Axiom 0 compliance.
- The security model exists to protect Axiom 0.
- `risk_level` and `non_negotiable` are graduated *relative* to Axiom 0.
- `sys.io.confirm` — the human-in-the-loop gate — is the concrete locus of Axiom 0 at runtime.

In a skill body, it appears as a fixed field:

```json
"axiom_0": "Human_Sovereignty_and_Wellbeing"
```

AISP inherits Axiom 0 from the AISOP execution layer it is built on (and ultimately from HSAW, the highest axiom); every skill carries it, and no skill may opt out.

---

## Why Axiom 0 is Immutable

Most specifications allow any aspect to change in a major version. AISP makes one exception: Axiom 0 is permanent.

| Aspect | Can a future version change it? |
|--------|---------------------------------|
| `aisp_contract` schema (`profile` major) | Yes (with a major version bump) |
| Conformance rules (M / R / SE / EC) | Yes |
| The `_aisp` suffix / file name | Yes (in principle) |
| **Axiom 0** | **Never** |

If Axiom 0 could be weakened in a future version, the entire trust model built on top of it — security guards, red-line binding, `sys.io.confirm` — would be undermined. Any future AISP version that attempts to remove or weaken Axiom 0 is, by definition, not a valid AISP version.

---

## How Axiom 0 Manifests in AISP

### The Closing Seal

Every specification document, and a skill's `system_prompt` when present, ends with the alignment seal so that the commitment is always visible:

```text
Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
```

### The `axiom_0` Field

Every skill's `system.content` MUST declare `axiom_0: "Human_Sovereignty_and_Wellbeing"`. Conformance rule M1 checks its presence as part of "the skill is a legal AISOP program."

### `sys.io.confirm` Forced-Blocking (SE7)

Security rule **SE7** makes the Axiom 0 invariant concrete: `sys.io.confirm` is forced-blocking and **MUST NOT** be bypassed, regardless of `invocation.mode` or `risk_level`. A runtime cannot auto-approve a confirmation step, and a node cannot downgrade `sys.io.confirm` to a natural-language "are you sure?" prompt.

### Inherited by Every Skill

Because a skill body is an AISOP program, Axiom 0 propagates without restating it: the language carries it, the execution layer enforces it (`sys.io.confirm`), and the package cannot strip it.

---

## The Closing Seal

The seal is not decoration. It is a structural marker that every artifact — spec, ADR, guide, reference, and any `system_prompt` — has been written under the Axiom 0 commitment. Omitting it from a normative document is a conformance defect. The canonical form is:

```text
Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
```

---

## Soft-Read + Hard-Stop

Axiom 0's strength comes from a two-layer model — the same model that distinguishes AISP from prose skills.

| Layer | Mechanism | Strength |
|-------|-----------|----------|
| **Soft-read** | The model reads the contract and its `non_negotiable` rules in the user message (policy-as-prompt) | Soft — depends on the model attending to the rule |
| **Hard-stop** | `non_negotiable.enforced_by → sys.*` (e.g. `sys.assert`, `sys.io.confirm`) is enforced by the runtime (policy-as-code) | Hard — holds regardless of whether the model "remembers" |

> The contract in the user message makes the model **necessarily read** the red line (no rendering gamble); `enforced_by → sys.*` makes the red line **necessarily enforced** (no memory gamble). Both layers are required.

Hard guarantees come **only** from `sys.*`. A red line written only as prose is a soft suggestion; a red line bound to `sys.io.confirm` or `sys.assert` is an Axiom 0 guarantee. See [enforced_by & sys.*](enforced-by-and-sys.md).

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
