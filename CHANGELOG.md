# Changelog

All notable changes to the AISP protocol are documented in this file. The documentation site has a short changelog entry point at [`docs/changelog.md`](docs/changelog.md), but this root file is authoritative.

The format follows [Keep a Changelog](https://keepachangelog.com/), and the protocol adheres to Semantic Versioning. The Axiom 0 immutability constraint supersedes all versioning rules.

---

## V1.0.0 — 2026-11-13 revision

### Changes

- Require a generated same-folder SKILL.md compatibility interface (M7), including for runtime-native packages. The fixed bootstrap delegates business execution to a conforming AISP/AISOP executor; SoulRun is the replaceable default, not a protocol dependency. Missing, legacy, malformed or drifted interfaces fail conformance. This tightens earlier V1.0.0 behavior; old and new interfaces are not equivalent.
- Add a frozen executor version policy supporting stable numeric >=X.Y.Z floors and ==X.Y.Z pins. Compatible installations run without an installation question; proven absence or mismatch requires consent, installation and a successful recheck. Probe errors stop. Existing explicit constraints take precedence, and ordinary regeneration/checking preserves the frozen policy without querying latest.
- Reject non-program JSON values such as null instead of reporting a successful empty result. Tighten ambiguous JSON, field types, mechanism references, resource confinement and mode matching, discovery/index handling, and bounded runtime-evidence shape/consistency checks. Preserve conditional tool-enforcement warnings; checks do not independently authenticate runtime events or provenance.
- Registry manifest 1.1 adds canonical full-program program_sha256 and binds it into package_sha256, covering business-function edits that legacy 1.0 hashes did not bind. Legacy manifests remain readable. Neither version covers every archive file or automatically authenticates the SKILL.md executor configuration.
- Make generated-file writes individually atomic, reject unsafe output aliases/links, and report partial batch failures honestly. Update the examples to supported assertion expressions and align documentation and embedded references. The yijing and stock examples now require exact disclaimer wording; their package versions remain 1.0.0. The native Creator example is 1.0.1; protocol/tools remain 1.0.0 and no runtime or engine is upgraded by these changes.
- Keep installed reference tools standard-library-only. Packaging uses the declared build-only setuptools floor; source-archive filtering and wheel/sdist regressions cover selected stale-list/private-file cases. These are bounded safeguards, not complete secret detection. This release does not publish aisp-protocol-tools to PyPI.

### Migration

1. Back up the program, resources and existing interface. Inspect SKILL.md before migration. Preview recognized generated legacy interfaces with --print and explicitly migrate with --write or --write-all; do not treat every failed check as a recognized legacy file.
2. Preserve valid launch commands and stored version policies. First generation or a recognized policy-free default migration resolves the official latest stable SoulRun release into a concrete lower bound; an explicit --executor-version-requirement takes precedence. Other executors require their own explicit constraint. Failed resolution stops without a stored/default fallback. Checks never resolve or migrate.
3. Damaged JSON/configuration, unknown handwritten content and fixed-body drift require explicit review, not silent defaults or automatic deletion. Only after confirming a stale old generated projection has no handwritten content or configuration to preserve may its backed-up SKILL.md be removed and regenerated as first generation.
4. Complete program/resource/snapshot changes and manifests, then regenerate README.md and SKILL.md. Run interface, core, bridge, README and applicable index checks. Regenerate registry evidence as manifest 1.1; old package hashes are not interchangeable with the new domain. Preserve historical failure records and review warnings rather than presenting them as independent trust or publication approval.

### Known Limitations

- Format, version reports, generated markers, hashes and trace fixtures are not executor certification, safety, external trust or proof of completed execution. Hosts must not bypass the executor; installation consent remains a host responsibility before an executor exists. The default runtime scope supports one active session, including waits.
- The SKILL.md launch-command placeholder does not specify where the user-message file must be created. A host may write it outside the project. Use an appropriately private working location and review permissions and disposable inputs; this release does not add a message-file location rule or change the template.
- In the tested Windows Codex sandbox, access to a newly created SoulRun runtime directory remains an executor/environment limitation. The documented 1.0.x workaround pre-creates an empty run directory. A successful run using that workaround does not establish that the default directory path works without it.
- Existing real-host evidence is scoped to the tested yijing package, hosts, versions and scenarios. Delegated installation consent is not user-per-gate participation, and a stand-in executor tests routing rather than actual skill execution. Other examples, sub-agent dispatch and untested scenarios are not certified by those runs. The yijing example's partial reference data and brief interpretation guide do not establish complete or authoritative source coverage.
- Copies of these examples and reference tools in other AIXP repositories are updated separately; until updated they may fail the current M7 check.
- Local validation, archive filtering and CI configuration are bounded checks. No hosted Actions success, complete runtime conformance, or cross-repository release qualification is implied.

### Reference Tool Content Digests

These SHA-256 values identify the reference tools in this revision, not a release signature or external trust proof.

| Tool | SHA-256 |
|---|---|
| `tools/aisp_skill_md.py` | `e08af2119133d9a24e141032a15ede041146e3ed2549100931665dfaf1a496f6` |
| `tools/aisp_validate.py` | `4b783569076ed9c6f8c299fe4b1a2a7dd8d849069eb0b25c493364c0138a7eb8` |
| `tools/aisp_validate_agent_skill_bridge.py` | `c590b57bce975741fbf740889594feba53d34f95122dd301f91751a4dfa246d0` |
| `tools/aisp_readme.py` | `78d11506c7c2f4c216ab16e1c7e09e6472ddf760a664c11e93e79dfb56b63254` |
| `tools/aisp_hash.py` | `ba7f81e74a4801d765e31bdda694c8a45044d4a64ae047e4a56e5e2c99c17a2d` |
| `tools/aisp_check_runtime_trace.py` | `bc345527d264136fcbb3764e584e296116b1601cec044321a13f7f9fc2b2ad01` |
| `tools/check_doc_sync.py` | `640ff82017fea3f52dc7e377718edb7cf096e35e45453b861bfb104d06118a69` |
| `tools/check_markdown_links.py` | `353c3b214c4cb3c2b703b9b4822867621a42dd035a3924bca0f65036a6aa4aee` |

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
