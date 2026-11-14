# AISP — AI Skill Protocol

[中文版 README](README_CN.md)

[![Validate](https://github.com/AIXP-Labs/AISP/actions/workflows/validate.yml/badge.svg)](https://github.com/AIXP-Labs/AISP/actions/workflows/validate.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Protocol](https://img.shields.io/badge/Protocol-AISP_V1.0.0-brightgreen.svg)](https://aisp.dev)
[![Python](https://img.shields.io/badge/Python-%3E%3D3.11-blue.svg)](pyproject.toml)
[![Axiom 0](https://img.shields.io/badge/Axiom_0-Human_Sovereignty_and_Wellbeing-orange.svg)](GOVERNANCE.md)

**AISP packages executable, governable, distributable AI skills as self-contained skill folders.**

AISP is an executable, governable skill package built on AISOP and bridged to agent platforms through the Agent Skills standard.

> **AISP V1.0.0 protocol revision:** the required M7 interfaces and version-gated bootstrap are implemented. SoulRun is the replaceable default, not a protocol dependency. Local conformance checks do not certify all runtime guarantees, external copies, or publication readiness. See the [release evidence requirements](docs/reference/release-evidence-matrix.md).

[Specification](specification/AISP_Protocol.md) | [Quick Start](#quick-start) | [Examples](#examples) | [Release Evidence](docs/reference/release-evidence-matrix.md) | [Validator Coverage](docs/reference/validator-coverage.md) | [AIXP Labs](#aixp-labs-aixpdev)

| Fact | Value |
|------|-------|
| Protocol | AISP V1.0.0 |
| Full name | AI Skill Protocol |
| Authority | [aisp.dev](https://aisp.dev) |
| Execution layer | [aisop.dev](https://aisop.dev) |
| Default executor (replaceable) | SoulRun (`soulrun.dev`) |
| Foundational axiom | Human Sovereignty and Wellbeing |

## What is AISP?

AISP defines the **skill-package layer** for AI. While [Agent Skills](https://agentskills.io/specification) (`SKILL.md`) describe a skill as prose plus progressive disclosure, AISP addresses a different problem: how to package a skill as a **real executable program** with a machine-checkable contract, declared resources, validation rules, and a distribution lifecycle.

A native AISP skill is a folder `aisp/<id>_aisp/` containing the fixed-name AISOP program `aisp.aisop.json`, the required generated `SKILL.md` interface, and its declared resources. A generated `README.md` introduces the package (recommended normally, required by the strict/release profile). The skill contract is `user.content.aisp_contract`, a real JSON object inside the program, not another file. Generation, evolution, and distribution use external tooling of the author's choice.

**Core philosophy**: hard guarantees are enforced, not hinted. Red lines bind to real mechanisms through `non_negotiable.enforced_by -> sys.*`, `aisop.main`, or restricted tools. Trust is never self-declared.

**Complementary, not a replacement**: the business definition stays in `aisp.aisop.json`; every conformant package MUST contain a generated same-folder `SKILL.md` compatibility interface (M7). The fixed bootstrap delegates to a conforming executor, SoulRun by default. Without one, stop; do not execute or continue the program yourself. Executor-mediated reads and user-requested review are allowed.

## Repository Scope

| This repository contains | Purpose |
|--------------------------|---------|
| `specification/` | The normative protocol specification, conformance standards, and Proto schema |
| `schemas/` | JSON Schemas for contracts, runtime traces, registry manifests, and tool capabilities |
| `tools/` | Zero-dependency reference validators, hash tools, README/SKILL.md generators, and bridge checker |
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
- **Required `SKILL.md` Compatibility Interface** — M7 checks existence, the skill-derived name/description/license and the fixed executor-only bootstrap. Five launch strings and one frozen version policy may vary; these are configuration values, not separate bootstrap flows. Business logic stays in the AISP program.
- **Axiom 0 Enforcement** — every skill inherits Human Sovereignty and Wellbeing; `sys.io.confirm` remains forced-blocking.

## Protocol Stack

```text
Application layer
      |
AISP  - skill-package layer (this protocol)
      |
AISOP - execution layer (.aisop.json flow programs)
      |
Conforming AISP/AISOP executor (SoulRun by default; replaceable)
```

AISP packages an AISOP program into a discoverable, invocable, governable, distributable skill unit. It builds on AISOP for execution and does not redefine the engine. Each layer independently upholds Axiom 0.

## How Skills Run

There is **one bootstrap flow and one core decision**: does the configured executor's installed package version satisfy the frozen `executor_version_policy.requirement`?

| Version state | Action |
|---|---|
| Satisfies `>=X.Y.Z` or `==X.Y.Z` | Run through the executor directly, without an installation/upgrade question. |
| Proven absent or does not satisfy the requirement | Ask whether to install a matching version. Only after consent, install, recheck the same condition, and run if it now matches. |

Refusal, installation failure, or a failed/mismatching recheck means stop. Unknown version output, permission denial and timeouts are probe errors, not proof of absence; stop rather than reinstall. An exact `==` pin requires that exact version, including explicit consent for a downgrade.

Default SoulRun bounds resolve to a concrete latest-stable snapshot at first generation or explicit refresh. Ordinary regeneration preserves the frozen bound; runtime version checks do not query latest. Explicit constraints take precedence. The checked-in examples currently use `>=1.0.1`; this is not a permanent protocol minimum or a claim about today's latest release. Installation may access a package source only after consent. Business confirmation gates remain mandatory after version acceptance.

## Quick Start

Prerequisite: Python 3.11 or newer. The reference tools use only the Python standard library at runtime; `jsonschema` is needed only for the schema-focused test coverage.

Run the reference scripts directly from this checkout; installing this repository
is not required. For schema-focused tests, install the declared test dependency:

```bash
python -m pip install "jsonschema>=4"
```

Optional developer installation: `python -m pip install -e ".[dev]"`.
The build configuration explicitly packages `tools`; offline editable metadata,
wheel construction and a clean-venv installation of all eight console entry
points have been checked. The wheel contains reference tools, not skill
examples, schemas or a runtime. Source commands below remain usable without
installing the repository. Neither installation nor a passing check confers
publication approval.

Packaging requires `setuptools>=84.1.0` as a build-only dependency; installed
reference tools remain standard-library-only. Ignore rules do not sanitize
tracked files, history or distribution archives. Review local outputs and built
artifacts before sharing; see the [security policy](SECURITY.md#repository-hygiene).
Wheel package-data settings and source-archive selection are separate:
[`MANIFEST.in`](MANIFEST.in) excludes known private files and selected runtime,
test, build and `.venv` residue from sdist even when an old source list exists.
This is a bounded safeguard, not a complete
secret detector; clean-source builds and archive review are still required.

### 1. Inspect the package shape

Normative AISP packages use this shape:

```text
aisp/
└── yijing_aisp/            # folder name == id, MUST end with _aisp
    ├── README.md           # generated introduction; SHOULD, required by strict/release
    ├── SKILL.md            # MUST: generated Agent Skills compatibility interface
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

Use `-IncludePytest` to also run pytest without writing `.pytest_cache/`; install
`pytest` separately first. The `[dev]` metadata declares only `jsonschema`, not pytest.
`-RequireClean` adds the final clean-tree check, but the wrapper always invokes
`git diff --check` even without that flag. When Git is prohibited, do not run
the wrapper: run only the permitted individual non-Git checks and report that
the full release gate was not run.

The shared reference commands below are not a literal wrapper/CI expansion:
both also check JSON syntax, the wrapper adds residue/private-path scans, and CI
checks committed whitespace with `git diff-tree --check --root -r HEAD`. See
[`scripts/release_check.ps1`](scripts/release_check.ps1) and
[the workflow](.github/workflows/validate.yml) for their exact steps.

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

### 5. Execute Through the Interface or Executor

For an Agent Skills host, expose the target skill folder through that host's supported skill-discovery mechanism and use its generated `SKILL.md`. The interface checks the version condition above and hands the same-folder business program to the configured executor. This repository is not itself a host plugin or runtime installer.

For a direct SoulRun invocation, first satisfy the declared version requirement. Prepare a private working directory outside this checkout (the example uses the sibling `../aisp-demo-run/`) and put a disposable copy of the actual user request in its `message.txt`. From the repository root:

```bash
soulrun --aisp examples/aisp/yijing_aisp --soulrun-cache-dir ../aisp-demo-run/.soulrun_cache --user-message-file ../aisp-demo-run/message.txt --host-tool "agent=false"
```

`agent=false` truthfully disables sub-agent capability for this inline-only example; do not use it to collapse an `agent` node in another skill. Runtime records can contain user messages and model answers, and SoulRun may move the message file into the run. Verify appropriate access permissions and the actual ignore-file state; a `.gitignore` is not access control or protection against deliberate publication. The CLI supplies the current turn's instructions to the host/model; a zero exit code is not a completed business run. Completion requires terminal run records and corresponding outputs, and waiting at a gate is not consent.

Other conforming executors use their own supported interface to load `aisp.aisop.json` and run `user.content.aisop.main` while honoring `user.content.aisp_contract`. The host must not interpret or continue the business program on its own.

## Validation Boundaries

The reference toolchain is a conformance gate, not a trust oracle.

| Check | Proves | Does not prove |
|-------|--------|----------------|
| Static validator | M1-M7 plus static SE/EC package checks | Full runtime behavior or external trust |
| Runtime trace checker | Published v1 trace shape and selected R-series event consistency checks | Generic schema validation, full runtime conformance, independent event authenticity or a trustworthy trace source |
| Generated README check | Consistency with `aisp.aisop.json` | Skill safety, trust, or registry approval |
| Hash tool | Recomputable local integrity records | Safety, endorsement, or provenance by itself |
| SKILL.md generator/check | Existence, skill-derived header, fixed bootstrap and launch configuration and version-policy format (M7) | Executor certification, platform behavior, safety, trust or completed execution |
| Bridge validator | Shared M7 plus frontmatter/path safety and native package validation | Runtime hard guarantees or completed execution |

Missing, legacy or drifted `SKILL.md` is an M7 failure, with no opt-out. Core and bridge checks share a read-only checker; success proves unchanged bootstrap text and valid format, not executor certification, trust, safety or completed execution. See specification §20 for explicit migration, launch configuration and version policy and session limits.

`enforced_by: tools` remains conditional in static-only mode. `--strict-tools` requires the checker's event/provenance evidence criteria; a bare `tool_enforcement: "hard"` self-attestation is insufficient. Passing those criteria does not independently authenticate the artifact or establish actual hard enforcement. That guarantee depends on the runtime's real permission controls and trustworthy evidence provenance.

Tool-capability artifacts also receive bounded v1 shape checks before evidence
consumption, even without `--strict-tools`; malformed artifacts fail rather than
becoming warnings. README/SKILL.md writes reject symbolic-link outputs and
replace individual files atomically. Batch preflight is not a multi-file
transaction; later I/O failures may leave explicitly reported earlier writes.

Documentation checks reject missing/out-of-root scan targets and derive anchors
from prose, not fenced or inline-code examples. This is a bounded Markdown
checker, not a full rendering engine. Trace checks reject explicit contract-read
or visibility denials that conflict with affirmative events; consistency still
does not authenticate the trace. Recorded dispatches for known inline nodes
(including omitted-mode defaults) must also remain inline. Invalid link paths
and unreadable anchor targets are reported as failures rather than tracebacks.

Strict validation rejects non-program JSON values, including `null`; parse
failure is not a successful empty report. Known optional text fields must be
strings when present, `params` must be an object, and `tools` must be an array of
non-blank strings; omission and an empty tools array remain allowed unless a
separate binding requires an allow-list. This does not add required fields,
certify license identifiers or prove prompt semantics. Only a missing license or
a blank license string triggers the presence warning; a non-string license fails
its type check instead. Index checks compare folder-derived
routing metadata as well as ids/paths, retaining EC2 warnings for stale caches.
Hash output refuses to overwrite its program/resource inputs (including aliases).
Shared resource roots must remain inside the selected `aisp/` directory before
files are read. Interface checks preserve `SKILL.md` link identity and reject
symbolic links; recursive projections reject escaping skill folders. Discovery
script scans are bounded AST checks, not a sandbox or a proof of harmless code.
Resource-mode checks cover selected literal reads and run/bg calls, including
ordinary quoted Python paths and harmless dot/separator aliases; dynamic commands
and runtime mode enforcement remain outside that static check.
Python option clusters are distinguished from file operands. Distinct scoped
resources may share names. If every matching declaration forbids an operation,
SE3 fails; otherwise unresolved literal usage warns without proving a selected
scope or combining permissions.

## Examples

Working examples include the required generated interfaces. Their version policies are concrete snapshots, not a permanent protocol minimum. Offline conformance does not replace real-host acceptance or publication authorization.

### Native AISP examples

| # | Skill | Risk | Demonstrates |
|---|-------|:----:|-------------|
| 1 | [`yijing_aisp/`](examples/aisp/yijing_aisp/) | **low** | Single-skill read-only divination; deterministic graph; `enforced_by -> sys.assert`; required same-folder `SKILL.md` compatibility interface |
| 2 | [`stock_analysis_aisp/`](examples/aisp/stock_analysis_aisp/) | **medium** | Stock analysis example; declared data/script/eval resources; example-local trace fixtures exercise strict evidence checks, not independently certified live enforcement; required same-folder `SKILL.md` compatibility interface |
| 3 | [`aisp_creator_evolution_aisp/`](examples/aisp/aisp_creator_evolution_aisp/) | **medium** | Meta-skill for AISP creation/evolution/conversion; strict candidate validation; required same-folder `SKILL.md` compatibility interface |

### AISP Creator / Evolution Example

This repository includes a native AISP creator/evolution example at [`examples/aisp/aisp_creator_evolution_aisp/`](examples/aisp/aisp_creator_evolution_aisp/). It demonstrates how an AISP skill can help create, evolve, research, validate, and review other native AISP skills while staying inside the AISP package model. The example bundles specification snapshots, schemas, reference tools, templates, and replayable eval evidence for offline review.

The creator is an example skill, not a trust authority or production runtime. Its bundled snapshots and manifests provide local reference and integrity evidence only; they do not prove upstream trust, freshness, or registry approval. Generated or evolved skills must still pass the reference validators, required-interface and README derivation checks, human review gates, and any external provenance or registry checks required by the publisher. Local validation or replay fixtures are not a claim that every create/evolve workflow has been tested with a real model.

See [`examples/README.md`](examples/README.md) for the discovery walkthrough and the `aisp/` directory contract.

The Creator's candidate gate includes executable script regressions, not only
read-only checks. It skips replays after static/evidence preflight failures and
stops on unexpected replay failures; reference warnings remain visible.
Review/trust both the tools and case commands and use an isolated host:
`shell=False` is not a sandbox or a no-network guarantee.

## Documentation

| Document | Description |
|----------|-------------|
| [AISP Protocol Specification](specification/AISP_Protocol.md) / [Chinese](specification/AISP_Protocol_cn.md) | Full protocol specification |
| [Conformance Standards](specification/standards/) | Machine-verifiable M / R / SE / EC conformance rules |
| [Conformance Walkthrough](docs/guides/conformance-walkthrough.md) / [Chinese](docs/guides/conformance-walkthrough_CN.md) | How to run and interpret validator output |
| [Release Evidence Matrix](docs/reference/release-evidence-matrix.md) / [Chinese](docs/reference/release-evidence-matrix_CN.md) | Publication checklist, evidence levels, expected warnings, and trust boundaries |
| [Validator Coverage](docs/reference/validator-coverage.md) | What the reference tools cover statically, from trace evidence, and from bridge checks |
| [Generated Skill README](docs/reference/generated-readme.md) | Per-skill README generation, checking, and trust boundaries |
| [Agent Skills Interface](docs/topics/interoperability-with-agent-skills.md) | Required SKILL.md, version conditions, explicit migration and host boundaries |
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
| [AIZP](https://aizp.dev) | AI Zenith-Zero Protocol — runtime behavioral alignment | aizp.dev |
| [AIIP](https://aiip.dev) | AI Intent Protocol — governed intent trees, priorities and feedback | aiip.dev |
| [AIKP](https://aikp.dev) | AI Knowledge Protocol — long-term knowledge organization, navigation and governance | aikp.dev |
| [AIJP](https://aijp.dev) | AI Job Protocol — schedulable work trees and job graphs | aijp.dev |
| [AINP](https://ainp.dev) | AI Neogenesis Protocol — governable generation projects: plan + content + evidence | ainp.dev |
| [AILP](https://ailp.dev) | AI List Protocol — agent discovery and capability advertising | ailp.dev |
| [AIVP](https://aivp.dev) | AI Value Protocol — international commerce, crypto asset settlement | aivp.dev |
| [AIRP](https://airp.dev) | AI RMB Protocol — Mainland China commerce, RMB licensed settlement | airp.dev |
| [AIBP](https://aibp.dev) | AI Bot Protocol — social communication and trust | aibp.dev |
| [AIAP](https://aiap.dev) | AI Application Protocol — governance and compliance | aiap.dev |
| [AISP](https://aisp.dev) | AI Skill Protocol — directory packages with a canonical AISOP skill entry and enforceable contract bindings **(this project)** | aisp.dev |
| [AISOP](https://aisop.dev) | AI Standard Operating Protocol — flow program definition | aisop.dev |
| [AIXPStore](https://aixpstore.dev) | Official marketplace for AIAP programs and AISP skills — discover, publish, and distribute AI capabilities | aixpstore.dev |
| [SoulSkill](https://soulskill.dev) | AISP skill reference library & multi-CLI plugin distribution | soulskill.dev |
| [SoulAgent](https://soulagent.dev) | Drop-in AI agent invoked directly by any CLI / SDK / IDE | soulagent.dev |
| [SoulBot](https://soulbot.dev) | AI agent runtime & orchestration framework (scheduling, agent-spawn, inter-agent comms) | soulbot.dev |
| [SoulRun](https://soulrun.dev) | AISOP execution engine as one call — runs AIAP programs and AISP skills for any host | soulrun.dev |
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

<a id="alignment-philosophy"></a>

## ⚓ Alignment & Philosophy

### Axiom 0: [HSAW | Human Sovereignty and Wellbeing](https://hsaw.dev)

- **No HITL, HSAW.**
  *Human Sovereignty and Wellbeing is Axiom 0, requiring no hypocritical human-in-the-loop.*
- **No w.a.s.h, Real h.s.a.w.**
- **人非蝼蚁，人为道。**
- **We are not beggars. We the People.**
