# ADR-003: One Folder Per Skill, Named `<id>_aisp`

## Status

Accepted

## Context

A skill must be a unit that can be browsed, zipped, hashed, published, and discovered. The questions were: (1) what is the boundary of a skill, (2) what is the file name, and (3) how does a tool tell a skill folder apart from a non-skill folder (like a shared-resources directory)?

Options considered:

1. **One file per skill** (a single `.aisop.json`), with resources referenced from elsewhere. Simple, but a skill with its own `data/` and `scripts/` is no longer self-contained, and there is no natural registry unit.
2. **A folder per skill with an arbitrary name** and a manifest field pointing to the entry file. Flexible, but the entry file name varies, and folder names carry no type information.
3. **A folder per skill, folder name == `id`, fixed entry file name, with a reserved suffix.** Self-contained, self-identifying, and aligned with the sibling AIAP convention (`_aiap`).

## Decision

**A skill is one self-contained folder `aisp/<id>/`; the folder name == `id` and MUST end with `_aisp`; the entry file is always named `aisp.aisop.json`.**

1. **Folder = skill**: the folder is the unit that can be zipped / published / hashed as a registry unit, and the single source of truth.
2. **Fixed file name `aisp.aisop.json`**: a well-known name (like `SKILL.md` / `package.json`); it is fundamentally a `.aisop.json` and follows the AISOP extension convention.
3. **`_aisp` suffix**: the folder name equals `system.content.id` and ends with `_aisp` (e.g. `yijing_aisp`, `stock_analysis_aisp`), mirroring the convention the sibling AIAP protocol uses for `_aiap`. The suffix makes a skill folder self-identifying and naturally excludes non-skill folders: a glob `aisp/*_aisp/aisp.aisop.json` finds every skill and skips `_shared/`.
4. **Custom resource layout**: `data/` / `scripts/` / etc. are not fixed; they are declared in `aisp_contract.resources`. `_shared/` (no `_aisp` suffix) holds cross-skill shared resources (`scope:shared`).

## Consequences

### What becomes easier

- **Self-contained distribution**: a skill folder is a clean registry / zip / hash unit.
- **Trivial discovery**: `aisp/*_aisp/aisp.aisop.json` finds all skills with no configuration; `_shared/` is excluded automatically.
- **Self-identifying folders**: the `_aisp` suffix carries type information, consistent with the sibling AIAP protocol's `_aiap` convention across the AIXP family.
- **Single source of truth**: the folder wins; `aisp_list.py` is a generator and `aisp_list.json` is a cache.

### What becomes harder

- **Naming discipline**: `id` == folder name AND ends with `_aisp` is now a hard rule (core M2); a mismatch fails conformance.
- **One entry per folder**: a skill cannot ship multiple entry files; multi-graph behavior must live inside one `aisp.aisop.json` (via `sub_mermaid` / `aisop.main` routing).
- **Reserved-name coupling**: tooling assumes the `aisp.aisop.json` name and the `_aisp` suffix; deviating breaks discovery.

### Relationship to other ADRs

- **ADR-001**: the folder-per-skill unit is what a registry indexes and records provenance over.
- **ADR-002**: the fixed file name and 2-message shape are what let `user.content.aisp_contract` be located deterministically by the discovery script.

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
