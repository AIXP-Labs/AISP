---
name: "stock-analysis"
description: "AISP-backed bridge for Analyze a stock's recent fundamentals and produce a written, not-advice analysis report. Use when analyze a stock or ticker; summarize a company's recent fundamentals. Do not use when placing or executing trades; personalized investment advice requiring a licensed advisor."
license: "Apache-2.0"
metadata:
  generated_from_aisp: "true"
  aisp_program: "aisp.aisop.json"
  protocol: "AISP V1.0.0"
  bridge_mode: "native_sidecar"
---

# Stock Analysis (AISP-backed Agent Skill)

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

- `data/sample_prices.csv` (data, read_only)
- `scripts/indicators.py` (script, execute_only)
- `finance_terms.md` (reference, read_only)
- `evals/runtime-traces/hard-pass.json` (eval, read_only)

## Non-negotiable boundaries

- Follow RUN aisop.main; analyze only after loading data. (`aisop.main`)
- Never place, execute, or recommend specific trades. The skill has no trading capability. (`tools`)
- Do not analyze without loaded market data. (`analyze.step1:sys.assert`)
- The report must state it is informational only and not financial advice. (`report.step2:sys.assert`)

## Runtime boundary

Agent Skills platforms can use this bridge to discover and inspect the package. Hard guarantees such as `sys.assert`, `sys.io.confirm`, tool gating, dispatch behavior, and path confinement require a conforming AISP/AISOP runtime. A generic non-AISOP agent can only follow the contract on a best-effort basis.

Passing `SKILL.md` generation or bridge validation proves only projection consistency and bridge shape. It does not prove external trust, safety, registry approval, or hard execution on a non-AISOP platform.

Align Axiom 0: Human Sovereignty and Wellbeing. AISP - AI Skill Protocol V1.0.0. www.aisp.dev
