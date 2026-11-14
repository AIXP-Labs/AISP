<!-- generated_from_aisp: true -->
<!-- source: aisp.aisop.json -->
<!-- generator: tools/aisp_readme.py -->

# Stock Analysis

This README is a deterministic projection of `aisp.aisop.json`. The contract remains the source of truth.

## Identity

| Field | Value |
| --- | --- |
| Skill ID | `stock_analysis_aisp` |
| Version | `1.0.0` |
| Protocol | `AISP V1.0.0` |
| License | `Apache-2.0` |
| Risk Level | `medium` |
| Category | finance |
| Tags | stocks, analysis, fundamentals, report |

## Purpose

Analyze a stock's recent fundamentals and produce a written, not-advice analysis report.

## When To Use

- analyze a stock or ticker
- summarize a company's recent fundamentals
- produce a written stock analysis report

## When Not To Use

- placing or executing trades
- personalized investment advice requiring a licensed advisor
- no ticker provided

## How To Run

This skill MUST run through a conforming AISP/AISOP executor (SoulRun by default; other conforming executors are allowed). Without an available executor, stop rather than executing or continuing the skill yourself.

Through the executor's regular interface:

1. Load `aisp.aisop.json`.
2. Read `user.content.aisp_contract` before execution.
3. Run `user.content.aisop.main` exactly as declared.
4. Enforce every `non_negotiable` rule and every referenced `sys.*` mechanism.
5. Treat `sys.io.confirm` and other human-confirmation gates as blocking controls.

With an Agent Skills host:

- Treat this README as bootstrap guidance only.
- Verify external provenance or obtain explicit human approval before executing an untrusted package.
- Use the same-folder `SKILL.md` compatibility interface to hand execution to the executor; do not treat this README as authoritative.
- Ask the user before installing an executor. Before installation, that confirmation depends on the host's controls, not an absent executor.
- Do not bypass the executor to execute or continue `aisp.aisop.json`. Reading through its regular interface or user-requested code review is allowed.
- Static interface checks prove only unchanged bootstrap text and valid format, not executor certification, safety or a completed run.
- Hard guarantees such as `sys.assert`, tool gating, and `sys.io.confirm` require a conforming executor; command exit 0 alone does not mean execution completed.

## Non-Negotiable Rules

| Rule | Enforced By |
| --- | --- |
| Follow RUN aisop.main; analyze only after loading data. | `aisop.main` |
| Never place, execute, or recommend specific trades. The skill has no trading capability. | `tools` |
| Do not analyze without loaded market data. | `analyze.step1:sys.assert` |
| The report must state it is informational only and not financial advice. | `report.step2:sys.assert` |

## Resources

| ID | Path | Kind | Mode | Scope | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| market_data | data/sample_prices.csv | data | read_only | skill |  |
| indicators | scripts/indicators.py | script | execute_only | skill |  |
| finance_terms | finance_terms.md | reference | read_only | shared |  |
| hard_runtime_trace | evals/runtime-traces/hard-pass.json | eval | read_only | skill |  |

## Integrity

| Hash | Value | Meaning |
| --- | --- | --- |
| `program_sha256` | `c016dbcc53aab9f291cca9425e2deee089b109d7c94e50c8194854fa4feedb71` | Canonical JSON hash of the complete two-message business program |
| `contract_sha256` | `a14234950a7285aea68ee1c246870c08cd5a56b3bf149577d84e2c7242d3e1c0` | Recomputable hash of `user.content.aisp_contract` |
| `resources_sha256` | `55c7bd2686e4e9e42f29991c69a8ee91472d5981f66d8f2a8deec99e7b0c641d` | Recomputable hash of declared resource records |

`package_sha256` belongs in an external registry/provenance artifact. Manifest 1.1 binds the complete program plus contract and declared-resource evidence, not every archive file or the SKILL.md executor configuration. Legacy 1.0 hashes did not bind the program body. Recompute with `tools/aisp_hash.py` at publication time.

These hashes show local integrity only. They do not prove trust, safety, or registry approval.

## Source Of Truth

`aisp.aisop.json` is authoritative. A successful README check proves only that this file matches the contract-derived projection; it does not prove that the skill is safe or trustworthy.
