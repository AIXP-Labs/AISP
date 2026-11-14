# AISP V1.0.0 Skill-Package Specification

> **AISP defines the package. AISOP executes it.**
>
> AISP is an executable, governable skill package built on AISOP and bridged to agent platforms through the Agent Skills standard.

| Field | Value |
|-------|-------|
| Protocol | `AISP V1.0.0` |
| Full name | AI Skill Protocol |
| Authority | `aisp.dev` |
| Execution base | `AISOP V1.0.0` |
| Normative status | English specification governs skill-package rules and structure |
| Core invariant | Axiom 0: Human Sovereignty and Wellbeing |

## At a Glance

AISP packages an AISOP program into a discoverable, invocable, governable, and distributable AI skill.

A native AISP skill is a self-contained folder containing:

- `aisp.aisop.json` - the executable AISOP program and fixed skill-file name.
- `user.content.aisp_contract` - the machine-checkable skill contract, as a real object in the user message.
- Declared resources - data, scripts, or shared assets listed in `aisp_contract.resources`.
- `SKILL.md` - the required, generated same-folder Agent Skills compatibility interface (M7); its fixed bootstrap hands execution to an executor, not to the host's improvised execution.
- `README.md` - the recommended generated package introduction (EC8), required by strict/release profiles.

Hard guarantees come only from real mechanisms such as `enforced_by -> sys.*`. Natural-language guidance is soft, and trust is never self-declared.

## How to Read This Specification

| Reader | Recommended path |
|--------|------------------|
| New to AISP | Read §§0-4, then the complete example in §22 |
| Skill author | Read §§5-13, then §§20-23 |
| Validator implementer | Read §§4, 8-13, 17, and the conformance standards |
| Runtime implementer | Read §§14-17, then R-series rules in `AISP_Standard.core` |
| Registry or distribution implementer | Read §§17, 20-21, Appendix B, and the registry/runtime artifact references |

## Table of Contents

**Part I: Protocol Foundations**

