# ADR-004: Red Lines Bind to Enforcement via `enforced_by` (Policy-as-Code), Not Prose

## Status

Accepted

## Context

Agent Skills (`SKILL.md`) express their rules as prose: "always confirm before deleting," "never give financial advice." Prose rules are policy-as-prompt — the model is asked to follow them, but nothing stops it if it does not. In a probabilistic system, a prose rule is a hope, not a guarantee.

AISP claims to be "executable + governable." For that claim to be meaningful, a skill's red lines must be more than prose. The question: how does a declared red line become a *real* guarantee that a machine can verify, without pretending that every rule can be made hard?

The relevant background: AISOP already provides a deterministic `sys.*` family (`sys.assert`, `sys.io.confirm`, etc.) handled by the runtime, not by LLM reasoning. AISP can bind a declared rule to one of these mechanisms.

## Decision

**Each `non_negotiable` rule binds a natural-language declaration (`rule`) to a real enforcement mechanism (`enforced_by`). Only `sys.*`-backed bindings are hard guarantees.**

The `enforced_by` grammar (each form MUST point to a mechanism that actually exists in the skill):

1. `<node>.stepN:<mechanism>` — a `sys.*` at a specific numeric execution step (most precise, recommended), e.g. `interpret.step1:sys.assert`. Verified: the node and numeric step exist and that step begins with the mechanism. Metadata keys such as `step_note` do not count.
2. `aisop.main` — enforced by graph topology (a required node/branch). Verified: the required node/branch exists.
3. `tools` — enforced by the `tools` allow-list. **Hard only when the runtime truly enforces tool permissions**; otherwise declarative only and MUST NOT be counted as a hard guarantee. Runtime declarations are attestations; strict gates need event-backed trace evidence or provenance-bearing tool capability evidence.

The distinction is explicit: the NL `rule` is **policy-as-prompt** (soft; the model reads it); `enforced_by → sys.*` is **policy-as-code** (hard; the runtime enforces it regardless of whether the model "remembers"). A declarative rule field is named `non_negotiable`, *not* `assert` — because `assert` is already `sys.assert`, a deterministic hard check, which would be the opposite semantics.

This "declaration ↔ enforcement, machine-verifiable" binding is AISP's core differentiator from prose skills.

## Consequences

### What becomes easier

- **Real guarantees**: a red line backed by `sys.assert` / `sys.io.confirm` is enforced by the runtime, not by model goodwill.
- **Machine verification**: a validator (core M4) can mechanically check that every `enforced_by` points to an existing node, numeric execution step, and mechanism — catching phantom guarantees.
- **Honest soft/hard split**: rules that cannot (yet) be made hard remain visible as policy-as-prompt, without being misrepresented as guarantees.
- **Auditability**: a registry or generator can report how many red lines are hard-bound versus soft.

### What becomes harder

- **Authoring effort**: writing a red line now means also wiring a real `sys.*` step, not just stating a sentence.
- **`tools` caveat**: `enforced_by: tools` is only as hard as the runtime's permission enforcement; on a runtime that does not enforce tool permissions, it is merely declarative — a subtlety implementers must respect.
- **No prose shortcuts**: a rule with no enforcement mechanism cannot claim to be `non_negotiable`; it is just guidance in `functions`.

### Relationship to other ADRs

- **ADR-002**: this ADR governs the *enforcement* side of the contract; ADR-002 places the *declaration* in the user message.
- **ADR-001**: the `sys.*` mechanisms that make a binding hard are provided by AISOP — AISP reuses, rather than rebuilds, the enforcement primitives.

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
