# AISP Skills

This folder is an example `aisp/` package root. Each skill is a folder
`<id>_aisp/` containing `aisp.aisop.json`, required generated `SKILL.md` (M7), plus its
own resources (custom layout, e.g. `data/`, `scripts/`). The folder name equals the
skill `id` and **ends with `_aisp`** (mirroring the convention the sibling AIAP protocol uses for `_aiap`).

## Discover skills

- **Read the index** (default, safe, no execution): open `aisp_list.json`
  (id, name, summary, path, category, tags, when_to_use, risk_level).
- **Refresh the index**: run `python -B aisp_list.py --json` (re-scans folders, rewrites
  `aisp_list.json`). Add `python -B aisp_list.py` to just print the list.
- **Glob fallback**: read each `*_aisp/aisp.aisop.json` and look at its
  `user.content.aisp_contract`.

> **Truth model.** The skill folders are the single source of truth; `aisp_list.py`
> is the generator; `aisp_list.json` is the cache. If the JSON looks stale, re-run
> the script. `_shared/` carries no `_aisp` suffix and is skipped automatically.

## Run a skill

Use the same-folder generated SKILL.md to hand execution to a conforming AISP/AISOP executor, SoulRun by default. The executor loads `<id>_aisp/aisp.aisop.json` and runs `aisop.main`; without an executor, stop rather than executing or continuing it yourself. Executor-mediated reads and user-requested code review remain allowed.
The contract is `user.content.aisp_contract` (a real object the model reads directly).
Resources are loaded only when a node reads or runs them. Required nodes are never
skipped, and `sys.io.confirm` is never bypassed (Axiom 0).

The interface has one version decision: a matching installed package version runs
directly; proven absence or mismatch prompts for a matching installation. Consent
is followed by installation and the same version recheck; refusal, failure or an
unusable/unknown probe stops. The examples freeze `>=1.0.1`, not a protocol-wide
minimum or a runtime latest lookup. Explicit `>=`/`==` requirements take precedence.

## Add a skill

Create `<new_id>_aisp/aisp.aisop.json` where the folder name == `id` and ends
with `_aisp`. Declare resources in `aisp_contract.resources`, bind each red line to a
real mechanism via `non_negotiable.enforced_by`, then run `python -B aisp_list.py --json`.
M7 requires generated same-folder SKILL.md: file existence, derived header and fixed
executor-only bootstrap must match, with only five valid launch strings and one
frozen version-policy object variable.
No opt-out; business truth remains only in the AISP program. Static checks do not
certify an executor, external trust or completed execution.
Per-skill `README.md` files SHOULD be generated from `aisp.aisop.json`; release
profiles treat them as required so standalone packages remain self-describing.

## What's here

| Skill | Risk | Demonstrates |
|-------|:----:|-------------|
| `yijing_aisp/` | low | Single-skill, read-only; `sys.code.exec` random cast; `enforced_by → sys.assert`; required same-folder Agent Skills `SKILL.md` compatibility interface |
| `stock_analysis_aisp/` | medium | `data/` + `scripts/` + `_shared/`; `enforced_by: tools` ("never place trades"); not-advice disclaimer via `report.step2:sys.assert`; example-local runtime trace evidence; required same-folder Agent Skills `SKILL.md` compatibility interface |
| `aisp_creator_evolution_aisp/` | medium | Creator/evolution meta-skill; creates, evolves, researches, validates, and reviews native AISP skills with embedded specification snapshots, reference tools, schemas, templates, replayable eval evidence, and required same-folder Agent Skills `SKILL.md` compatibility interface |
| `_shared/` | — | Cross-skill shared resources (`finance_terms.md`); not a skill folder |

## Runtime evidence

Static validation keeps `enforced_by: tools` conditional. For release-style checks, example-local trace fixtures describe contract visibility, tool enforcement and R7 `agent` dispatch. They exercise validation rules, not independent certification of those events:

```bash
python -B ../../tools/aisp_validate.py --strict-tools --runtime-trace stock_analysis_aisp/evals/runtime-traces/hard-pass.json stock_analysis_aisp
python -B ../../tools/aisp_validate.py --strict-tools --runtime-trace aisp_creator_evolution_aisp/evals/runtime-traces/hard-pass.json aisp_creator_evolution_aisp
python -B ../../tools/aisp_check_runtime_trace.py stock_analysis_aisp stock_analysis_aisp/evals/runtime-traces/hard-pass.json
```

For the repository-level publication checklist, warning policy, and trust
boundaries, see [`docs/reference/release-evidence-matrix.md`](../../docs/reference/release-evidence-matrix.md).

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
