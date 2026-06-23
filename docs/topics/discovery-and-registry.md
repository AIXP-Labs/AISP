# Discovery & Registry

> AISP Protocol — Conceptual Guide
> Classification: Infrastructure

AISP skills do not exist in isolation. They are discovered on a file system, indexed for routing, and — when published — recorded in a registry with verifiable provenance. This document explains the three discovery paths, the truth model behind them, progressive disclosure, the discovery-script contract, and how a registry provides provenance (AISP is registry-agnostic).

---

## Introduction

Discovery in AISP is **runtime-independent**: any agent with `bash` + `python` can run the discovery script, and any agent that reads JSON (no `python`) can read the index. There is no dependency on a dedicated AISP runtime to *find* skills.

Paths in this document use `aisp/...` for a distributed AISP package. The repository examples live under `examples/aisp/...`.

---

## The Three Discovery Paths

| Path | How | Properties |
|------|-----|------------|
| **Read the index (default)** | Read `aisp/aisp_list.json` | Fast, safe (no execution), language-agnostic; may be stale |
| **Run the script (refresh)** | `python -B aisp/aisp_list.py [--json]` | Fresh; `--json` regenerates the index; needs `python` + execute permission and avoids `__pycache__/` residue |
| **Direct glob (fallback)** | Read each `aisp/*_aisp/aisp.aisop.json`'s `aisp_contract` | The script's internal logic, done by hand |

---

## The Truth Model

> The skill folder is the single source of truth. `aisp_list.py` is the generator. `aisp_list.json` is the cache.

The three do not compete. When the index and the folders disagree, the **folder wins**; re-running `python -B aisp/aisp_list.py --json` regenerates the index to match. The convention: read the JSON first; if it is missing, suspected stale, or you need the latest, run the script.

For this repository's examples, use `python -B examples/aisp/aisp_list.py --json` from the repository root.

```mermaid
graph LR
    F[skill folders &lt;id&gt;_aisp/] -- generator --> P[aisp_list.py]
    P -- --json --> J[aisp_list.json cache]
    J -. may be stale .-> F
```

---

## Progressive Disclosure

Triggering relies entirely on the contract's `invocation` + `discovery` (replacing the `SKILL.md` description mechanism). Disclosure proceeds in three levels:

```text
L1  metadata     →  aisp_list.json (or script output): each skill's
                    summary / invocation / discovery — lightweight routing.
L2  instructions →  on a hit, load the full aisp/<id>/aisp.aisop.json
                    (contract + aisop.main + functions).
L3  resources    →  nodes load via sys.io.read / sys.run on demand
                    (per the resources inventory + AISP's fixed loading_mode: "node").
```

`aisp/README.md` (MUST) explains this discovery contract for human and AI readers. Each `*_aisp/README.md` SHOULD be generated from `aisp.aisop.json` so an independently distributed skill folder remains self-describing. That file is bootstrap guidance only: it does not replace the contract, and a passing check is not a trust or safety proof.

---

## The `aisp_list.py` Contract

The reference script is zero-dependency (stdlib only). It globs `*_aisp/aisp.aisop.json`, reads each skill's `data[1].content.aisp_contract`, filters by the `aisp.skill.` profile prefix, prints a human/AI-readable list, and with `--json` writes `aisp_list.json`.

Extracted per skill: `id`, `name`, `summary`, `path`, `category`, `tags`, `when_to_use`, `risk_level`.

### Script Safety

> Running `aisp_list.py` = executing code.

The script MUST be:

- **Minimal** and **auditable** — small enough to read before running.
- **Zero-dependency** — stdlib only; no network calls, no `subprocess`, no deletion.
- **Side-effect-free except one write** — its only write target is `aisp_list.json`.

> Stated as guarantees (SE5): `aisp_list.py` MUST be zero-dependency (standard library only) and human-auditable. It MUST NOT: access the network; import third-party packages; execute skill scripts; modify any file except `aisp_list.json`; read files outside the `aisp/` directory (except declared `_shared` metadata).

For untrusted directories, a consumer SHOULD prefer **reading** `aisp_list.json` (no execution) and pass a trust gate before running the script. This is the same trust discipline applied to any skill resource (see [Security Model](security-model.md)).

---

## Registry & Provenance

When a skill is published, distribution and provenance are handled by **a registry** of the author's choice. AISP is registry-agnostic — it does not build or require a specific registry; the skill folder is the unit, and any conforming registry records provenance over it.

| Concern | Mechanism |
|---------|-----------|
| Unit of distribution | The skill folder (`aisp/<id>_aisp/`) — zippable / hashable |
| Provenance | `source` / `commit` / `contract_sha256` / `resources_sha256` recorded by the registry |
| Index fields | `discovery` + `invocation` + `risk_level` + provenance |
| Trust / scoring / scanning | **Generated by the registry — never trusting self-declarations** |

> A skill MUST NOT self-declare trust (`trusted` / `verified` / `safe`) — conformance rule M6 / SE6. The registry, scanner, or user judges trust; the skill only states facts (its `risk_level`, its declared resources).

The repository includes a zero-dependency provenance helper:

```bash
python -B tools/aisp_hash.py --json examples/aisp/yijing_aisp
```

The repository also includes a deterministic README projection helper:

```bash
python -B tools/aisp_readme.py examples/aisp/yijing_aisp --write
python -B tools/aisp_readme.py examples --check-all
```

The hash output follows [`schemas/registry-manifest-v1.schema.json`](../../schemas/registry-manifest-v1.schema.json). Runtime evidence follows [`schemas/runtime-trace-v1.schema.json`](../../schemas/runtime-trace-v1.schema.json). Optional tool permission declarations follow [`schemas/tool-capabilities-v1.schema.json`](../../schemas/tool-capabilities-v1.schema.json).

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
