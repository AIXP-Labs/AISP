# ADR-001: AISP Is an Independent Skill-Package Layer Built on AISOP Only, Not a New Engine

## Status

Accepted

## Context

When designing AISP, a fundamental architectural decision needed to be made about the protocol's scope. The AIXP ecosystem already includes a protocol that addresses the execution layer of the stack:

- **AISOP** defines the execution language — how a single AI program is written (`.aisop.json`, Mermaid/JSON flow, the `sys.*` system-call family).

Other protocols exist as **siblings** in the AIXP family (e.g. **AIAP**, the AI Application Protocol). Those siblings are not part of AISP's stack — AISP does not depend on them for its base, governance, lifecycle, or registry.

Earlier exploratory work (the `00`–`11` "Skill in AISOP" documents) tried to fit a native skill package *inside* AISOP. That conflated two different concerns: writing an executable program (AISOP's job) versus packaging / discovering / triggering / distributing a reusable capability (everything *around* the program). This is the "language vs package ecosystem" distinction. AISP could have rebuilt its own execution engine, but doing so would have fragmented the ecosystem and duplicated mature machinery.

## Decision

AISP is an **independent skill-package layer built on AISOP only**. It does not redefine the execution language (that is AISOP's responsibility). Instead, AISP governs the *skill package* and owns its own lifecycle:

1. **Packaging** — the folder-per-skill structure, the `_aisp` suffix, the fixed `aisp.aisop.json` file name, and the `_shared/` scope.
2. **The skill contract** — `user.content.aisp_contract` (a real object): invocation, red-line binding, discovery, risk, resource inventory.
3. **Discovery / triggering** — `aisp_list.py` / `aisp_list.json` and the `invocation` + `discovery` metadata.
4. **Red-line binding** — `non_negotiable.enforced_by → sys.*` (policy-as-code).
5. **Conformance** — the M / R / SE / ST / EC rule families a skill and runtime must satisfy.

A skill body (`aisp.aisop.json`) is structurally a legal AISOP V1.0.0 program. AISP's lifecycle (generation / evolution / distribution / registry) is **AISP-native and tool-agnostic**: it is handled by external tooling of the author's choice, not delegated to any other protocol. AISP builds on AISOP without rebuilding the engine, and it is a separate protocol from its AIXP siblings.

## Consequences

### What becomes easier

- **No engine duplication**: AISP skills run on any AISOP runtime. There is no new interpreter to maintain.
- **Separation of concerns**: teams can evolve the language (AISOP) and the packaging (AISP) independently; AISP's lifecycle conformance is defined once and is tool-agnostic.
- **One flag, not ten**: skills are "packaged AISOP applications" under a single AISP banner, rather than fragmenting into many new protocols.
- **Independence**: AISP carries no dependency on any sibling protocol for its governance, lifecycle, or registry; adopters implement AISP against AISOP alone.

### What becomes harder

- **Dependency on the base layer**: AISP's guarantees are only as strong as the AISOP runtime beneath it. A skill that is perfectly packaged still depends on the underlying engine to enforce `sys.*`.
- **Open-world coupling**: AISP relies on AISOP tolerating extra keys (`aisp_contract`, `license`) and not gating on the `protocol` value (see ADR-002 / §24). Closed-world AISOP validators reject AISP files.
- **Lifecycle tooling is the author's responsibility**: because generation / evolution / distribution are tool-agnostic, AISP defines the conformance but ships no mandated toolchain; an adopter must supply (or choose) conforming tools.

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
