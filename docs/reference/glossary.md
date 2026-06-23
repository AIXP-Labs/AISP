# Glossary

> Alphabetical listing of AISP terms, abbreviations, and concepts.

---

## Terms

| Term | Definition |
|------|------------|
| **Agent Skills** | The cross-vendor `SKILL.md` standard for prose-described skills. AISP is **complementary** to it (executable + governable), and authoring/distribution tools SHOULD include a thin same-folder `SKILL.md` sidecar by default for interop unless the author opts out. |
| **AIAP** | AI Application Protocol — a sibling protocol in the AIXP family, **not** part of AISP's stack. `aiap.dev`. |
| **AISOP** | AI Standard Operating Protocol — the execution language a skill body is written in (`.aisop.json`, Mermaid/JSON flow, the `sys.*` family); AISP's only base. `aisop.dev`. |
| **AISP** | AI Skill Protocol — this protocol; the independent skill-package layer built on AISOP only. `aisp.dev`. |
| **`aisp.aisop.json`** | The fixed skill-file name. Structurally a legal AISOP V1.0.0 program (a 2-message array). One per skill folder. |
| **`aisp_contract`** | The skill contract — a real JSON object at `user.content.aisp_contract`: `profile`, `invocation`, `non_negotiable`, `discovery`, `risk_level`, `resources`. Tier S. |
| **`aisp_list.json`** | The discovery index cache: one row per skill (`id`, `name`, `summary`, `path`, `category`, `tags`, `when_to_use`, `risk_level`). Derived from the folders. |
| **`aisp_list.py`** | The zero-dependency discovery script: globs `*_aisp/aisp.aisop.json`, reads each `aisp_contract`, prints a list, `--json` regenerates the index. Running it = executing code. |
| **`_aisp` suffix** | The reserved skill-folder suffix. The folder name == `id` and ends with `_aisp` (mirroring the convention the sibling AIAP protocol uses for `_aiap`). Makes a skill folder self-identifying. |
| **Axiom 0** | "Human Sovereignty and Wellbeing." The immutable alignment principle inherited from HSAW; `sys.io.confirm` is forced-blocking. |
| **Discovery** | The runtime-independent process of finding skills: read the index, run the script, or glob the folders. |
| **`enforced_by`** | The binding from a `non_negotiable` rule to a real mechanism: `<node>.stepN:<mechanism>` \| `aisop.main` \| `tools`. The step segment must be a numeric execution step such as `step1`; metadata fields such as `step_note` do not count. The policy-as-code layer. |
| **Sidecar bridge** | A default-generated but core-optional same-folder thin `SKILL.md` that only guides loading/running `aisp.aisop.json`. Never copies logic; deletable without breaking the skill under an AISP/AISOP runtime. |
| **`flow_format`** | The skill's flow representation: `"mermaid"` \| `"jsonflow"` \| `"hybrid"`. |
| **Folder-per-skill** | The structural rule: one skill = one self-contained folder `aisp/<id>_aisp/`, zippable / hashable as a registry unit. |
| **`functions`** | The per-node execution steps (Tier A). Holds role, principles, knowledge, failure handling, and structured output. |
| **`instruction`** | The user-message directive, fixed as `"STRICTLY OBEY aisp_contract; its non_negotiable rules are inviolable; then RUN aisop.main"`. |
| **`invocation`** | The triggering metadata (`mode`, `when_to_use`, `when_not_to_use`) — decided before execution. |
| **`execute_mode`** | A per-node dispatch field inherited from AISOP (§5.2.8): `"inline"` (default current context for short/simple nodes) \| `"agent"` (independent sub-agent for isolation, source gathering, complex validation, generation, or high-impact decisions). If omitted, runtime falls back to inline and static validation warns. `>10` numeric `stepN` execution steps is a review heuristic for non-agent nodes, not a restriction on shorter `agent` nodes. Honored by **R7**; a dispatch attribute, not an `enforced_by` mechanism. |
| **`loading_mode`** | The AISP skill loading strategy. AISP skills fix this to `"node"` for progressive disclosure. |
| **`non_negotiable`** | The red lines — an array of `{rule, enforced_by}`. The declaration ↔ enforcement binding that differentiates AISP from prose skills. |
| **Open-world validation** | AISOP's tolerance of unknown keys and non-gating on the `protocol` value, which lets AISP add `aisp_contract` / `license` and declare `protocol: "AISP V1.0.0"` (R4). |
| **policy-as-code** | A rule enforced deterministically by the runtime via `enforced_by → sys.*`, graph topology, or the tool allow-list. **Hard.** |
| **policy-as-prompt** | A rule stated in natural language that the model is asked to follow. **Soft.** |
| **`profile`** | The contract schema marker, `"aisp.skill.v1"`; a runtime detects an AISP skill by the `aisp.skill.` prefix. |
| **Progressive disclosure** | Loading metadata first (L1 index), then the full skill on a hit (L2), then resources on demand (L3). |
| **`protocol`** | The authorship marker, fixed `"AISP V1.0.0"`; the file is still structurally an AISOP program. |
| **`resources`** | The resource inventory (`id`, `path`, `kind`, `mode`, …) in the contract. Inventory, not usage; nodes use resources via `sys.io.read` / `sys.run`. |
| **`risk_level`** | A single risk grade: `low` \| `medium` \| `high` \| `critical`. |
| **Skill file** | The `aisp.aisop.json` of a skill. |
| **Skill folder** | An `aisp/<id>_aisp/` directory. |
| **Skill package** | The `aisp/<id>_aisp/` folder as a whole — the unit of distribution. |
| **`sys.*`** | AISOP's deterministic system-call family (`sys.assert`, `sys.io.confirm`, `sys.io.read`, `sys.run`, `sys.llm.json`, `sys.code.exec`, …) handled by the runtime, not by LLM reasoning. The source of all hard guarantees. |
| **Tier A** | The execution tier — `aisop.main` + `functions` + `sys.*` + `tools` / `params`. Heavy. |
| **Tier S** | The contract tier — `user.content.aisp_contract`. Lean metadata only. |
| **Trust (not self-declared)** | A skill MUST NOT claim `trusted` / `verified` / `safe`; trust is judged by the runtime / registry / user / scanner (M6 / SE6). |
| **`_shared/`** | A cross-skill shared-resources directory. Not a skill folder; no `_aisp` suffix; reached via `scope:shared`. |

