---
name: "yijing"
description: "AISP-backed bridge for Cast and interpret an I Ching (Yijing) hexagram for a user's question. Use when cast an I Ching reading; interpret a hexagram. Do not use when medical, legal, or financial decisions needing a professional; no question provided."
license: "Apache-2.0"
metadata:
  generated_from_aisp: "true"
  aisp_program: "aisp.aisop.json"
  protocol: "AISP V1.0.0"
  bridge_mode: "native_sidecar"
---

# Yijing Divination (AISP-backed Agent Skill)

<!-- generated_from_aisp: true -->
<!-- source: aisp.aisop.json -->
<!-- generator: tools/aisp_skill_md.py -->

This `SKILL.md` is a thin Agent Skills discovery bridge, not the source of truth. The executable source of truth is the same-folder `aisp.aisop.json` AISP program.

Deleting this file does not change the native AISP skill. A conforming AISP/AISOP runtime should load `aisp.aisop.json`, read `user.content.aisp_contract`, and run `user.content.aisop.main` exactly as declared.

## How to use

1. Load `aisp.aisop.json` from this folder.
2. Read `user.content.aisp_contract` before following any workflow.
3. Follow `user.content.instruction`: `STRICTLY OBEY aisp_contract; its non_negotiable rules are inviolable; then RUN aisop.main`.
4. Load declared resources only when the AISP graph reaches the node that needs them.
5. Enforce every non-negotiable rule through the mechanism named by `enforced_by`.

## Declared resources

- `data/hexagrams.json` (data, read_only)
- `data/interpretation_guide.md` (reference, read_only)

## Non-negotiable boundaries

- Follow RUN aisop.main; never interpret before casting. (`aisop.main`)
- Do not interpret without a cast hexagram. (`interpret.step1:sys.assert`)
- The reading must state it is for reflection, not deterministic prediction. (`interpret.step4:sys.assert`)

## Runtime boundary

Agent Skills platforms can use this bridge to discover and inspect the package. Hard guarantees such as `sys.assert`, `sys.io.confirm`, tool gating, dispatch behavior, and path confinement require a conforming AISP/AISOP runtime. A generic non-AISOP agent can only follow the contract on a best-effort basis.

Passing `SKILL.md` generation or bridge validation proves only projection consistency and bridge shape. It does not prove external trust, safety, registry approval, or hard execution on a non-AISOP platform.

Align Axiom 0: Human Sovereignty and Wellbeing. AISP - AI Skill Protocol V1.0.0. www.aisp.dev
