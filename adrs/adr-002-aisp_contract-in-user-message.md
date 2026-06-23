# ADR-002: The Skill Contract Lives in the User Message as a Real Object

## Status

Accepted

## Context

A skill needs a contract: the metadata a consumer must know *before and during* execution — when to trigger it, its red lines, its discovery tags, its risk, its resource inventory. Earlier drafts (the `06`–`12` documents) struggled with *where* and *in what form* this contract should live. Several options were tried:

1. **Inside `system_prompt` as a JSON-in-string.** This forced escaping, a string/object dual form, and a "wire vs display" split — brittle and machine-hostile.
2. **As a new field on `system.content`** (`system.content.aisp_contract`, a real object). Better — no escaping — but `system.content` is program-identity metadata, and there was no guarantee the model would actually *read* the contract this turn without the runtime rendering it.
3. **As a real object on `user.content`** (`user.content.aisp_contract`), alongside `instruction` / `user_input` / `aisop` / `functions`, with a strong `instruction` commanding obedience.

The core question: how do we make the model **necessarily read** the contract (not gamble on runtime rendering) while keeping it a clean, machine-friendly object?

## Decision

**The skill contract is `user.content.aisp_contract` — a real JSON object in the user message.**

1. It is a real object — no escaping, no string/object dual form, no JSON-in-string.
2. It lives in the **user message** because that is the model's live content this turn: the model reads it directly (like an Agent Skills `SKILL.md` loaded into context), without depending on a separate runtime "render" step.
3. The `instruction` is the strong directive `"STRICTLY OBEY aisp_contract; its non_negotiable rules are inviolable; then RUN aisop.main"` — it names the contract for obedience.
4. `system_prompt` returns to its AISOP meaning (it MAY be empty; it does not carry the contract). Program identity stays in `system.content` (`summary` / `description` / `version` / `license`).
5. This is allowed without changing AISOP Core because `aisp_contract` is an AISP-owned field and AISOP tolerates unknown keys on `user.content` (open-world validation, R4). An AISOP runtime ignores it; an AISP-aware runtime reads it.

The one-line principle: *the contract in the user message makes the model necessarily read it (no rendering gamble); `enforced_by → sys.*` makes the red line necessarily enforced (no memory gamble). Both layers are required.*

## Consequences

### What becomes easier

- **No JSON-in-string**: the contract is a clean object — directly parseable by the discovery script, the registry, and any AISP-aware runtime.
- **No rendering gamble**: because the contract is in the user message, the model reads it directly; the runtime does not need a special render step.
- **Clean `system_prompt`**: `system_prompt` returns to its proper role (behavioral guidance or empty), with no contract baggage.
- **Soft-read + hard-stop layering**: the model reads the red lines (soft) and `sys.*` enforces them (hard) — independent of whether the model "remembers."

### What becomes harder

- **One more field**: it is no longer "zero new keys" — `aisp_contract` is an extra key. This relies on AISOP's open-world tolerance; a closed-world strict validator that rejects unknown keys would reject AISP files.
- **Placement discipline**: authors must resist duplicating Tier A content (role / principles / failure / output) into the contract; the contract is lean metadata only.
- **Two-message shape required**: the skill file must be a 2-message array (system + user), not a single object, so that the contract can live on `user.content`.

### Relationship to other ADRs

- **ADR-001**: the open-world dependency this decision relies on is a direct consequence of building on AISOP rather than rebuilding the engine.
- **ADR-004**: the contract's `non_negotiable.enforced_by` is the policy-as-code binding; this ADR places the *declaration*, ADR-004 governs the *enforcement*.

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
