# AISP Reference Tools Snapshot

This directory is an offline snapshot of the AISP reference tools from
`https://github.com/AIXP-Labs/AISP/tree/main/tools`.

- source commit: `self-contained-init-force-release`
- snapshot date: `2026-06-22`
- snapshot state: `init_force_single_commit`
- snapshot note: bundled in the same single init-force release commit; use the
  published release commit plus this manifest as local integrity evidence only.
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