---

## Risk Levels

| Level | Meaning |
|-------|---------|
| `low` | Read-only / analysis |
| `medium` | Writes locally |
| `high` | Delete / deploy / exfiltrate |
| `critical` | Mandatory human review or no autonomy |

---

## Conformance Series

| Series | Scope | Source |
|--------|-------|--------|
| **M** | Skill conformance (M1–M6) | `AISP_Standard.core` |
| **R** | Runtime conformance (R1–R7) | `AISP_Standard.core` |
| **SE** | Security (SE1–SE8) | `AISP_Standard.security` |
| **ST** | Skill threats (ST1–ST6) | `AISP_Standard.security` |
| **EC** | Ecosystem (EC1–EC8) | `AISP_Standard.ecosystem` |

---

## Abbreviations

| Abbreviation | Expansion |
|--------------|-----------|
| AISP | AI Skill Protocol |
| AISOP | AI Standard Operating Protocol |
| AIAP | AI Application Protocol |
| HSAW | Human Sovereignty and Wellbeing |
| IR | Intermediate Representation |
| NL | Natural Language |
| SemVer | Semantic Versioning |
| SPDX | Software Package Data Exchange (license identifiers) |

---

## Cross-Reference: Where Terms Appear

| Term | Primary Reference Document |
|------|----------------------------|
| `aisp.aisop.json` fields | [aisp-fields.md](aisp-fields.md) |
| `aisp_contract` fields | [aisp_contract-fields.md](aisp_contract-fields.md) |
| `enforced_by` grammar | [enforced_by-grammar.md](enforced_by-grammar.md) |
| Conformance rules (M / R / SE / EC) | [conformance-rules.md](conformance-rules.md) |
| Generated per-skill README | [generated-readme.md](generated-readme.md) |
| Threats (ST1–ST6) | [threat-taxonomy.md](threat-taxonomy.md) |
| Violation codes | [error-codes.md](error-codes.md) |
| Axiom 0 | [../topics/axiom-0.md](../topics/axiom-0.md) |
| Discovery | [../topics/discovery-and-registry.md](../topics/discovery-and-registry.md) |
| Security model | [../topics/security-model.md](../topics/security-model.md) |

---

Align Axiom 0: Human Sovereignty and Wellbeing | Protocol: AISP | Execution: AISOP | Executor: SoulBot
