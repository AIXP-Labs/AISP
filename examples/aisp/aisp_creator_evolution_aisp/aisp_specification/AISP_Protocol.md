# AISP V1.0.0 Skill-Package Specification

> **AISP defines the package. AISOP executes it.**
>
> AISP is an executable skill-package protocol, not another `SKILL.md` format.

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
- Default projections - generated per-skill `README.md` and same-folder thin `SKILL.md` sidecar bridges for distribution and interoperability. Core AISP conformance does not require `SKILL.md`, but authoring tools SHOULD generate it by default unless the author explicitly opts out.

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

- [20. Interoperability: Default SKILL.md Sidecar Bridge](#20-interoperability)
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
| `aisp.proto` | Discovery and conformance data structures and service APIs | **Authoritative** for data-object schemas and service contracts |

**Conflict resolution**: when any artifact appears to contradict another, this Markdown specification is the tie-breaker for *rules and structure*; `aisp.proto` is the tie-breaker for *data shapes and API signatures*. Translations (e.g. `AISP_Protocol_cn.md`) are always non-normative — the English text governs in case of divergence.

> **What this document is NOT.** AISP does not redefine the AISOP language (graph syntax, `sys.*` semantics) — that is `aisop.dev`. AISP does not delegate its lifecycle to another protocol; generation / evolution / distribution are AISP-native and tool-agnostic. AISP defines only the *skill package*: how an AISOP program becomes a discoverable, invocable, governable, distributable skill.

---

## 2. Core Definitions

> AISOP is the language a skill is written in. **AISP is the package.**

A **native AISP skill** is a **self-contained folder** containing one fixed-name AISOP program `aisp.aisop.json` plus that skill's own custom-layout resources. It expresses a **reusable, executable, governable, evolvable** capability using AISOP's own structure — it does **not** require or depend on an Agent Skills `SKILL.md`. A `SKILL.md` MAY exist only as a same-folder sidecar projection; authoring and distribution tools SHOULD include that sidecar by default unless the author explicitly opts out.

```text
A native AISP skill =
    one folder (folder = skill; folder name = id; MUST end with _aisp)
  + aisp.aisop.json (an AISOP program: contract + execution graph + nodes + sys.*)
  + custom resources (data/ scripts/ … declared in aisp_contract.resources)
```

| Concept | Analogy | Definition |
|---------|---------|------------|
| **AISOP** | Programming language (Python) | The execution language — `.aisop.json` files, Mermaid/JSON flow, `sys.*` calls. AISP's only base. |
| **AISP** | Package format + manifest (npm package, a Skill) | This protocol — packages an AISOP program into a discoverable, governable skill |
| **AISP skill** | A published package | A self-contained `aisp/<id>_aisp/` folder conformant to this specification |

### 2.1 The Skill Is the Program

Agent Skills (`SKILL.md`) describe a skill as Markdown prose plus progressive disclosure. AISP keeps the *spirit* of that (reusable capability, triggering, progressive disclosure, resources) and discards the *form* (the `SKILL.md` body). The truly executable subject is `aisp.aisop.json`, discovered and executed directly by an AISP/AISOP runtime. To run on an existing Agent Skills platform, authoring tools SHOULD add a thin same-folder `SKILL.md` sidecar bridge by default (§20), while authors MAY omit it for native-only packages.

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
| Standardization | Cross-vendor open standard | AISP's own; **can include a `SKILL.md` sidecar** to plug into those platforms |
| Relationship | — | **Complementary**: AISP provides the executable + governable that Agent Skills lack, and is backward-compatible via a default-generated but core-optional sidecar |

Public framing: **"AISP does not replace Agent Skills; it provides executable, verifiable, governable skills alongside them, and can include a thin `SKILL.md` sidecar to interoperate with Agent Skills platforms."**

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
- **M3** MUST contain `user.content.aisp_contract` (a real object) whose `profile` starts with `aisp.skill.`, and which contains `invocation` and `non_negotiable` (§8).
- **M4** Every `non_negotiable.enforced_by` MUST point to a mechanism that **actually exists** in the skill (§10).
- **M5** Each `resources[].path` (if any) MUST be a relative path, confined to the skill folder or `_shared/`, with no `../` escape (§17).
- **M6** A skill MUST NOT self-declare trust (`trusted` / `verified` / `safe`) — trust is judged by the consumer (§17).

### 4.2 Runtime Conformance

- **R1 (MUST)** An AISP runtime MUST read `user.content.aisp_contract` as the skill contract; MUST NOT skip required nodes of `aisop.main`; MUST NOT bypass `sys.io.confirm` (inherited from Axiom 0).
- **R2 (MUST)** For `non_negotiable`, the runtime MUST enforce the hard constraint via the mechanism its `enforced_by` points to.
- **R3 (MUST)** `aisp_contract` is in the **user message** — it is already part of the model's context this turn; the runtime MUST hand it to the model with the user message (it MUST NOT be hidden or stripped), and no separate "render" step is required. The `instruction` commands the model to obey the contract via a strong directive (e.g. `"STRICTLY OBEY aisp_contract; …; then RUN aisop.main"`).
- **R4 (MUST, dependency on the underlying AISOP runtime)** The underlying AISOP runtime MUST apply **open-world validation** to both `system.content` and `user.content` (tolerating unknown keys), so that the AISP fields `user.content.aisp_contract` and `system.content.license` coexist; and MUST NOT gate on the `protocol` value (it accepts `AISP V1.0.0`). The AISOP reference implementation `flow_runtime.py` satisfies this (it checks required fields only, does not reject extra keys, and does not validate the `protocol` value).
- **R5 (SHOULD)** Before handling an untrusted skill/resource, a runtime SHOULD pass it through a user trust gate; it SHOULD prefer reading `aisp_list.json` (no script execution, §16).
- **R6 (SHOULD)** A runtime SHOULD declare whether its tool enforcement is hard (permissions actually enforced) or advisory. If advisory, `enforced_by: tools` MUST NOT be treated as a hard guarantee.
- **R7 (MUST)** A runtime MUST honor each node's `execute_mode` — an inherited AISOP node-level field (AISOP spec §5.2.8). A node declared `execute_mode: "agent"` MUST be dispatched to an independent sub-agent and MUST NOT be collapsed inline; a node declared `"inline"` executes in the current context. If `execute_mode` is omitted, the runtime falls back to `inline` and the static validator emits a warning so the dispatch intent can be made explicit. A conformant AISP skill MUST NOT declare any explicit value other than `"inline"` or `"agent"`. This is the execution-fidelity guarantee. `execute_mode` is a dispatch attribute the runtime honors — NOT an `enforced_by` mechanism (§15).

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
| Sidecar bridge | A default-generated but core-optional same-folder `SKILL.md`, only for Agent Skills platform interop |

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
    README.md                  # SHOULD: generated bootstrap projection from aisp.aisop.json
    data/
      hexagrams.json
      interpretation_guide.md
  stock_analysis_aisp/
    aisp.aisop.json
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
7. No core-required `SKILL.md`; authoring tools SHOULD add a same-folder sidecar bridge by default for new or distributed skills unless the author explicitly opts out (§20).
8. Discovery: read `aisp/aisp_list.json` or run `aisp/aisp_list.py` via bash, with a glob fallback `aisp/*_aisp/aisp.aisop.json` (§16).

---

## 6. The `aisp/` Directory

| File | Level | Role |
|------|-------|------|
| `README.md` | **MUST** | Introduces (for human/AI): what this is, how to discover, how to run, how to add a skill (the human-readable version of the discovery contract) |
| `aisp_list.json` | SHOULD | Index cache: each skill's `id` / `name` / `summary` / `path` / `category` / `tags` / `when_to_use` / `risk_level` |
| `aisp_list.py` | SHOULD | Discovery script: globs `*_aisp/aisp.aisop.json`, reads `aisp_contract`, prints a list, `--json` regenerates the index (zero-dependency reference in Appendix C) |

**Truth model**: **the skill folder is the single source of truth; `aisp_list.py` is the generator; `aisp_list.json` is the cache.** The three do not compete — the folder wins; if the JSON is suspected stale, re-run the script.

Per-skill `README.md` is a generated projection for independent package bootstrap. A successful README check proves only consistency with `aisp.aisop.json`; it does not prove trust, safety, or registry approval. Generic non-AISOP agents can follow it only as best-effort guidance; hard guarantees require a conforming AISOP runtime.

---

## 7. The Skill File

`aisp.aisop.json` is an AISOP program containing two tiers:

| Tier | What it holds | Where |
|------|---------------|-------|
| **Tier A (execution, heavy)** | flow / steps / role / principles / knowledge / constraints / failure / confirmation / validation / structured output / resource reading / tools / state | `aisop.main` + `functions` + `sys.*` + `tools` / `params` |
| **Tier S (contract, lean)** | triggering, red-line binding, discovery, risk, resource inventory | `user.content.aisp_contract` (a real object) |

The contract holds only what the execution tier cannot express, or what the consumer needs to know in advance; everything else is placed in Tier A (§15).

---

## Part III: The Skill Contract

## 8. `aisp_contract` Fields

The skill contract is **`user.content.aisp_contract`** — a **real JSON object**, in the **user message**, alongside `instruction` / `user_input` / `aisop` / `functions`; the `instruction` commands the model to obey it via a strong directive (§14). (Program identity metadata `id` / `name` / `version` / `license` / `tools` / `params` stays in `system.content`.)

```json
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
| `profile` | MUST | `aisp.skill.v1` (the runtime detects it by the `aisp.skill.` prefix) |
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

A red line = a declaration (NL `rule`) + **a binding to a real enforcement mechanism** (`enforced_by`). This is what distinguishes AISP from a prose skill: **declaration ↔ enforcement is machine-verifiable.**

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
| `functions.<node>.step` | **Task instructions** (what each step does; role / principles / knowledge are placed here) | The AISOP engine feeds them node by node |
| `enforced_by → sys.*` | **Hard guarantees** (confirm / assert / tool gate) | Enforced by the runtime (R2, MUST), regardless of whether the model "remembers" |
| `system_prompt` (system.content) | MAY be empty; or hold the actual model system prompt; or inject `{system_prompt}` | Author / runtime |

**Normative**:
- The contract is in the **user message** → the model reads it directly this turn (**no** separate runtime render step needed; R3 MUST NOT hide it).
- The `instruction` names the contract for obedience via a **strong directive** (OBEY / inviolable).
- `system_prompt` does not carry the contract (**MAY be empty**).
- The model's task instructions are **in functions**.
- **Soft-read + hard-stop, two layers**: the model reads the red lines (policy-as-prompt, soft) + `enforced_by → sys.*` truly stops them (policy-as-code, hard). **Hard guarantees come only from `sys.*`** — whether the model "remembers" a red line does not affect the hard constraint.

> That is: the contract in the user message makes the model **necessarily read it** (no rendering gamble); `sys.*` makes the red line **necessarily enforced** (no memory gamble). Both layers are required.

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

> **`execute_mode` (dispatch fidelity).** Each node MAY declare `execute_mode`: `"inline"` (the default mode; runs in the current context and is right for short routing, classification, confirmation, and simple summarization) or `"agent"` (runs in an independent sub-agent and MAY be used for nodes that need isolation, independent context, multi-file work, web/source gathering, complex validation, generation, or high-impact decisions). Step count is not the sole criterion for choosing `agent`; short nodes may still be `agent` when isolation or impact justifies it. If omitted, the runtime falls back to `"inline"` and a conformant AISP validator emits `AISP_W_M1_EXECUTE_MODE_DEFAULT_INLINE`. Explicit values other than `"inline"` / `"agent"` fail static conformance. A runtime MUST honor `agent` (**R7**): an `agent` node MUST be dispatched to a sub-agent and MUST NOT be collapsed inline. Nodes with more than 10 numeric `stepN` execution steps SHOULD be reviewed for `execute_mode: "agent"`; the reference validator warns when such a non-agent node remains inline. Metadata fields such as `step_note` are ignored by this heuristic and cannot satisfy `enforced_by`. This threshold is a review heuristic, not a restriction on using `agent` for shorter but high-isolation nodes. `execute_mode` is an inherited AISOP field (AISOP §5.2.8), a runtime dispatch attribute — **not** an `enforced_by` mechanism, and **not** part of the contract (it is Tier A, per-node).

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

1. `path` is relative, **confined to the skill folder or `_shared/`, no `../` escape** (M5).
2. Remote URLs are disabled by default and require user confirmation.
3. `mode` gating: `execute_only` scripts are not injected in full into the model; `read_only` is not executed.
4. Scripts use `requires_tools` for least authority; dangerous commands trigger `sys.io.confirm`.
5. **Trust is not self-declared** (M6) — `verified` / `trusted` / `safe` are judged by the runtime / registry / user / scanner.
6. The registry records provenance (source / commit / `contract_sha256` / `resources_sha256`).
7. A folder has a file not declared in `resources` → a validator SHOULD warn.
8. `aisp_list.py` is a script, so **running it = executing code**: it MUST be minimal, auditable, zero-dependency, and only write `aisp_list.json` with no other side effects; untrusted directories SHOULD prefer reading `aisp_list.json` (no execution), passing a trust gate before running the script.
9. **Axiom 0**: every skill inherits "Human Sovereignty and Wellbeing"; `sys.io.confirm` 🔒 cannot be bypassed.
10. **Read-only during execution**: an AISP runtime SHOULD treat skill packages (files and resources) as read-only during normal execution. Modifications happen only through a deliberate evolution/edit step.

---

## 18. Naming Rules

| Identifier | Rule |
|------------|------|
| `aisp_contract` field name | Fixed; not `aisp_skill_contract` ("skill" is redundant — AISP already contains it) / not a bare `skill_contract` (lacks namespace) |
| Skill `id` (= folder name) | **MUST end with `_aisp`**; lowercase alphanumeric + underscore; e.g. `yijing_aisp`, `stock_analysis_aisp` |
| `profile` | `aisp.skill.v1` (detected by the `aisp.skill.` prefix) |
| `SKILL.md` sidecar `name` (if any) | `id` minus `_aisp` / converted to hyphens, lowercase; **MUST NOT contain "anthropic" / "claude"**; ≤ 64 (§20) |
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

**A native AISP skill does not require `SKILL.md` for core conformance.** To be discovered on Agent Skills platforms (Claude Code / Codex / Gemini / Copilot / Cursor), authoring tools SHOULD generate a thin same-folder `SKILL.md` sidecar bridge inside the native `*_aisp/` skill folder by default, unless the author explicitly opts out. The sidecar only guides loading and running the local `aisp.aisop.json`; it never copies logic; deleting it leaves the native AISP skill working under an AISP/AISOP runtime.

```markdown
---
name: yijing
description: Cast and interpret an I Ching (Yijing) hexagram for a question. Use when asked for a yijing/I Ching reading or hexagram interpretation. Do not use for medical, legal, or financial decisions needing a professional.
license: Apache-2.0
metadata:
  generated_from_aisp: "true"
  aisp_program: aisp.aisop.json
  protocol: AISP V1.0.0
  bridge_mode: native_sidecar
---

# Yijing Divination (AISP-backed)

This `SKILL.md` is a thin discovery bridge, not the source of truth.
The executable source of truth is the same-folder `aisp.aisop.json` (AISP V1.0.0 skill over an AISOP V1.0.0 program).
Runtime compatibility note: hard execution requires a conforming AISP/AISOP runtime; this bridge alone is only a discovery and loading guide.

When invoked:
1. Load `aisp.aisop.json`.
2. Execute `RUN aisop.main`.
3. Treat `user.content.aisp_contract` as the skill contract,
   `user.content.aisop.main` as the topology, `user.content.functions` as node ops.
4. Load resources (declared in `aisp_contract.resources`) only when a node reads them.
   Never skip required nodes.
```

Bridge field projection:

| `SKILL.md` field | Projected from | Constraint |
|------------------|----------------|------------|
| `name` | Same-folder AISP `id` | Drop `_aisp`, convert underscores to hyphens, lowercase; it MAY differ from the `_aisp` folder name; never include `anthropic` or `claude` |
| `description` | `aisp_contract.invocation` + summary | Include triggers and exclusions; max 1024 chars; injection-safe |
| `license` | `system.content.license` | Default `Apache-2.0` |
| `metadata.generated_from_aisp` | Generator marker | Literal `"true"` for generated bridges |
| `metadata.aisp_program` | Same-folder program path | MUST be `aisp.aisop.json`; no absolute path, URL, subdirectory, or `..` escape |
| `metadata.bridge_mode` | Bridge shape marker | SHOULD be `native_sidecar` for generated sidecars |
| `allowed-tools` | `system.content.tools` | Include only when the host platform supports the field |

Generated bridges MUST NOT invent custom top-level frontmatter keys such as `compatibility`; put runtime compatibility and hard-execution boundaries in the body text or in documented metadata accepted by the target platform.

Defaulting rule:

- Core AISP conformance: missing `SKILL.md` is allowed.
- Authoring/scaffold tools: generate `SKILL.md` by default unless the user opts out.
- Public examples, release packages, and registry distributions: SHOULD include `SKILL.md`; a missing sidecar is an ecosystem warning, not a core failure.

Sidecar generation and validation:

```bash
python -B tools/aisp_skill_md.py examples --check-all
python -B tools/aisp_validate_agent_skill_bridge.py examples/aisp --strict-readme
```

A passing sidecar generation check proves only that `SKILL.md` matches the deterministic projection from `aisp.aisop.json`. A passing bridge check proves only sidecar shape, safe same-folder pointer confinement, and native AISP validation. Neither proves external trust, registry approval, or hard execution on a non-AISOP platform.

---

## 21. Lifecycle

A skill's generation, evolution, and distribution are **AISP-native and tool-agnostic** — handled by external tooling of the author's choice. AISP defines the *package* and the conformance a skill must satisfy at each stage (M1–M6), **not** the toolchain. The descriptions below specify what any conforming tool MUST do, regardless of implementation.

- **Generation**: a generator builds `aisp/<id>_aisp/aisp.aisop.json` (lean contract + rich Tier A) + custom resources; validates that `id` == the folder name and ends with `_aisp`, that each `enforced_by` is real, that resource paths are legal, and that resources referenced by functions are declared; produces / updates `aisp_list.json`; and generates per-skill `README.md` plus the default same-folder `SKILL.md` sidecar unless the author explicitly opts out. A generated skill MUST still satisfy core M1–M6.
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
      "description": "Native AISP skill: clarify the question, cast a hexagram via a deterministic toss, and interpret it for reflection (not deterministic prediction).",
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
          "step3": "sys.llm.json('Interpret the hexagram for the question using guide', schema={summary:'string', guidance:'string', changing_lines:'array', disclaimer:'string'}) -> reading",
          "step4": "sys.assert(\"'reflection' in reading.disclaimer.lower() or 'not deterministic' in reading.disclaimer.lower()\", 'Reading must state it is for reflection, not deterministic prediction')",
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
| Contract | [ ] `user.content.aisp_contract` is a real object in the user message; `profile` starts with `aisp.skill.`; contains `invocation` and `non_negotiable` |
| Run directive | [ ] `instruction` strongly names the contract and then runs the graph, e.g. `STRICTLY OBEY aisp_contract; ... then RUN aisop.main` |
| Red lines | [ ] Every `non_negotiable.enforced_by` target exists; high-risk actions use `sys.io.confirm` and/or `sys.assert` |
| Resources | [ ] Resource paths are relative and non-escaping; modes are declared; scripts declare `requires_tools`; remote use is gated |
| Trust language | [ ] The package does not self-declare trust, verification, or safety; external provenance remains outside the package |
| `aisp/` directory | [ ] Directory `README.md` exists; `aisp_list.json` / `aisp_list.py` are kept zero-dependency and index-only |
| Per-skill README | [ ] Published `*_aisp/README.md` files are generated from `aisp.aisop.json`; strict/release checks may fail missing, manual, drifted, bad-source, or unsupported-generator README files |
| Runtime | [ ] Runtime reads the contract, preserves it in the user message, honors open-world AISOP compatibility, enforces `enforced_by`, and does not bypass `sys.io.confirm` |
| Tier A | [ ] Role, principles, and knowledge live in functions; failures live in `aisop.main` / `sys.*`; structured output uses `sys.llm.json`; the graph has an end node |
| Sidecar bridge | [ ] Same-folder `SKILL.md` is generated by default for authoring/distribution unless explicitly opted out; it uses official fields, legal `name`, safe `aisp.aisop.json` pointer, generated markers, and thin guidance only; it never copies AISP logic |

Reference tooling map:

- Static package validation: `tools/aisp_validate.py`; coverage details: [`docs/reference/validator-coverage.md`](https://github.com/AIXP-Labs/AISP/blob/main/docs/reference/validator-coverage.md).
- Generated README checks: `tools/aisp_readme.py`; trust boundary: [`docs/reference/generated-readme.md`](https://github.com/AIXP-Labs/AISP/blob/main/docs/reference/generated-readme.md).
- Optional bridge checks: `tools/aisp_validate_agent_skill_bridge.py`; coverage is summarized in the validator matrix.
- Runtime trace and registry evidence: [`docs/reference/registry-runtime-artifacts.md`](https://github.com/AIXP-Labs/AISP/blob/main/docs/reference/registry-runtime-artifacts.md). Trace checks prove only behaviors evidenced by a trusted trace source.

---

## 24. Honest Boundaries

1. **The cost of native-only = losing direct runnability on existing platforms**: `SKILL.md` is already supported by Claude Code / Codex / Gemini / Copilot / Cursor; a native AISP skill needs an AISP/AISOP runtime to run. Mitigation = default-generate the same-folder `SKILL.md` sidecar bridge for authoring/distribution while keeping it core-optional (§20). Stated plainly.
2. **Dependency on AISOP's open world** (R4): two points — ① `aisp_contract` / `license` are keys outside the AISOP field table, relying on "tolerate extra keys"; ② the `protocol` value is `AISP V1.0.0`, relying on AISOP "not gating on the protocol value." The AISOP reference implementation satisfies both; but **a closed-world strict validator (rejecting unknown keys), or a tool that hard-checks `protocol == "AISOP V1.0.0"`, will reject** AISP files. The AISOP spec does not mandate such closed validation, but this is AISP's declared dependency.
3. **The structured payoff is on the machine side** (validation / evolution / registry / Axiom 0 chain + identity consistency), not model adherence; the only real guarantee is policy-as-code (`enforced_by → sys.*`); NL rules are policy-as-prompt (soft).
4. **Trust is not self-declared**; trust / verified are judged by the runtime / registry / user / scanner.
5. **"Skill" naming and Agent Skills**: "skill" is a generic word with low legal risk; differentiation comes from "executable + governable + complementary + export"; **zero Claude / Anthropic branding**; **trademark search before public release** (this specification is not legal advice).

---

## 25. Common Mistakes

1. A skill embeds / depends on `SKILL.md` to run its logic ✗ → the truth is in `aisp.aisop.json`; `SKILL.md` is only a default-generated but core-optional sidecar bridge.
2. Stuffing the contract into `system_prompt` (JSON-in-string) ✗ → use `user.content.aisp_contract`, a real object.
3. Non-uniform file name / `id` ≠ folder name / not ending with `_aisp` ✗.
4. `enforced_by` points to a non-existent `node.stepN:mechanism`, or to metadata such as `node.step_note:mechanism` ✗.
5. Reading a resource not declared in `resources` / a `path` that escapes / an unconfirmed remote URL ✗.
6. Treating `kind` as an enum / `mode` as open vocabulary ✗ (it is reversed: kind is open, mode is the enum).
7. Treating `loading_mode` as a free strategy choice ✗ → AISP skills MUST use `loading_mode: "node"` for progressive disclosure.
8. Omitting `execute_mode` everywhere and assuming that proves dispatch behavior ✗ → omission falls back to inline with a warning; real `agent` dispatch is proven only by runtime trace evidence.
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
    SKILL.md                        # optional: Agent Skills sidecar bridge
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
meets all of these: it imports only `json` and `sys` from the stdlib, globs only
`*_aisp/aisp.aisop.json` under its own directory, and writes only
`aisp_list.json`.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
USAGE = """usage: python -B aisp_list.py [--json] [--check] [--help]

Discover AISP skills under this directory.

Options:
  --json   regenerate aisp_list.json from *_aisp/aisp.aisop.json folders
  --check  verify aisp_list.json is current without writing
  --help   show this help
"""

def discover():
    skills = []
    errors = []
    for f in sorted(ROOT.glob("*_aisp/aisp.aisop.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8-sig"))
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
        c = uc.get("aisp_contract", {})              # real object field in the user message
        skill_id = sc.get("id")
        if not skill_id:
            errors.append(f"{f}: missing system.content.id")
            continue
        if not isinstance(c, dict) or not str(c.get("profile", "")).startswith("aisp.skill."):
            errors.append(f"{f}: missing aisp.skill.* profile")
            continue
        skills.append({
            "id": skill_id,
            "name": sc.get("name"),
            "summary": sc.get("summary") or sc.get("description", ""),
            "path": str(f.relative_to(ROOT.parent)).replace("\\", "/"),
            "category": c.get("discovery", {}).get("category"),
            "tags": c.get("discovery", {}).get("tags", []),
            "when_to_use": c.get("invocation", {}).get("when_to_use", []),
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
    if "--check" in sys.argv:
        out = ROOT / "aisp_list.json"
        if not out.exists():
            print(f"{out} is missing; run python -B aisp_list.py --json", file=sys.stderr)
            return 1
        actual = out.read_text(encoding="utf-8-sig")
        if normalized(actual) != normalized(expected):
            print(f"{out} is stale; run python -B aisp_list.py --json", file=sys.stderr)
            return 1
        print("aisp_list.json ok")
        return 0
    if "--json" in sys.argv:
        out = ROOT / "aisp_list.json"
        out.write_text(expected, encoding="utf-8", newline="\n")
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
Skill = aisp/<id>_aisp/aisp.aisop.json + custom resources + _shared/. No core-required SKILL.md; authoring/distribution SHOULD include a same-folder sidecar by default unless opted out.
Contract = user.content.aisp_contract (real object): invocation + non_negotiable.enforced_by + discovery + risk_level + resources.
Everything else → aisop.main / functions / sys.*. system_prompt may be empty.
Execution = AISOP. Lifecycle (generation/evolution/distribution) = AISP-native, tool-agnostic. Complementary to Agent Skills (default-generated but core-optional SKILL.md sidecar).
Hard rules only via enforced_by → sys.*. Trust is never self-declared.
```

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
