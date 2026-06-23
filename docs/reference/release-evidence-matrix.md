# Release Evidence Matrix

[中文版](release-evidence-matrix_CN.md)

> Publication checklist for AISP repositories and skill packages. This page separates what each release gate proves from what it cannot prove.

The release gate is layered on purpose. Static validation, generated-document checks, runtime trace checks, and clean-tree checks are different kinds of evidence. Passing all of them makes the repository releasable; it still does not make any unsigned package a trusted package.

---

## Audience Paths

| Audience | Start with | Then read |
|----------|------------|-----------|
| Skill author | [`docs/guides/first-aisp-skill.md`](../guides/first-aisp-skill.md) | [`docs/guides/conformance-walkthrough.md`](../guides/conformance-walkthrough.md), [`docs/reference/generated-readme.md`](generated-readme.md) |
| Runtime implementer | [`docs/reference/registry-runtime-artifacts.md`](registry-runtime-artifacts.md) | [`docs/reference/validator-coverage.md`](validator-coverage.md), [`specification/AISP_Protocol.md`](../../specification/AISP_Protocol.md) |
| Release reviewer | This page | [`docs/reference/validator-coverage.md`](validator-coverage.md), [`docs/topics/security-model.md`](../topics/security-model.md) |
| Registry maintainer | [`docs/reference/registry-runtime-artifacts.md`](registry-runtime-artifacts.md) | [`docs/reference/threat-taxonomy.md`](threat-taxonomy.md), [`docs/topics/discovery-and-registry.md`](../topics/discovery-and-registry.md) |

---

## Evidence Levels

| Evidence level | Produced by | Good for | Not good for |
|----------------|-------------|----------|--------------|
| Static package evidence | `aisp_validate.py`, schemas, index checks | Proving folder shape, contract shape, bindings, resource paths, and static security rules | Proving runtime behavior |
| Derived projection evidence | `aisp_readme.py`, `aisp_skill_md.py`, bridge validator | Proving `README.md` / `SKILL.md` are deterministic projections of `aisp.aisop.json` | Proving safety, trust, or platform execution |
| Runtime trace evidence | `aisp_check_runtime_trace.py`, `--runtime-trace` | Proving selected R-series behavior happened in the supplied trace | Proving an unsigned trace source is trustworthy |
| Integrity evidence | `aisp_hash.py`, manifests | Recomputing local content integrity | Proving endorsement, safety, or provenance by itself |
| Repository hygiene evidence | doc checks, tests, clean-tree checks | Proving docs, links, tests, and committed artifacts are coherent | Proving external trust or runtime behavior |

---

## Release Gate

