# Interoperability with Agent Skills

AISP is designed to coexist with Agent Skills (`SKILL.md`), not to replace it. A native AISP skill does not require `SKILL.md` for core conformance, but authoring and public-distribution workflows SHOULD add a thin same-folder sidecar bridge by default unless the author explicitly opts out. This document explains where each layer sits, how the default-but-core-optional bridge works, and the honest cost of staying native.

---

## Introduction

Agent Skills is a cross-vendor open standard for prose-and-disclosure skills, already supported by major agent platforms. AISP occupies a layer Agent Skills does not address: an *executable, governable* skill whose body is a real AISOP program with machine-verifiable red lines. Rather than competing, AISP absorbs the spirit of Agent Skills and offers a same-folder sidecar bridge for interop.

---

## Each Layer in the Stack

| Layer | Role | Domain |
|-------|------|--------|
| **Agent Skills (`SKILL.md`)** | Prose instructions + progressive disclosure; cross-vendor portability | agentskills.io |
| **AISOP** | The execution language a skill body is written in — AISP's only base | aisop.dev |
| **AISP** | The skill package: folder, contract, discovery, `enforced_by → sys.*` | aisp.dev |

> **AIAP** and the other AIXP protocols (e.g. `aiap.dev`) are **sibling projects** in the AIXP family, not part of AISP's stack.

### Complementary, Not Competing

AISP keeps the **spirit** of Agent Skills — a reusable capability, triggering, progressive disclosure, resources — and discards its **form** (the Markdown body). What AISP adds is exactly what prose skills lack:

| Agent Skills lacks | AISP provides |
|--------------------|---------------|
| An executable body | A real AISOP V1.0.0 program (`aisp.aisop.json`) |
| Machine-verifiable red lines | `non_negotiable.enforced_by → sys.*` (M4) |
| A declared resource inventory + gates | `resources` with `mode` gating, path confinement |
| Trust that cannot be self-declared | M6 / SE6 — trust judged externally |

Public framing: **"AISP does not replace Agent Skills; it provides executable, verifiable, governable skills alongside them, and can include a thin `SKILL.md` sidecar to interoperate with Agent Skills platforms."**

---

## The Default `SKILL.md` Sidecar Bridge

A native AISP skill does not require `SKILL.md` for core conformance. For generated, scaffolded, or public-distribution packages, tooling SHOULD create a thin same-folder `SKILL.md` sidecar bridge by default unless the author explicitly opts out. The bridge only **guides** loading and running the local `aisp.aisop.json` — it never copies the logic, and deleting it leaves the skill fully working under an AISP/AISOP runtime.

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
The executable source of truth is the same-folder `aisp.aisop.json`.
Runtime compatibility note: hard execution requires a conforming AISP/AISOP runtime; this bridge alone is only a discovery and loading guide.

When invoked:
1. Load `aisp.aisop.json`.
2. Execute `RUN aisop.main`.
3. Treat `user.content.aisp_contract` as the skill contract,
   `user.content.aisop.main` as the topology, `user.content.functions` as node ops.
4. Load resources (declared in `aisp_contract.resources`) only when a node reads them.
   Never skip required nodes.
```

### Field Projection

| `SKILL.md` field | Projected from | Rule |
|------------------|----------------|------|
| `name` | Same-folder AISP `id` | Drop `_aisp`, convert underscores to hyphens, lowercase; **MUST NOT contain "anthropic" or "claude"**; ≤ 64 |
| `description` | `invocation` (`when_to_use` / `when_not_to_use`) | Includes triggers; ≤ 1024; injection-safe |
| `metadata.generated_from_aisp` | Generator/projection provenance | Must be `"true"` for generated bridges |
| `metadata.aisp_program` | Same-folder AISP package path | Must be `aisp.aisop.json`; no absolute path, URL, subdirectory, or `..` escape |
| `metadata.protocol` | `system.content.protocol` | `AISP V1.0.0` |
| `metadata.bridge_mode` | Bridge shape marker | SHOULD be `native_sidecar` for generated sidecars |
| `allowed-tools` | `tools` | Space-separated + scoped when supported by the host platform |
| `license` | `system.content.license` | Default `Apache-2.0` |

Generated bridges MUST NOT invent custom top-level frontmatter keys such as `compatibility`; put runtime compatibility and hard-execution boundaries in the body text or in documented metadata accepted by the target platform.

> The bridge is a projection, not a second source of truth. It guides a platform to load and run the AISOP program; the logic lives only in `aisp.aisop.json`.

### Generated-Projection Marker

A generated `SKILL.md` SHOULD declare its provenance in the frontmatter so consumers know it is a thin projection, not the source of truth:

```yaml
metadata:
  generated_from_aisp: "true"
  aisp_program: aisp.aisop.json
  protocol: AISP V1.0.0
  bridge_mode: native_sidecar
```

Add a one-line note in the body stating that the `SKILL.md` is a generated thin projection, not the source of truth. The native `aisp.aisop.json` remains authoritative; deleting the bridge leaves the skill fully working.

Validate bridge examples with:

```bash
python -B tools/aisp_skill_md.py examples --check-all
python -B tools/aisp_validate_agent_skill_bridge.py examples/aisp --strict-readme
```

A passing `aisp_skill_md.py --check` proves only sidecar projection consistency. A passing bridge check proves only bridge shape, safe same-folder path confinement, and native AISP validation. Neither proves external trust or hard execution on a non-AISOP platform. Missing `SKILL.md` is a core-conformant ecosystem warning unless a stricter release/generation profile required the default sidecar.

---

## The Honest Cost of Native-Only

A native AISP skill needs an AISP/AISOP runtime to run; it is **not** directly runnable on an Agent Skills platform without the sidecar bridge. This is a deliberate trade-off, stated plainly:

- **What you gain (native):** an executable body, machine-verifiable red lines, governed lifecycle, declared resources — guarantees prose cannot offer.
- **What you give up (native-only):** direct runnability on platforms that only understand `SKILL.md`.
- **The mitigation:** the default same-folder `SKILL.md` sidecar bridge restores discoverability on those platforms, with zero duplication of logic.

AISP also depends on AISOP's open-world validation (it tolerates the extra `aisp_contract` / `license` keys and does not gate on the `protocol` value). A closed-world validator that rejects unknown keys, or one that hard-checks `protocol == "AISOP V1.0.0"`, will reject AISP files — a declared dependency, not a defect.

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
