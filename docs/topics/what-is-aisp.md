# What is AISP?

The AI Skill Protocol (AISP) is a skill-package standard for AI. It defines how a reusable AI capability is **packaged**, **discovered**, **invoked**, and **governed** — turning a skill from prose advice into a self-contained, executable, governable unit. AISP exists because the current generation of AI skills lacks the foundational discipline that every other domain of software packaging takes for granted: a standard way to bundle, verify, and trust what gets shipped, with hard guarantees that hold regardless of whether the model "remembers" the rules.

---

## The Problem

Today's dominant skill format — Agent Skills (`SKILL.md`) — is Markdown prose plus progressive disclosure. That is excellent for portability and human readability, but it leaves three structural gaps.

### 1. Prose Skills Give No Executable or Governable Guarantee

A prose `SKILL.md` describes *what to do*. Its frontmatter and package layout can be validated, and hosts may provide their own controls; that does not by itself supply AISP's executable graph, required-node topology or contract bindings. AISP adds those structures while retaining the Agent Skills interface.

### 2. Trust by Prose

A prose skill can *say* "always confirm before deleting" or "never give financial advice," but nothing **stops** the model if it ignores the line. A red line written as a sentence is a hope, not a guarantee. Worse, a skill can simply *claim* to be `verified` or `safe` — self-declared trust that a consumer has no way to mechanically check.

### 3. Supply-Chain Risk of SKILL.md

Because a skill bundles resources (scripts, templates, data, sometimes remote URLs), and because those resources are loaded into a model's context or executed, `SKILL.md` packages carry a semantic supply-chain attack surface: undeclared files, path traversal, injected remote content, and over-broad tool authority. Prose offers no declared inventory of what counts as a resource, and no gate on how each is used.

---

## What is AISP?

AISP is an executable, governable skill package built on AISOP and bridged to agent platforms through the Agent Skills standard. Its business body is a real AISOP program; the generated same-folder SKILL.md is a required compatibility interface, not business truth:

```text
A native AISP skill =
    one folder  (folder = skill; folder name = id; MUST end with _aisp)
  + aisp.aisop.json  (an AISOP program: contract + execution graph + nodes + sys.*)
  + SKILL.md  (required generated compatibility interface, M7)
  + custom resources (data/ scripts/ … declared in aisp_contract.resources)
  + optional sibling aisp/_shared/ resources (declared with shared scope)
```

The skill's business source **is** the program. Its contract, `user.content.aisp_contract`, is a real JSON object in the user message carrying triggers, red-line bindings, discovery, risk and resource inventory. Hard guarantees require actual runtime enforcement of `sys.*`, graph topology or genuinely restricted tools. Static declarations alone are not enforcement; trust is **never** self-declared.

AISP does not rebuild an engine. Execution builds on **AISOP** (AISP's only base). Its lifecycle (generation / evolution / distribution) is AISP-native and tool-agnostic. AISP defines only the *package*.

---

## AISP vs Agent Skills

| | Agent Skills (`SKILL.md`) | **AISP (this protocol)** |
|---|---|---|
| Nature | Prose instructions + progressive disclosure | **Executable flow + governable** (AISOP graph + `enforced_by → sys.*` hard constraints) |
| Red lines | Sentences the model is asked to follow (soft) | `non_negotiable` bound to real mechanisms; machine-verifiable (M4) |
| Trust | Can self-declare `verified` / `safe` | **Never self-declared** (M6); judged by registry / scanner / user |
| Body | Markdown prose | A real AISOP V1.0.0 program (`aisp.aisop.json`) |
| Standardization | Cross-vendor open standard | AISP packaging plus a **required generated same-folder compatibility interface** |
| Relationship | — | **Complementary**, not a replacement |

Public framing: **"AISP is an executable, governable skill package built on AISOP and bridged to agent platforms through the Agent Skills standard."**

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

### soulrun.dev — Executor (Default, Replaceable)

SoulRun is the default reference executor; any conforming AISP/AISOP executor is allowed. It discovers skills, reads the contract, runs the graph, enforces real mechanisms and blocking gates, and dispatches agent nodes independently. No executor means no execution: hosts must not execute or continue the business program themselves. Five configuration strings and command exit 0 do not prove compatibility or completion.

```text
DEFINES   →  aisop.dev   (the execution language a skill is written in)
PACKAGES  →  aisp.dev    (the skill package: folder, contract, discovery, red lines)
EXECUTES  →  soulrun.dev (default reference executor; other conforming executors allowed)
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
│  Executor                               │  SoulRun by default; replaceable
└─────────────────────────────────────────┘
```

Complementary to AISP, **Agent Skills** provides the required generated same-folder compatibility interface (M7), handing execution to a conforming executor without duplicating the business program. No interface opt-out is allowed.

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Executable Skill IR** | The skill body is a real AISOP V1.0.0 program, not another `SKILL.md`. The skill is the program. |
| **Contract in the user message** | `user.content.aisp_contract` is a real object the model reads directly this turn — no JSON-in-string, no rendering gamble. |
| **Policy-as-code red lines** | `non_negotiable.enforced_by` binds rules to checkable mechanisms; actual hardness depends on runtime enforcement. |
| **Folder-per-skill, `_aisp` suffix** | One self-contained folder (name == `id`, ends with `_aisp`); zippable / hashable as a registry unit. |
| **Runtime-independent discovery** | `aisp_list.py` (zero-dependency) + `aisp_list.json` index + glob fallback. |
| **Two tiers** | Heavy execution (Tier A) / lean contract (Tier S); no duplication. |
| **Conformance** | M1–M7 (skill), R1–R7 (runtime), SE/ST (security), EC (ecosystem) — machine-verifiable. |
| **Required `SKILL.md` interface** | M7 requires the generated same-folder executor bootstrap, with no opt-out. One version condition chooses direct execution or a consented, rechecked installation; business logic remains in the AISP program. |
| **Axiom 0 enforcement** | Every skill inherits "Human Sovereignty and Wellbeing"; `sys.io.confirm` is forced-blocking. |

---

## Next Steps

- [Core Concepts](core-concepts.md) — the skill folder, the two tiers, the file anatomy.
- [The Skill Contract](skill-contract.md) — a deep dive into `user.content.aisp_contract`.
- [enforced_by & sys.*](enforced-by-and-sys.md) — how red lines become real guarantees.
- [Getting Started](../guides/getting-started.md) — your first steps with AISP.

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
