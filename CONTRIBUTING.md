# Contributing to AISP

Thank you for your interest in contributing to the AI Skill Protocol! This document provides guidelines for contributing to the project.

> ⚠️ **Contribution Status (Current Stage)**
>
> We welcome **discussion through GitHub Issues** at this stage of development.
>
> **External Pull Requests are not currently accepted.** If you have a proposal — bug report, feature idea, specification clarification, or conformance rule suggestion — please open an issue describing it. If we agree it adds value, maintainers will implement it and credit you.
>
> This policy may be revisited in the future.

> **Stage Status (V1.0.0)**
>
> AISP is at an early specification stage (V1.0.0). The processes below describe the *target* governance model. Initial decisions are made by AIXP Labs core maintainers; community discussion period scales as the contributor base grows.

## How to Contribute

### Reporting Issues

- Use [GitHub Issues](https://github.com/AIXP-Labs/AISP/issues) to report bugs, suggest features, or propose specification changes
- For specification changes, use the `spec-change` issue template
- Provide clear descriptions with examples where possible

### Discussion-Driven Development

Instead of submitting PRs directly:

1. **Open an issue** describing your proposal, bug, or idea
2. **Discuss** with maintainers — clarify scope, design, and approach
3. **Wait for review** — significant proposals follow the [Specification Changes](#specification-changes) process below
4. **If accepted**, maintainers will implement the change and credit you in commit/release notes

### Specification Changes

Proposals affecting normative content (anything in `specification/`) follow this process:

1. An issue with the `spec-change` label describing the proposed change
2. A minimum 14-day discussion period for non-trivial changes (target governance model; current discussion windows scale with contributor count)
3. An Architecture Decision Record (ADR) in `adrs/` for significant decisions
4. Axiom 0 compliance review by maintainers
5. Updated documentation reflecting the change

### Documentation Changes

Suggestions for non-normative content (topics, guides, reference) are welcome via issues — typo fixes, clarifications, additional examples are particularly valued. Maintainers will implement accepted suggestions.

## Writing Guidelines

### RFC 2119 Keywords

When writing normative specification text, use the keywords defined in [RFC 2119](https://tools.ietf.org/html/rfc2119):

- **MUST** / **MUST NOT** — Absolute requirements
- **SHOULD** / **SHOULD NOT** — Strong recommendations with documented exceptions
- **MAY** — Truly optional behavior

These keywords MUST be capitalized when used in their normative sense.

### Terminology

- Use "AISP skill" (not "AISP agent" or "AISP application") for a governed skill package
- Use "skill folder" for an `aisp/<id>_aisp/` directory and "skill file" for its `aisp.aisop.json`
- Use "skill contract" for `user.content.aisp_contract`
- Capitalize "Axiom 0" (it is a proper noun)
- Write "Tier A" (execution) and "Tier S" (contract)
- Never use "Claude" or "Anthropic" as branding; the suffix is always `_aisp`

### Document Structure

- Begin each topic document with a one-paragraph introduction
- Use tables for field specifications
- Use code blocks with language annotations for examples
- Use Mermaid diagrams for flow and architecture illustrations
- Cross-reference between documents using relative links

### Closing Seal

All specification documents MUST end with:

```
Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
```

## Code of Conduct

All contributors must follow our [Code of Conduct](CODE_OF_CONDUCT.md). The Axiom 0 pledge applies to all contributions.

## License of Contributions

By submitting an issue or any other content (including specification proposals, code snippets in issues, or design suggestions), you agree that your submitted content may be used by maintainers under the terms of the [Apache License 2.0](LICENSE), the same license as the project.

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
