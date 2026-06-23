# AISP — AI Skill Protocol

[中文版 README](README_CN.md)

[![Validate](https://github.com/AIXP-Labs/AISP/actions/workflows/validate.yml/badge.svg)](https://github.com/AIXP-Labs/AISP/actions/workflows/validate.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Protocol](https://img.shields.io/badge/Protocol-AISP_V1.0.0-brightgreen.svg)](https://aisp.dev)
[![Python](https://img.shields.io/badge/Python-%3E%3D3.11-blue.svg)](pyproject.toml)
[![Axiom 0](https://img.shields.io/badge/Axiom_0-Human_Sovereignty_and_Wellbeing-orange.svg)](GOVERNANCE.md)

**AISP packages executable, governable, distributable AI skills as self-contained skill folders.**

It is not another `SKILL.md` format. AISP defines the skill package; AISOP executes the program inside it.

[Specification](specification/AISP_Protocol.md) | [Quick Start](#quick-start) | [Examples](#examples) | [Release Evidence](docs/reference/release-evidence-matrix.md) | [Validator Coverage](docs/reference/validator-coverage.md) | [AIXP Labs](#aixp-labs-aixpdev)

| Fact | Value |
|------|-------|
| Protocol | AISP V1.0.0 |
| Full name | AI Skill Protocol |
| Authority | [aisp.dev](https://aisp.dev) |
| Execution layer | [aisop.dev](https://aisop.dev) |
| Runtime example | [soulbot.dev](https://soulbot.dev) |
| Foundational axiom | Human Sovereignty and Wellbeing |

## What is AISP?

AISP defines the **skill-package layer** for AI. While [Agent Skills](https://agentskills.io/specification) (`SKILL.md`) describe a skill as prose plus progressive disclosure, AISP addresses a different problem: how to package a skill as a **real executable program** with a machine-checkable contract, declared resources, validation rules, and a distribution lifecycle.

A native AISP skill is a folder `aisp/<id>_aisp/` containing one fixed-name AISOP program `aisp.aisop.json` plus that skill's resources. The execution body is an AISOP program; the skill contract is `user.content.aisp_contract` (a real JSON object); generation, evolution, and distribution are handled by external tooling of the author's choice.

**Core philosophy**: hard guarantees are enforced, not hinted. Red lines bind to real mechanisms through `non_negotiable.enforced_by -> sys.*`, `aisop.main`, or restricted tools. Trust is never self-declared.

**Complementary, not a replacement**: AISP does not replace Agent Skills. It provides executable and governable skill packages. Core conformance does not require `SKILL.md`, but authoring and distribution tools SHOULD include a thin same-folder `SKILL.md` sidecar by default for Agent Skills platforms unless the author opts out.

## Repository Scope

| This repository contains | Purpose |
|--------------------------|---------|
| `specification/` | The normative protocol specification, conformance standards, and Proto schema |
| `schemas/` | JSON Schemas for contracts, runtime traces, registry manifests, and tool capabilities |
| `tools/` | Zero-dependency reference validators, hash tools, README generator, and bridge checker |
| `examples/aisp/` | Native AISP skill packages used for examples and validation |
| `docs/` | Guides, references, ADRs, lifecycle notes, and trust-boundary documentation |
| `tests/` | Regression tests and invalid/valid fixtures |

This repository does **not** bundle a production AISOP runtime, registry service, or trust authority. You can read, discover, validate, hash, and inspect skills here. To execute a skill, use an AISOP-compatible runtime that honors AISP's runtime rules.

## Key Features

- **Executable Skill IR** — the skill body is a legal AISOP V1.0.0 program (`aisop.main`, `functions`, `sys.*`), not prose instructions.
- **Contract in the User Message** — `user.content.aisp_contract` is a real JSON object that the model reads directly this turn.
- **Policy-as-Code Red Lines** — `non_negotiable.enforced_by` binds rules to real mechanisms; only runtime-enforced mechanisms are hard guarantees.
- **Folder-per-Skill** — one skill is one self-contained folder; folder name equals `id` and ends with `_aisp`.
- **Runtime-Independent Discovery** — `aisp_list.json`, `aisp_list.py`, and folder globbing let agents discover skills without executing a runtime.
- **Two Tiers** — Tier A holds executable structure and operations; Tier S holds invocation, red lines, discovery, risk, and resource inventory.
- **Machine-Checkable Conformance** — M/R/SE/EC rule families make package, runtime, security, and ecosystem expectations explicit.
- **Default `SKILL.md` Sidecar Bridge** — native skill folders SHOULD include a thin Agent Skills sidecar by default for generated/distributed packages; it guides loading `aisp.aisop.json`, never copies executable logic, and remains optional for core conformance.
- **Axiom 0 Enforcement** — every skill inherits Human Sovereignty and Wellbeing; `sys.io.confirm` remains forced-blocking.

## Protocol Stack

```text
Application layer
      |
AISP  - skill-package layer (this protocol)
      |
AISOP - execution layer (.aisop.json flow programs)
      |
AISOP-compatible runtime (SoulBot is one example)
```

AISP packages an AISOP program into a discoverable, invocable, governable, distributable skill unit. It builds on AISOP for execution and does not redefine the engine. Each layer independently upholds Axiom 0.

## Quick Start

Prerequisite: Python 3.11 or newer. The reference tools use only the Python standard library at runtime; `jsonschema` is needed only for the schema-focused test coverage.

For the full test suite, install the optional development dependency once:

```bash
python -m pip install -e ".[dev]"
```

### 1. Inspect the package shape

Normative AISP packages use this shape:

```text
aisp/
└── yijing_aisp/            # folder name == id, MUST end with _aisp
    ├── README.md           # generated bootstrap projection
    ├── SKILL.md            # default Agent Skills sidecar projection; core-optional
    ├── aisp.aisop.json     # fixed filename; the skill body
    └── data/
        ├── hexagrams.json
        └── interpretation_guide.md
```

In this repository, example packages live under `examples/aisp/`:

```text
examples/aisp/
├── README.md
├── aisp_list.json
├── aisp_list.py
├── _shared/
├── yijing_aisp/
├── stock_analysis_aisp/
└── aisp_creator_evolution_aisp/
```

### 2. Read the contract excerpt

The complete example is [`examples/aisp/yijing_aisp/aisp.aisop.json`](examples/aisp/yijing_aisp/aisp.aisop.json). Its contract lives in the user message:

```json
{
  "role": "user",
  "content": {
    "instruction": "STRICTLY OBEY aisp_contract; its non_negotiable rules are inviolable; then RUN aisop.main",
    "aisp_contract": {
      "profile": "aisp.skill.v1",
      "invocation": {
        "mode": "auto_or_manual",
        "when_to_use": ["..."],
        "when_not_to_use": ["..."]
      },
      "non_negotiable": [
        { "rule": "...", "enforced_by": "interpret.step1:sys.assert" }
      ],
      "discovery": { "category": "culture", "tags": ["..."] },
      "risk_level": "low",
      "resources": [
        { "id": "hexagrams", "path": "data/hexagrams.json", "kind": "data", "mode": "read_only" }
      ]
    }
  }
}
```

### 3. Discover example skills

```bash
# Read the generated index safely; no scripts are executed.
python -B -m json.tool examples/aisp/aisp_list.json

# Regenerate the index by scanning the example skill folders.
python -B examples/aisp/aisp_list.py --json
```

The skill folder is the source of truth. `aisp_list.py` is the generator, and `aisp_list.json` is a cache.

### 4. Validate before execution

Minimum local check:

```bash
python -B tools/aisp_validate.py examples/aisp
python -B tools/aisp_readme.py examples --check-all
python -B tools/aisp_skill_md.py examples --check-all
python -B tools/aisp_validate_agent_skill_bridge.py examples/aisp --strict-readme
```

Full release-style gate:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\release_check.ps1
```

Use `-IncludePytest` to also run pytest without writing `.pytest_cache/`, and
use `-RequireClean` only for the final pre-publish clean-tree check. The expanded
CI-equivalent command list is:

```bash
python -B tools/aisp_validate.py examples/aisp
python -B tools/aisp_validate.py --json examples/aisp/yijing_aisp
python -B tools/aisp_validate.py --strict-tools --runtime-trace examples/aisp/stock_analysis_aisp/evals/runtime-traces/hard-pass.json examples/aisp/stock_analysis_aisp
python -B tools/aisp_validate.py --strict-tools --runtime-trace examples/aisp/aisp_creator_evolution_aisp/evals/runtime-traces/hard-pass.json examples/aisp/aisp_creator_evolution_aisp
python -B tools/aisp_check_runtime_trace.py examples/aisp/stock_analysis_aisp examples/aisp/stock_analysis_aisp/evals/runtime-traces/hard-pass.json
python -B tools/aisp_check_runtime_trace.py examples/aisp/aisp_creator_evolution_aisp examples/aisp/aisp_creator_evolution_aisp/evals/runtime-traces/hard-pass.json
python -B tools/aisp_hash.py --json examples/aisp/yijing_aisp
python -B examples/aisp/aisp_list.py --check
python -B tools/aisp_readme.py examples --check-all
python -B tools/aisp_skill_md.py examples --check-all
python -B tools/aisp_validate.py --strict-readme examples/aisp
python -B tools/aisp_validate_agent_skill_bridge.py examples/aisp --strict-readme
python -B tools/check_doc_sync.py --root .
python -B tools/check_markdown_links.py --root .
git diff --check
git diff --exit-code
git status --porcelain=v1 --untracked-files=all
python -B -m unittest discover -s tests
```

`git diff --exit-code` catches tracked file drift. `git status --porcelain=v1 --untracked-files=all` must print nothing for the final clean-tree check; it catches both tracked drift and untracked generated artifacts.

For what each command proves, what warnings are expected, and where runtime evidence is required, see the [Release Evidence Matrix](docs/reference/release-evidence-matrix.md). In static-only validation, `AISP_W_R6_TOOLS_CONDITIONAL` is an honest signal for `enforced_by: tools`, not a failure by itself.

Regenerate derived files only when you intentionally update them:

```bash
python -B examples/aisp/aisp_list.py --json
python -B tools/aisp_readme.py examples/aisp/yijing_aisp --write
python -B tools/aisp_skill_md.py examples/aisp/yijing_aisp --write
```

### 5. Execute with an AISOP runtime

This repository validates and packages skills; it does not claim to execute them by itself. To run a skill, load the target `aisp.aisop.json` into an AISP/AISOP-compatible runtime and then execute `RUN aisop.main`.

For example, an AISP/AISOP runtime would load:

```text
examples/aisp/yijing_aisp/aisp.aisop.json
```

and then execute the graph in `user.content.aisop.main` while honoring the contract in `user.content.aisp_contract`.

## Validation Boundaries

The reference toolchain is a conformance gate, not a trust oracle.

| Check | Proves | Does not prove |
|-------|--------|----------------|
| Static validator | M1-M6 plus static SE/EC package checks | Full runtime behavior or external trust |
| Runtime trace checker | R-series behavior evidenced by the trace | That an unsigned trace source is trustworthy |
| Generated README check | Consistency with `aisp.aisop.json` | Skill safety, trust, or registry approval |
| Hash tool | Recomputable local integrity records | Safety, endorsement, or provenance by itself |
| SKILL.md generator/check | Consistency of the default same-folder sidecar projection | Agent Skills platform behavior, safety, or external trust |
| Bridge validator | Safe thin `SKILL.md` sidecar shape and native AISP validation | Hard execution guarantees on non-AISOP platforms |

Missing `SKILL.md` is an EC7 warning, not a core AISP failure. Authoring, distribution, or creator release profiles may upgrade that missing default sidecar to a failure unless the author explicitly opts out.

`enforced_by: tools` remains conditional in static-only mode. It becomes hard only with event-backed runtime trace evidence or provenance-bearing hard tool capability evidence; a bare `tool_enforcement: "hard"` self-attestation is not enough for `--strict-tools`.

## Examples

Working examples demonstrate native AISP packages; public examples include same-folder Agent Skills `SKILL.md` sidecars by default while keeping them core-optional.

### Native AISP examples

| # | Skill | Risk | Demonstrates |
|---|-------|:----:|-------------|
| 1 | [`yijing_aisp/`](examples/aisp/yijing_aisp/) | **low** | Single-skill read-only divination; deterministic graph; `enforced_by -> sys.assert`; default same-folder `SKILL.md` sidecar |
| 2 | [`stock_analysis_aisp/`](examples/aisp/stock_analysis_aisp/) | **medium** | Stock analysis example; declared data/script/eval resources; `enforced_by -> tools` conditional boundary closed by example-local runtime trace evidence for release checks; default same-folder `SKILL.md` sidecar |
| 3 | [`aisp_creator_evolution_aisp/`](examples/aisp/aisp_creator_evolution_aisp/) | **medium** | Meta-skill for AISP creation/evolution/conversion; strict candidate validation; default same-folder `SKILL.md` sidecar |

### AISP Creator / Evolution Example

This repository includes a native AISP creator/evolution example at [`examples/aisp/aisp_creator_evolution_aisp/`](examples/aisp/aisp_creator_evolution_aisp/). It demonstrates how an AISP skill can help create, evolve, research, validate, and review other native AISP skills while staying inside the AISP package model. The example bundles specification snapshots, schemas, reference tools, templates, and replayable eval evidence for offline review.

The creator is an example skill, not a trust authority or production runtime. Its bundled snapshots and manifests provide local reference and integrity evidence only; they do not prove upstream trust, freshness, or registry approval. Generated or evolved skills must still pass the reference validators, README derivation checks, human review gates, and any external provenance or registry checks required by the publisher.

See [`examples/README.md`](examples/README.md) for the discovery walkthrough and the `aisp/` directory contract.

## Documentation

| Document | Description |
|----------|-------------|
| [AISP Protocol Specification](specification/AISP_Protocol.md) / [Chinese](specification/AISP_Protocol_cn.md) | Full protocol specification |
| [Conformance Standards](specification/standards/) | Machine-verifiable M / R / SE / EC conformance rules |
| [Conformance Walkthrough](docs/guides/conformance-walkthrough.md) / [Chinese](docs/guides/conformance-walkthrough_CN.md) | How to run and interpret validator output |
| [Release Evidence Matrix](docs/reference/release-evidence-matrix.md) | Publication checklist, evidence levels, expected warnings, and trust boundaries |
| [Validator Coverage](docs/reference/validator-coverage.md) | What the reference tools cover statically, from trace evidence, and from bridge checks |
| [Generated Skill README](docs/reference/generated-readme.md) | Per-skill README generation, checking, and trust boundaries |
| [Registry & Runtime Artifacts](docs/reference/registry-runtime-artifacts.md) | Runtime trace, registry manifest, and tool capability schemas |
| [Snapshot Release Workflow](docs/guides/snapshot-release-workflow.md) | Refreshing embedded creator snapshots and release metadata |
| [aisp.proto](specification/aisp.proto) | Proto3 schemas for skill discovery and conformance services |
| [Topics](docs/topics/) | Conceptual guides: Axiom 0, skill contract, security model, enforced_by, resources, lifecycle |
| [Guides](docs/guides/) | Step-by-step tutorials: getting started, first skill, discovery, conformance |
| [Reference](docs/reference/) | Field references, grammar, glossary, error codes, and threat taxonomy |
| [ADRs](adrs/) | Architecture Decision Records |
| [CHANGELOG](CHANGELOG.md) | Release history |

## AIXP Labs [aixp.dev](https://aixp.dev)

AIXP Labs develops and maintains the following core projects:

| Project | Description | Website |
|---------|-------------|---------|
| [HSAW](https://hsaw.dev) | Human Sovereignty and Wellbeing — Axiom 0 white paper (foundation) | hsaw.dev |
| [AISP](https://aisp.dev) | AI Skill Protocol — executable, governable skill packages (this project) | aisp.dev |
| [AIAP](https://aiap.dev) | AI Application Protocol — governance and compliance | aiap.dev |
| [AISOP](https://aisop.dev) | AI Standard Operating Protocol — flow program definition | aisop.dev |
| [AIBP](https://aibp.dev) | AI Bot Protocol — social communication and trust | aibp.dev |
| [AIVP](https://aivp.dev) | AI Value Protocol — international commerce, crypto asset settlement | aivp.dev |
| [AILP](https://ailp.dev) | AI List Protocol — agent discovery and capability advertising | ailp.dev |
| [SoulBot](https://soulbot.dev) | AI agent runtime and framework | soulbot.dev |
| [SoulACP](https://soulacp.dev) | Adapter library — bridging CLI tools and LLM providers | soulacp.dev |

## Contributing

AISP is an open protocol. Contributions, feedback, and discussion are welcome.

- **Issues**: [GitHub Issues](https://github.com/AIXP-Labs/AISP/issues)
- **Guide**: [CONTRIBUTING.md](CONTRIBUTING.md) / [中文版 CONTRIBUTING_CN.md](CONTRIBUTING_CN.md)

## Disclaimer

This protocol specification and the reference implementations are provided for **research and educational purposes only**. They are **experimental** and not intended for production use. Use at your own risk. The authors assume no liability for any damages arising from use of this software. See [LICENSE](LICENSE) for full terms (Apache 2.0).

## License

[Apache License 2.0](LICENSE) - Copyright 2026 AIXP Labs AIXP.dev | AISP.dev

> The AIXP ecosystem uses unified **Apache 2.0** licensing across all layers (aisop.dev, aiap.dev, aisp.dev, soulbot.dev) for patent protection and ecosystem consistency. See [GOVERNANCE.md](GOVERNANCE.md#the-layered-chain).

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
