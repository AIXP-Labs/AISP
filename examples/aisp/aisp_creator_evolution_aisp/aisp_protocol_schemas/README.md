# AISP Protocol Schemas Snapshot

This directory is a read-only offline reference snapshot of the AISP protocol
schemas from `https://github.com/AIXP-Labs/AISP/tree/main/schemas`.

- source commit: `self-contained-init-force-release`
- snapshot date: `2026-06-22`
- snapshot state: `init_force_single_commit`
- snapshot note: bundled in the same single init-force release commit; use the
  published release commit plus this manifest as local integrity evidence only.
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
