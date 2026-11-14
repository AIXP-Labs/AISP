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

The required same-folder `SKILL.md` compatibility interface is generated separately (M7). Its fixed bootstrap delegates to a conforming executor, SoulRun by default; the business source remains `aisp.aisop.json`:

```bash
python -B tools/aisp_skill_md.py examples/aisp/yijing_aisp --write
python -B tools/aisp_skill_md.py examples --check-all
python -B tools/aisp_validate_agent_skill_bridge.py examples/aisp --strict-readme
```

`--write` emits UTF-8 without BOM and LF line endings. `--check` normalizes UTF-8 BOM, CRLF, and CR before comparing, so Windows checkout line endings do not create false drift.

Both generators share strict business-JSON loading and reject symbolic-link
output files. Writes replace each file atomically, so existing hardlinks are
not truncated in place. Batch writes prepare every projection before changing
any file; a later I/O failure reports earlier completed writes. The batch is
not one transaction, and this is not isolation against hostile concurrent
directory replacement.

A passing `--check` means only:

```text
The local README matches the deterministic projection from the current aisp.aisop.json.
```

It does not mean:

```text
The skill is trusted, safe, registry-approved, or runtime-conformant.
```

The check does not inspect commit history or prove that the local file has been committed or published.

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
- `program_sha256` (the complete two-message program);
- `resources_sha256`.

They intentionally do not embed `package_sha256`: publication-time manifests are external artifacts. The current manifest covers the program and declared resources, not every archive byte. Declaring the generated README as its own hashed resource would create a self-reference; keep generated projections outside their own hash inputs. Hashes must not depend on host-local paths.

Hashes prove local integrity only. They do not prove trust, safety, endorsement, registry approval, or runtime conformance. A malicious package can still generate consistent hashes for malicious content.

Manifest 1.1 adds full-program binding; legacy 1.0 does not bind business-function-only edits. Neither version automatically binds all generated SKILL.md bytes or its five launch strings plus the frozen version policy. Review/pin the actual interface separately; do not treat a matching package hash as approval of its commands.

---

## Generic AI Boundary

A generic AI or non-AISOP host can browse a generated README, but MUST hand execution through the required interface to a conforming AISP/AISOP executor. Without an executor, stop; do not execute or continue the skill yourself. Executor-mediated reads and user-requested code review are allowed. The installation confirmation before an executor exists depends on the host's controls.

Hard guarantees require a conforming AISP/AISOP executor, including:

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

If the README and `aisp.aisop.json` disagree, review the intended business program and regenerate the projection. The program is the content source of truth, not proof that the package is trustworthy; external provenance or a human trust decision is still required.

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
