# What is AISP?

The AI Skill Protocol (AISP) is a skill-package standard for AI. It defines how a reusable AI capability is **packaged**, **discovered**, **invoked**, and **governed** — turning a skill from prose advice into a self-contained, executable, governable unit. AISP exists because the current generation of AI skills lacks the foundational discipline that every other domain of software packaging takes for granted: a standard way to bundle, verify, and trust what gets shipped, with hard guarantees that hold regardless of whether the model "remembers" the rules.

---

## The Problem

Today's dominant skill format — Agent Skills (`SKILL.md`) — is Markdown prose plus progressive disclosure. That is excellent for portability and human readability, but it leaves three structural gaps.

### 1. Prose Skills Give No Executable or Governable Guarantee

A `SKILL.md` describes *what to do* in natural language. There is no execution graph, no required-node topology, and no machine-checkable structure. The skill "works" only insofar as the model follows the prose. There is no compile-time object the way a real program has — nothing a tool can validate before the skill runs.

### 2. Trust by Prose

A prose skill can *say* "always confirm before deleting" or "never give financial advice," but nothing **stops** the model if it ignores the line. A red line written as a sentence is a hope, not a guarantee. Worse, a skill can simply *claim* to be `verified` or `safe` — self-declared trust that a consumer has no way to mechanically check.

### 3. Supply-Chain Risk of SKILL.md

Because a skill bundles resources (scripts, templates, data, sometimes remote URLs), and because those resources are loaded into a model's context or executed, `SKILL.md` packages carry a semantic supply-chain attack surface: undeclared files, path traversal, injected remote content, and over-broad tool authority. Prose offers no declared inventory of what counts as a resource, and no gate on how each is used.

---

## What is AISP?

AISP keeps the **spirit** of Agent Skills (a reusable capability, triggering, progressive disclosure, resources) and discards the **form** (the `SKILL.md` body). A native AISP skill is a self-contained folder whose body is a real **AISOP V1.0.0 program**:

```text
A native AISP skill =
    one folder  (folder = skill; folder name = id; MUST end with _aisp)
  + aisp.aisop.json  (an AISOP program: contract + execution graph + nodes + sys.*)
  + custom resources (data/ scripts/ … declared in aisp_contract.resources)
  + _shared/  (cross-skill shared resources)
```

The skill **is** the program. Its contract — `user.content.aisp_contract`, a real JSON object in the user message — carries lean metadata: when to trigger, the red lines bound to real enforcement, discovery tags, risk, and the resource inventory. Hard guarantees come **only** from `non_negotiable.enforced_by → sys.*`; trust is **never** self-declared.

