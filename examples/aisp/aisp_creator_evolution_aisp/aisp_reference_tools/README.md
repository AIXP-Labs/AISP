# AISP Reference Tools Snapshot

This directory is an offline snapshot of the AISP reference tools from
`https://github.com/AIXP-Labs/AISP/tree/main/tools`.

- source commit: `uncommitted-working-tree`
- snapshot date: `2026-11-13`
- snapshot state: `working_tree_revision`
- snapshot note: local internal protocol candidate copied from the working tree;
  no Git or network verification. Manifest hashes prove local integrity only,
  not an unchanged upstream commit or external trust.
- manifest: `MANIFEST.sha256.json`

## Files

- `aisp_validate.py`
- `aisp_hash.py`
- `aisp_readme.py`
- `aisp_skill_md.py`
- `aisp_check_runtime_trace.py`
- `aisp_validate_agent_skill_bridge.py`
- `check_doc_sync.py`
- `check_markdown_links.py`
- `__init__.py`

## Boundary

These files are reference implementations and optional local helpers. They are
not a trust root.

Interface checking and ordinary regeneration stay offline. First generation or
an explicit refresh of the default SoulRun policy queries official PyPI and
freezes a concrete lower bound; it never installs an executor. To generate
offline or configure another executor, provide an explicit
`--executor-version-requirement '>=X.Y.Z'` or `'==X.Y.Z'`. Explicit policies are
preserved on refresh. SoulRun is the replaceable default, not an AISP dependency.

Use `aisp_validate.py`, `aisp_hash.py`, `aisp_readme.py`,
`aisp_skill_md.py`, `aisp_check_runtime_trace.py`, and
`aisp_validate_agent_skill_bridge.py` for
stronger local checks when their inputs are available. `check_doc_sync.py` and
`check_markdown_links.py` are repository-doc oriented and should be treated as
read-only reference material inside this standalone skill package.

Passing a reference tool check means only that the checked artifact satisfies
the rules implemented by that tool for the supplied inputs. Runtime enforcement,
tool-hardness, signatures, registry provenance, and publication trust still
require independent external evidence.
