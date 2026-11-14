# Release Evidence Matrix

[中文版](release-evidence-matrix_CN.md)

> Publication checklist for AISP repositories and skill packages. This page separates what each release gate proves from what it cannot prove.

The release gate is layered on purpose. Static validation, generated-document checks, runtime trace checks, and clean-tree checks are different kinds of evidence. Passing the repository checks is necessary, not sufficient, for publication: applicable real-host/runtime acceptance, review of known limitations, and explicit publication authorization are separate requirements. None makes an unsigned package trusted.

---

## Audience Paths

| Audience | Start with | Then read |
|----------|------------|-----------|
| Skill author | [`docs/guides/first-aisp-skill.md`](../guides/first-aisp-skill.md) | [`docs/guides/conformance-walkthrough.md`](../guides/conformance-walkthrough.md), [`docs/reference/generated-readme.md`](generated-readme.md) |
| Runtime implementer | [`docs/reference/registry-runtime-artifacts.md`](registry-runtime-artifacts.md) | [`docs/reference/validator-coverage.md`](validator-coverage.md), [`specification/AISP_Protocol.md`](https://github.com/AIXP-Labs/AISP/blob/main/specification/AISP_Protocol.md) |
| Release reviewer | This page | [`docs/reference/validator-coverage.md`](validator-coverage.md), [`docs/topics/security-model.md`](../topics/security-model.md) |
| Registry maintainer | [`docs/reference/registry-runtime-artifacts.md`](registry-runtime-artifacts.md) | [`docs/reference/threat-taxonomy.md`](threat-taxonomy.md), [`docs/topics/discovery-and-registry.md`](../topics/discovery-and-registry.md) |

---

## Evidence Levels

| Evidence level | Produced by | Good for | Not good for |
|----------------|-------------|----------|--------------|
| Static package evidence | `aisp_validate.py`, schemas, index checks | Proving folder shape, contract shape, bindings, resource paths, and static security rules | Proving runtime behavior |
| Derived interface evidence | `aisp_readme.py`, `aisp_skill_md.py`, bridge validator | README derivation; SKILL.md consistency with business program, five launch strings plus the frozen version policy and generator revision | Executor certification, safety, trust or platform execution |
| Runtime trace evidence | `aisp_check_runtime_trace.py`, `--runtime-trace` | Checking selected R-series event claims in the supplied trace | Independently proving those events happened or that the trace source is trustworthy |
| Integrity evidence | `aisp_hash.py`, manifests | Recomputing local content integrity | Proving endorsement, safety, or provenance by itself |
| Repository hygiene evidence | doc checks, tests, clean-tree checks | Proving docs, links, tests, and committed artifacts are coherent | Proving external trust or runtime behavior |

---

## Release Gate

Run the release gate from the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\release_check.ps1
```

Add `-IncludePytest` for the optional pytest path (install pytest separately;
`[dev]` metadata only declares jsonschema). `-RequireClean` adds the final clean-tree
check, but `git diff --check` always runs in the wrapper. If Git is prohibited,
do not invoke the wrapper; run only permitted individual non-Git checks and
record that the full release gate was not run.

The following shared reference list is not a literal wrapper/CI expansion.
Both also check JSON syntax, the wrapper includes extra residue/private-path
scans, and CI checks committed whitespace rather than the working-tree diff.

The private-path scan checks selected generic path/key markers in files smaller
than 5 MB outside `.git`; it is not a complete secret or personal-data detector.
An unreadable scanned file fails the scan rather than being silently skipped;
an empty readable file is valid. No per-person username denylist is embedded.

Ignored runtime/evolution caches still fail the residue gate. Ignore entries do
not sanitize tracked files, history or distribution archives; review actual
wheel/sdist contents and redacted evidence separately before sharing. Credential
rotation and any history cleanup require separate authorized maintenance.

The archive regression requires the declared build backend and tests stale
`*.egg-info/SOURCES.txt` as well as real wheel/sdist payloads. `MANIFEST.in`
excludes selected private patterns; wheel package-data settings alone are not
an sdist filter. Each hook's input is checked against the reinjected stale list.
Both formats reject selected private controls; public data controls remain in
sdist, not in the tools-only wheel. Required modules/legal files are compared with
source bytes in both formats; public data controls also require their expected bytes.
Wheel checks exclude public controls by path as well as payload.
Similar directory names and ordinary files named `build`/`dist` remain selected;
actual pruned directory names stay excluded. Keep public sources outside those
directories. These controls do not promise full-repository inclusion.
CI installs the backend and sets `AISP_REQUIRE_ARCHIVE_TEST=1`
to reject an unevaluated build test; an unavailable/older local backend
without that profile skips this specific test and does not supply
archive-verification evidence. The local release wrapper also requires the
archive test and restores the caller's profile afterward; it does not install
dependencies. Prepare the declared build backend before invoking that wrapper.
Where PowerShell is available, a regression exercises the extracted real unit-test
gate with a child-local `python` stub producing controlled native exit codes
`0`, `1` (the usual unittest failure) and `7` (an additional nonzero control).
Literal labels/cleanup paths are read from AST values, allowing ordinary quoting
changes. The stub checks the fixed command's argument count, order and values,
not a joined string; this is not a general shell-equivalence checker.
Labels/approved paths use ordinal case-insensitive equality; command arguments
must be scalar strings with ordinal case-sensitive equality. Arrays and object
argument forms are outside this fixed-command test profile, not forbidden by AISP.
The harness does not emulate native argument-array flattening.
Setup/cleanup comes from the wrapper, in source order; asymmetric initial settings
detect crossed environment restoration. Restored environment values are compared
ordinally as well; legitimate original Unicode values must survive unchanged,
not be sanitized or normalized. Initial-value controls include mixed-case NFC/NFD
forms as well as zero-width characters, on both settings. Missing and empty states follow the host's actual
observable representation. It does not recursively run unit discovery
or execute the full Git-bearing wrapper. This bounded regression is not a full release run.

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
| `python -B tools/aisp_check_runtime_trace.py examples/aisp/stock_analysis_aisp ... hard-pass.json` | Bounded v1 shape and selected runtime checks for stock | PASS for implemented shape/rule checks; not event authentication or full runtime certification. |
| `python -B tools/aisp_check_runtime_trace.py examples/aisp/aisp_creator_evolution_aisp ... hard-pass.json` | Bounded v1 shape and selected runtime checks for creator | PASS for implemented shape/rule checks; not event authentication or full runtime certification. |
| `python -B tools/aisp_hash.py --json examples/aisp/yijing_aisp` | Recomputable package integrity manifest | Emits deterministic hashes; not a trust proof. |
| `python -B examples/aisp/aisp_list.py --check` | Discovery index consistency | PASS when `aisp_list.json` matches folders. |
| `python -B tools/aisp_readme.py examples --check-all` | Generated per-skill README consistency | PASS when README projections are deterministic and current. |
| `python -B tools/aisp_skill_md.py examples --check-all` | Required interface M7 consistency | PASS only for current fixed bootstrap, derived header and legal launch configuration and version policy. |
| `python -B tools/aisp_validate.py --strict-readme examples/aisp` | Release-profile README requirement | PASS when missing/manual/drifted generated READMEs are absent. |
| `python -B tools/aisp_validate_agent_skill_bridge.py examples/aisp --strict-readme` | Shared M7 plus frontmatter/path and native package validation | PASS does not certify an executor or prove completed execution. |
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
| `AISP_W_R6_TOOLS_ATTESTED_NOT_VERIFIED` | A hard-enforcement claim lacks the checker's required event/provenance structure. | Do not treat as proof. Satisfying that structure still does not independently authenticate the evidence. |
| `AISP_W_M5_AMBIGUOUS_USE` | A literal path names distinct scoped resources; at least one declaration permits the operation, but the target remains unknown. If all candidates forbid it, SE3 fails instead. | Review runtime scope resolution and enforcement, or use distinct paths. Do not merge permissions or treat the warning as mode proof. |
| M7 / legacy EC7 interface failures | Required interface is missing, old, malformed or drifted. | Core failure, no opt-out. Explicitly migrate recognized old projections; repair fixed-text drift before writing. Five-value format success is not executor certification. |
| EC8 generated README warnings | Per-skill README is missing/manual/drifted outside strict mode. | Regenerate or run strict release profile to make drift fail. |
| Missing `execute_mode` warnings | A function omits explicit dispatch intent; runtime falls back to inline. | Acceptable compatibility fallback, but release-quality examples should declare `inline` or `agent` explicitly. |
| `AISP_W_M1_EXECUTE_MODE_AGENT_RECOMMENDED` | A non-agent function has more than 10 numeric `stepN` execution steps. | Review whether `agent` is appropriate. The threshold is a review heuristic, not a restriction on using `agent` for shorter high-isolation nodes. |

`--warnings-fail` makes the CLI return nonzero for remaining warnings; it does
not rewrite their severity or codes, nor change a warning-only report's
`conformant: true` into a conformance failure. `--strict-tools` checks R6 evidence
and `--strict-readme` promotes EC8 README problems; neither resolves M5 ambiguity.
The Creator candidate gate retains nonblocking reference warnings, so its success
alone does not discharge the required review of those warnings.
For multiple targets, any conformance/input failure returns 1; otherwise
`--warnings-fail` returns 1 if any target has a warning. A clean target cannot
cancel another target's failure or warning, regardless of argument order.

---

## Trust Boundary

This gate proves repository and package coherence. It does not prove that a package from an untrusted source is safe to run.

- Checked-in example traces are regression fixtures, not independent recordings or certification of a live executor. Events and provenance fields can themselves be self-reported; the checker does not authenticate them merely by accepting their shape.
- One version-gated bootstrap can be assessed through several acceptance scenarios. Scenario coverage is not a set of different bootstrap implementations, exhaustive version coverage, or a substitute for real business/runtime assertions.
- Keep completed execution, unverified assertions, expected refusal/failure stops and delegated answers distinct. A delegated decision is not evidence that an individual-human confirmation requirement was exercised.
- A passing generated README check proves derivation consistency, not trust.
- A passing M7/interface check proves unchanged bootstrap and valid format, not executor certification or hard execution on Agent Skills platforms.
- A passing hash check proves local integrity, not endorsement.
- A passing runtime trace check proves only what the supplied trace records, subject to trace provenance.
- External trust still comes from registry policy, signatures, provenance, human review, and the runtime's real enforcement behavior.

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