Run the release gate from the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\release_check.ps1
```

Add `-IncludePytest` for the optional pytest path, and `-RequireClean` for the
final pre-publish clean-tree check. The auditable command expansion is:

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

---

## Command Matrix

| Command | Evidence produced | Expected release result |
|---------|-------------------|-------------------------|
| `powershell -ExecutionPolicy Bypass -File scripts\release_check.ps1` | Local wrapper for the release gate plus residue, private-path, and forbidden AIAP-structure scans | PASS when all bundled checks pass; use `-RequireClean` only after intended edits are committed. |
| `python -B tools/aisp_validate.py examples/aisp` | Static M/SE/EC package validation for all examples | PASS. Static-only runs may retain `AISP_W_R6_TOOLS_CONDITIONAL` for `enforced_by: tools`; that warning is honest unless runtime/tool evidence is supplied. |
| `python -B tools/aisp_validate.py --json examples/aisp/yijing_aisp` | Machine-readable static validation output for a low-risk reference skill | PASS with zero failures. |
| `python -B tools/aisp_validate.py --strict-tools --runtime-trace ... stock_analysis_aisp` | Strict R6/R7 evidence consumption for the stock example | PASS only when event-backed runtime trace evidence matches the skill. |
| `python -B tools/aisp_validate.py --strict-tools --runtime-trace ... aisp_creator_evolution_aisp` | Strict R6 evidence consumption for the creator example | PASS only when event-backed runtime trace evidence matches the skill. |
| `python -B tools/aisp_check_runtime_trace.py examples/aisp/stock_analysis_aisp ... hard-pass.json` | Direct runtime trace schema/behavior check for stock | PASS for the checked trace. |
| `python -B tools/aisp_check_runtime_trace.py examples/aisp/aisp_creator_evolution_aisp ... hard-pass.json` | Direct runtime trace schema/behavior check for creator | PASS for the checked trace. |
| `python -B tools/aisp_hash.py --json examples/aisp/yijing_aisp` | Recomputable package integrity manifest | Emits deterministic hashes; not a trust proof. |
| `python -B examples/aisp/aisp_list.py --check` | Discovery index consistency | PASS when `aisp_list.json` matches folders. |
| `python -B tools/aisp_readme.py examples --check-all` | Generated per-skill README consistency | PASS when README projections are deterministic and current. |
| `python -B tools/aisp_skill_md.py examples --check-all` | Generated same-folder `SKILL.md` projection consistency | PASS when sidecars are deterministic and current. |
| `python -B tools/aisp_validate.py --strict-readme examples/aisp` | Release-profile README requirement | PASS when missing/manual/drifted generated READMEs are absent. |
| `python -B tools/aisp_validate_agent_skill_bridge.py examples/aisp --strict-readme` | Thin sidecar bridge shape plus native AISP validation | PASS when `SKILL.md` sidecars stay source-of-truth safe. |
| `python -B tools/check_doc_sync.py --root .` | Synchronized command references, snapshots, workflow checks, ADR mirrors | PASS when docs and generated snapshots do not drift. |
| `python -B tools/check_markdown_links.py --root .` | Local Markdown link and anchor resolution | PASS when repository-local docs resolve. |
| `git diff --check` | Whitespace/conflict-marker hygiene | PASS when no whitespace errors exist. |
| `git diff --exit-code` | Tracked file cleanliness | PASS only after all tracked intended edits are committed. |
| `git status --porcelain=v1 --untracked-files=all` | Full working tree cleanliness, including untracked files | PASS only when it prints no output. |
| `python -B -m unittest discover -s tests` | Regression suite | PASS when tool behavior and fixtures still match expectations. |

---

## Warning Policy

Warnings are not all equal:

| Warning class | Meaning | Release handling |
|---------------|---------|------------------|
| `AISP_W_R6_TOOLS_CONDITIONAL` | A skill uses `enforced_by: tools`, but the current check is static-only or lacks hard evidence. | Expected in static-only review. Resolve with event-backed runtime trace or provenance-bearing hard tool capability evidence for strict release gates. |
| `AISP_W_R6_TOOLS_ATTESTED_NOT_VERIFIED` | A runtime/tool artifact claims hard enforcement but lacks independent evidence. | Do not treat as proof. Add event/provenance evidence or keep the warning visible. |
| EC7 `SKILL.md` warnings | The optional/default sidecar is missing or drifted. | Core AISP can remain valid, but release profiles may require the sidecar unless explicitly opted out. |
| EC8 generated README warnings | Per-skill README is missing/manual/drifted outside strict mode. | Regenerate or run strict release profile to make drift fail. |
| Missing `execute_mode` warnings | A function omits explicit dispatch intent; runtime falls back to inline. | Acceptable compatibility fallback, but release-quality examples should declare `inline` or `agent` explicitly. |
| `AISP_W_M1_EXECUTE_MODE_AGENT_RECOMMENDED` | A non-agent function has more than 10 numeric `stepN` execution steps. | Review whether `agent` is appropriate. The threshold is a review heuristic, not a restriction on using `agent` for shorter high-isolation nodes. |

---

## Trust Boundary

This gate proves repository and package coherence. It does not prove that a package from an untrusted source is safe to run.

- A passing generated README check proves derivation consistency, not trust.
- A passing `SKILL.md` bridge check proves sidecar shape, not hard execution on Agent Skills platforms.
- A passing hash check proves local integrity, not endorsement.
- A passing runtime trace check proves only what the supplied trace records, subject to trace provenance.
- External trust still comes from registry policy, signatures, provenance, human review, and the runtime's real enforcement behavior.

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
