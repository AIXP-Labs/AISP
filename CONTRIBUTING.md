# Contributing to AISP

[中文版](CONTRIBUTING_CN.md)

Thank you for your interest in contributing to the AI Skill Protocol! This document provides guidelines for contributing to the project.

> ⚠️ **Contribution Status (Current Stage)**
>
> We welcome **discussion through GitHub Issues** at this stage of development.
>
> **External Pull Requests are not currently accepted.** If you have a proposal — bug report, feature idea, specification clarification, or conformance rule suggestion — please open an issue describing it. If we agree it adds value, maintainers will implement it and credit you.
>
> This policy may be revisited in the future.

> **Stage Status (V1.0.0)**
>
> AISP is at an early specification stage (V1.0.0). The processes below describe the *target* governance model. Initial decisions are made by AIXP Labs core maintainers; community discussion period scales as the contributor base grows.

## How to Contribute

### Reporting Issues

- Use [GitHub Issues](https://github.com/AIXP-Labs/AISP/issues) to report bugs, suggest features, or propose specification changes
- For specification changes, open an issue describing the proposal; maintainers apply the `spec-change` label
- Provide clear descriptions with examples where possible

### Discussion-Driven Development

Instead of submitting PRs directly:

1. **Open an issue** describing your proposal, bug, or idea
2. **Discuss** with maintainers — clarify scope, design, and approach
3. **Wait for review** — significant proposals follow the [Specification Changes](#specification-changes) process below
4. **If accepted**, maintainers will implement the change and credit you in commit/release notes

### Specification Changes

Proposals affecting normative content (anything in `specification/`) follow this process:

1. An issue with the `spec-change` label describing the proposed change
2. A minimum 14-day discussion period for non-trivial changes (target governance model; current discussion windows scale with contributor count)
3. An Architecture Decision Record (ADR) in `adrs/` for significant decisions
4. Axiom 0 compliance review by maintainers
5. Updated documentation reflecting the change

### Documentation Changes

Suggestions for non-normative content (topics, guides, reference) are welcome via issues — typo fixes, clarifications, additional examples are particularly valued. Maintainers will implement accepted suggestions.

## Writing Guidelines

### RFC 2119 Keywords

When writing normative specification text, use the keywords defined in [RFC 2119](https://tools.ietf.org/html/rfc2119):

- **MUST** / **MUST NOT** — Absolute requirements
- **SHOULD** / **SHOULD NOT** — Strong recommendations with documented exceptions
- **MAY** — Truly optional behavior

These keywords MUST be capitalized when used in their normative sense.

### Terminology

- Use "AISP skill" (not "AISP agent" or "AISP application") for a governed skill package
- Use "skill folder" for an `aisp/<id>_aisp/` directory and "skill file" for its `aisp.aisop.json`
- Use "skill contract" for `user.content.aisp_contract`
- Capitalize "Axiom 0" (it is a proper noun)
- Write "Tier A" (execution) and "Tier S" (contract)
- Never use "Claude" or "Anthropic" as branding; the suffix is always `_aisp`

### Document Structure

- Begin each topic document with a one-paragraph introduction
- Use tables for field specifications
- Use code blocks with language annotations for examples
- Use Mermaid diagrams for flow and architecture illustrations
- Use relative links within the documentation-site tree; link repository-only specifications/schemas through public source URLs so MkDocs does not emit broken outside-tree links
- Keep existing English/Chinese pairs aligned in requirements, commands, examples and limitations; do not imply that English-only references already have translations
- Explain one version-gated bootstrap, not several bootstrap types; preserve explicit constraints, consent, post-install checks and executor neutrality
- Separate static/fixture success, real-host results and publication authorization; never remove red lines or hide runtime warnings to make a check pass

### Documentation Checks

Keep runtime/evolution caches, logs, private keys and local credential files out
of distributable packages. `.gitignore` is protection against accidental addition,
not access control, a secret scanner or removal of already tracked/history data.
The public `.env.example` exception is for reviewed placeholders only. Do not
blanket-ignore JSON/Markdown, fixtures or evidence directories to hide findings.

Build in an isolated environment satisfying `setuptools>=84.1.0`; the reference
tools still have no runtime dependencies. Tests use the separate `jsonschema>=4`
extra; pytest and MkDocs Material remain optional, separately installed tools.
Inspect wheel/sdist contents, not only the checkout. CI uses verified full action
SHAs and read-only contents permission, with credential persistence disabled;
updating those pins requires a fresh upstream check. These settings do not prove
that hosted CI or a complete vulnerability audit has passed.

Use a clean source staging directory as well as an isolated environment: stale
`*.egg-info/SOURCES.txt` can reintroduce files into sdist. `MANIFEST.in` filters
the selected private patterns, while wheel package data stays disabled. The
archive regression reinjects an old source list before each wheel/sdist build,
checking each hook's actual input and private residue exclusions independently.
Selected public data controls remain in sdist, not in the tools-only wheel;
required Python modules and legal files are compared byte-for-byte with the source
in both formats, not merely checked for matching filenames.
Retention does not mean that the tools distributions include the entire repository.
CI installs the declared build backend and sets
`AISP_REQUIRE_ARCHIVE_TEST=1`, making missing/old backends fail rather than skip.
The local release wrapper requires this test too; it does not install the backend
for you. Without this required profile, an older or missing active backend makes
this specific local test skip, not pass; use an
isolated test environment rather than changing global packages automatically.

The reference scripts run from the checkout without installing this repository.
The `[dev]` extra declares jsonschema only. Optional developer installation is
`python -m pip install -e ".[dev]"`; explicit `tools` packaging avoids flat-layout
discovery errors. Source scripts do not require installation.
Install `jsonschema>=4` separately for schema tests and pytest separately if used.
To build the site, install its separate dependency in your chosen environment:

```bash
python -m pip install mkdocs-material
```

From the repository root, choose a dedicated build-output directory outside the
checkout that contains no personal files; MkDocs cleans its output directory:

```bash
python -B tools/check_doc_sync.py --root .
python -B tools/check_markdown_links.py --root .
python -B -m mkdocs build --strict --site-dir ../aisp-docs-site
```

These checks do not run models or authorize publication. A local-link check alone
does not test MkDocs' `docs/` boundary. The full `release_check.ps1` wrapper invokes
Git even without `-RequireClean`; do not run it when Git is prohibited.

### Closing Seal

All specification documents MUST end with:

```
Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
```

## Code of Conduct

All contributors must follow our [Code of Conduct](CODE_OF_CONDUCT.md). The Axiom 0 pledge applies to all contributions.

## License of Contributions

By submitting an issue or any other content (including specification proposals, code snippets in issues, or design suggestions), you agree that your submitted content may be used by maintainers under the terms of the [Apache License 2.0](LICENSE), the same license as the project.

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
