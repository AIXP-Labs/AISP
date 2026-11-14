# Discovering Skills

This guide explains how AISP skills are discovered. Discovery is runtime-independent: any agent with bash and Python can run the discovery script, and any agent that reads JSON can read the index. You do not need a dedicated AISP runtime to find skills.

This guide uses `aisp/...` for the normative package layout. In this repository, the example package root is `examples/aisp/...`; use the repository commands shown below when trying the examples locally.

---

## The Three Discovery Paths

| Path | How | Properties |
|------|-----|------------|
| **Read the index (default)** | Read `aisp/aisp_list.json` | Fast, safe (no execution), language-agnostic; may be stale |
| **Run the script (refresh)** | `python -B aisp/aisp_list.py [--json]` | Fresh; `--json` regenerates the index; needs Python + execute permission and avoids `__pycache__/` residue |
| **Glob (fallback)** | Read each `aisp/*_aisp/aisp.aisop.json` and look at `user.content.aisp_contract` | The script's internal logic, by hand |

> **Truth model.** The skill folders are the single source of truth; `aisp_list.py` is the generator; `aisp_list.json` is the cache. The three never compete — the folder wins. If the JSON looks stale, re-run the script.

---

## Reading the Index

Inside a distributed AISP package:

```bash
cat aisp/aisp_list.json
```

Inside this repository:

```bash
python -B -m json.tool examples/aisp/aisp_list.json
```

Each row carries the lightweight metadata needed for routing: `id`, `name`, `summary`, `path`, `category`, `tags`, `when_to_use`, `risk_level`. This is **L1 metadata** in progressive disclosure — enough to decide whether a skill applies, without loading the full body.

```json
{
  "aisp_list_version": "1.0",
  "skills": [
    {
      "id": "yijing_aisp",
      "name": "Yijing Divination",
      "summary": "Cast and interpret an I Ching (Yijing) hexagram for a user's question.",
      "path": "aisp/yijing_aisp/aisp.aisop.json",
      "category": "culture",
      "tags": ["yijing", "iching", "divination", "hexagram"],
      "when_to_use": ["cast an I Ching reading", "interpret a hexagram", "yijing divination for a question"],
      "risk_level": "low"
    }
  ]
}
```

---

## Running the Script

Inside a distributed AISP package:

```bash
cd aisp
python -B aisp_list.py         # print the list
python -B aisp_list.py --json  # also (re)generate aisp_list.json
```

Inside this repository:

```bash
cd examples/aisp
python -B aisp_list.py         # print the list
python -B aisp_list.py --json  # also (re)generate aisp_list.json
```

The script rejects duplicate JSON keys and non-JSON numeric constants, checks the metadata types used by the index, and scans `*_aisp/` directories, rejects missing/malformed or out-of-root programs, reads each skill's `user.content.aisp_contract`, requires the versioned `aisp.skill.v<major>` profile, prints a human/AI-readable list, and (with `--json`) writes `aisp_list.json`. It rejects a symlinked output index instead of following it, and refuses --json writes to detected hardlinked indexes. The readonly --check mode does not modify hardlinked files. The static directory validator also checks cached routing metadata under EC2; it never runs the discovery script automatically. `_shared/` carries no `_aisp` suffix, so it is skipped automatically.

> **Running the script = executing code.** `aisp_list.py` MUST be minimal, auditable, zero-dependency, and only write `aisp_list.json` with no other side effects (conformance rule SE5). For an untrusted directory, prefer reading `aisp_list.json` and pass a trust gate before running the script (R5).

The directory validator rejects unreadable/non-file discovery scripts and escaping
script links before inspection, and rejects symlinked index files before reading.
Its AST scan checks selected patterns without running the script; it cannot prove
arbitrary Python harmless. Manual review and the trust gate are still required.

---

## Progressive Disclosure

Discovery feeds a three-level disclosure model:

```text
L1 metadata: aisp_list.json (or script output) — summary / invocation / discovery; lightweight routing.
L2 instructions: on a hit, load the full aisp/<id>/aisp.aisop.json (contract + aisop.main + functions).
L3 resources: nodes load via sys.io.read / sys.run on demand (per the resources inventory + AISP's fixed loading_mode: "node").
```

Native routing derives from `aisp_contract.invocation` (`when_to_use` / `when_not_to_use`) and `discovery` (`category` / `tags`). The required generated `SKILL.md` exposes derived discovery text to Agent Skills hosts; it complements this contract metadata rather than replacing or duplicating the business program. Discovery is not permission to execute an untrusted package.

---

## Routing on a Match

When a runtime considers a skill:

1. Does the request match `when_to_use`?
2. Does it hit `when_not_to_use`?
3. On conflict, `when_not_to_use` wins.
4. If uncertain, ask the user.

---

## Registry and Provenance

When skills are published, a registry indexes them by `discovery` + `invocation` + `risk_level` and records provenance (`source` / `commit` / `contract_sha256` / `resources_sha256`). AISP is registry-agnostic — it does not build or require a specific registry. Trust, scoring, and scanning are generated by the registry — never trusting a skill's self-declaration (M6 / SE6).

---

## Next Steps

- [The Skill Contract](../topics/skill-contract.md) — what the index is derived from.
- [Security Model](../topics/security-model.md) — why the discovery script is part of the attack surface.
- [Discovery & Registry](../topics/discovery-and-registry.md) — the conceptual deep dive.

---

> Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
