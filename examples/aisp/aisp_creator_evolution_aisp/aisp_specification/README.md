# AISP Specification Snapshot

This directory is a read-only offline reference snapshot of the complete
`specification/` directory from
`https://github.com/AIXP-Labs/AISP/tree/main/specification`.

- source commit: `uncommitted-working-tree`
- snapshot date: `2026-11-14`
- snapshot state: `working_tree_revision`
- snapshot note: local internal protocol candidate copied from the working tree;
  no Git or network verification. Manifest hashes prove local integrity only,
  not an unchanged upstream commit or external trust.
- scope: complete AISP specification files copied from the source
  `specification/` directory
- manifest: `MANIFEST.sha256.json`

## Files

- `AISP_Protocol.md`
- `AISP_Protocol_cn.md`
- `aisp.proto`
- `standards/AISP_Standard.core.aisop.json`
- `standards/AISP_Standard.ecosystem.aisop.json`
- `standards/AISP_Standard.security.aisop.json`

## Boundary

The files in this directory are reference material for AISP skill package
structure, contract semantics, conformance rules, ecosystem rules, and standard
profiles. They are not a trust root.

The Markdown specification files are copied from the local working tree. Links
to AISP repository companion materials use public GitHub URLs so the snapshot
remains readable when the skill package is distributed outside the repository.

The hashes in `MANIFEST.sha256.json` provide local integrity evidence only. They
show whether the copied snapshot has changed after capture; they do not prove
that the upstream source is trusted, current, safe, or authoritative.
