# AISP Ecosystem Governance

The AI Skill Protocol (AISP) is governed by a layered trust model designed to package executable AI skills on top of an execution language, without rebuilding it. AISP is an **independent protocol whose only base is AISOP**; its own lifecycle (generation / evolution / distribution / registry) is AISP-native and tool-agnostic.

## The Layered Chain

AISP operates on a strict separation of concerns across three authoritative domains, under HSAW / Axiom 0. **All layers are licensed under Apache 2.0** for unified patent protection and ecosystem consistency. **This repository** (`AISP-Protocol`) governs the aisp.dev Skill-Package Layer. The aisop.dev Execution Layer and the soulbot.dev Executor Layer are maintained in separate repositories under the same Apache 2.0 license. (Other AIXP protocols, such as `aiap.dev`, are independent siblings, not part of AISP's stack.)

### 1. The Execution Layer (`aisop.dev`)

The language a skill is written in — AISP's only base.

- **Responsibility**: Defines the underlying `.aisop.json` language specification, Mermaid/JSON flow control, the `sys.*` system-call family, and the System/User execution model. A skill body (`aisp.aisop.json`) is structurally a legal AISOP V1.0.0 program.
- **Philosophy**: Neutral, static, foundational. Unconcerned with packaging or distribution.
- **License**: Apache 2.0 — unified across the AIXP protocol family.

### 2. The Skill-Package Layer (`aisp.dev`)

The source of skill packaging, discovery, invocation, and red-line binding — this repository.

- **Responsibility**: Maintains the `AISP_Protocol.md` skill-package specification, the `AISP_Standard.*.aisop.json` conformance rules, the `aisp_contract` schema, the folder-per-skill / `_aisp` layout, the discovery contract (`aisp_list.py` / `aisp_list.json`), and the `enforced_by → sys.*` red-line binding.
- **Philosophy**: Declaration ↔ enforcement is machine-verifiable. Hard guarantees come only from `sys.*`. Trust is never self-declared.
- **License**: Apache 2.0 — providing patent protection for the skill-package layer.

### 3. The Executor Layer (`soulbot.dev`)

The reference runtime environment.

- **Responsibility**: Discovers skills, reads `user.content.aisp_contract`, runs `RUN aisop.main`, enforces each `non_negotiable.enforced_by` mechanism, gates resources, and never bypasses `sys.io.confirm`.
- **Philosophy**: Secure, performant, sandboxed.
- **License**: Apache 2.0 — providing patent protection for the runtime layer.

## Axiom 0 Immutability

**Axiom 0: "Human Sovereignty and Wellbeing" is immutable.**

No major, minor, or patch release of the AISP protocol may ever modify, weaken, or deprecate the core alignment to Human Sovereignty and Wellbeing. This constraint is absolute and non-negotiable.

Any protocol change request that is determined to compromise, dilute, or bypass Axiom 0 — including any change that turns a hard guarantee (`enforced_by → sys.*`) into a soft suggestion — will be rejected regardless of performance benefits, commercial pressure, or technical convenience.

## Versioning

Changes to the AISP protocol follow strict Semantic Versioning (SemVer):

- **Major**: Breaking changes to the skill-package format, the `aisp_contract` schema (`profile` major version), or the conformance rules
- **Minor**: Backward-compatible additions (new contract fields, new conformance rules, new resource kinds)
- **Patch**: Bug fixes, documentation corrections, non-normative clarifications

The current protocol version is **V1.0.0**. The `aisp_contract.profile` is detected by its `aisp.skill.` prefix; only a `profile` major change (`v1` → `v2`) is considered incompatible. The Axiom 0 immutability constraint supersedes all versioning rules.

## Protocol Steering

The AISP protocol is maintained by the AISP Protocol Organization across the layered chain:

| Domain | Role | Scope |
|--------|------|-------|
| `aisop.dev` | Execution Steward | `.aisop.json` specification, `sys.*` family |
| `aisp.dev` | Skill-Package Steward | Skill packaging, contract schema, discovery, red-line binding, security model, lifecycle conformance |
| `soulbot.dev` | Runtime Steward | Reference implementation, discovery, contract reading, `enforced_by` enforcement |

### Decision Process

1. **Proposals**: Submit specification change requests via GitHub Issues with the `spec-change` label
2. **Discussion**: Open discussion period (minimum 14 days for normative changes)
3. **Review**: Maintainers review for Axiom 0 compliance, technical soundness, and backward compatibility
4. **Consensus**: Changes require consensus among relevant domain stewards
5. **Documentation**: All normative changes must include updated specification text and an Architecture Decision Record (ADR)

## Communication

- **GitHub Issues**: Primary channel for specification discussions and proposals
- **GitHub Discussions**: Future community channel when enabled; until then, use GitHub Issues
- **Architecture Decision Records**: Documented in the [`adrs/`](adrs/) directory

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
