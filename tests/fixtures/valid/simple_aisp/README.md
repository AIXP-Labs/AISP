<!-- generated_from_aisp: true -->
<!-- source: aisp.aisop.json -->
<!-- generator: tools/aisp_readme.py -->

# Simple AISP

This README is a deterministic projection of `aisp.aisop.json`. The contract remains the source of truth.

## Identity

| Field | Value |
| --- | --- |
| Skill ID | `simple_aisp` |
| Version | `1.0.0` |
| Protocol | `AISP V1.0.0` |
| License | `Apache-2.0` |
| Risk Level | `low` |
| Category | test |
| Tags | test |

## Purpose

Minimal valid AISP skill for validator tests.

## When To Use

- test a valid AISP skill

## When Not To Use

- no test requested

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
| Follow RUN aisop.main. | `aisop.main` |

## Resources

No declared resources.

## Integrity

| Hash | Value | Meaning |
| --- | --- | --- |
| `contract_sha256` | `29356a44b77a865114ed272bfd4b26378face1663a4146f36517c582753e5753` | Recomputable hash of `user.content.aisp_contract` |
| `resources_sha256` | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | Recomputable hash of declared resource records |

`package_sha256` is intentionally not embedded here because a README is part of the distributed package and package-level hashes belong in external registry/provenance artifacts. Recompute it with `tools/aisp_hash.py` at publication time.

These hashes show local integrity only. They do not prove trust, safety, or registry approval.

## Source Of Truth

`aisp.aisop.json` is authoritative. A successful README check proves only that this file matches the contract-derived projection; it does not prove that the skill is safe or trustworthy.
