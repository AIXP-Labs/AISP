# Lifecycle

AISP skills follow a defined lifecycle from creation to distribution. AISP does not rebuild the execution engine, and its lifecycle is **AISP-native and tool-agnostic**: generation, evolution, and distribution are handled by external tooling of the author's choice. This document explains how a skill is created, how it changes safely, how it is versioned, and the documentation completeness levels.

---

## Introduction

A skill is a packaged, governed AISOP program. The package layer (AISP) sits on top of the execution layer (AISOP), AISP's only base. AISP defines the *conformance* a skill must satisfy at each lifecycle stage (M1–M6) and what any conforming tool MUST do — not a specific pipeline or toolchain.

---

## Division of Labor

> **AISP defines the package. AISOP executes it.**

| Concern | AISOP | AISP |
|---------|-------|------|
| Execution graph | Defines | Uses |
| `functions` | Defines | Uses |
| `sys.*` | Defines | Uses |
| Skill-package structure | — | Defines |
| `invocation` | — | Defines |
| `discovery` | — | Defines |
| `resources` | — | Defines |
| Generation | — | Defines conformance |
| Evolution | — | Defines conformance |
| Registry / distribution | — | Defines unit + conformance (registry-agnostic) |
| `provenance` | — | Provides hash source |
| Compliance audit | Partial log | Provides contract info |
| Axiom 0 | Execution inherits | Skill inherits |

---

## Creation (Generation)

A generator generates a skill. It MUST produce `aisp/<id>_aisp/aisp.aisop.json` (a lean contract plus a rich Tier A) together with the skill's custom resources, and it MUST validate that:

- `id` equals the folder name **and** ends with `_aisp`;
- every `non_negotiable.enforced_by` points to a mechanism that actually exists;
- every `resources[].path` is legal (relative, confined, non-escaping);
- every resource referenced by a `functions` node is declared in `resources`.

The generator SHOULD produce or update `aisp_list.json` and SHOULD generate the per-skill `README.md` projection from `aisp.aisop.json`. A generated skill MUST still pass conformance rules M1–M6 independently of how it was generated. Generation is tool-agnostic — AISP defines what a conforming generator does, not which tool performs it.

---

## Evolution

An evolution governs change through a deliberate evolution/edit step. A change MAY edit contract fields (`invocation` / `non_negotiable` / `discovery` / `risk_level` / `resources`) or the body (`functions` / `aisop.main`). Changing resources MUST enter the evolution step with a changelog entry and a security scan.

An evolution MUST NOT, without explicit justification:

- remove a safety constraint;
- lower `risk_level`;
- expand `tools`.

These guardrails ensure a skill cannot silently become less safe across versions.

---

## Distribution (Registry)

The unit of distribution is the skill folder. AISP is **registry-agnostic** and does not build or require a specific registry. Any registry MAY index `discovery` + `invocation` + `risk_level` + provenance (hashes) and generate trust / scoring / scanning results. A per-skill `README.md` improves independent package bootstrap, but it is only a generated projection; `--check` proves consistency, not safety or trust. Per conformance rule M6, a registry MUST NOT trust self-declarations — a skill states facts, and the registry judges trust. See [Discovery & Registry](discovery-and-registry.md).

---

## Versioning

Three independent version markers apply to a skill, each with a distinct meaning.

- **Protocol version** — this specification, **V1.0.0**. The `protocol` field literal is `AISP V1.0.0`. The structural base is still an AISOP V1.0.0 program; recording AISP in `protocol` is a brand / protocol-authorship declaration.
- **Contract profile** — `aisp.skill.v1`. A runtime detects an AISP skill by the `aisp.skill.` **prefix**. Only a major change (`v1` → `v2`) is considered incompatible.
- **Skill version** — `system.content.version` (SemVer), the skill's own version, advanced by Evolution.

The Axiom 0 immutability constraint supersedes all versioning rules: no version may weaken Axiom 0.

---

## Documentation Completeness Levels

A skill SHOULD document itself proportionally to its risk and reach.

- **Level 1 — Minimum.** A conformant `aisp.aisop.json` (M1–M6) with a complete contract. This is the floor; a skill that does not meet it is not a valid AISP skill.
- **Level 2 — Recommended.** Level 1 plus an `aisp/README.md` describing discovery, a generated per-skill `README.md`, a populated `aisp_list.json`, and a `description` that makes the skill understandable to a reviewer.
- **Level 3 — Complete.** Level 2 plus declared provenance for publication, a default same-folder `SKILL.md` sidecar bridge for Agent Skills interop unless explicitly opted out, and a changelog reflecting its Evolution history.

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