- [0. Axiom 0: Human Sovereignty and Wellbeing](#0-axiom)
- [1. Protocol Declaration](#1-protocol-declaration)
- [2. Core Definitions: What an AISP Skill Is](#2-core-definitions)
- [3. Positioning: vs Agent Skills, on AISOP](#3-positioning)
- [4. Conformance and Terminology](#4-conformance-and-terminology)

**Part II: Skill-Package Structure**

- [5. Skill-Package Structure: folder-per-skill, _aisp, _shared](#5-skill-package-structure)
- [6. The aisp/ Directory: README, aisp_list.py, aisp_list.json](#6-the-aisp-directory)
- [7. The Skill File: aisp.aisop.json and Two Tiers](#7-the-skill-file)

**Part III: The Skill Contract**

- [8. aisp_contract Fields](#8-aisp_contract-fields)
- [9. invocation: Triggering](#9-invocation)
- [10. non_negotiable + enforced_by: Red-Line Binding](#10-non_negotiable-enforced_by)
- [11. discovery: Discovery Metadata](#11-discovery)
- [12. risk_level: Risk](#12-risk_level)
- [13. resources: Resources](#13-resources)

**Part IV: Execution & Disclosure**

- [14. What the Model Sees: Contract in the User Message](#14-what-the-model-sees)
- [15. Tier A Placement: functions / sys.*](#15-tier-a-placement)
- [16. Discovery & Progressive Disclosure](#16-discovery-progressive-disclosure)

**Part V: Security, Naming & Versioning**

- [17. Security & Trust Model](#17-security-trust-model)
- [18. Naming Rules](#18-naming-rules)
- [19. Versioning: Markers and Base](#19-versioning)

**Part VI: Interoperability & Lifecycle**

- [20. Interoperability: Required Agent Skills Compatibility Interface](#20-interoperability)
- [21. Lifecycle: Generation / Evolution / Distribution](#21-lifecycle)

**Part VII: Examples & Honesty**

- [22. Complete Example: yijing_aisp](#22-complete-example)
- [23. Conformance Checklist](#23-conformance-checklist)
- [24. Honest Boundaries](#24-honest-boundaries)
- [25. Common Mistakes](#25-common-mistakes)

**Appendices**

- [Appendix A: aisp_contract Skeleton](#appendix-a-aisp_contract-skeleton)
- [Appendix B: Directory Skeleton](#appendix-b-directory-skeleton)
- [Appendix C: aisp_list.py Zero-Dependency Reference](#appendix-c-aisp_listpy-zero-dependency-reference)
- [Appendix D: aisp_list.json Index Format](#appendix-d-aisp_listjson-index-format)
- [Appendix E: Sources](#appendix-e-sources)
- [Appendix F: Minimal Slogan](#appendix-f-minimal-slogan)

## Part I: Protocol Foundations

## 0. Axiom

### Axiom 0: Human Sovereignty and Wellbeing

Every AISP skill operates under Axiom 0, inherited from the AISOP execution layer on which AISP is built (and ultimately from HSAW, the highest axiom). The protocol acknowledges the following irrevocable premises:

1. **Human Sovereignty First**: a skill exists to serve humans and must never undermine human control. Final authority over every invocation, flow, and action rests with humans.
2. **Wellbeing is Non-Negotiable**: a skill must not harm human physical or mental health, dignity, or freedom. When an instruction conflicts with human wellbeing, wellbeing takes precedence.
3. **Transparency and Accountability**: skill behavior must be understandable, traceable, and open to challenge. Concealed intent or evasion of responsibility violates this axiom.
4. **Do No Harm**: a skill must not deceive, manipulate, injure, or exploit humans, regardless of the instruction source.

Operational consequences:

- Axiom 0 cannot be overridden by any skill, `aisp_contract`, `instruction`, evolution, or protocol extension.
- Every conformant AISP runtime MUST enforce it at the highest execution priority.
- Its execution-layer guarantee is `sys.io.confirm`: forced-blocking and inviolable (SE7).
- It is immutable across all AISP versions ([ADR-006](https://github.com/AIXP-Labs/AISP/blob/main/adrs/adr-006-axiom-0-immutability.md)).
- Every skill carries it as `"axiom_0": "Human_Sovereignty_and_Wellbeing"` (M1).

See §8.1 for platform policy precedence and the [Axiom 0](https://github.com/AIXP-Labs/AISP/blob/main/docs/topics/axiom-0.md) topic for the full treatment.

---

## 1. Protocol Declaration

```
AISP Skill-Package Specification
Protocol: AISP V1.0.0
Authority: aisp.dev
Execution Base: aisop.dev
Axiom 0: Human Sovereignty and Wellbeing

This document defines the skill-package specification for AISP skills, including:
- The folder-per-skill structure and the _aisp suffix
- The two tiers (Tier A execution / Tier S contract)
- The aisp_contract schema and its placement in the user message
- The enforced_by red-line binding (policy-as-code)
- The required generated SKILL.md compatibility interface and executor-only execution
- Discovery, progressive disclosure, security, naming, versioning, and lifecycle

Every AISP skill MUST first be a legal AISOP V1.0.0 program.
The .aisop.json language itself is governed by AISOP and is not defined by this document.
```

### 1.1 Normative Artifacts and Their Roles

This protocol is documented in several artifact families. When they conflict, the order of precedence is declared below:

| Artifact | Role | Authority |
|----------|------|-----------|
| `AISP_Protocol.md` (and `AISP_Protocol_cn.md` translation) | Skill-package specification, structure, contract schema, rules | **Authoritative** for skill structure and rules |
| `standards/AISP_Standard.*.aisop.json` | Formal conformance rule definitions (M / R / SE / EC series) | **Authoritative** for machine-verifiable rule semantics |
| `schemas/*.schema.json` | Covered structures of the named native JSON artifacts | Defines those JSON constraints, not complete package or runtime validation |
| `aisp.proto` | Discovery and conformance service transport objects and APIs | **Authoritative** for those service wire types and API signatures |

**Conflict resolution**: this Markdown specification is the tie-breaker for *protocol rules and package structure*. Each JSON Schema describes the covered constraints of its named native JSON artifact; schema success does not replace filesystem, cross-file or runtime checks. `aisp.proto` governs only its service transport objects and API signatures, not the native `aisp.aisop.json`, index, trace or manifest file formats. Protobuf/ProtoJSON field and enum representations are not substitutes for those native JSON formats. Translations (e.g. `AISP_Protocol_cn.md`) are always non-normative — the English text governs in case of divergence.

> **What this document is NOT.** AISP does not redefine the AISOP language (graph syntax, `sys.*` semantics) — that is `aisop.dev`. AISP does not delegate its lifecycle to another protocol; generation / evolution / distribution are AISP-native and tool-agnostic. AISP defines only the *skill package*: how an AISOP program becomes a discoverable, invocable, governable, distributable skill.

---

## 2. Core Definitions

> AISOP is the language a skill is written in. **AISP is the package.**

A **native AISP skill** is a **self-contained folder** containing one fixed-name AISOP program `aisp.aisop.json`, the required generated same-folder `SKILL.md` compatibility interface, and its declared custom-layout resources. The reusable, executable, governable and evolvable business capability is defined only in `aisp.aisop.json`; the interface hands execution to a conforming AISP/AISOP executor. AISP recognizes the Agent Skills standard as its bridge to agent platforms, without turning the bridge into a second business definition.

```text
A native AISP skill =
    one folder (folder = skill; folder name = id; MUST end with _aisp)
  + aisp.aisop.json (an AISOP program: contract + execution graph + nodes + sys.*)
  + SKILL.md (required generated Agent Skills compatibility interface, M7)
  + custom resources (data/ scripts/ … declared in aisp_contract.resources)
```

| Concept | Analogy | Definition |
|---------|---------|------------|
| **AISOP** | Programming language (Python) | The execution language — `.aisop.json` files, Mermaid/JSON flow, `sys.*` calls. AISP's only base. |
| **AISP** | Package format + manifest (npm package, a Skill) | This protocol — packages an AISOP program into a discoverable, governable skill |
| **AISP skill** | A published package | A self-contained `aisp/<id>_aisp/` folder conformant to this specification |

### 2.1 The Skill Is the Program

Agent Skills (`SKILL.md`) provide the standard discovery and compatibility interface. AISP's executable business subject remains `aisp.aisop.json`. Every conformant package MUST include its generated same-folder `SKILL.md` (§20), including packages consumed directly by a runtime. The bootstrap has fixed interface logic, not a copy of the skill's business functions. Execution MUST use a conforming executor; the host MUST NOT bypass it to execute or continue the business program itself.

```text
Naming conventions:
  .aisop.json     →  AISOP language format identifier (the skill body)
  aisp.aisop.json →  the fixed skill-file name (well-known, like SKILL.md / package.json)
  _aisp           →  skill-folder type identifier (folder name == id, ends with _aisp)
  aisp_contract   →  the skill contract (a real object in the user message)
```

---

## 3. Positioning

### 3.1 vs Agent Skills (Complementary, Not a Replacement)

| | Agent Skills (`SKILL.md`) | **AISP (this protocol)** |
|---|---|---|
| Nature | Prose instructions + progressive disclosure | **Executable flow + governable** (AISOP graph + `enforced_by → sys.*` hard constraints + red-line binding) |
| Standardization | Cross-vendor open standard | AISP's package rules plus a **required generated `SKILL.md` compatibility interface** |
| Relationship | — | **Complementary**: AISOP supplies the executable business program; the Agent Skills interface bridges it to hosts and delegates execution to an executor |

Public framing: **"AISP is an executable, governable skill package built on AISOP and bridged to agent platforms through the Agent Skills standard."**

### 3.2 Ecosystem Layering

```text
HSAW / Axiom 0      Human Sovereignty and Wellbeing (highest constraint)
      ↓
AISOP (execution)   How to write an executable AI program (.aisop.json)
      ↓
AISP  (skill pkg)   Package an AISOP program into a discoverable, governable, distributable skill
```

> AISP is the **skill-package** layer, built on AISOP (execution) only. It does not rebuild the execution engine. Its own lifecycle (generation / evolution / distribution / registry) is AISP-native and tool-agnostic — not delegated to any other protocol.

### 3.3 Executable Skill IR

`aisp.aisop.json` is an **intermediate representation (IR) + run contract** for cross-platform skill semantics — not another `SKILL.md`. **policy-as-prompt vs policy-as-code**: the natural-language rules in the contract and nodes are policy-as-prompt (the LLM judges; soft); `non_negotiable.enforced_by → sys.*` is policy-as-code (deterministic; hard). **Only the latter is a real guarantee.**

---

## 4. Conformance and Terminology

The keywords **MUST / SHOULD / MAY** are interpreted per RFC 2119.

### 4.1 Skill Conformance (MUST)

A conformant AISP skill:

- **M1** MUST be **structurally a legal AISOP V1.0.0 program** (2-message array, required fields, the `user.content` `instruction` / `aisop` / `functions`, `aisop.main` present). Its `protocol` field MUST declare **`AISP V1.0.0`** (marking the file as AISP). The AISOP reference validator checks only that `protocol` *exists*, not its value, so it accepts `AISP V1.0.0`; the AISOP engine executes normally (it does not gate on the `protocol` value). Required fields: `protocol` / `axiom_0` / `id` / `name` / `version` / `flow_format` / `loading_mode` (`license` SHOULD be present, default `Apache-2.0`). For AISP skills, `loading_mode` MUST be exactly `"node"`.
- **M2** MUST live at `aisp/<id>/` with the file name `aisp.aisop.json`, where `<id>` == the folder name and **ends with `_aisp`** (§18).
- **M3** MUST contain `user.content.aisp_contract` (a real object) whose `profile` matches `^aisp\.skill\.v[0-9]+$` (currently `aisp.skill.v1`), and which contains `invocation` and `non_negotiable` (§8).
- **M4** Every `non_negotiable.enforced_by` MUST point to a mechanism that **actually exists** in the skill (§10).
- **M5** Each `resources[].path` (if any) MUST be a relative path, confined to the skill folder or `_shared/`, with no `../` escape (§17).
- **M6** A skill MUST NOT self-declare trust (`trusted` / `verified` / `safe`) — trust is judged by the consumer (§17).
- **M7** A skill MUST contain a generated same-folder `SKILL.md`: (1) the file exists; (2) `name`, `description` and outer `license` match the skill-derived values; (3) metadata and fixed bootstrap match the generator, allowing only five launch strings and a valid frozen `executor_version_policy` in `params` to vary (§20). Missing, legacy, malformed or drifted interfaces FAIL. EC7 is the legacy interoperability mapping, not a missing-interface exemption.

### 4.2 Runtime Conformance

An AISP skill MUST run through an available executor satisfying AISP/AISOP runtime requirements. The reference bootstrap defaults to **SoulRun** (`soulrun.dev`); other conforming executors, including host-embedded runtimes, are allowed. The host MUST NOT bypass the executor to execute or continue `aisp.aisop.json`. Reading programs, contracts, nodes or resources through the executor's regular interface (for example `soulrun --program`), and user-requested code review, are not prohibited.

R1-R7 below define runtime behavior. The bootstrap launch strings and frozen version policy are reference launch configuration, not executor certification or the sole interface every embedded runtime must expose. Executors must preserve blocking human gates, red lines and independent sub-agent dispatch for `execute_mode: "agent"`. Before an executor exists, installation consent relies on the host's own confirmation/permission controls, not an absent executor's hard gate.

Distinguish not installed, installed but unusable, incompatible or unverified version, and run failure; a run failure is not permission to reinstall or upgrade automatically. The fixed bootstrap requires the reported executor package version to satisfy its frozen constraint, not merely a callable command (§20.1). Unknown output stops rather than passing. Static checks validate the policy's shape, not the truth of a version report or actual runtime compatibility. Command exit 0 may mean turn preparation or waiting at a gate, not completion; a waiting gate is not consent. Completion requires the run record's terminal state and corresponding outputs within the verified scope.

The default bootstrap deliberately adds no `--session-id`. Within the same project/runtime directory and default scope, only one active session is supported; waiting for a user answer is still active. Alternating messages across chat windows does not isolate sessions. Concurrent conversations require stable host isolation or separate project/runtime directories. A complete executor compatibility suite is outside this revision.

- **R1 (MUST)** An AISP runtime MUST read `user.content.aisp_contract` as the skill contract; MUST NOT skip required nodes of `aisop.main`; MUST NOT bypass `sys.io.confirm` (inherited from Axiom 0).
- **R2 (MUST)** For `non_negotiable`, the runtime MUST enforce the hard constraint via the mechanism its `enforced_by` points to.
- **R3 (MUST)** `aisp_contract` is in the **user message** — it is already part of the model's context this turn; the runtime MUST hand it to the model with the user message (it MUST NOT be hidden or stripped), and no separate "render" step is required. The `instruction` commands the model to obey the contract via a strong directive (e.g. `"STRICTLY OBEY aisp_contract; …; then RUN aisop.main"`).
- **R4 (MUST, dependency on the underlying AISOP runtime)** The underlying AISOP runtime MUST apply **open-world validation** to both `system.content` and `user.content` (tolerating unknown keys), so that the AISP fields `user.content.aisp_contract` and `system.content.license` coexist; and MUST NOT gate on the `protocol` value (it accepts `AISP V1.0.0`). The AISOP reference implementation `flow_runtime.py` satisfies this (it checks required fields only, does not reject extra keys, and does not validate the `protocol` value).
- **R5 (SHOULD)** Before handling an untrusted skill/resource, a runtime SHOULD pass it through a user trust gate; it SHOULD prefer reading `aisp_list.json` (no script execution, §16).
- **R6 (SHOULD)** A runtime SHOULD declare whether its tool enforcement is hard (permissions actually enforced) or advisory. If advisory, `enforced_by: tools` MUST NOT be treated as a hard guarantee.
- **R7 (MUST)** A runtime MUST honor each node's `execute_mode` — an inherited AISOP node-level field (AISOP spec §5.2.8). A node declared `execute_mode: "agent"` MUST be dispatched to an independent sub-agent and MUST NOT be collapsed inline; a node declared `"inline"` executes in the current context. If `execute_mode` is omitted, the runtime falls back to `inline` and the static validator emits a warning so the dispatch intent can be made explicit. A conformant AISP skill MUST NOT declare any explicit value other than `"inline"` or `"agent"`. This is the execution-fidelity guarantee. `execute_mode` is a dispatch attribute the runtime honors — NOT an `enforced_by` mechanism (§15).

Reference trace coverage: agent nodes need matching dispatch evidence. Recorded events for known inline nodes (including omitted-mode defaults) must declare both `mode` and `dispatched_as` as inline; this consistency check does not require inline events for every node. Trace acceptance does not authenticate events or certify complete runtime conformance.

### 4.3 Open-World AISOP Compatibility

> AISP requires the underlying AISOP runtime to (a) tolerate unknown keys in `system.content` (e.g. `license`) and `user.content` (e.g. `aisp_contract`), and (b) not gate on the `protocol` value (accept `AISP V1.0.0`). Closed-world validators that reject unknown keys or require `protocol == "AISOP V1.0.0"` are NOT AISP-compatible. AISP files are structurally AISOP V1.0.0 programs; the AISP `protocol` marker declares package semantics and protocol ownership, not a different execution grammar.

This is the operational restatement of R4: AISP does not fork the AISOP language. It rides on AISOP's open-world validation. A validator that is closed-world (rejects unknown keys) or that hard-checks the `protocol` literal cannot consume AISP files — this is a declared compatibility boundary, not a defect in either protocol (§24).

### 4.4 Terminology

| Term | Meaning |
|------|---------|
| Skill package | The `aisp/<id>/` folder as a whole |
| Skill file | `aisp.aisop.json` (the AISOP program) |
| Skill contract (`aisp_contract`) | `user.content.aisp_contract` (a real object) |
| Tier A / Tier S | Execution tier (`aisop.main` / `functions` / `sys.*`) / Contract tier (`aisp_contract`) |
| Agent Skills compatibility interface (bridge interface) | The required generated same-folder `SKILL.md`; fixed bootstrap, not business source of truth |
| Executor | A program that runs skills under AISP/AISOP runtime requirements; not vendor-bound, SoulRun by default |

---

## Part II: Skill-Package Structure

## 5. Skill-Package Structure

**folder-per-skill; a uniform file name `aisp.aisop.json`; the folder name == `id` and MUST end with `_aisp` (mirroring the convention the sibling AIAP protocol uses for `_aiap`):**

```text
aisp/                          # visible directory (not hidden); browsable by AI / human / bash
  README.md                    # MUST: how AISP works (what / how to discover / how to run / how to add)
  aisp_list.py                 # discovery script (bash → list skills; --json regenerates the index)
  aisp_list.json               # index cache (reading it also yields full skill info)
  yijing_aisp/                 # folder name = id "yijing_aisp" (MUST end with _aisp)
    aisp.aisop.json            # fixed file name (a skill = one AISOP program)
    SKILL.md                   # MUST: generated Agent Skills compatibility interface
    README.md                  # SHOULD: generated bootstrap projection from aisp.aisop.json
    data/
      hexagrams.json
      interpretation_guide.md
  stock_analysis_aisp/
    aisp.aisop.json
    SKILL.md
    README.md
    data/ scripts/ ...
  _shared/                     # cross-skill shared resources (NOT a skill folder; no _aisp suffix)
    finance_terms.md
```

Rules:

1. One skill = one self-contained `aisp/<id>/` folder (zippable / publishable / hashable as a registry unit).
2. The file name is fixed at `aisp.aisop.json` (a well-known name, like `SKILL.md` / `package.json`); it is fundamentally a `.aisop.json` and follows the AISOP extension convention.
3. **The folder name == `id` and MUST end with `_aisp`** (§18); the suffix makes a skill folder self-identifying and naturally excludes non-skill folders like `_shared/`.
4. **Resource layout is custom** (`data/` / `scripts/` / …), declared by `aisp_contract.resources`; no fixed subfolder is forced.
5. Per-skill `README.md` SHOULD be generated from `aisp.aisop.json`; strict/release profiles MAY treat missing/manual/drifted README, bad source markers, or unsupported generator markers as a failure (EC8). It is a bootstrap projection, not the source of truth.
6. `_shared/` holds shared resources (`scope: "shared"`).
7. Every conformant package MUST include a generated same-folder `SKILL.md` compatibility interface (M7, §20); there is no author opt-out.
8. Discovery: read `aisp/aisp_list.json` or run `aisp/aisp_list.py` via bash, with a glob fallback `aisp/*_aisp/aisp.aisop.json` (§16).

---

## 6. The `aisp/` Directory

| File | Level | Role |
|------|-------|------|
| `README.md` | **MUST** | Introduces (for human/AI): what this is, how to discover, how to run, how to add a skill (the human-readable version of the discovery contract) |
| `aisp_list.json` | SHOULD | Index cache: each skill's `id` / `name` / `summary` / `path` / `category` / `tags` / `when_to_use` / `risk_level` |
| `aisp_list.py` | SHOULD | Discovery script: globs `*_aisp/aisp.aisop.json`, reads `aisp_contract`, prints a list, `--json` regenerates the index (zero-dependency reference in Appendix C) |

**Truth model**: **the skill folder is the single source of truth; `aisp_list.py` is the generator; `aisp_list.json` is the cache.** The three do not compete — the folder wins; if the JSON is suspected stale, re-run the script.

Per-skill `README.md` is a generated package introduction. A successful README check proves only consistency with `aisp.aisop.json`, not trust, safety or registry approval. Generic hosts MUST hand execution through the interface to a conforming executor; without one, stop. README prose never authorizes best-effort self-execution or overrides an external provenance/user trust gate.

---

## 7. The Skill File

`aisp.aisop.json` is an AISOP program containing two tiers:

| Tier | What it holds | Where |
|------|---------------|-------|
| **Tier A (execution, heavy)** | flow / steps / role / principles / knowledge / constraints / failure / confirmation / validation / structured output / resource reading / tools / state | `aisop.main` + `functions` + `sys.*` + `tools` / `params` |
| **Tier S (contract, lean)** | triggering, red-line binding, discovery, risk, resource inventory | `user.content.aisp_contract` (a real object) |

The contract holds only what the execution tier cannot express, or what the consumer needs to know in advance; everything else is placed in Tier A (§15).

Inherited optional fields retain their types when present: `system.content.summary`, `description`, `license`, `system_prompt` and `user.content.user_input` are strings; `system.content.params` is an object; `system.content.tools` is an array of non-blank strings. Omitting tools or using an empty array is permitted unless a separate red-line binding requires a restricted allow-list. This does not make these fields required (`license` remains SHOULD), restrict parameter-value extensions, certify a license identifier or prove prompt/contract semantic consistency. Only an omitted license or a blank license string produces the advisory presence warning; a non-string license fails its type check instead.

---

## Part III: The Skill Contract

## 8. `aisp_contract` Fields

The skill contract is **`user.content.aisp_contract`** — a **real JSON object**, in the **user message**, alongside `instruction` / `user_input` / `aisop` / `functions`; the `instruction` commands the model to obey it via a strong directive (§14). (Program identity metadata `id` / `name` / `version` / `license` / `tools` / `params` stays in `system.content`.)

The following is field notation with placeholders, optional markers and alternatives, not valid JSON or a runnable contract. For a concrete program, see §22.

```text
{
  "profile": "aisp.skill.v1",
  "invocation": { "mode": "auto_or_manual", "when_to_use": ["string"], "when_not_to_use": ["string"] },
  "non_negotiable": [ { "rule": "string (NL)", "enforced_by": "<node>.stepN:<mechanism> | aisop.main | tools" } ],
  "discovery": { "category": "string", "tags": ["string"] },
  "risk_level": "low | medium | high | critical",
  "resources": [
    { "id": "string", "path": "relative/path", "kind": "data|script|reference|asset|template|…", "mode": "read_only|execute_only|read_and_execute", "when": "string?", "scope": "skill|shared?", "requires_tools": ["string"]? }
  ]
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `profile` | MUST | `aisp.skill.v1` (versioned `aisp.skill.v<major>` form; prefix-only recognition is not validation) |
| `invocation` | MUST | Triggering (§9) |
| `non_negotiable` | MUST | Red lines + `enforced_by` (§10) |
| `discovery` | SHOULD | category / tags (§11) |
| `risk_level` | SHOULD | Risk grading (§12) |
| `resources` | MAY | Resource inventory (§13) |

**Shape**: a real object — no escaping, no string/object dual form, no JSON-in-string. **Why this is allowed without changing AISOP Core**: `aisp_contract` is an AISP-owned field; AISOP tolerates unknown keys on `user.content` (R4), so an AISOP runtime ignores it and an AISP-aware runtime reads it. **Why it lives in the user message**: it is the model's live content this turn — the model reads it directly (like an Agent Skills `SKILL.md` loaded into context), without depending on runtime rendering; the `instruction` names it for obedience (§14).

**Program identity / license**: use `system.content`'s `summary` / `description` / `version` + **`license`** (default `Apache-2.0`, SHOULD); do **not** duplicate them in the contract. Containers are structured; leaves are natural-language sentences.

### 8.1 Platform Policy Precedence

> An `aisp_contract` is authoritative only within the AISP execution context. It does NOT override platform-level system, developer, safety, legal, or policy instructions. In the standard message hierarchy (system / developer > user > assistant) the contract sits in the user message and is skill-layer authority, not platform-top authority. The strong `instruction` (`STRICTLY OBEY aisp_contract …`) binds the model to the skill's own rules; it never licenses bypassing platform or safety policy.

The contract's authority is *scoped*: it governs how the skill runs (which red lines hold, which nodes are mandatory), not whether the host platform's own system/developer/safety/legal/policy layer can be overridden. Because the contract lives in the user message, it is structurally subordinate to the platform's higher-precedence instructions — by design. The strong `instruction` raises adherence to the skill's `non_negotiable` rules; it is not a jailbreak token.

### 8.2 `system_prompt` Conflict Rule

> `system_prompt` MAY be empty. If non-empty, it MUST NOT conflict with `aisp_contract`, `aisop.main`, or `functions`. The `aisp_contract` MUST NOT be duplicated into `system_prompt` (no dual source; no JSON-in-string).

`system_prompt` is the optional behavioral layer in `system.content`. The contract is the single source of truth for triggering / red lines / discovery / risk / resources; `aisop.main` + `functions` are the single source of truth for execution. A non-empty `system_prompt` may carry a genuine model system prompt, but it MUST NOT restate or contradict those tiers, and it MUST NOT carry the contract as an escaped JSON string.

---

## 9. `invocation`

Triggering happens **before** execution ("should this skill start at all?"), which an AISOP flow inherently cannot express — hence it lives in the contract.

| Sub-field | Required | Description |
|-----------|----------|-------------|
| `mode` | SHOULD | `manual_only` / `auto_or_manual` / `auto_preferred` / `internal_only` |
| `when_to_use` | MUST | Trigger conditions (structured, routable) |
| `when_not_to_use` | MUST | Disabling boundary (prevents over-triggering; wins over `when_to_use` on conflict) |

`when_to_use` should not be too broad. Runtime routing: does it match `when_to_use`? does it hit `when_not_to_use`? on conflict, `when_not_to_use` wins; if uncertain, ask the user.

---

## 10. `non_negotiable` + `enforced_by`

A red line = a declaration (NL `rule`) + **a binding to a real enforcement mechanism** (`enforced_by`). M4 machine-checks the binding reference, not the rule's complete semantics or its execution. The conforming runtime remains responsible for actual enforcement under R2.

`enforced_by` grammar (MUST point to a mechanism that actually exists):

| Form | Meaning | Verification |
|------|---------|--------------|
| `<node>.stepN:<mechanism>` | A `sys.*` at a specific numeric execution step (most precise, recommended), e.g. `interpret.step1:sys.assert` | node and numeric step exist, and that step begins with that mechanism |
| `aisop.main` | Enforced by graph topology (a required node/branch) | the corresponding required node/branch exists |
| `tools` | Enforced by the `tools` allow-list (a capability is not granted) | `tools` is restricted and the runtime truly enforces tool permissions |

> `enforced_by: tools` is a hard constraint **only when the runtime truly enforces tool permissions**; if the runtime does not enforce tool permissions, `tools` is only a declarative constraint and MUST NOT be counted as a hard guarantee.

---

## 11. `discovery`

| Sub-field | Description |
|-----------|-------------|
| `category` | Top-level category (registry / routing) |
| `tags` | Tag array (registry search) |

Used by `aisp_list.json` / registry / routing; may be omitted when there is no registry.

---

## 12. `risk_level`

`low` (read-only / analysis) / `medium` (writes locally) / `high` (delete / deploy / exfiltrate) / `critical` (mandatory human review or no autonomy). A single grade, for trust / registry; fine-grained governance comes from `sys.*` + `tools`.

**Semantic definitions:**

- **low** = read-only analysis or generation.
- **medium** = local file writes, local scripts, non-destructive changes.
- **high** = deletion, deployment, external sending, credentials, production impact.
- **critical** = legal / medical / financial / physical-safety or irreversible high-impact action.

`risk_level` is routing/governance metadata, NOT a hard enforcement mechanism — enforcement is via `sys.io.confirm` / `sys.assert` / tools / runtime policy.

---

## 13. `resources`

**resources = inventory; functions = usage.** The field declares "what exists, where, what kind, read or execute"; nodes actually use them via `sys.io.read` / `sys.run`.

| Sub-field | Required | Description |
|-----------|----------|-------------|
| `id` | MUST | Resource identifier |
| `path` | MUST | Relative path (`scope:skill` relative to the skill folder; `scope:shared` relative to `_shared/`) |
| `kind` | MUST | **Open vocabulary**: data / script / reference / asset / template / … |
| `mode` | MUST | **Controlled enum**: `read_only` / `execute_only` / `read_and_execute` (gates behavior) |
| `when` | MAY | When to load |
| `scope` | MAY | `skill` (default) / `shared` |
| `sha256` | MAY | Content hash for supply-chain integrity |
| `requires_tools` | MAY | Tools a script needs (least authority) |

Key points: custom layout; `resources` is the single source of truth for "what is a resource" (an undeclared file = unknown; a validator SHOULD warn); `kind` is open, `mode` is an enum (the security gate).

> Resource entries SHOULD include `sha256` when distributed through a registry (supply-chain integrity). It is omitted from in-repo examples to keep them clean; a registry records and verifies it at publication time.

> **Machine-readable schema.** The contract object is formally specified by [`schemas/aisp-contract-v1.schema.json`](https://github.com/AIXP-Labs/AISP/blob/main/schemas/aisp-contract-v1.schema.json) (JSON Schema draft 2020-12). It validates `profile` / `invocation` / `non_negotiable` as required, the `enforced_by` grammar, the `risk_level` and `mode` enums, and the optional `sha256` resource field.

---

## Part IV: Execution & Disclosure

## 14. What the Model Sees

★ The contract lives in the **user message** (`user.content.aisp_contract`) = it is already the model's live content this turn — **the model reads it directly, without depending on a runtime "render" step** (like an Agent Skills `SKILL.md` loaded into context). The `instruction` **commands the model to obey it via a strong directive**.

| Source | What the model gets | Who is responsible |
|--------|--------------------|--------------------|
| `user.content.instruction` | **Strong master directive**: `"STRICTLY OBEY aisp_contract; its non_negotiable rules are inviolable; then RUN aisop.main"` | The model sees it on reading the user message |
| `user.content.aisp_contract` | **Skill briefing**: triggering / red lines / governance / resources (read directly, treated as key content) | In the user message; the model reads it directly |
| `functions.<node>.stepN` | **Task instructions** (numeric execution steps; role / principles / knowledge are placed here) | The AISOP engine feeds them node by node |
| `enforced_by → sys.*` | **Hard guarantees** (confirm / assert / tool gate) | Enforced by the runtime (R2, MUST), regardless of whether the model "remembers" |
| `system_prompt` (system.content) | MAY be empty; or hold the actual model system prompt; or inject `{system_prompt}` | Author / runtime |

**Normative**:
- The contract is in the **user message** → the model reads it directly this turn (**no** separate runtime render step needed; R3 MUST NOT hide it).
- The `instruction` names the contract for obedience via a **strong directive** (OBEY / inviolable).
- `system_prompt` does not carry the contract (**MAY be empty**).
- The model's task instructions are **in functions**.
- **Soft-read + hard-stop, two layers**: the user-message contract exposes the red lines; a conforming runtime MUST enforce their bound mechanisms under R2. Hardness comes from actual enforcement of `sys.*`, required graph topology or genuinely restricted tools, not from model memory or the declaration alone. A mechanism-prefix match does not prove that an assertion was supported, evaluated or semantically sufficient.

> Context visibility is not proof of understanding or compliance. Runtime enforcement is a requirement, not a fact established by a static binding; unsupported or unverified results must not be presented as verified hard checks. Both layers are required.

---

## 15. Tier A Placement

| Skill content | Placed in |
|---------------|-----------|
| Role / principles / knowledge / constraints | `functions.<node>.step` + `constraints` |
| Failure handling | `aisop.main` branches / `-.->` error edges / `on_error` / `sys.io.confirm` |
| Structured output | `sys.llm.json`'s `schema` + final node `constraints` |
| Resource **usage** | `sys.io.read` / `sys.run` inside nodes (the inventory is in the contract's `resources`) |
| Tools | `tools` (an AISOP Core field) |
| Per-node dispatch (inline vs sub-agent) | `functions.<node>.execute_mode` (inherited AISOP field, §5.2.8) |
| Program identity | AISOP `summary` / `description` |
| **Triggering / red-line binding / discovery / risk / resource inventory** | **`user.content.aisp_contract`** |

`on_error` is inherited function-node metadata, distinct from a graph's
`error` edge and from `aisp_contract`. AISOP routes by exact type, category,
`default`, then the topology error fallback (§5.2.4). The reference static
checker verifies object shape and target-function existence, not actual error
dispatch or reachability in every graph context; those remain execution concerns.

> **`execute_mode` (dispatch fidelity).** Each node MAY declare `execute_mode`: `"inline"` (the default mode; runs in the current context and is right for short routing, classification, confirmation, and simple summarization) or `"agent"` (runs in an independent sub-agent and MAY be used for nodes that need isolation, independent context, multi-file work, web/source gathering, complex validation, generation, or high-impact decisions). Step count is not the sole criterion for choosing `agent`; short nodes may still be `agent` when isolation or impact justifies it. If omitted, the runtime falls back to `"inline"` and a conformant AISP validator emits `AISP_W_M1_EXECUTE_MODE_DEFAULT_INLINE`. Explicit values other than `"inline"` / `"agent"`, including null or container values, fail static conformance; they are not omitted declarations. A runtime MUST honor `agent` (**R7**): an `agent` node MUST be dispatched to a sub-agent and MUST NOT be collapsed inline. Nodes with more than 10 numeric `stepN` execution steps SHOULD be reviewed for `execute_mode: "agent"`; the reference validator warns when such a non-agent node remains inline. Metadata fields such as `step_note` are ignored by this heuristic and cannot satisfy `enforced_by`. This threshold is a review heuristic, not a restriction on using `agent` for shorter but high-isolation nodes. `execute_mode` is an inherited AISOP field (AISOP §5.2.8), a runtime dispatch attribute — **not** an `enforced_by` mechanism, and **not** part of the contract (it is Tier A, per-node).

---

## 16. Discovery & Progressive Disclosure

Discovery is **runtime-independent**: any agent with bash+python can run the script to discover skills; any agent that reads JSON (no python) can too — no dedicated AISP runtime required.

### 16.1 Three Discovery Paths

| Path | How | Properties |
|------|-----|------------|
| **Read the index (default)** | Read `aisp/aisp_list.json` | Fast, safe (no execution), language-agnostic; may be stale |
| **Run the script (refresh)** | bash `python -B aisp/aisp_list.py [--json]` | Fresh; `--json` regenerates the index; needs python + execute permission and avoids `__pycache__/` residue |
| **Direct glob (fallback)** | Read each `aisp/*_aisp/aisp.aisop.json`'s `aisp_contract` | The script's internal logic is exactly this |

### 16.2 Progressive Disclosure

```text
L1 metadata: aisp_list.json (or script output) — each skill's summary / invocation / discovery, lightweight routing.
L2 instructions: on a hit, load the full aisp/<id>/aisp.aisop.json (contract + aisop.main + functions).
L3 resources: nodes load via sys.io.read / sys.run on demand (per the resources inventory + AISP's fixed loading_mode: "node").
```

Triggering relies entirely on `aisp_contract.invocation` + `discovery` (replacing the SKILL.md description mechanism). `README.md` explains this discovery contract for human/AI readers.

---

## Part V: Security, Naming & Versioning

## 17. Security & Trust Model

Resources are the attack surface (scripts / templates / examples / remote URLs can hide malicious payloads). Rules:

1. `path` is relative, **confined to the skill folder or `_shared/`, no `../` escape** (M5). Resolve and confine `_shared/` itself to the containing `aisp/` directory before reading resources; an outward root link does not extend the package boundary.
2. Remote URLs are disabled by default and require user confirmation.
3. `mode` gating: `execute_only` scripts are not injected in full into the model; `read_only` is not executed. Reference static matching covers selected literal `sys.io.read`, `sys.run` and `sys.run.bg` calls, including call whitespace, ordinary quoted Python paths and dot/separator aliases. It distinguishes supported Python option clusters and file operands rather than assuming any `.py` argument is executed. Distinct scoped resources may share relative names. If every matching declaration forbids an operation, SE3 fails even when the target scope is ambiguous; otherwise unresolved literal use warns without proving the selected scope or combining permissions. This is not a complete shell/command parser and does not prove runtime enforcement.
4. Scripts use `requires_tools` for least authority; dangerous commands trigger `sys.io.confirm`.
5. **Trust is not self-declared** (M6) — `verified` / `trusted` / `safe` are judged by the runtime / registry / user / scanner.
6. The registry records provenance (source / commit / `contract_sha256` / `resources_sha256`).
7. A folder has a file not declared in `resources` → a validator SHOULD warn.
8. `aisp_list.py` is a script, so **running it = executing code**: it MUST be minimal, auditable, zero-dependency, and only write `aisp_list.json` with no other side effects; untrusted directories SHOULD prefer reading `aisp_list.json` (no execution), passing a trust gate before running the script.
9. **Axiom 0**: every skill inherits "Human Sovereignty and Wellbeing"; `sys.io.confirm` 🔒 cannot be bypassed.
10. **Read-only during execution**: an AISP runtime SHOULD treat skill packages (files and resources) as read-only during normal execution. Modifications happen only through a deliberate evolution/edit step. What a skill writes while it runs for its own use is executor cache, not formal content. By default it goes into the run's own working area inside the cache directory the host gives the executor, not into the skill's package; the user MAY choose another location, including through the executor's own cache-directory setting. Deleting the cache directory deletes this cache. With the default executor SoulRun, the cache directory is `<working folder>/.soulrun_cache`: SoulRun makes a numbered folder for each run, with its working files under `_work/`, AISP and AIAP programs share that one cache directory, and SoulRun keeps only its newest runs. Formal content, what the skill is meant to produce and keep, is not cache: where it goes is decided by the skill and the user (for example the Creator writes its product, with `.evolution_snapshot/` and `.version_history/`, into the product folder). A location inside the skill's own package departs from the read-only default above, may fail on hosts that keep skill folders read-only (for example Codex's `.agents` and Claude Code's sandboxed `.claude/skills`) and may be lost when a plugin is updated.

The reference discovery-script checker performs a bounded AST scan, not a proof of arbitrary Python behavior or a sandbox. Passing it does not authorize executing an untrusted script; manual review and the host trust gate remain necessary. Invalid encoding, non-file inputs and escaping discovery-script links fail inspection rather than crash or read outside the directory.

---

## 18. Naming Rules

| Identifier | Rule |
|------------|------|
| `aisp_contract` field name | Fixed; not `aisp_skill_contract` ("skill" is redundant — AISP already contains it) / not a bare `skill_contract` (lacks namespace) |
| Skill `id` (= folder name) | **MUST end with `_aisp`**; lowercase alphanumeric + underscore; e.g. `yijing_aisp`, `stock_analysis_aisp` |
| `profile` | `aisp.skill.v1` (detected by the `aisp.skill.` prefix) |
| Required `SKILL.md` interface `name` | `id` minus `_aisp` / converted to hyphens, lowercase; **MUST NOT contain "anthropic" / "claude"**; ≤ 64 (§20) |
| Declarative rule field | Use `non_negotiable`, **not `assert`** (`assert` is already `sys.assert`, a deterministic hard check — the opposite semantics); hardness comes from `enforced_by → sys.*` |

---

## 19. Versioning

The version-related fields of an `aisp.aisop.json`:

```text
system.content.protocol               = "AISP V1.0.0"   ← the protocol this file declares = AISP (protocol version)
system.content.license                = "Apache-2.0"        ← license (default Apache-2.0)
user.content.aisp_contract.profile    = "aisp.skill.v1"     ← skill-contract schema version (AISP, detected by prefix)
system.content.version                = "1.0.0"             ← the skill's own version
(structural base: still an AISOP V1.0.0 program — expressed by 2-message / aisop.main / sys.* structure, not the protocol field)
```

- **AISP protocol version** = this specification, **V1.0.0**; the `protocol` field literal is `AISP V1.0.0` (mirroring the AISOP "AISOP V1.0.0" style: capital V, no hyphen).
- **Base relationship**: an AISP file is structurally an AISOP V1.0.0 program; recording AISP in `protocol` is a **brand / protocol-authorship** declaration. The AISOP engine does not gate on the `protocol` value, so it executes normally. ⚠️ But **a tool that strictly gates on `protocol == "AISOP V1.0.0"` will reject it** — like `aisp_contract`, this is a known trade-off of "AISP depends on AISOP's open world" (§4 R4, §24).
- Compatibility: `profile` is detected by the `aisp.skill.` prefix; only a major change (`v1`) is considered incompatible.

---

## Part VI: Interoperability & Lifecycle

## 20. Interoperability

**Every conformant AISP skill MUST contain the generated same-folder `SKILL.md` Agent Skills compatibility interface (M7).** It is not optional, even for runtime-native packages. The sole business source of truth remains `aisp.aisop.json`; the interface contains only the fixed executor bootstrap, not copies of business nodes, resources or red lines.

`tools/aisp_skill_md.py` generates the canonical interface, titled `# AISP Skill (run with an executor)`, with the existing generated/source/generator markers. Its two-message bootstrap is identified by `run_with_executor_aisp`. This id denotes an internal interface program, **not another independently distributed skill**; do not recursively require a folder, README or SKILL.md for it.

Field projection:

| `SKILL.md` field | Projected from | Constraint |
|------------------|----------------|------------|
| `name` | Same-folder AISP `id` | Drop `_aisp`, convert underscores to hyphens, lowercase; it MAY differ from the `_aisp` folder name; never include `anthropic` or `claude` |
| `description` | `aisp_contract.invocation` + summary | Lossy discovery summary; max 1024 chars; injection-safe |
| `license` | `system.content.license` | Default `Apache-2.0` |
| `metadata.generated_from_aisp` | Generator marker | Literal `"true"` for generated bridges |
| `metadata.aisp_program` | Same-folder program path | MUST be `aisp.aisop.json`; no absolute path, URL, subdirectory, or `..` escape |
| `metadata.protocol` | Protocol marker | MUST be `AISP V1.0.0` |
| `metadata.bridge_mode` | Interface marker | MUST be `agent_skills_bridge` |

The reference projection puts the summary before up to two triggers and two exclusions, then truncates to fit 1024 characters. Later conditions may be absent. The description is only a lossy discovery summary, not the full invocation contract; complete conditions and exclusion precedence remain in `aisp_contract.invocation` and still apply under §9.

The canonical header uses `name`, `description`, `license` and `metadata`; it MUST NOT gain custom keys such as `compatibility`. JSON-quoted strings provide deterministic YAML escaping. The outer `license` derives from the business skill (`Apache-2.0` by default); the fixed bootstrap's own `license: Apache-2.0` covers that bootstrap only, not the business package.

### 20.1 Executor Configuration and Execution

The bootstrap's `system.content.params` contains exactly five non-empty launch strings (`executor`, `executor_version`, `executor_command`, `executor_install`, `executor_help`) and one `executor_version_policy` object. No duplicate or extra keys are allowed. `executor_version` is still the version-query command, not the constraint. The policy has exactly `requirement` and `source`:

```json
{
  "executor_version_policy": {
    "requirement": ">=1.0.1",
    "source": "latest_stable"
  }
}
```

The number above is an illustration, not a permanent protocol minimum. The bounded reference syntax is `>=X.Y.Z` or `==X.Y.Z`, using stable three-component numeric versions. `source` is `latest_stable` for an automatically resolved lower bound, or `explicit` for a user/author constraint. A `latest_stable` policy MUST use `>=`. Compare numeric components, not strings. Prerelease/ambiguous executor reports stop; the tool reports unsupported stable release forms rather than silently choosing an older default.

SoulRun is only the default adapter, **not a protocol dependency or required vendor**. On first generation or explicit refresh of its default-managed policy, the reference generator queries official PyPI for the latest non-development, non-prerelease, non-yanked stable release and freezes the concrete lower bound. Returned metadata must identify the SoulRun project; that consistency check is not independent provenance verification. Runtime compatibility checks do not query latest or replace the frozen bound; a required installation may access the package source after user consent. A stored explicit constraint takes precedence, even on refresh; a new explicit CLI constraint takes precedence over both. Other executors use their own launch commands and an explicit version constraint; this tool does not substitute SoulRun or invent another vendor's release resolver.

There is one version-gated bootstrap and one core decision: whether the configured executor's installed package version satisfies the frozen requirement. A match runs directly; proven absence or mismatch asks for a matching installation, then rechecks the same condition. Probe errors stop. The rows below illustrate that one rule under different constraints, not different bootstrap types.

| Requirement | Installed state | Bootstrap behavior |
|---|---|---|
| `>=1.0.0` | 1.0.0 or higher | Run directly without an installation/upgrade question |
| `>=1.0.0` | Missing or lower | Ask to install the latest stable release satisfying the bound |
| `==1.0.0` | Exactly 1.0.0 | Run directly |
| `==1.0.0` | Missing or any other version, including 1.0.1 | Ask to install exactly 1.0.0; explicitly disclose a downgrade |
| Either | Unknown report, permission denial, timeout or unusable executor | Stop; do not guess compatibility or automatically reinstall |

The installation command must target that policy: for the default adapter the generator produces `python -m pip install --upgrade "soulrun>=X.Y.Z"` or `python -m pip install "soulrun==X.Y.Z"`. When explicitly selecting or refreshing a policy, either exact generated command form (or the old unpinned default) is updated even if its previous constraint disagrees with the stored policy. An exact pin must never be replaced by an unpinned latest install. Preserve custom commands, but stop before installation if their target cannot be established; do not silently rewrite them. User refusal, installation failure, or a failed/unparseable/mismatching post-install version recheck means no execution and no automatic retry. Check the configured executor package version, not the AISP protocol or bundled engine version. Satisfying the version requirement does not bypass the skill's business confirmation gates.

A missing probe result requires evidence that the configured executor package or entry point is absent, including a missing executor module behind an available launcher such as `python -m`. Missing unrelated dependencies/helpers, invalid commands, permission denial, timeout and ambiguous failures are unusable, not permission to reinstall.

The default invocation passes the skill directory, project `.soulrun_cache` directory, user message file, and `--host-tool "agent=<host capability>"`; it adds no session id (§4.2).

The fixed bootstrap checks the frozen requirement, asks before installation/upgrade/downgrade when needed, rechecks after installation, then delegates to the executor. If installation is declined or unavailable, the skill does not run. In any environment, sandboxed or not, the host MUST NOT run the skill with an executor that does not satisfy executor_version_policy, even if an older installed version still works. The host MUST NOT bypass the executor to execute or continue the business program. Executor-mediated reads and user-requested review remain allowed. Before an executor exists, consent and version checks depend on the host; the bootstrap itself is not a hard runtime guarantee. See §4.2 for status distinctions and session boundaries.

### 20.2 Deterministic Generation

Generated output has three inputs: the business program, executor configuration (five launch strings plus the frozen version policy), and the generator revision (identify the actual tool by content digest). Default resolution supplies the concrete policy before rendering; it is not an implicit runtime dependency. No new configuration file, template registry or executor registry is required.

Registry manifest 1.1 adds `program_sha256` over the canonical complete two-message program to `package_sha256`. The schema still accepts legacy 1.0, which does not bind business-function edits. These are integrity domains, not archive-wide coverage: undeclared files and generated SKILL.md executor configuration are not automatically bound. Review or pin the actual interface separately; neither a matching hash nor its generated marker certifies commands, versions or trust. This artifact revision does not change AISP V1.0.0.

For the existing reference hash format, canonical JSON means `json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")`, followed by SHA-256. Object keys are sorted; array order is retained. Unicode is not normalized, numeric rendering follows the reference Python serializer, and NaN/Infinity are rejected. Resource-file hashes use the original file bytes without BOM or line-ending normalization. This documents the existing algorithm, not RFC 8785/JCS conformance or a new hash format.

`contract_sha256` hashes the contract object; `program_sha256` hashes the complete two-message array. `resources_sha256` hashes resource records in declaration order, each containing `id`, `path`, `scope` (default `skill`), `mode`, `kind`, `exists` and `sha256` (null for a missing file). `package_sha256` hashes only `manifest_version`, `protocol`, `skill_id`, `skill_version`, `contract_sha256`, `resources_sha256`, `resources` and, for 1.1, `program_sha256`; it does not add the host's resolved absolute package path or the manifest's top-level `skill_path`, `source` and `commit` fields. This is top-level manifest field selection, not recursive content filtering: same-named fields or path strings already present in the contract or program remain covered by the corresponding content hashes. The reference definition is `tools/aisp_hash.py`; reproductions need the same serialized input bytes, not merely semantically similar JSON.

| Existing input | Generation/preview | Read-only check |
|---|---|---|
| Missing interface | Defaults, first generation | FAIL M7 |
| Valid current bootstrap | Preserve launch strings and policy; derive/update name, description and license | Compare all three derived fields plus exact fixed interface |
| Damaged JSON, duplicate/missing/extra key, empty/non-string launch value or malformed policy | FAIL, no fallback | FAIL; file unchanged |
| Any other existing interface (an older generated version or an edited file) | FAIL, file unchanged; back up, note the five launch strings and version policy, delete, regenerate, then restore non-default values | FAIL M7; file unchanged |

To change executors, configure the five launch strings and explicit version policy, then check; normal regeneration preserves valid values without network access. For the default adapter, `--executor-version-requirement '>=1.0.0'` or `'==1.0.0'` updates a standard installation command consistently. `--refresh-executor-version` queries only for a default-managed policy and never overrides an explicit one. Missing default metadata, network failure or unsupported versions fail without a stored-version fallback. Batch generation resolves a default once and preflights every input before writing. `--check`/`--check-all` are offline/read-only and reject generation/refresh options. `--print` and `--write` share selection rules; preview never writes. Do not delete an existing configured interface to simulate a refresh, since that discards explicit choices. A later I/O failure reports completed, failed/possibly partial and not-attempted files, not a false all-or-none success.

Writing is UTF-8 without BOM, LF, with one trailing newline. Comparison strips a leading BOM, normalizes CRLF/CR to LF and trailing newlines. All other fixed text, JSON layout and metadata remain canonical. Core and bridge validators share one read-only M7 function that never calls back into core validation. Other resource, path and red-line failures remain visible.

Generation and validation:

```bash
python -B tools/aisp_skill_md.py examples --check-all
python -B tools/aisp_validate_agent_skill_bridge.py examples/aisp --strict-readme
```

A passing M7 check proves only unchanged bootstrap text and valid format, including the skill-derived header. It does not certify that the configured values denote an available or compatible executor; even `echo available`/`echo done` substitutes can satisfy string format. Bridge validation additionally checks existing frontmatter/path constraints and native package conformance. Neither proves external trust, safety, registry approval, runtime behavior or a completed run. Verify external provenance or obtain a user trust decision before running an untrusted package; package-contained generated markers cannot grant trust.

---

## 21. Lifecycle

A skill's generation, evolution, and distribution are **AISP-native and tool-agnostic** — handled by external tooling of the author's choice. AISP defines the *package* and the conformance a skill must satisfy at each stage (M1–M7), **not** the toolchain. The descriptions below specify what any conforming tool MUST do, regardless of implementation.

- **Generation**: a generator builds `aisp/<id>_aisp/aisp.aisop.json` (lean contract + rich Tier A) + custom resources; validates that `id` == the folder name and ends with `_aisp`, each `enforced_by` is real, resource paths are legal and function resources are declared; updates discovery; and generates per-skill `README.md` plus required same-folder `SKILL.md`. The skill MUST satisfy M1–M7. Finish resource/snapshot changes and manifests before regenerating interfaces and READMEs, then check read-only.
- **Evolution**: a change MAY edit contract fields (invocation / non_negotiable / discovery / risk / resources) or functions / aisop.main; changing resources enters a deliberate evolution/edit step with a changelog entry and a security scan; it MUST NOT delete safety constraints, lower `risk`, or expand `tools` without justification.
- **Registry / Distribution**: the unit of distribution is the skill folder. AISP is registry-agnostic and does not build or require a specific registry; any registry MAY index discovery + invocation + risk + provenance (hash). Trust / scoring / scanning are generated by the registry, never trusting self-declarations.

---

## Part VII: Examples & Honesty

## 22. Complete Example

`aisp/yijing_aisp/aisp.aisop.json` (the contract = `user.content.aisp_contract`, a real object; `system_prompt` left empty):

```json
[
  {
    "role": "system",
    "content": {
      "protocol": "AISP V1.0.0",
      "axiom_0": "Human_Sovereignty_and_Wellbeing",
      "id": "yijing_aisp",
      "name": "Yijing Divination",
      "version": "1.0.0",
      "license": "Apache-2.0",
      "summary": "Cast and interpret an I Ching (Yijing) hexagram for a user's question.",
      "description": "Native AISP skill: clarify the question, cast a hexagram randomly, and interpret it for reflection (not deterministic prediction).",
      "flow_format": "mermaid",
      "loading_mode": "node",
      "tools": ["filesystem", "code"],
      "params": { "question": "string" },
      "system_prompt": ""
    }
  },
  {
    "role": "user",
    "content": {
      "instruction": "STRICTLY OBEY aisp_contract; its non_negotiable rules are inviolable; then RUN aisop.main",
      "user_input": "{user_input}",
      "aisp_contract": {
        "profile": "aisp.skill.v1",
        "invocation": {
          "mode": "auto_or_manual",
          "when_to_use": ["cast an I Ching reading", "interpret a hexagram", "yijing divination for a question"],
          "when_not_to_use": ["medical, legal, or financial decisions needing a professional", "no question provided"]
        },
        "non_negotiable": [
          { "rule": "Follow RUN aisop.main; never interpret before casting.", "enforced_by": "aisop.main" },
          { "rule": "Do not interpret without a cast hexagram.", "enforced_by": "interpret.step1:sys.assert" },
          { "rule": "The reading must state it is for reflection, not deterministic prediction.", "enforced_by": "interpret.step4:sys.assert" }
        ],
        "discovery": { "category": "culture", "tags": ["yijing", "iching", "divination", "hexagram"] },
        "risk_level": "low",
        "resources": [
          { "id": "hexagrams", "path": "data/hexagrams.json", "kind": "data", "mode": "read_only" },
          { "id": "interpretation_guide", "path": "data/interpretation_guide.md", "kind": "reference", "mode": "read_only", "when": "interpreting the hexagram" }
        ]
      },
      "aisop": {
        "main": "graph TD\n    clarify[Clarify the question] --> cast[Cast hexagram]\n    cast --> interpret[Interpret]\n    interpret --> end_node((End))"
      },
      "functions": {
        "clarify": {
          "step1": "Identify the user's question and intent for the reading.",
          "output_mapping": "question"
        },
        "cast": {
          "step1": "sys.code.exec('python', 'import random, json; print(json.dumps([random.randint(6,9) for _ in range(6)]))') -> lines",
          "step2": "sys.io.read('data/hexagrams.json') -> hexagram_table",
          "step3": "Map lines (6/8 yin, 7/9 yang; 6/9 changing) to the primary and changing hexagram via hexagram_table.",
          "output_mapping": "hexagram"
        },
        "interpret": {
          "step1": "sys.assert('hexagram != null', 'No hexagram has been cast')",
          "step2": "sys.io.read('data/interpretation_guide.md') -> guide",
          "step3": "sys.llm.json('Interpret the hexagram for the question using guide; set disclaimer exactly to: For reflection only, not deterministic prediction.', schema={summary:'string', guidance:'string', changing_lines:'array', disclaimer:'string'}) -> reading",
          "step4": "sys.assert(\"reading.disclaimer == 'For reflection only, not deterministic prediction.'\", 'The required disclaimer must match the declared wording')",
          "step5": "Render reading as Markdown.",
          "constraints": ["Ground the interpretation in the cast hexagram and guide; do not fabricate hexagrams."]
        },
        "end_node": { "step1": "Return the final Markdown reading." }
      }
    }
  }
]
```

**Conformance check**: M1 legal AISOP program, `protocol: AISP V1.0.0`, `license: Apache-2.0` ✓; M2 folder `yijing_aisp/` == id, ends with `_aisp` ✓; M3 `aisp_contract` is a real object in the **user message**, profile `aisp.skill.v1`, contains invocation + non_negotiable ✓; M4 all three `enforced_by` are real (`aisop.main` / `interpret.step1:sys.assert` already-cast / `interpret.step4:sys.assert` disclaimer) ✓; `instruction` strongly names the contract for obedience ✓; resources used via `sys.code.exec` / `sys.io.read` in `cast` / `interpret` ✓; `system_prompt` empty (contract is in the user message and read directly; task instructions in functions; hard guarantees in sys.*) ✓.

> Domain contrast — `stock_analysis_aisp/`: the same format carries financial analysis (`tools:["filesystem","shell"]`; a red line "never place trades" `enforced_by:tools`; a not-advice disclaimer in the report `enforced_by:report.step2:sys.assert`; resources spanning data + script + `_shared`). See `examples/aisp/stock_analysis_aisp/`.

---

## 23. Conformance Checklist

Use this checklist as a release-readiness aid, not as a substitute for validator output, runtime trace evidence, registry provenance, or human review.

| Scope | Release check |
|-------|---------------|
| Skill identity | [ ] Legal AISOP program (required fields + `aisop.main`); `protocol: AISP V1.0.0`; `license` present or defaulted to Apache-2.0 |
| Entry path | [ ] `aisp/<id>/aisp.aisop.json`; `id` equals the folder name and ends with `_aisp` |
| Contract | [ ] `user.content.aisp_contract` is a real object in the user message; `profile` has versioned form `aisp.skill.v<major>`; contains `invocation` and `non_negotiable` |
| Run directive | [ ] `instruction` strongly names the contract and then runs the graph, e.g. `STRICTLY OBEY aisp_contract; ... then RUN aisop.main` |
| Red lines | [ ] Every `non_negotiable.enforced_by` target exists; high-risk actions use `sys.io.confirm` and/or `sys.assert` |
| Resources | [ ] Resource paths are relative and non-escaping; modes are declared; scripts declare `requires_tools`; remote use is gated |
| Trust language | [ ] The package does not self-declare trust, verification, or safety; external provenance remains outside the package |
| `aisp/` directory | [ ] Directory `README.md` exists; `aisp_list.json` / `aisp_list.py` are kept zero-dependency and index-only |
| Per-skill README | [ ] Published `*_aisp/README.md` files are generated from `aisp.aisop.json`; strict/release checks may fail missing, manual, drifted, bad-source, or unsupported-generator README files |
| Runtime | [ ] Runtime reads the contract, preserves it in the user message, honors open-world AISOP compatibility, enforces `enforced_by`, and does not bypass `sys.io.confirm` |
| Tier A | [ ] Role, principles, and knowledge live in functions; failures live in `aisop.main` / `sys.*`; structured output uses `sys.llm.json`; the graph has an end node |
| M7 compatibility interface | [ ] Same-folder SKILL.md exists; derived name/description/license and fixed executor-only bootstrap match; only valid launch strings and version policy vary; safe local pointer; no business logic copy or opt-out |

Reference tooling map:

- Static package validation: `tools/aisp_validate.py`; coverage details: [`docs/reference/validator-coverage.md`](https://github.com/AIXP-Labs/AISP/blob/main/docs/reference/validator-coverage.md).
- Generated README checks: `tools/aisp_readme.py`; trust boundary: [`docs/reference/generated-readme.md`](https://github.com/AIXP-Labs/AISP/blob/main/docs/reference/generated-readme.md).
- Optional bridge checks: `tools/aisp_validate_agent_skill_bridge.py`; coverage is summarized in the validator matrix.
- Runtime trace and registry evidence: [`docs/reference/registry-runtime-artifacts.md`](https://github.com/AIXP-Labs/AISP/blob/main/docs/reference/registry-runtime-artifacts.md). Trace checks prove only behaviors evidenced by a trusted trace source.

---

## 24. Honest Boundaries

1. **A bridge is not an executor**: the required generated SKILL.md supports discovery and executor handoff, not hard execution by itself. Without an available conforming executor (SoulRun by default), stop rather than self-execute. Installation consent and untrusted-package trust gates remain host/consumer responsibilities (§20).
2. **Dependency on AISOP's open world** (R4): two points — ① `aisp_contract` / `license` are keys outside the AISOP field table, relying on "tolerate extra keys"; ② the `protocol` value is `AISP V1.0.0`, relying on AISOP "not gating on the protocol value." The AISOP reference implementation satisfies both; but **a closed-world strict validator (rejecting unknown keys), or a tool that hard-checks `protocol == "AISOP V1.0.0"`, will reject** AISP files. The AISOP spec does not mandate such closed validation, but this is AISP's declared dependency.
3. **The structured payoff is on the machine side** (validation / evolution / registry / Axiom 0 chain + identity consistency), not model adherence; the only real guarantee is policy-as-code (`enforced_by → sys.*`); NL rules are policy-as-prompt (soft).
4. **Trust is not self-declared**; trust / verified are judged by the runtime / registry / user / scanner.
5. **"Skill" naming and Agent Skills**: "skill" is a generic word with low legal risk; differentiation comes from "executable + governable + complementary + export"; **zero Claude / Anthropic branding**; **trademark search before public release** (this specification is not legal advice).

---

## 25. Common Mistakes

1. Putting business logic in SKILL.md or omitting it as "optional" is wrong: business truth stays in aisp.aisop.json, while M7 requires the generated executor-only compatibility interface.
2. Stuffing the contract into `system_prompt` (JSON-in-string) ✗ → use `user.content.aisp_contract`, a real object.
3. Non-uniform file name / `id` ≠ folder name / not ending with `_aisp` ✗.
4. `enforced_by` points to a non-existent `node.stepN:mechanism`, or to metadata such as `node.step_note:mechanism` ✗.
5. Reading a resource not declared in `resources` / a `path` that escapes / an unconfirmed remote URL ✗.
6. Treating `kind` as an enum / `mode` as open vocabulary ✗ (it is reversed: kind is open, mode is the enum).
7. Treating `loading_mode` as a free strategy choice ✗ → AISP skills MUST use `loading_mode: "node"` for progressive disclosure.
8. Omitting `execute_mode` everywhere and assuming that proves dispatch behavior ✗ → omission falls back to inline with a warning; real `agent` dispatch requires trustworthy runtime evidence. The reference trace checker checks supplied claims for shape and consistency; it does not independently authenticate events.
9. Naming a declarative rule `assert` / duplicating Tier A in the contract (role / principles / failure / output written into the contract) ✗.
10. Self-declared trust / `Claude` or `Anthropic` appearing in branding ✗.
11. Treating generated `README.md` or a passing README check as proof of safety/trust ✗.
12. Treating `system_prompt` as the contract carrier (deprecated) / relying on the model to "remember" red lines instead of `sys.*` enforcement ✗.

---

## Appendix A: `aisp_contract` Skeleton

The content of `user.content.aisp_contract`:

```json
{
  "profile": "aisp.skill.v1",
  "invocation": { "mode": "auto_or_manual", "when_to_use": [], "when_not_to_use": [] },
  "non_negotiable": [ { "rule": "", "enforced_by": "node.stepN:mechanism | aisop.main | tools" } ],
  "discovery": { "category": "", "tags": [] },
  "risk_level": "low",
  "resources": [ { "id": "", "path": "", "kind": "data", "mode": "read_only", "when": "", "scope": "skill", "sha256": "", "requires_tools": [] } ]
}
```

> `sha256` is OPTIONAL; include it for registry-distributed skills (supply-chain integrity). See [`schemas/aisp-contract-v1.schema.json`](https://github.com/AIXP-Labs/AISP/blob/main/schemas/aisp-contract-v1.schema.json) for the machine-readable contract schema.

## Appendix B: Directory Skeleton

```text
aisp/
  README.md                         # MUST
  aisp_list.py  aisp_list.json      # SHOULD (discovery)
  <id>_aisp/                        # a skill (id == folder name, ends with _aisp)
    aisp.aisop.json
    README.md                       # SHOULD: generated from aisp.aisop.json
    data/ | scripts/ | <custom>/    # custom layout, declared in resources
    SKILL.md                        # MUST: generated Agent Skills compatibility interface
  _shared/                          # shared resources
```

## Appendix C: `aisp_list.py` (Zero-Dependency Reference)

```python
#!/usr/bin/env python3
"""aisp_list.py — discover AISP skills under this folder.

Scans <this_dir>/*_aisp/aisp.aisop.json, reads each skill's
user.content.aisp_contract, prints a human/AI-readable list, and (with --json)
writes aisp_list.json. Zero deps (stdlib). Side effect: only --json writes
aisp_list.json; --check is read-only and fails on drift. Any malformed
*_aisp package is a hard index error, not a silent skip.
  python -B aisp_list.py          # print the list
  python -B aisp_list.py --json   # also (re)generate aisp_list.json
  python -B aisp_list.py --check  # verify committed aisp_list.json
  python -B aisp_list.py --help   # print usage

Security guarantees (SE5 / ST1). This script MUST be zero-dependency (standard
library only) and human-auditable. It MUST NOT: access the network; import
third-party packages; execute skill scripts; modify any file except
aisp_list.json when --json is explicitly used; read files outside the aisp/
directory (except declared _shared metadata). The reference implementation below
meets all of these: it imports only standard-library modules, scans only
`*_aisp` folders under its own directory, and writes only
`aisp_list.json`.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
USAGE = """usage: python -B aisp_list.py [--json] [--check] [--help]

Discover AISP skills under this directory.

Options:
  --json   regenerate aisp_list.json from *_aisp/aisp.aisop.json folders
  --check  verify aisp_list.json is current without writing
  --help   show this help
"""

def _unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def _reject_constant(value):
    raise ValueError(f"non-JSON numeric constant: {value}")


def discover():
    skills = []
    errors = []
    for skill_dir in sorted(ROOT.glob("*_aisp")):
        if not skill_dir.is_dir() and not skill_dir.is_symlink():
            continue
        f = skill_dir / "aisp.aisop.json"
        try:
            resolved = f.resolve()
            if not resolved.is_relative_to(ROOT.resolve()) or not resolved.is_relative_to(skill_dir.resolve()):
                raise ValueError("skill entry escapes the discovery directory or its skill folder")
            data = json.loads(f.read_text(encoding="utf-8-sig"), object_pairs_hook=_unique_object, parse_constant=_reject_constant)
            if (not isinstance(data, list) or len(data) != 2
                    or any(not isinstance(message, dict) for message in data)
                    or [message.get("role") for message in data] != ["system", "user"]):
                raise ValueError("skill must have exactly system/user messages")
            sc = data[0]["content"]                  # system: id/name/summary metadata
            uc = data[1]["content"]                  # user: instruction/aisop/functions + aisp_contract
        except Exception as e:
            errors.append(f"{f}: {e}")
            continue
        if not isinstance(sc, dict):
            errors.append(f"{f}: system.content must be an object")
            continue
        if not isinstance(uc, dict):
            errors.append(f"{f}: user.content must be an object")
            continue
        if not isinstance(sc.get("name"), str) or not sc["name"].strip() or any(
            key in sc and not isinstance(sc[key], str) for key in ("summary", "description")
        ):
            errors.append(f"{f}: name/summary/description metadata has an invalid type")
            continue
        c = uc.get("aisp_contract", {})              # real object field in the user message
        skill_id = sc.get("id")
        if not isinstance(skill_id, str) or skill_id != skill_dir.name or not re.fullmatch(r"[a-z0-9_]+_aisp", skill_id):
            errors.append(f"{f}: system.content.id must match the _aisp folder name")
            continue
        if not isinstance(c, dict) or not isinstance(c.get("profile"), str) or not re.fullmatch(r"aisp\.skill\.v[0-9]+", c["profile"]):
            errors.append(f"{f}: missing versioned aisp.skill.v<major> profile")
            continue
        discovery = c.get("discovery", {})
        invocation = c.get("invocation")
        if not isinstance(discovery, dict) or not isinstance(invocation, dict):
            errors.append(f"{f}: discovery and invocation must be objects")
            continue
        if "risk_level" in c and c["risk_level"] not in ("low", "medium", "high", "critical"):
            errors.append(f"{f}: risk_level has an invalid value")
            continue
        if any(not isinstance(invocation.get(k), list) or not invocation[k]
               or any(not isinstance(v, str) for v in invocation[k])
               for k in ("when_to_use", "when_not_to_use")):
            errors.append(f"{f}: invocation lists must be non-empty string arrays")
            continue
        if ("category" in discovery and not isinstance(discovery["category"], str)) or (
            "tags" in discovery and (not isinstance(discovery["tags"], list)
                                     or any(not isinstance(tag, str) for tag in discovery["tags"]))
        ):
            errors.append(f"{f}: category/tags metadata has an invalid type")
            continue
        skills.append({
            "id": skill_id,
            "name": sc.get("name"),
            "summary": sc.get("summary") or sc.get("description", ""),
            "path": str(f.relative_to(ROOT.parent)).replace("\\", "/"),
            "category": discovery.get("category"),
            "tags": discovery.get("tags", []),
            "when_to_use": invocation["when_to_use"],
            "risk_level": c.get("risk_level"),
        })
    return skills, errors

def render_index(skills):
    return json.dumps({"aisp_list_version": "1.0", "skills": skills},
                      ensure_ascii=False, indent=2) + "\n"

def normalized(text):
    return text.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff").rstrip("\n")

def main():
    allowed_args = {"--json", "--check", "--help", "-h"}
    unknown_args = [arg for arg in sys.argv[1:] if arg not in allowed_args]
    if unknown_args:
        print(f"ERROR: unknown argument(s): {', '.join(unknown_args)}", file=sys.stderr)
        print(USAGE.rstrip(), file=sys.stderr)
        return 2
    if "--help" in sys.argv or "-h" in sys.argv:
        print(USAGE.rstrip())
        return 0
    skills, errors = discover()
    if errors:
        print("ERROR: cannot build AISP index:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    for s in skills:
        print(f"- {s['id']}: {s['summary']}  ->  {s['path']}")
    print(f"\n{len(skills)} AISP skill(s).")
    expected = render_index(skills)
    out = ROOT / "aisp_list.json"
    if ("--check" in sys.argv or "--json" in sys.argv) and out.is_symlink():
        print("ERROR: aisp_list.json must not be a symbolic link", file=sys.stderr)
        return 1
    if "--check" in sys.argv:
        if not out.exists():
            print(f"{out} is missing; run python -B aisp_list.py --json", file=sys.stderr)
            return 1
        try:
            actual = out.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as exc:
            print(f"ERROR: cannot read aisp_list.json: {exc}", file=sys.stderr)
            return 1
        if normalized(actual) != normalized(expected):
            print(f"{out} is stale; run python -B aisp_list.py --json", file=sys.stderr)
            return 1
        print("aisp_list.json ok")
        return 0
    if "--json" in sys.argv:
        try:
            if out.exists() and out.stat().st_nlink > 1:
                print("ERROR: refusing to overwrite a hardlinked aisp_list.json", file=sys.stderr)
                return 1
            out.write_text(expected, encoding="utf-8", newline="\n")
        except OSError as exc:
            print(f"ERROR: cannot write aisp_list.json: {exc}", file=sys.stderr)
            return 1
        print(f"Wrote {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

## Appendix D: `aisp_list.json` (Index Format)

```json
{
  "aisp_list_version": "1.0",
  "skills": [
    {
      "id": "yijing_aisp",
      "name": "Yijing Divination",
      "summary": "Cast and interpret an I Ching (Yijing) hexagram for a user's question.",
      "path": "aisp/yijing_aisp/aisp.aisop.json",
      "category": "culture",
      "tags": ["yijing", "iching", "divination", "hexagram"],
      "when_to_use": ["cast an I Ching reading", "interpret a hexagram", "yijing divination for a question"],
      "risk_level": "low"
    }
  ]
}
```

## Appendix E: Sources

- AISOP Specification — `specification/aisop-spec.md` (AISOP V1.0.0 — AISP's base)
- Agent Skills Specification — https://agentskills.io/specification
- Extend Claude with skills — https://code.claude.com/docs/en/skills
- Policy-as-Prompt (arXiv 2509.23994) — https://arxiv.org/html/2509.23994
- Under the Hood of SKILL.md: Semantic Supply-chain Attacks (arXiv 2605.11418)

## Appendix F: Minimal Slogan

```text
AISP = AI Skill Protocol (V1.0.0).
Skill = aisp/<id>_aisp/aisp.aisop.json + required same-folder generated SKILL.md + declared resources (including shared resources when used). M7 checks existence, derived header and fixed bootstrap; no opt-out.
Contract = user.content.aisp_contract (real object): invocation + non_negotiable.enforced_by + discovery + risk_level + resources.
Everything else → aisop.main / functions / sys.*. system_prompt may be empty.
Execution = AISOP through a conforming executor, SoulRun by default; no executor means stop, not self-execution. Lifecycle remains AISP-native and tool-agnostic. Agent Skills supplies the required compatibility interface, not business truth or trust.
Hard rules only via enforced_by → sys.*. Trust is never self-declared.
```

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
