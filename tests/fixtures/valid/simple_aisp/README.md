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
| Follow RUN aisop.main. | `aisop.main` |

## Resources

No declared resources.

## Integrity

| Hash | Value | Meaning |
| --- | --- | --- |
| `program_sha256` | `c835ad166bed7729cf48b46e90572d5d2f234bf1ed6262203d96a3e5376856a8` | Canonical JSON hash of the complete two-message business program |
| `contract_sha256` | `29356a44b77a865114ed272bfd4b26378face1663a4146f36517c582753e5753` | Recomputable hash of `user.content.aisp_contract` |
| `resources_sha256` | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | Recomputable hash of declared resource records |

`package_sha256` belongs in an external registry/provenance artifact. Manifest 1.1 binds the complete program plus contract and declared-resource evidence, not every archive file or the SKILL.md executor configuration. Legacy 1.0 hashes did not bind the program body. Recompute with `tools/aisp_hash.py` at publication time.

These hashes show local integrity only. They do not prove trust, safety, or registry approval.

## Source Of Truth

`aisp.aisop.json` is authoritative. A successful README check proves only that this file matches the contract-derived projection; it does not prove that the skill is safe or trustworthy.
