# Validator Coverage Matrix

> Reference map for what the AISP reference tools check, what remains runtime-evidence-only, and what is outside local validation.

The reference toolchain is a conformance gate, not a trust oracle. A passing static validator, README check, bridge check, runtime trace check, or schema check proves only the property that tool is designed to prove.

For the runnable publication checklist and warning policy, see the [Release Evidence Matrix](release-evidence-matrix.md). This page explains coverage; the release matrix explains how to use that coverage before publishing.

---

## Tool Scope

| Tool | Scope | Proves | Does not prove |
|------|-------|--------|----------------|
| `tools/aisp_validate.py` | Native AISP skill folders and `aisp/` directories | Static M1-M6 plus static SE/EC checks; optional event/provenance-backed R6 evidence | Full runtime behavior, external trust, registry approval |
| `tools/aisp_check_runtime_trace.py` | Runtime trace JSON for one skill | R1/R3/R6/R7 trace evidence and confirm-bypass evidence | That the trace source is trustworthy unless provenance/signature exists |
| `tools/aisp_hash.py` | Contract/resource/package hash manifest | Recomputable local integrity records | Safety, trust, or registry approval |
| `tools/aisp_readme.py` | Generated per-skill `README.md` projections | README derivation consistency with `aisp.aisop.json` | Skill safety or trust |
| `tools/aisp_skill_md.py` | Generated same-folder Agent Skills `SKILL.md` sidecar projections | Sidecar derivation consistency with `aisp.aisop.json` | Agent Skills platform behavior, external trust, or hard execution guarantees |
| `tools/aisp_validate_agent_skill_bridge.py` | Default-but-core-optional Agent Skills `SKILL.md` sidecars | Frontmatter shape, bridge metadata, safe same-folder path to native AISP, native AISP validation | Agent Skills platform behavior, external trust, or AISOP runtime hard guarantees |
| `tools/check_doc_sync.py` | English/Chinese command references | Core command synchronization across docs | Semantic translation quality outside the checked command set |
| `tools/check_markdown_links.py` | Local Markdown links and heading anchors | Repository-local documentation links resolve | External website availability or semantic correctness |

---

## Rule Coverage

| Rule | Static validator | Runtime trace checker | Bridge validator | Notes |
|------|------------------|-----------------------|------------------|-------|
| M1 Legal AISOP program | Full | No | Via native AISP validation | 2-message array, required fields, fixed `loading_mode: "node"`, `aisop.main`, graph/function shape, static `execute_mode` declaration checks |
| M2 Folder/file/id shape | Full | No | Via native AISP validation | `_aisp` suffix and `id == folder` |
| M3 `aisp_contract` object | Full | No | Via native AISP validation | Rejects JSON-in-string and missing/invalid contract basics |
| M4 `enforced_by` mechanism exists | Full for static references | No | Via native AISP validation | `tools` hardness still depends on R6 evidence |
| M5 Resource path/mode inventory | Partial/full static | No | Via native AISP validation | Declared paths, escapes, modes, undeclared-use warnings |
| M6 No self-declared trust | Full static | No | Via native AISP validation | Registry/user/runtime decide trust |
| R1 Contract read and node fidelity | No | Trace evidence | No | Requires real runtime events |
| R2 Enforce `enforced_by` | Static binding only | Partial trace evidence | No | Static check proves mechanism exists, not that runtime used it |
| R3 Contract visible to model | No | Trace evidence | No | Requires runtime trace |
| R4 Open-world AISOP compatibility | Documented boundary | No | No | Requires AISOP runtime behavior, not local package shape |
| R5 Trust gate / prefer index | No | Advisory trace evidence | No | Registry/runtime/user policy concern |
| R6 Tool-enforcement declaration | Static warning/strict evidence consumption | Trace event evidence | No | Bare top-level hard attestation is not enough |
| R7 `execute_mode` dispatch fidelity | Static declaration only | Trace evidence | No | Static validation checks missing/invalid declarations and warns when non-agent nodes exceed the 10-step review heuristic; real sub-agent dispatch requires runtime events |
| SE1 Path confinement | Full static for declared resources | No | Bridge path confinement for `metadata.aisp_program` | Resource and bridge paths are separate checks |
| SE2 Remote resource gate | Static resource check | No | Bridge URL rejection for `metadata.aisp_program` | Runtime still must gate actual remote use |
| SE3 Mode gating | Static resource-use check | No | No | Cannot prove runtime will obey modes without trace |
| SE4 Least authority | Static script/tool warning | No | No | Requires review/runtime policy for full assurance |
| SE5 Discovery script safety | Static script scan | No | No | Applies to `aisp_list.py` |
| SE6 No self trust | Full static | No | Via native AISP validation | Mirrors M6 |
| SE7 Confirm invariant | Static references only | Trace confirm-bypass evidence | No | Hard guarantee requires runtime behavior |
| SE8 Read-only during execution | No | Trace/event evidence if emitted | No | Runtime/lifecycle concern |
| EC1 `aisp/` directory contract | Static directory check | No | No | Directory-level README/index/script |
| EC2 Index/folder consistency | Static directory check | No | No | `aisp_list.json` is a cache |
| EC3 `_shared/` scope | Static directory/resource check | No | No | Shared resources are not skills |
| EC4 Registry provenance | Hash/schema artifact support | No | No | Registry-side evidence |
| EC5 Generation | Advisory/documented | No | No | Generated skills still pass M1-M6 |
| EC6 Evolution safety | Advisory/documented | No | No | Needs diff/review workflow |
| EC7 Default `SKILL.md` bridge | Lightweight warning in main validator when missing or drifted; no core failure | No | Full sidecar validation | Checks bridge shape, metadata, safe same-folder path, native AISP |
| EC8 Generated per-skill README | Warning/default or strict fail in main validator | No | Via native AISP validation when `--strict-readme` is used | Derivation consistency only |

---

## Release Gate Recommendation

For repository CI and release candidates, run:

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

Regenerate derived files only when you intentionally update them:

```bash
python -B examples/aisp/aisp_list.py --json
python -B tools/aisp_readme.py examples/aisp/yijing_aisp --write
python -B tools/aisp_skill_md.py examples/aisp/yijing_aisp --write
```

This gate is intentionally layered:

- Static conformance catches malformed or inconsistent packages before execution.
- Runtime trace evidence proves selected runtime behaviors, only to the extent the trace source is trusted.
- README and `SKILL.md` sidecar generation/checks prove derived artifact consistency and bridge shape, not safety.
- Hash manifests prove local integrity, not trust.

---

Align Axiom 0: Human Sovereignty and Wellbeing | Protocol: AISP | Execution: AISOP | Executor: SoulBot
