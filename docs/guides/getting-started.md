# Getting Started

Welcome to the AI Skill Protocol. This guide introduces the core ideas behind AISP and helps you take your first steps toward building executable, governable, distributable AI skills.

---

## What You'll Learn

By the end of this guide you will understand:

1. What an AISP skill is and how it differs from a prose `SKILL.md`.
2. The shape of a skill folder and its `aisp.aisop.json` body.
3. Where the skill contract lives and why.

**AISP is not a framework or a library. It is a skill-package protocol** — a standard way to package an AISOP program into a discoverable, governable, distributable skill, built on AISOP for execution. Its lifecycle (generation / evolution / distribution) is AISP-native and tool-agnostic.

---

## Prerequisites

| Prerequisite | Why It Matters |
|--------------|----------------|
| Familiarity with JSON | A skill body (`aisp.aisop.json`) is JSON |
| Basic Mermaid (optional) | `aisop.main` is usually a Mermaid graph |
| Python 3.11+ (optional) | To run the zero-dependency reference tools and discovery script |

You do **not** need a special AISP runtime to *read* or *discover* skills — any agent that reads JSON can. You need an AISOP runtime only to *run* one.

---

## Key Concepts Quick Reference

| Term | Full Name | What It Is |
|------|-----------|------------|
| AISP | AI Skill Protocol | This protocol — packages an AISOP program as a skill |
| AISOP | AI Standard Operating Protocol | The execution language a skill body is written in |
| AIAP | AI Application Protocol | A sibling protocol in the AIXP family (not part of AISP's stack) |
| Skill folder | — | `aisp/<id>_aisp/` — one self-contained skill, folder name == id, ends with `_aisp` |
| Skill file | `aisp.aisop.json` | The skill body — a legal AISOP V1.0.0 program |
| Skill contract | `user.content.aisp_contract` | A real JSON object: invocation, red lines, discovery, risk, resources |
| Tier A / Tier S | execution / contract | `aisop.main`+`functions`+`sys.*` / the lean `aisp_contract` |

---

## Understanding the File Structure

A native AISP skill is one self-contained folder:

```text
aisp/
└── yijing_aisp/                # folder name == id, MUST end with _aisp
    ├── aisp.aisop.json         # the skill body (an AISOP V1.0.0 program)
    └── data/
        ├── hexagrams.json
        └── interpretation_guide.md
```

The skill body is a 2-message array. The `system` message holds identity metadata; the `user` message holds the strong `instruction`, the real-object `aisp_contract`, the `aisop.main` graph, and the per-node `functions`. Core conformance does **not** require `SKILL.md`, but generated or distributed skills SHOULD include a thin same-folder sidecar by default unless explicitly opted out.

---

## Your First Skill

The fastest way to learn is to read a working skill, then build one:

- Read [`examples/aisp/yijing_aisp/aisp.aisop.json`](https://github.com/AIXP-Labs/AISP/blob/main/examples/aisp/yijing_aisp/aisp.aisop.json) — a complete conformant skill package, executable by an AISOP-compatible runtime.
- Then follow [First AISP Skill](first-aisp-skill.md) to build it step by step.

---

## Next Steps

| Resource | Description |
|----------|-------------|
| [What is AISP?](../topics/what-is-aisp.md) | The problem AISP solves and why it exists |
| [First AISP Skill](first-aisp-skill.md) | Build the `yijing_aisp` skill from scratch |
| [Discovering Skills](discovering-skills.md) | How `aisp_list.py` / `aisp_list.json` work |
| [The Skill Contract](../topics/skill-contract.md) | Deep dive into `aisp_contract` |

---

## Summary

An AISP skill is a self-contained folder whose body is a real AISOP program, whose contract is a real object in the user message, and whose red lines are bound to real mechanisms. The skill is the program; hard guarantees come only from `enforced_by → sys.*`; trust is never self-declared.

---

> Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
