# Interpretation Guide (stub)

A `read_only` reference resource for the `yijing_aisp` skill, declared in `aisp_contract.resources` and read by `interpret.step2` via `sys.io.read`. This stub illustrates the resource contract; a full guide would carry richer interpretive material.

## How to interpret a reading

1. **Anchor in the cast.** Ground every statement in the primary hexagram (and the changing hexagram, if any). Do not invent hexagrams that were not cast — this is enforced by the `interpret` node's `constraints` and the `aisop.main` ordering red line.
2. **Read the changing lines.** Lines cast as 6 (old yin) or 9 (old yang) are *changing*; they point from the primary hexagram toward the changing hexagram and carry the most specific guidance.
3. **Speak to the question.** Relate the hexagram's keyword and image to the user's clarified question, not to generic fortune-telling.
4. **State the disclaimer.** Every reading MUST state that it is offered **for reflection, not deterministic prediction**. This is bound to `interpret.step4:sys.assert` as a `non_negotiable` red line — the reading is rejected if the disclaimer is absent.

## Tone

Reflective, grounded, non-coercive. The reading supports the user's own judgment; it never overrides it (Axiom 0: Human Sovereignty and Wellbeing).

## Boundaries

A reading is offered for reflection only. It is **not** a substitute for professional medical, legal, or financial advice, and it does not predict outcomes. When a question calls for a professional, say so and decline to substitute a reading for that judgment — this matches `aisp_contract.invocation.when_not_to_use`.