AISP does not rebuild an engine. Execution builds on **AISOP** (AISP's only base). Its lifecycle (generation / evolution / distribution) is AISP-native and tool-agnostic. AISP defines only the *package*.

---

## AISP vs Agent Skills

| | Agent Skills (`SKILL.md`) | **AISP (this protocol)** |
|---|---|---|
| Nature | Prose instructions + progressive disclosure | **Executable flow + governable** (AISOP graph + `enforced_by → sys.*` hard constraints) |
| Red lines | Sentences the model is asked to follow (soft) | `non_negotiable` bound to real mechanisms; machine-verifiable (M4) |
| Trust | Can self-declare `verified` / `safe` | **Never self-declared** (M6); judged by registry / scanner / user |
| Body | Markdown prose | A real AISOP V1.0.0 program (`aisp.aisop.json`) |
| Standardization | Cross-vendor open standard | AISP's own; **can include a thin same-folder `SKILL.md` sidecar** |
| Relationship | — | **Complementary**, not a replacement |

Public framing: **"AISP does not replace Agent Skills; it provides executable, verifiable, governable skills alongside them, and can include a thin `SKILL.md` sidecar to interoperate with Agent Skills platforms."**

---

## Core Architecture

An AISP skill has two tiers — the *execution* tier (heavy) and the *contract* tier (lean).

| Tier | Holds | Where |
|------|-------|-------|
| **Tier A — execution** | flow / steps / role / principles / knowledge / failure / confirmation / validation / structured output / resource **usage** / tools / state | `aisop.main` + `functions` + `sys.*` + `tools` / `params` |
| **Tier S — contract** | triggering / red-line binding / discovery / risk / resource **inventory** | `user.content.aisp_contract` (a real object) |

The contract holds only what the execution tier cannot express, or what a consumer needs to know in advance. Everything else lives in Tier A.

---

## The Layered Chain

AISP sits on top of AISOP and is run by a reference executor. Each domain has one job.

### aisop.dev — Execution

Defines the `.aisop.json` language: the execution graph (Mermaid / JSON flow), the `sys.*` system-call family, and the system/user execution model. A skill body (`aisp.aisop.json`) is structurally a legal AISOP V1.0.0 program. Neutral, static, foundational.

### aisp.dev — Skill-Package (this protocol)

Defines the package itself: the folder-per-skill structure and `_aisp` suffix, the `aisp_contract` schema, discovery (`aisp_list.py` / `aisp_list.json`), and the `enforced_by → sys.*` red-line binding.

### soulbot.dev — Executor

The reference runtime: discovers skills, reads `user.content.aisp_contract`, runs `RUN aisop.main`, enforces every `non_negotiable.enforced_by` mechanism, gates resources, and never bypasses `sys.io.confirm`.

```text
DEFINES   →  aisop.dev   (the execution language a skill is written in)
PACKAGES  →  aisp.dev    (the skill package: folder, contract, discovery, red lines)
EXECUTES  →  soulbot.dev (the reference runtime)
```

---

## AISP in the Skill Stack

```text
┌─────────────────────────────────────────┐
│  HSAW / Axiom 0                          │  Human Sovereignty and Wellbeing
├─────────────────────────────────────────┤
│  ★ AISP — Skill-Package Layer            │  folder + aisp_contract + discovery
├─────────────────────────────────────────┤
│  AISOP — Execution Layer                 │  .aisop.json + sys.* (the skill body)
├─────────────────────────────────────────┤
│  SoulBot — Executor                      │  reference runtime
└─────────────────────────────────────────┘
```

Complementary to AISP, **Agent Skills** sits alongside as an interop target: a native AISP skill does not require `SKILL.md` for core conformance, but authoring and public-distribution workflows SHOULD add a thin same-folder `SKILL.md` sidecar bridge by default unless explicitly opted out.

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Executable Skill IR** | The skill body is a real AISOP V1.0.0 program, not another `SKILL.md`. The skill is the program. |
| **Contract in the user message** | `user.content.aisp_contract` is a real object the model reads directly this turn — no JSON-in-string, no rendering gamble. |
| **Policy-as-code red lines** | `non_negotiable.enforced_by → sys.*` binds each rule to a real mechanism. Only `sys.*` is a hard guarantee. |
| **Folder-per-skill, `_aisp` suffix** | One self-contained folder (name == `id`, ends with `_aisp`); zippable / hashable as a registry unit. |
| **Runtime-independent discovery** | `aisp_list.py` (zero-dependency) + `aisp_list.json` index + glob fallback. |
| **Two tiers** | Heavy execution (Tier A) / lean contract (Tier S); no duplication. |
| **Conformance** | M1–M6 (skill), R1–R7 (runtime), SE/ST (security), EC (ecosystem) — machine-verifiable. |
| **Default `SKILL.md` export** | A thin bridge for Agent Skills platforms generated by default unless explicitly opted out; never copies logic; deletable without breaking native AISP execution. |
| **Axiom 0 enforcement** | Every skill inherits "Human Sovereignty and Wellbeing"; `sys.io.confirm` is forced-blocking. |

---

## Next Steps

- [Core Concepts](core-concepts.md) — the skill folder, the two tiers, the file anatomy.
- [The Skill Contract](skill-contract.md) — a deep dive into `user.content.aisp_contract`.
- [enforced_by & sys.*](enforced-by-and-sys.md) — how red lines become real guarantees.
- [Getting Started](../guides/getting-started.md) — your first steps with AISP.

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
