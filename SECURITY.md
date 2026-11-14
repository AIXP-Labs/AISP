# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in the AISP protocol specification or reference implementations, please report it responsibly through GitHub's private security advisory channel:

**[Report a vulnerability on GitHub](https://github.com/AIXP-Labs/AISP/security/advisories/new)**

This keeps the report private until a fix is released and coordinated disclosure is complete.

Please include:

- Description of the vulnerability
- Steps to reproduce (if applicable)
- Potential impact assessment
- Suggested fix (if any)

## A Note on the Skill Attack Surface

AISP skills carry executable resources (scripts, templates, data) and a discovery script (`aisp_list.py`). The most relevant classes of issue are:

- **Resource path escape** — a `resources[].path` that traverses outside the skill folder or `_shared/` (`../`).
- **Undeclared resources** — files in a skill folder not listed in `aisp_contract.resources` (unknown surface).
- **Phantom enforcement** — a `non_negotiable.enforced_by` that points to a node/step/mechanism that does not exist, giving a false sense of a hard guarantee.
- **Discovery script side effects** — `aisp_list.py` doing anything beyond scanning folders and (with `--json`) writing `aisp_list.json`.
- **Self-declared trust** — a skill claiming to be `verified` / `trusted` / `safe`.
- **Remote resources** — resources referencing remote URLs without a user confirmation gate.
- **Executor bootstrap configuration** — malicious version, installation or execution commands in `SKILL.md`; a generated marker or valid M7 format does not authenticate those commands.
- **Misleading evidence** — fabricated traces, provenance fields or version reports that pass format checks but do not establish actual enforcement or external trust.

## Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 7 days
- **Resolution Plan**: Within 14 days

## Scope

This security policy covers:

- The AISP protocol specification (`specification/AISP_Protocol.md`)
- The AISP conformance standards (`specification/standards/`)
- The AISP proto definition (`specification/aisp.proto`)
- The reference discovery script (`examples/aisp/aisp_list.py`)
- Reference validators, hash tools and README/SKILL.md generators (`tools/`)
- Official documentation and examples

Out of scope:

- Third-party AISP implementations and runtimes (report to those projects directly)
- The AISOP execution language itself (report to the [AISOP-Protocol](https://github.com/AIXP-Labs/AISOP) repository)
- AIAP governance rules — a separate sibling protocol in the AIXP family (report to the [AIAP-Protocol](https://github.com/AIXP-Labs/AIAP) repository)
- SoulRun or SoulBot runtime issues (report to the [SoulRun](https://github.com/AIXP-Labs/SoulRun) or [SoulBot](https://github.com/AIXP-Labs/SoulBot) repository)
- Skills authored by third parties (report to their respective authors / registries)

## Repository Hygiene

Runtime caches and evolution residue can contain prompts, responses and local
paths. The ignore policy covers `.soulrun_cache/`, `.execution_cache/`, local
evolution snapshots, logs and common credential files. The release residue check
and Creator package checks reject runtime caches rather than treating an ignored
directory as safe to distribute. Public templates and regression evidence remain
reviewable; never put real credentials in `.env.example`.

[Ignore rules affect untracked files](https://git-scm.com/docs/gitignore), not
access permissions, already tracked content, history or archive payloads. Review
the actual files and built wheel/sdist before sharing. The local path/key scan
covers selected literal markers in files smaller than 5 MB outside `.git`; it is
not a complete personal-data/secret detector. If credentials were exposed,
revoke/rotate them and handle history/log cleanup through separately authorized
maintenance, rather than assuming an ignore entry repairs the disclosure.

Reference tools use only the Python standard library. `jsonschema` is a test
extra; pytest and MkDocs Material are optional tooling, not runtime requirements.
Setuptools is build-only, with a floor of 84.1.0 excluding older affected releases
described by the upstream [PackageIndex advisory](https://github.com/pypa/setuptools/security/advisories/GHSA-5rjg-fvgr-3xxf)
and [legacy wheel-installation advisory](https://github.com/pypa/setuptools/security/advisories/GHSA-xmj3-9gf7-h52w).
This does not establish that every dependency or code path is vulnerability-free.
Upstream also reports [Unicode-sensitive sdist exclusion](https://github.com/pypa/setuptools/security/advisories/GHSA-h35f-9h28-mq5c);
do not treat filename exclusions as proof that an archive is safe.

`include-package-data = false` limits wheel data, not sdist selection. A stale
`*.egg-info/SOURCES.txt` can retain private files; `MANIFEST.in` explicitly
excludes known credential/key/log/cache patterns even in that case, preserving
reviewed `.env.example` templates outside private cache directories. The exclusions
also cover selected test/build and `.venv` residue at root and nested paths.
Public files with merely similar names are not blanket-excluded. This is not
a complete content classifier. Use a clean source staging directory and
inspect the actual archives; see the upstream [distribution/cache guidance](https://setuptools.pypa.io/en/latest/userguide/miscellaneous.html).

CI actions are pinned to verified release commits, with read-only contents
permission and checkout credential persistence disabled, following
[GitHub's secure-use guidance](https://docs.github.com/en/actions/reference/security/secure-use).
These are local configuration safeguards, not proof of a completed hosted run.

## Coordinated Disclosure

We follow a coordinated disclosure process. Please do not publicly disclose vulnerabilities until a fix has been released and announced.

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
