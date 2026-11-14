# Validator Coverage Matrix

> Reference map for what the AISP reference tools check, what remains runtime-evidence-only, and what is outside local validation.

The reference toolchain is a conformance gate, not a trust oracle. A passing static validator, README check, bridge check, runtime trace check, or schema check proves only the property that tool is designed to prove.

For the runnable publication checklist and warning policy, see the [Release Evidence Matrix](release-evidence-matrix.md). This page explains coverage; the release matrix explains how to use that coverage before publishing.

---

## Tool Scope

| Tool | Scope | Proves | Does not prove |
|------|-------|--------|----------------|
| `tools/aisp_validate.py` | Native AISP skill folders and `aisp/` directories | Static M1-M7 plus static SE/EC checks; bounded v1 capability-shape validation and optional event/provenance-bearing R6 evidence criteria | Full runtime behavior, external trust, registry approval |
| `tools/aisp_check_runtime_trace.py` | Runtime trace JSON for one skill | Published v1 trace shape plus selected R1/R3/R6/R7 and confirm-bypass checks | Generic schema-engine behavior, complete runtime conformance, independent event authenticity or provenance/signature authentication |
| `tools/aisp_hash.py` | Contract/resource/package hash manifest | Recomputable local integrity records | Safety, trust, or registry approval |
| `tools/aisp_readme.py` | Generated per-skill `README.md` projections | README derivation consistency with `aisp.aisop.json` | Skill safety or trust |
| `tools/aisp_skill_md.py` | Required same-folder Agent Skills interface (M7) | Existence, skill-derived name/description/license, fixed bootstrap and launch configuration and version-policy format; explicit recognized-legacy migration only on write | Executor availability/certification, external trust, runtime behavior or completion |
| `tools/aisp_validate_agent_skill_bridge.py` | Required generated Agent Skills compatibility interfaces | Same shared read-only M7 check, existing frontmatter/injection/path checks and native AISP validation | Host runtime behavior, trust or executor certification |
| `tools/check_doc_sync.py` | English/Chinese references and protocol layout | Commands, one ordered set of numbered protocol sections, intact M3 rule, snapshot metadata/hashes and ADR mirrors | General prose/translation quality, complete normative equivalence or upstream origin |
| `tools/check_markdown_links.py` | Confined Markdown scan targets, prose links and heading anchors | Missing/out-of-root targets fail; ordinary backtick/tilde fences and inline examples do not create links/anchors | Complete CommonMark rendering, every container/HTML construct, MkDocs build-directory boundaries, external availability or semantic correctness |

---

## Rule Coverage

The runtime tools use only the standard library and do not invoke jsonschema.
The checker implements the bounded published v1 trace shape: required fields,
types, enums and dispatch-event conditionals. Optional development tests compare
these cases with the JSON Schema; unknown fields/events remain permitted.
Malformed modes and string booleans fail before runtime-rule checks. R7 requires
every recorded dispatch for an agent node to declare both mode and dispatch as
agent; a later valid event cannot hide an earlier contradiction. R6 rejects
hard declarations conflicting with advisory/unknown events. This is not a
generic schema engine, event authentication or full runtime certification.
Recorded events for known inline nodes must also declare inline mode/dispatch,
including nodes with no explicit mode. This adds no mandatory inline-event
coverage; statically invalid declarations still belong to core validation.
`runtime_conformant` still means no implemented check failed.

