# ADR-005: AISP Is Complementary to Agent Skills, Not a Replacement

## Status

Accepted direction; the current V1.0.0 tightening remains an internal protocol candidate. The local native Creator's M7 migration is present; applicable host/distribution evidence and publication authorization remain separate release requirements.

## Context

AISP needs an executable, governable business program and a standard interface for agent platforms. AISOP supplies the execution language; Agent Skills supplies the compatibility interface. Neither should become a duplicate source of business truth.

The earlier core-optional discovery projection is replaced by mandatory M7 and an executor-only bootstrap. This tightens conformance despite the deliberately retained V1.0.0 marker; it is not equivalent old/new validation.

## Decision

**AISP is an executable, governable skill package built on AISOP and bridged to agent platforms through the Agent Skills standard.**

1. `aisp.aisop.json` remains the sole business definition.
2. Every conformant package MUST include a generated same-folder `SKILL.md` compatibility interface. There is no opt-out.
3. M7 checks existence, derived name/description/license and the exact fixed bootstrap, allowing five launch strings plus the frozen executor version policy. Core and bridge share one read-only, offline check without a core callback. The version policy does not bind AISP to SoulRun or certify runtime behavior.
4. Execution MUST use a conforming AISP/AISOP executor, SoulRun by default but not vendor-bound. Without one, stop; hosts must not improvise execution or continuation. Executor-mediated reads and user-requested review remain permitted.
5. The fixed bootstrap is not a second independently distributed skill and does not copy business logic. Its own Apache-2.0 license does not override the business license.
6. Generated markers, string-format checks and hashes do not confer trust, executor certification or proof of execution. Installation consent before an executor exists relies on the host's controls.
7. Keep neutral derived names (no `anthropic`/`claude`) and existing frontmatter/path safety rules.

## Consequences

- Standard discovery and executor handoff are present in all conformant packages; missing, old or drifted interfaces fail M7, with EC7 retained only as a legacy mapping.
- Existing generated interfaces need explicit migration. Damaged/unknown files are rejected rather than silently overwritten or reset to defaults.
- Five launch strings and one frozen version policy remain configurable inside the existing interface. One version condition determines direct execution or a consented, rechecked installation; no registry, extra config or template framework is introduced.
- A successful static check does not establish runtime behavior, supported host operation or completed execution.
- The default scope supports one active session, including waiting gates; concurrent conversations require host isolation or separate project/runtime directories.
- Distributed creator copies must be checked against the intended interface revision before publication; this repository does not certify external copies. The protocol candidate cannot be published on the basis of static tool success alone.

## Related Decisions

- ADR-001: AISP packages programs built on AISOP.
- ADR-004: hard guarantees rely on real `enforced_by -> sys.*` mechanisms, not prose.
- Specification §20: canonical rendering, launch strings, frozen version policy and controlled migration.

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
