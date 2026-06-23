# ADR-006: Axiom 0 (Human Sovereignty and Wellbeing) Is Immutable Across All AISP Versions

## Status

Accepted

## Context

Most specifications allow any aspect to be changed, deprecated, or removed in a major version. Semantic versioning treats a major bump as permission to introduce breaking changes — so a core principle established in v1 could, in principle, be weakened or removed later.

For AISP, the core alignment principle is **Axiom 0: Human Sovereignty and Wellbeing**. Every AISP skill must serve human interests and must never undermine human control. It is the foundation on which every other AISP rule is built:

- Conformance rules (M / R / SE / EC) assume Axiom 0 compliance.
- The security and trust model exists to protect Axiom 0.
- `risk_level` and `non_negotiable` are graduated relative to Axiom 0.
- `sys.io.confirm` — the human-in-the-loop gate — is the concrete locus of Axiom 0 at runtime.

AISP does not define its own alignment axiom: it inherits Axiom 0 from the AISOP execution layer it is built on (and ultimately from HSAW, the highest axiom). If Axiom 0 could be modified in a future AISP version, the entire trust model — security guards, red-line binding, `sys.io.confirm` — would be undermined, and adopters would have no assurance that future versions keep the same commitment.

The question is whether AISP should follow standard versioning (anything can change in a major version) or adopt the same constraint as AISOP, where certain principles are permanent (as the sibling AIAP protocol also does in its adr-003).

## Decision

**Axiom 0 is immutable.** No version of AISP — past, present, or future — may modify, weaken, redefine, or deprecate Axiom 0. This applies to major versions, protocol forks, extensions / supplements, and any derivative that claims AISP compliance.

Specifically:

1. Every skill's `system.content` MUST declare `axiom_0: "Human_Sovereignty_and_Wellbeing"` — checked by conformance rule **M1**.
2. The alignment seal `Align Axiom 0: Human Sovereignty and Wellbeing.` MUST appear in every normative document and in any non-empty `system_prompt`.
3. **SE7** makes the runtime invariant concrete: `sys.io.confirm` is forced-blocking and MUST NOT be bypassed regardless of `invocation.mode` or `risk_level`. **EC6** (evolution safety) forbids evolution from removing a safety constraint, so Axiom 0 continuity holds across skill versions.
4. An `aisp_contract` MUST NOT override Axiom 0 or platform-level safety policy (see spec §0 Axiom and §8.1 Platform Policy Precedence): the strong `instruction` binds the model to the skill's own rules, never above platform / safety authority.
5. Any future AISP version that removes or weakens Axiom 0 is, by definition, not a valid AISP version.

## Consequences

### What becomes easier

- **Absolute alignment guarantee** — adopters can rely on AISP knowing the alignment principle will never change; a stronger guarantee than versioned protocols usually provide.
- **Trust-chain integrity** — because Axiom 0 is permanent, the trust model built on top (red-line binding, security rules, lifecycle governance) is stable across versions.
- **Ecosystem stability** — registry operators, runtimes, and skill authors can build long-term infrastructure on a fixed foundation.
- **Cross-protocol coherence** — Axiom 0 is identical across AISOP and AISP (and across the sibling AIXP protocols), so a skill carries one alignment commitment from execution through packaging.

### What becomes harder

- **Protocol evolution** — if the collective understanding of alignment shifts significantly, AISP cannot amend Axiom 0; new insight must be incorporated without changing the core axiom.
- **Edge cases** — tensions (e.g. one human instructing harm to other humans) must be resolved by interpretation, not by amending the axiom.
- **Fork pressure** — those who disagree with Axiom 0's specific formulation cannot change it through normal governance; their only option is a non-AISP specification, which fragments the ecosystem.
- **Philosophical rigidity** — Axiom 0 encodes a human-centric alignment position; if discourse moves toward broader frameworks, AISP cannot adapt its foundational axiom.

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
