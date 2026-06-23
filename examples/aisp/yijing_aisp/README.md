<!-- generated_from_aisp: true -->
<!-- source: aisp.aisop.json -->
<!-- generator: tools/aisp_readme.py -->

# Yijing Divination

This README is a deterministic projection of `aisp.aisop.json`. The contract remains the source of truth.

## Identity

| Field | Value |
| --- | --- |
| Skill ID | `yijing_aisp` |
| Version | `1.0.0` |
| Protocol | `AISP V1.0.0` |
| License | `Apache-2.0` |
| Risk Level | `low` |
| Category | culture |
| Tags | yijing, iching, divination, hexagram |

## Purpose

Cast and interpret an I Ching (Yijing) hexagram for a user's question.

## When To Use

- cast an I Ching reading
- interpret a hexagram
- yijing divination for a question

## When Not To Use

- medical, legal, or financial decisions needing a professional
- no question provided

## How To Run

With an AISOP runtime:

1. Load `aisp.aisop.json`.
2. Read `user.content.aisp_contract` before execution.
3. Run `user.content.aisop.main` exactly as declared.
4. Enforce every `non_negotiable` rule and every referenced `sys.*` mechanism.
5. Treat `sys.io.confirm` and other human-confirmation gates as blocking controls.

With a generic AI or non-AISOP agent:

- Treat this README as bootstrap guidance only.
- Verify external provenance or obtain explicit human approval before executing an untrusted package.
- Load the contract from `aisp.aisop.json`; do not treat this README as authoritative.
- Follow `RUN aisop.main` and the non-negotiable rules on a best-effort basis.
- Hard guarantees such as `sys.assert`, tool gating, and `sys.io.confirm` exist only in a conforming AISOP runtime.

## Non-Negotiable Rules

| Rule | Enforced By |
| --- | --- |
| Follow RUN aisop.main; never interpret before casting. | `aisop.main` |
| Do not interpret without a cast hexagram. | `interpret.step1:sys.assert` |
| The reading must state it is for reflection, not deterministic prediction. | `interpret.step4:sys.assert` |

## Resources

| ID | Path | Kind | Mode | Scope | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| hexagrams | data/hexagrams.json | data | read_only | skill |  |
| interpretation_guide | data/interpretation_guide.md | reference | read_only | skill |  |

## Integrity

| Hash | Value | Meaning |
| --- | --- | --- |
| `contract_sha256` | `d37e8a05a4efc2e7f72928eba3f9f6f9c889a395b123415baebe62511659a24d` | Recomputable hash of `user.content.aisp_contract` |
| `resources_sha256` | `f5c18e30e1d11c52f816d954d5955213363c349df0a97c8feef8fbdda6fc7dac` | Recomputable hash of declared resource records |

`package_sha256` is intentionally not embedded here because a README is part of the distributed package and package-level hashes belong in external registry/provenance artifacts. Recompute it with `tools/aisp_hash.py` at publication time.

These hashes show local integrity only. They do not prove trust, safety, or registry approval.

## Source Of Truth

`aisp.aisop.json` is authoritative. A successful README check proves only that this file matches the contract-derived projection; it does not prove that the skill is safe or trustworthy.
