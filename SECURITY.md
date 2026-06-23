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
- Official documentation and examples

Out of scope:

- Third-party AISP implementations and runtimes (report to those projects directly)
- The AISOP execution language itself (report to the [AISOP-Protocol](https://github.com/AIXP-Labs/AISOP) repository)
- AIAP governance rules — a separate sibling protocol in the AIXP family (report to the [AIAP-Protocol](https://github.com/AIXP-Labs/AIAP) repository)
- SoulBot runtime issues (report to the [SoulBot](https://github.com/AIXP-Labs/SoulBot) repository)
- Skills authored by third parties (report to their respective authors / registries)

## Coordinated Disclosure

We follow a coordinated disclosure process. Please do not publicly disclose vulnerabilities until a fix has been released and announced.

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
