# Generated Skill README

> Reference for per-skill `README.md` files generated from `aisp.aisop.json`.

Every `*_aisp/` skill SHOULD include a generated `README.md` for independent package bootstrap. In strict/release profiles, a missing, manual, drifted, bad-source, or unsupported-generator README is a failure under EC8.

---

## Role

Per-skill `README.md` is an AISP-native generated bootstrap artifact.

It is for:

- human review;
- generic AI/package browsing;
- registry and marketplace display;
- independent skill folders copied or published without their parent `aisp/` index.

It is not:

- the executable program;
- the skill contract;
- the resource inventory source of truth;
- a trust signal;
- a safety certificate;
- registry endorsement;
- runtime conformance evidence.

The executable source of truth remains `aisp.aisop.json`. The contract source of truth remains `user.content.aisp_contract`.

---

## Generate And Check

```bash
python -B tools/aisp_readme.py examples/aisp/yijing_aisp --write
python -B tools/aisp_readme.py examples --check-all
python -B tools/aisp_validate.py --strict-readme examples/aisp
```

`SKILL.md` sidecars are a separate generated projection:

```bash
python -B tools/aisp_skill_md.py examples/aisp/yijing_aisp --write
python -B tools/aisp_skill_md.py examples --check-all
python -B tools/aisp_validate_agent_skill_bridge.py examples/aisp --strict-readme
```

`--write` emits UTF-8 without BOM and LF line endings. `--check` normalizes UTF-8 BOM, CRLF, and CR before comparing, so Windows checkout line endings do not create false drift.

A passing `--check` means only:

```text
The committed README matches the deterministic projection from the current aisp.aisop.json.
```

It does not mean:

```text
The skill is trusted, safe, registry-approved, or runtime-conformant.
```

---

## Required Markers

Generated READMEs use these markers:

```markdown
<!-- generated_from_aisp: true -->
<!-- source: aisp.aisop.json -->
<!-- generator: tools/aisp_readme.py -->
```

Validation behavior:

| Condition | Default | `--strict-readme` |
| --- | --- | --- |
| Missing README | WARN | FAIL |
| Missing generated marker | WARN | FAIL |
| Bad source marker | WARN | FAIL |
| Unsupported generator marker | WARN | FAIL |
| Drift from generated output | WARN | FAIL |

---

## Hash Boundary

Generated READMEs include:

- `contract_sha256`;
- `resources_sha256`.

They intentionally do not embed `package_sha256`. A README is part of the distributed package, so embedding a package hash in the README creates a self-referential hash problem. Publication-time package hashes belong in external registry/provenance artifacts and must not depend on host-local paths.

Hashes prove local integrity only. They do not prove trust, safety, endorsement, registry approval, or runtime conformance. A malicious package can still generate consistent hashes for malicious content.

---

## Generic AI Boundary

A generic AI or non-AISOP agent can use a generated README only as best-effort bootstrap guidance.

Hard guarantees require a conforming AISOP runtime, including:

- `sys.assert`;
- `sys.io.confirm`;
- resource mode gates;
- tool permission gates;
- runtime trace evidence.

For untrusted standalone packages, verify external provenance, registry/signature status, or obtain explicit human approval before execution.

---

## Source Of Truth

The README must not override:

- `user.content.aisp_contract`;
- `user.content.aisop.main`;
- `user.content.functions`;
- `aisp_contract.resources`;
- `aisp_contract.non_negotiable`.

If the README and `aisp.aisop.json` disagree, regenerate the README and trust `aisp.aisop.json`.

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
