# Changelog

All notable changes to the AISP protocol are documented in this file. The documentation site has a short changelog entry point at [`docs/changelog.md`](docs/changelog.md), but this root file is authoritative.

The format follows [Keep a Changelog](https://keepachangelog.com/), and the protocol adheres to Semantic Versioning. The Axiom 0 immutability constraint supersedes all versioning rules.

---

## [1.0.0] — 2026-06-19

The first public AISP specification — the finalized **V1.0.0** release. AISP packages an AISOP program into a discoverable, invocable, governable, distributable skill, building on AISOP only; its lifecycle (generation / evolution / distribution) is AISP-native and tool-agnostic. (The `00`–`12` documents were exploratory/convergence records, superseded by this version.)

### Added — Core Specification

- **`AISP_Protocol.md` / `AISP_Protocol_cn.md`** — the full skill-package specification: folder-per-skill structure, the `_aisp` suffix, the two tiers (Tier A execution / Tier S contract), the `aisp_contract` schema, `invocation` / `non_negotiable` / `discovery` / `risk_level` / `resources`, the `enforced_by` grammar, discovery and progressive disclosure, the security/trust model, naming, versioning, the default-but-core-optional same-folder `SKILL.md` sidecar bridge, and the AISP-native, tool-agnostic lifecycle.
- **`## 0. Axiom`** — a dedicated Axiom 0 (Human Sovereignty and Wellbeing) foundation: the four irrevocable premises, immutability, the `sys.io.confirm` / SE7 execution-layer guarantee, and cross-links (mirrors AISOP's `## 0. Axiom`).
- **`aisp_contract` as a real object in the USER message** (no JSON-in-string), alongside `instruction` / `user_input` / `aisop` / `functions`. The `instruction` is the strong directive `"STRICTLY OBEY aisp_contract; its non_negotiable rules are inviolable; then RUN aisop.main"`.
- **`protocol` field literal `"AISP V1.0.0"`** declaring AISP authorship; the structural base remains an AISOP V1.0.0 program (relies on AISOP's open-world validation — tolerates extra keys; does not gate on the `protocol` value).
- **`license` field** in `system.content` (default `Apache-2.0`, SHOULD).
- **`enforced_by` grammar** — `<node>.<step>:<mechanism>` | `aisop.main` | `tools`. The declaration ↔ enforcement binding (policy-as-code) is AISP's core differentiator from prose Agent Skills.
- **Discovery toolkit** — `aisp/README.md` (MUST), generated per-skill `README.md` (SHOULD; strict/release gate), `aisp_list.py` (zero-dependency reference), and `aisp_list.json` (index).
- **Conformance standards** — `AISP_Standard.core` (M1–M6 skill / R1–R7 runtime), `AISP_Standard.security` (SE1–SE8 / ST1–ST6), `AISP_Standard.ecosystem` (EC1–EC8).
- **Reference tools** — `aisp_validate.py`, `aisp_check_runtime_trace.py`, `aisp_hash.py`, `aisp_readme.py`, `aisp_skill_md.py`, `aisp_validate_agent_skill_bridge.py`, `check_doc_sync.py`, and `check_markdown_links.py`.
- **Release evidence matrix** — a publication checklist separating static package evidence, derived projection evidence, runtime trace evidence, integrity evidence, repository hygiene, expected warnings, and trust boundaries.
- **`aisp.proto`** — proto3 schemas for skill discovery and conformance services.
- **`schemas/aisp-contract-v1.schema.json`** — JSON Schema (draft 2020-12) for `aisp_contract`: required `profile` / `invocation` / `non_negotiable`; `profile` `aisp.skill.` prefix; `enforced_by` grammar; `risk_level` / resource `mode` / `scope` enums; optional resource `sha256`.
- **ADR-001 … ADR-006** — key decisions: skill-package layer on AISOP (independent of any sibling protocol), `aisp_contract` in the user message, `_aisp` suffix & folder-per-skill, `enforced_by` policy-as-code, complementary to Agent Skills, and **ADR-006 Axiom 0 immutability** (as the sibling AIAP protocol's ADR-003 also does).
- **Examples** — native `examples/aisp/`: `yijing_aisp`, `stock_analysis_aisp`, and `aisp_creator_evolution_aisp`, each with a default same-folder Agent Skills `SKILL.md` sidecar while keeping core AISP conformance independent of it.

### Added — Normative Boundary Clauses

- **Platform policy precedence** — an `aisp_contract` is authoritative only within the AISP execution context; it does NOT override platform system / developer / safety / legal / policy instructions. The strong `instruction` never licenses bypassing platform or safety policy (spec §8.1).
- **`system_prompt` conflict rule** — MAY be empty; if non-empty MUST NOT conflict with `aisp_contract` / `aisop.main` / `functions`; the contract MUST NOT be duplicated into it (spec §8.2).
- **Tool enforcement hard vs advisory (R6)** — a runtime SHOULD declare whether tool enforcement is hard or advisory; if advisory, `enforced_by: tools` is not a hard guarantee.
- **`execute_mode` dispatch fidelity (R7)** — a runtime MUST honor each node's `execute_mode` (an inherited AISOP node field, AISOP §5.2.8): `agent` nodes MUST run in an independent sub-agent (never collapsed inline); `inline` / unset is the default. Documented in the field reference and §15; the `stock_analysis_aisp` `analyze` node demonstrates it. `execute_mode` is a dispatch attribute, not an `enforced_by` mechanism, and stays in `functions` (Tier A), not the contract.
- **Open-world AISOP compatibility** — closed-world validators that reject unknown keys or require `protocol == "AISOP V1.0.0"` are NOT AISP-compatible (spec §4.3).
- **AISOP / AISP division-of-labor + slogan** — "AISP defines the package. AISOP executes it."
- **`risk_level` semantic definitions** — low / medium / high / critical; routing/governance metadata, not a hard enforcement mechanism.
- **`aisp_list.py` security clause** — zero-dependency, human-auditable, no network / no third-party imports / no skill-script execution / writes only `aisp_list.json` / reads only within `aisp/`.
- **Read-only during execution (SE8)** — a runtime SHOULD treat skill packages as read-only during normal execution; modifications happen only through a deliberate evolution/edit step.
- **`SKILL.md` sidecar generation and validation** — `aisp_skill_md.py` generates/checks the deterministic same-folder sidecar projection; a generated sidecar declares its provenance (`metadata.generated_from_aisp`, `aisp_program`, `protocol`, `bridge_mode`) and is validated as a thin projection with a confined same-folder path to the native AISP program.
- **Resource `sha256` (optional)** — resource entries SHOULD include `sha256` when distributed through a registry (supply-chain integrity).

### Security

- `resources[].path` MUST be relative, confined to the skill folder or `_shared/`, with no `../` escape (M5 / SE1).
- A skill MUST NOT self-declare trust (`trusted` / `verified` / `safe`) — trust is judged by the consumer / registry / scanner (M6 / SE6).
- Every `non_negotiable.enforced_by` MUST point to a mechanism that actually exists in the skill (M4).
- `sys.io.confirm` is forced-blocking and cannot be bypassed (Axiom 0 invariant, SE7, inherited from AISOP).

### Honest Boundary

- Native-only skills require an AISP/AISOP runtime to run; the default same-folder `SKILL.md` sidecar bridge mitigates this for Agent Skills platforms, but remains core-optional.
- AISP depends on AISOP's open-world validation (extra keys tolerated; `protocol` value not gated). Closed-world validators that reject unknown keys, or that hard-check `protocol == "AISOP V1.0.0"`, will reject AISP files. This is a declared dependency, not a defect.

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
