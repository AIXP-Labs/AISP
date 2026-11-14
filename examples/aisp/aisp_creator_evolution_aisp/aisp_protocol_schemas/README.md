# AISP Protocol Schemas Snapshot

This directory is a read-only offline reference snapshot of the AISP protocol
schemas from `https://github.com/AIXP-Labs/AISP/tree/main/schemas`.

- source commit: `uncommitted-working-tree`
- snapshot date: `2026-11-13`
- snapshot state: `working_tree_revision`
- snapshot note: local internal protocol candidate copied from the working tree;
  no Git or network verification. Manifest hashes prove local integrity only,
  not an unchanged upstream commit or external trust.
- manifest: `MANIFEST.sha256.json`

## Files

- `aisp-contract-v1.schema.json`
- `registry-manifest-v1.schema.json`
- `runtime-trace-v1.schema.json`
- `tool-capabilities-v1.schema.json`

## Boundary

These schemas are protocol-level machine-readable references. They complement
the generator's own internal schemas in `schemas/`, which describe research,
skill-design, and evolution-evidence objects used by this meta-skill.

Schema validation proves shape and selected constraints only. It does not prove
that a skill, runtime trace, registry manifest, or tool-capability document is
trusted, safe, current, or signed by an external authority.
