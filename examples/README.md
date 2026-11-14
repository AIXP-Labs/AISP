# AISP Examples

Three native AISP example packages, discovery tools, shared resources and required generated same-folder SKILL.md compatibility interfaces (M7). Execution MUST use a conforming executor, SoulRun by default; hosts must not execute or continue the business program themselves. The creator's local generation/release checks have been manually migrated to M7; that engineering work does not certify every real-model workflow or grant publication readiness.

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
    │   ├── SKILL.md                      # required Agent Skills compatibility interface; not the truth source
    │   └── data/
    │       ├── hexagrams.json            # read_only data resource
    │       └── interpretation_guide.md   # read_only reference resource
    ├── stock_analysis_aisp/
    │   ├── aisp.aisop.json
    │   ├── README.md                     # generated bootstrap projection; not a trust proof
    │   ├── SKILL.md                      # required Agent Skills compatibility interface; not the truth source
    │   ├── data/sample_prices.csv        # read_only data resource
    │   ├── evals/runtime-traces/hard-pass.json
    │   └── scripts/indicators.py         # execute_only script resource (requires_tools: shell)
    └── aisp_creator_evolution_aisp/      # creator/evolution meta-skill example
        ├── aisp.aisop.json
        ├── README.md                     # generated bootstrap projection; not a trust proof
        ├── README_CN.md                  # hand-maintained Chinese operator notes
        ├── SKILL.md                      # required Agent Skills compatibility interface; not the truth source
        ├── templates/                    # generated skill templates
        ├── scripts/                      # validation/simulation helpers
        └── evals/                        # replayable behavior evidence
```

## Skill Directory

| # | Skill | Risk | What it demonstrates |
|---|-------|:----:|----------------------|
| 1 | [`aisp/yijing_aisp/`](aisp/yijing_aisp/) | **low** | A single read-only skill; a random `sys.code.exec` cast and explicit flow; three `non_negotiable` bindings via `aisop.main` and `interpret.step1/step4:sys.assert`; required same-folder `SKILL.md` compatibility interface for Agent Skills discovery. |
| 2 | [`aisp/stock_analysis_aisp/`](aisp/stock_analysis_aisp/) | **medium** | A domain skill spanning `data/` + `scripts/` + `_shared/`; `enforced_by: tools` ("never place trades"); a not-advice disclaimer enforced by `report.step2:sys.assert`; an `execute_only` script with least-authority `requires_tools`; required same-folder `SKILL.md` compatibility interface; example-local runtime trace evidence for strict tool/R7 checks; the `analyze` node uses `execute_mode: "agent"` (sub-agent dispatch, R7) while simpler nodes explicitly declare `execute_mode: "inline"` |
| 3 | [`aisp/aisp_creator_evolution_aisp/`](aisp/aisp_creator_evolution_aisp/) | **medium** | A creator/evolution meta-skill for native AISP packages; demonstrates embedded spec snapshots, reference tools, schemas, templates, replayable eval evidence, required same-folder `SKILL.md` compatibility interface generation, and strict boundaries that avoid AIAP structures. |

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

The stock example's stdin-only script accepts UTF-8 CSV (optional BOM; LF, CRLF or
CR line endings) with exactly one `close` column and finite numeric values on every data row. Empty, malformed
or invalid series return a JSON error with a nonzero exit code. Its `volatility`
is the population standard deviation of sampled closing prices, rounded only
after calculation, not annualized return volatility or investment advice.

## Conformance at a Glance

The listed packages demonstrate M1–M7: legal AISOP program, correct folder/id, real-object contract, existing red-line bindings, confined resources, no self-declared trust, and the required generated interface. Static success does not certify runtime behavior, assertion evaluation or real sub-agent dispatch. All three use the same version-gated bootstrap: matching versions run directly; proven absence/mismatch requires installation consent and a matching recheck. See [`docs/guides/conformance-walkthrough.md`](../docs/guides/conformance-walkthrough.md).

Static validation intentionally keeps `enforced_by: tools` conditional. Example packages include trace fixtures under `evals/runtime-traces/` to exercise the checker's evidence rules. Accepting those fixtures does not authenticate their event claims or prove live runtime enforcement:

```bash
python -B tools/aisp_validate.py --strict-tools --runtime-trace examples/aisp/stock_analysis_aisp/evals/runtime-traces/hard-pass.json examples/aisp/stock_analysis_aisp
python -B tools/aisp_validate.py --strict-tools --runtime-trace examples/aisp/aisp_creator_evolution_aisp/evals/runtime-traces/hard-pass.json examples/aisp/aisp_creator_evolution_aisp
python -B tools/aisp_check_runtime_trace.py examples/aisp/stock_analysis_aisp examples/aisp/stock_analysis_aisp/evals/runtime-traces/hard-pass.json
```

For the full publication checklist and the meaning of expected warnings, see [`docs/reference/release-evidence-matrix.md`](../docs/reference/release-evidence-matrix.md).

## Contributing a New Example

Create `aisp/<new_id>_aisp/aisp.aisop.json`, declare resources and real red-line bindings, generate the required same-folder SKILL.md using `tools/aisp_skill_md.py`, then generate README and update discovery with `python -B aisp_list.py --json`. Keep business truth in the AISP program; there is no interface opt-out.

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
