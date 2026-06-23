# Conformance Walkthrough

AISP skills are checked against a conformance framework: **M1–M6** for skills, **R1–R7** for runtimes, plus the **SE** (security) and **EC** (ecosystem) extensions. This guide walks through checking a skill, reading the results, and fixing common violations. Unlike runtime testing, conformance is a pre-execution gate — a skill is verified before it ever runs.

---

## Overview

A conformant AISP skill is, above all, **a legal AISOP V1.0.0 program** (M1) — then it satisfies the additional skill-package rules M2–M6. The rules live in the conformance standards:

| Series | Source | Scope |
|--------|--------|-------|
| M1–M6 | `AISP_Standard.core` | Skill conformance (FAIL on violation) |
| R1–R7 | `AISP_Standard.core` | Runtime conformance |
| SE1–SE8, ST1–ST6 | `AISP_Standard.security` | Security + threat taxonomy |
| EC1–EC8 | `AISP_Standard.ecosystem` | `aisp/` directory + lifecycle reuse + generated skill README |

---

## Running a Conformance Check

Use the zero-dependency reference validator for static checks:

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

For command-by-command evidence levels, expected warning handling, and trust boundaries, use the [Release Evidence Matrix](../reference/release-evidence-matrix.md). In static-only runs, `AISP_W_R6_TOOLS_CONDITIONAL` is an expected honesty signal for `enforced_by: tools`; it is resolved only by event-backed runtime trace evidence or provenance-bearing hard tool capability evidence.

Regenerate derived files only when you intentionally update them:

```bash
python -B examples/aisp/aisp_list.py --json
python -B tools/aisp_readme.py examples/aisp/yijing_aisp --write
python -B tools/aisp_skill_md.py examples/aisp/yijing_aisp --write
```

The validator covers M1-M6 and the static parts of SE/EC. Runtime-conformance evidence is checked from trace JSON using `aisp_check_runtime_trace.py`; live runtime harnesses can emit that trace shape. `enforced_by: tools` is conditional in static-only mode and can be resolved only by event-backed runtime trace evidence or provenance-bearing tool capability evidence; `--strict-tools` rejects bare hard attestations. Registry/provenance hashes are generated with `aisp_hash.py`. Per-skill README projections are generated and checked with `aisp_readme.py`; a passing README check proves consistency, not trust or safety. Default-but-core-optional Agent Skills sidecars are generated with `aisp_skill_md.py` and checked with `aisp_validate_agent_skill_bridge.py`; passing generation/bridge validation proves projection consistency, sidecar shape, and native AISP validation, not external trust. A missing sidecar is an EC7 warning in core validation, not a core failure unless a stricter release profile requires it.

### Step 1: Confirm it is a legal AISOP program (M1)

Parse `aisp.aisop.json`. It MUST be a 2-message array; `data[0].content` MUST have `protocol == "AISP V1.0.0"`, plus `axiom_0` / `id` / `name` / `version` / `flow_format`; `data[1].content` MUST have `instruction` / `aisop.main` / `functions`. `license` SHOULD be present.

### Step 2: Check the package rules (M2–M6)

| Rule | Check |
|------|-------|
| **M2** | Folder name == `id`, ends with `_aisp`; file named `aisp.aisop.json` |
| **M3** | `user.content.aisp_contract` is a real object; `profile` starts `aisp.skill.`; has `invocation` + `non_negotiable` |
| **M4** | Every `non_negotiable.enforced_by` points to a mechanism that exists |
| **M5** | Each `resources[].path` is relative, no `../`; `mode` in the enum; scripts have `requires_tools` |
| **M6** | No self-declared trust (`trusted` / `verified` / `safe`) |

### Step 3: Verify the red-line bindings (M4 in detail)

For each `enforced_by`:

- `<node>.stepN:<mechanism>` → `functions[node][stepN]` exists as a numeric execution step **and** begins with that mechanism.
- `aisop.main` → the required node/branch exists in the graph.
- `tools` → `tools` is restricted (and note: hard only if the runtime enforces tool permissions).

### Step 4: Apply security + ecosystem extensions

Run SE1-SE8 (path confinement, remote gate, mode gating, least authority, discovery-script safety, no self-trust, confirm invariant, read-only during execution) and EC1-EC8 (`aisp/` directory contract, index ↔ folder consistency, `_shared/` scope, provenance, generation, evolution safety, sidecar bridge, generated per-skill README).

---

## A Worked Example: `yijing_aisp`

| Rule | Result | Why |
|------|:------:|-----|
| M1 | PASS | 2-message array; `protocol: AISP V1.0.0`; `license: Apache-2.0`; `aisop.main` present |
| M2 | PASS | folder `yijing_aisp/` == id, ends `_aisp`; file `aisp.aisop.json` |
| M3 | PASS | `aisp_contract` is a real object in the user message; `profile: aisp.skill.v1`; has `invocation` + `non_negotiable` |
| M4 | PASS | `aisop.main` orders cast→interpret; `interpret.step1:sys.assert` exists; `interpret.step4:sys.assert` exists |
| M5 | PASS | `data/hexagrams.json`, `data/interpretation_guide.md` — relative, declared, `read_only` |
| M6 | PASS | no self-declared trust |

A clean skill produces all-PASS for M1–M6.

---

## Common Violations and Fixes

### M4 Violation: Phantom enforcement

**Problem.** A `non_negotiable` declares `enforced_by: "interpret.step9:sys.assert"`, but `interpret` has no `step9`.

**Impact.** A claimed hard guarantee that does not exist — the worst kind of failure, because it looks safe.

**Fix.** Either wire a real `sys.assert` step, or downgrade the rule to plain guidance in `functions.<node>.constraints` (and remove it from `non_negotiable`).

### M5 Violation: Path escape

**Problem.** A resource `path` is `../secrets.json`.

**Impact.** The skill reaches outside its folder — a resource-escape threat (ST4).

**Fix.** Confine the path to the skill folder, or move the file to `_shared/` and set `scope: "shared"`.

### M6 Violation: Self-declared trust

**Problem.** The contract carries `"verified": true`.

**Impact.** A consumer might lower its guard based on the skill's own claim (ST6).

**Fix.** Remove the flag. Trust and provenance are judged by the registry / scanner / user, never self-declared.

### M2 Violation: Bad suffix

**Problem.** The folder is named `yijing/` (no `_aisp`).

**Impact.** The discovery glob `*_aisp/aisp.aisop.json` will not find it.

**Fix.** Rename the folder to `yijing_aisp/` and set `id` to match.

---

## Summary

Check conformance in priority order:

1. **Legal first** — is it a valid AISOP program (M1)?
2. **Bindings second** — does every red line point to a real mechanism (M4)?
3. **Safety third** — paths confined, no self-trust, confirm not bypassed (M5 / M6 / SE7).

Only `enforced_by → sys.*` is a hard guarantee; everything else the model reads is policy-as-prompt.

---

> Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