| Rule | Static validator | Runtime trace checker | Bridge validator | Notes |
|------|------------------|-----------------------|------------------|-------|
| M1 Legal AISOP program | Listed static structure checks | No | Via native AISP validation | 2-message array, required fields, known optional text types, params object and tools string array, fixed `loading_mode: "node"`, JSON-flow object/edge-field shape, graph/function references, on_error shape/handler existence and `execute_mode` declarations; not license-identifier certification, parameter-value schemas, prompt semantics, error dispatch, every graph context or expression's runtime validity |
| M2 Folder/file/id shape | Full | No | Via native AISP validation | `_aisp` suffix and `id == folder` |
| M3 `aisp_contract` object | Full | No | Via native AISP validation | Rejects JSON-in-string and missing/invalid contract basics |
| M4 `enforced_by` mechanism exists | Full for static references | No | Via native AISP validation | `tools` hardness still depends on R6 evidence |
| M5 Resource path/mode inventory | Partial/full static | No | Via native AISP validation | Declared paths, escapes, modes, undeclared-use warnings |
| M6 No self-declared trust | Full static | No | Via native AISP validation | Registry/user/runtime decide trust |
| M7 Required generated compatibility interface | Shared full static check | No | The same function, without core callback | Launch strings and frozen version policy prove format only, not compatibility or execution |
| R1 Contract read and node fidelity | No | Partial contract-read/identity claims plus explicit false/event contradiction rejection | No | General node fidelity needs separate runtime evidence; accepting a trace is not event authentication |
| R2 Enforce `enforced_by` | Static binding only | No general assertion/semantic check | No | Separate R6/R7 and SE7 checks do not prove that every bound assertion was evaluated |
| R3 Contract visible to model | No | Trace evidence; reject explicit denial/event conflicts | No | Requires runtime trace |
| R4 Open-world AISOP compatibility | Documented boundary | No | No | Requires AISOP runtime behavior, not local package shape |
| R5 Trust gate / prefer index | No | No | Registry/runtime/user policy concern; not verified by the reference trace checker |
| R6 Tool-enforcement declaration | Static warning/strict evidence consumption | Trace event evidence | No | Bare top-level hard attestation is not enough |
| R7 `execute_mode` dispatch fidelity | Static declaration only | Trace evidence | No | Static validation checks missing/invalid declarations and warns when non-agent nodes exceed the 10-step review heuristic; real sub-agent dispatch requires runtime events |
| SE1 Path confinement | Resolved resource and shared-root confinement | No | Bridge path confinement for `metadata.aisp_program`; SKILL.md link identity retained | Checked before reads; not a guarantee against hostile concurrent filesystem changes |
| SE2 Remote resource gate | Static resource check | No | Bridge URL rejection for `metadata.aisp_program` | Runtime still must gate actual remote use |
| SE3 Mode gating | Selected literal reads and run/bg calls | No | No | Handles supported Python option clusters/file operands and lexical aliases; same-file conflicts are order-independent; all-deny scoped candidates fail, other unresolved scope warns without merging permissions; no runtime proof |
| SE4 Least authority | Static script/tool warning | No | No | Requires review/runtime policy for full assurance |
| SE5 Discovery script safety | Bounded AST scan of selected imports/calls | No | No | Confines and checks `aisp_list.py` without executing it; not arbitrary-code verification or a sandbox; trust gate/manual review remain necessary |
| SE6 No self trust | Full static | No | Via native AISP validation | Mirrors M6 |
| SE7 Confirm invariant | Static references only | Trace confirm-bypass evidence | No | Hard guarantee requires runtime behavior |
| SE8 Read-only during execution | No | No | Requires separate runtime/file-change evidence; the reference trace checker has no SE8 enforcement check |
| EC1 `aisp/` directory contract | Static directory check | No | No | Directory-level README/index/script |
| EC2 Index/folder consistency | Static directory check | No | No | Compare ids/paths and name, summary, category, tags, when_to_use and risk_level; drift remains a warning because the folder is authoritative |
| EC3 `_shared/` scope | Static directory/resource check | No | No | Shared resources are not skills |
| EC4 Registry provenance | Hash/schema artifact support | No | No | Registry-side evidence |
| EC5 Generation | Advisory/documented | No | No | Generated skills still pass M1-M7 |
| EC6 Evolution safety | Advisory/documented | No | No | Needs diff/review workflow |
| EC7 Legacy interoperability mapping | Missing/old/drifted interface fails M7; no opt-out | No | M7 plus existing bridge checks | `agent_skills_bridge`; fixed bootstrap is not business-logic copying |
| EC8 Generated per-skill README | Warning/default or strict fail in main validator | No | Via native AISP validation when `--strict-readme` is used | Derivation consistency only |

---

## Creator Candidate Gate

`scripts/check_generated_candidate.py` inside the Creator example is a static
preflight plus executable regression runner, not a read-only/no-network
sandbox. Static failures prevent candidate-script execution; every script
case is shape-checked before any replay, and unexpected failures stop later
cases. Reference warnings are retained in the candidate summary. Replay
success does not prove safety or faithful runtime enforcement; trust/review
the tools and commands, and use an isolated host. Schema resources follow
their declared skill/shared scope; behavior cases need declared inputs and
non-empty expectations.

Package residue guards reject `.execution_cache/` and `.soulrun_cache/` along
with Python bytecode and local evolution residue. These are engineering-package
checks, not a complete private-data detector or runtime enforcement mechanism.
Reviewed evidence directories such as `evals/runtime-traces/` are not hidden by
the ignore policy or rejected merely for containing regression records.

Native and bridge success claims cannot override failed summaries/results or
empty result lists. Bridge warnings remain visible and legacy release-blocking
warnings still fail. Candidate JSON inputs (including schema/eval artifacts and
checker output) reject duplicate keys and non-JSON numeric constants. Consistent
report structure does not authenticate a checker or prove its claims.

The Creator lightweight validator agrees on the selected M1 metadata types,
including optional tools arrays, and the missing/blank-string license warning.
It also checks the existing M4 non-empty allow-list requirement when a red line
binds to tools; an unbound omitted/empty inventory remains allowed. This does
not evaluate R6 hardness or grant permissions.
It remains a subset; its success alone does not replace reference M1-M7, M4/R6
tool-binding/evidence checks or the candidate gate.

Repository snapshot auditing rejects malformed/duplicate-key manifests and
escaping paths before reading listed file bytes. Resource-use matching keeps
dotfiles such as `.env` distinct from `env`; a basename coincidence must not
borrow another resource's mode.

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
- README checks prove derivation consistency. M7 checks the required interface's derived header, fixed bootstrap and launch configuration and version-policy format; neither certifies an executor, safety, trust or completed execution.
- Hash manifests prove local integrity, not trust.

The checked-in traces are fixtures. The reference checker does not authenticate an event or a provenance claim simply because the required fields are present. Offline checks cannot discharge a real-host assertion failure, certify independent human gate handling, or grant publication authorization.

For documentation-site delivery, run a separate strict MkDocs build to a
dedicated directory outside the checkout. A repository-local link can exist
on disk yet still point outside MkDocs' `docs/` input tree and fail the build.

---

Align Axiom 0: Human Sovereignty and Wellbeing | Protocol: AISP | Execution: AISOP | Default Executor: SoulRun (replaceable)
