# Snapshot Release Workflow

The `aisp_creator_evolution_aisp` example carries offline snapshots of AISP
specification files, protocol schemas, reference tools, and AISOP specification
files. These snapshots make the example package reviewable when it is copied or
distributed outside the repository.

Snapshots are local integrity evidence only. They are not a trust root, registry
approval, freshness proof, or signature.

---

## When To Refresh

Refresh the relevant snapshot whenever one of these source areas changes:

| Source area | Snapshot directory |
|-------------|--------------------|
| `specification/` | `examples/aisp/aisp_creator_evolution_aisp/aisp_specification/` |
| `schemas/` | `examples/aisp/aisp_creator_evolution_aisp/aisp_protocol_schemas/` |
| `tools/` | `examples/aisp/aisp_creator_evolution_aisp/aisp_reference_tools/` |
| AISOP upstream specification | `examples/aisp/aisp_creator_evolution_aisp/aisop_specification/` |

If a new reference tool is added, also update:

- `examples/aisp/aisp_creator_evolution_aisp/aisp.aisop.json`
- `examples/aisp/aisp_creator_evolution_aisp/aisp_reference_tools/README.md`
- `examples/aisp/aisp_creator_evolution_aisp/aisp_reference_tools/MANIFEST.sha256.json`
- `examples/aisp/aisp_creator_evolution_aisp/README.md` via `aisp_readme.py --write`
- `examples/aisp/aisp_creator_evolution_aisp/SKILL.md` via `aisp_skill_md.py --write`

---

## Working-Tree Snapshot

Before the final release commit exists, snapshot metadata SHOULD say
`snapshot_state: working_tree_uncommitted`. This is an honesty marker: the
snapshot reflects the local working tree, not an immutable published commit.

Run the normal gate while the snapshot is in that state:

```bash
python -B tools/aisp_validate.py examples/aisp
python -B tools/aisp_validate.py --json examples/aisp/yijing_aisp
python -B tools/aisp_validate.py --strict-tools --runtime-trace examples/aisp/stock_analysis_aisp/evals/runtime-traces/hard-pass.json examples/aisp/stock_analysis_aisp
python -B tools/aisp_validate.py --strict-tools --runtime-trace examples/aisp/aisp_creator_evolution_aisp/evals/runtime-traces/hard-pass.json examples/aisp/aisp_creator_evolution_aisp
python -B tools/aisp_check_runtime_trace.py examples/aisp/stock_analysis_aisp examples/aisp/stock_analysis_aisp/evals/runtime-traces/hard-pass.json
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
python -B -m unittest discover -s tests
```

`git diff --exit-code` is a final clean-tree check. It should fail while the
working-tree snapshot is still carrying intentional uncommitted edits.

---

## Final Release Snapshot

After the final commit is created, refresh snapshot metadata to the final commit
hash before publishing. The snapshot state can then move from
`working_tree_uncommitted` to a release-state value chosen by the maintainer,
for example `committed`.

Required checks after metadata refresh:

```bash
python -B tools/check_doc_sync.py --root .
python -B tools/check_markdown_links.py --root .
git diff --check
git diff --exit-code
python -B examples/aisp/aisp_list.py --check
python -B tools/aisp_readme.py examples/aisp --check-all
python -B tools/aisp_skill_md.py examples/aisp --check-all
python -B tools/aisp_validate.py --strict-readme examples/aisp
python -B examples/aisp/aisp_creator_evolution_aisp/scripts/check_generated_candidate.py examples/aisp/aisp_creator_evolution_aisp --creator-root examples/aisp/aisp_creator_evolution_aisp
python -B examples/aisp/aisp_creator_evolution_aisp/scripts/simulate_aisp_flow.py examples/aisp/aisp_creator_evolution_aisp
```

If any snapshot file changes, regenerate the creator README and SKILL.md projections:

```bash
python -B tools/aisp_readme.py examples/aisp/aisp_creator_evolution_aisp --write
python -B tools/aisp_skill_md.py examples/aisp/aisp_creator_evolution_aisp --write
```

If the release history is rewritten after this step, for example by squashing
to a single init-style commit or by force-publishing a recreated history, rerun
the final release snapshot refresh after the rewrite and before publishing.
Otherwise `source_commit` can name a commit that no longer exists in the
published repository.

Single-commit init-force releases are a special case: a commit cannot embed its
own final hash in tracked files, because changing those files changes the
commit hash. For that profile, set `snapshot_state` to
`init_force_single_commit` and `source_commit` to
`self-contained-init-force-release`, then treat the published release commit
plus the manifest hashes as local integrity evidence only. Do not reuse this
sentinel for normal multi-commit releases where a concrete source commit exists.

---

## Trust Boundary

Snapshot hashes prove only that the local snapshot contents match the recorded
manifest. They do not prove that the upstream source is trustworthy, current, or
safe. Publication trust still requires external provenance, registry policy, or
signature evidence outside the skill package.

> Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
