# AISP Examples

A complete, conformance-ready `aisp/` scaffold demonstrating the AI Skill Protocol: three worked skills, the discovery toolkit, a shared resource, and default same-folder Agent Skills `SKILL.md` sidecars for public examples. `SKILL.md` is still core-optional: every skill is a self-contained folder with an `aisp.aisop.json` body and a `user.content.aisp_contract`; executing one requires an AISP/AISOP-compatible runtime.

## Directory Layout

```text
examples/
└── aisp/                                # NATIVE AISP skills (discovered via aisp_list)
    ├── README.md                        # the aisp/ usage contract (human/AI readable)
    ├── aisp_list.py                     # zero-dependency discovery script
    ├── aisp_list.json                   # generated index (cache)
    ├── _shared/
    │   └── finance_terms.md             # cross-skill shared resource (no _aisp suffix)
    ├── yijing_aisp/                      # folder name == id, ends with _aisp
    │   ├── aisp.aisop.json              # the skill body (AISOP V1.0.0 program)
    │   ├── README.md                     # generated bootstrap projection; not a trust proof
    │   ├── SKILL.md                      # default Agent Skills sidecar; not the truth source
    │   └── data/
    │       ├── hexagrams.json            # read_only data resource
    │       └── interpretation_guide.md   # read_only reference resource
    ├── stock_analysis_aisp/
    │   ├── aisp.aisop.json
    │   ├── README.md                     # generated bootstrap projection; not a trust proof
    │   ├── SKILL.md                      # default Agent Skills sidecar; not the truth source
    │   ├── data/sample_prices.csv        # read_only data resource
    │   ├── evals/runtime-traces/hard-pass.json
    │   └── scripts/indicators.py         # execute_only script resource (requires_tools: shell)
    └── aisp_creator_evolution_aisp/      # creator/evolution meta-skill example
        ├── aisp.aisop.json
        ├── README.md                     # generated bootstrap projection; not a trust proof
        ├── README_CN.md                  # hand-maintained Chinese operator notes
        ├── SKILL.md                      # default Agent Skills sidecar; not the truth source
        ├── templates/                    # generated skill templates
        ├── scripts/                      # validation/simulation helpers
        └── evals/                        # replayable behavior evidence
```

## Skill Directory

| # | Skill | Risk | What it demonstrates |
|---|-------|:----:|----------------------|
| 1 | [`aisp/yijing_aisp/`](aisp/yijing_aisp/) | **low** | A single read-only skill; a deterministic `sys.code.exec` cast; three `non_negotiable` red lines bound via `aisop.main` and `interpret.step1/step4:sys.assert`; default same-folder `SKILL.md` sidecar for Agent Skills discovery. |
| 2 | [`aisp/stock_analysis_aisp/`](aisp/stock_analysis_aisp/) | **medium** | A domain skill spanning `data/` + `scripts/` + `_shared/`; `enforced_by: tools` ("never place trades"); a not-advice disclaimer enforced by `report.step2:sys.assert`; an `execute_only` script with least-authority `requires_tools`; default same-folder `SKILL.md` sidecar; example-local runtime trace evidence for strict tool/R7 checks; the `analyze` node uses `execute_mode: "agent"` (sub-agent dispatch, R7) while simpler nodes explicitly declare `execute_mode: "inline"` |
| 3 | [`aisp/aisp_creator_evolution_aisp/`](aisp/aisp_creator_evolution_aisp/) | **medium** | A creator/evolution meta-skill for native AISP packages; demonstrates embedded spec snapshots, reference tools, schemas, templates, replayable eval evidence, default same-folder `SKILL.md` sidecar generation, and strict boundaries that avoid AIAP structures. |

## How to Read an Example

1. **Open `aisp.aisop.json`.** It is a 2-message array. The `system` message holds identity metadata (`protocol: AISP V1.0.0`, `id`, `name`, `version`, `license`, …). The `user` message holds the strong `instruction`, the real-object `aisp_contract`, the `aisop.main` graph, and the `functions`.
2. **Read `aisp_contract`** (Tier S): `invocation` (when to trigger), `non_negotiable` (red lines + `enforced_by`), `discovery`, `risk_level`, `resources` (the inventory).
3. **Trace `aisop.main` and `functions`** (Tier A): the execution graph and each node's steps. Confirm that every `enforced_by` points to a node/step/mechanism that actually exists (conformance rule M4).

## Running the Discovery

```bash
cd examples/aisp

# print the discovered skills
python -B aisp_list.py

# (re)generate the index cache
python -B aisp_list.py --json
```

The script globs `*_aisp/aisp.aisop.json`, reads each `user.content.aisp_contract`, and prints / writes `aisp_list.json`. The skill folders are the single source of truth; `_shared/` is skipped automatically because it has no `_aisp` suffix.

## Conformance at a Glance

All listed skills satisfy the core skill rules (M1–M6): a legal AISOP program (M1), folder name == id ending in `_aisp` (M2), a real-object `aisp_contract` in the user message (M3), every `enforced_by` real (M4), confined relative resource paths (M5), and no self-declared trust (M6). See [`docs/guides/conformance-walkthrough.md`](../docs/guides/conformance-walkthrough.md).

Static validation intentionally keeps `enforced_by: tools` as conditional. Example packages that use `tools` may include replayable runtime evidence under `evals/runtime-traces/` so release checks can prove the specific trace, without pretending static inspection proves runtime enforcement:

```bash
python -B tools/aisp_validate.py --strict-tools --runtime-trace examples/aisp/stock_analysis_aisp/evals/runtime-traces/hard-pass.json examples/aisp/stock_analysis_aisp
python -B tools/aisp_validate.py --strict-tools --runtime-trace examples/aisp/aisp_creator_evolution_aisp/evals/runtime-traces/hard-pass.json examples/aisp/aisp_creator_evolution_aisp
python -B tools/aisp_check_runtime_trace.py examples/aisp/stock_analysis_aisp examples/aisp/stock_analysis_aisp/evals/runtime-traces/hard-pass.json
```

For the full publication checklist and the meaning of expected warnings, see [`docs/reference/release-evidence-matrix.md`](../docs/reference/release-evidence-matrix.md).

## Contributing a New Example

Create `aisp/<new_id>_aisp/aisp.aisop.json` (folder name == id, ends with `_aisp`), declare resources in `aisp_contract.resources`, bind each red line to a real mechanism, then run `python -B aisp_list.py --json`. Authoring and public-distribution workflows SHOULD add a generated same-folder `README.md` and `SKILL.md` sidecar by default unless the author explicitly opts out of the sidecar; keep all executable truth in the AISP program.

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
