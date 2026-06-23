# AISP Protocol Documentation

Welcome to the **AI Skill Protocol (AISP)** documentation.

AISP is an open standard for packaging executable, governable, distributable AI skills. It ensures **executable behavior** through AISOP program bodies, **machine-verifiable red lines** through `enforced_by → sys.*`, and **immutable alignment** through Axiom 0.

This documentation site covers the protocol, examples, schemas, reference validators, and governance model. It does not bundle a production AISOP runtime, registry service, or trust authority. A conforming AISOP runtime is required to execute a skill and enforce runtime-only guarantees.

---

## What is AISP?

AISP defines how an AI skill should be made executable, governable, and distributable. Every AISP skill is a self-contained folder containing:

- **`aisp.aisop.json`** --- the skill body, a legal AISOP V1.0.0 program (execution graph, step-based functions, `sys.*` calls).
- **`user.content.aisp_contract`** --- a real JSON object in the user message holding invocation, red-line binding, discovery, risk, and resource inventory.
- **Custom resources** --- `data/` / `scripts/` / etc., declared in the contract, plus a shared `_shared/` directory.

The skill is the program. The contract is lean metadata. Hard guarantees come only from `enforced_by → sys.*`; trust is never self-declared. The protocol is anchored by **Axiom 0: Human Sovereignty and Wellbeing** --- an immutable principle that no version of AISP may weaken or remove.

---

## Quick Navigation

### Choose a Path

| Audience | Best entry point | Why |
|----------|------------------|-----|
| Skill authors | [First AISP Skill](guides/first-aisp-skill.md) | Build a native `*_aisp` folder and learn the contract shape. |
| Runtime implementers | [Registry & Runtime Artifacts](reference/registry-runtime-artifacts.md) | Understand runtime traces, R-series evidence, and tool capability artifacts. |
| Release reviewers | [Release Evidence Matrix](reference/release-evidence-matrix.md) | Run the publication gate and interpret static checks, runtime evidence, expected warnings, and clean-tree checks. |
| Registry maintainers | [Discovery & Registry](topics/discovery-and-registry.md) | Separate package integrity, provenance, registry policy, and trust decisions. |

### For Newcomers

| Resource | Description |
|----------|-------------|
| [What is AISP?](topics/what-is-aisp.md) | Understanding the protocol and why it exists |
| [Getting Started](guides/getting-started.md) | Quick introduction for first-time users |
| [Core Concepts](topics/core-concepts.md) | Key ideas: the skill folder, the two tiers, the contract, discovery |
| [Repository README](https://github.com/AIXP-Labs/AISP#readme) | Fastest path to local validation commands and repository scope |

### For Developers

| Resource | Description |
|----------|-------------|
| [First AISP Skill](guides/first-aisp-skill.md) | Step-by-step tutorial to build the `yijing_aisp` skill |
| [Discovering Skills](guides/discovering-skills.md) | How `aisp_list.py` / `aisp_list.json` discovery works |
| [Snapshot Release Workflow](guides/snapshot-release-workflow.md) | Refreshing embedded specification/tool snapshots and release metadata |
| [The Skill Contract](topics/skill-contract.md) | Deep dive into `user.content.aisp_contract` |
| [enforced_by & sys.*](topics/enforced-by-and-sys.md) | Binding red lines to real enforcement |

### For Reviewers

| Resource | Description |
|----------|-------------|
| [Specification](specification.md) | Complete AISP V1.0.0 protocol specification |
| [Conformance Walkthrough](guides/conformance-walkthrough.md) | Checking a skill against M1-M6 / R1-R7 |
| [Release Evidence Matrix](reference/release-evidence-matrix.md) | Publication gate, evidence levels, expected warnings, and trust boundaries |
| [Security Model](topics/security-model.md) | Resource attack surface, trust, the threat taxonomy |
| [Axiom 0](topics/axiom-0.md) | The immutable alignment principle |

### Reference

| Resource | Description |
|----------|-------------|
| [aisp.aisop.json Fields](reference/aisp-fields.md) | Complete reference for the skill-file fields |
| [aisp_contract Fields](reference/aisp_contract-fields.md) | Complete reference for the contract fields |
| [enforced_by Grammar](reference/enforced_by-grammar.md) | The red-line binding grammar |
| [Conformance Rules](reference/conformance-rules.md) | All conformance rules (M / R / SE / EC series) |
| [Validator Coverage](reference/validator-coverage.md) | What the reference tools cover statically, from trace evidence, and from bridge checks |
| [Release Evidence Matrix](reference/release-evidence-matrix.md) | Runnable release checklist and interpretation matrix |
| [Generated Skill README](reference/generated-readme.md) | Per-skill README generation, checking, and trust boundaries |
| [Threat Taxonomy](reference/threat-taxonomy.md) | Skill threat categories and mitigations |
| [Error Codes](reference/error-codes.md) | Error code reference |
| [Glossary](reference/glossary.md) | Term definitions for the AISP vocabulary |

### Project Governance

| Resource | Description |
|----------|-------------|
| [Governance](https://github.com/AIXP-Labs/AISP/blob/main/GOVERNANCE.md) | Layered chain, Axiom 0 immutability, steering, and communication |
| [Contributing](https://github.com/AIXP-Labs/AISP/blob/main/CONTRIBUTING.md) | Current contribution policy and writing guidelines |
| [Security](https://github.com/AIXP-Labs/AISP/blob/main/SECURITY.md) | Vulnerability reporting and security scope |
| [Code of Conduct](https://github.com/AIXP-Labs/AISP/blob/main/CODE_OF_CONDUCT.md) | Axiom 0 pledge and community standards |

---

## Ecosystem

AISP is an **independent skill-package protocol** whose only base is AISOP:

- **AISOP (AI Standard Operating Protocol)** is the execution language a skill body is written in — AISP's only base.
- **Agent Skills (`SKILL.md`)** is complementary — generated/distributed AISP skills SHOULD include a thin same-folder `SKILL.md` sidecar by default unless explicitly opted out.
- **AIAP (AI Application Protocol)** and the other AIXP protocols are **sibling projects**, not part of AISP's stack.

AISP packages an AISOP program into a discoverable, governable, distributable skill, without rebuilding the engine. Its lifecycle (generation / evolution / distribution / registry) is AISP-native and tool-agnostic.

---

## Contributing

AISP is an open protocol. Contributions are welcome:

- **Repository**: [github.com/AIXP-Labs/AISP](https://github.com/AIXP-Labs/AISP)
- **Website**: [aisp.dev](https://aisp.dev)

---

> Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
