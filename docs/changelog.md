# Changelog

The authoritative changelog is maintained in the repository root: [CHANGELOG.md](https://github.com/AIXP-Labs/AISP/blob/main/CHANGELOG.md).

This documentation-site page is intentionally short. It points readers to the source of truth instead of duplicating release notes that can drift.

## V1.0.0 — 2026-11-14 revision

The fixed SKILL.md bootstrap now prohibits substitute answers when execution is unavailable, requires user-message files to stay inside the working folder, and rechecks the executor after a failed installation or upgrade. In every environment, an executor that does not satisfy the frozen version policy must not run the skill, even if an older installation still works.

The generator accepts only the current interface. For older or edited interfaces, back up the file, record the five launch strings and version policy, delete it, regenerate, restore non-default values and recheck. The LEGACY-specific M7 code is retired; read-only checks never migrate or repair. Current valid configuration remains preserved without a latest-version query unless a default-managed policy is explicitly refreshed.

The specification and standards distinguish executor cache from formal content: cache defaults to the executor's per-run working area, users may choose another location, and formal output locations are decided by the skill and user. SoulRun-specific directory and retention behavior describes only the replaceable default executor. The native Creator's content and embedded references are updated; its version remains 1.0.1, while protocol/tools remain 1.0.0. Specification §1.1, §8, §20, §20.2 and §25 also clarify artifact authority, field notation, the lossy SKILL.md description, the existing hash serialization and trace-checker limits; rules, schemas, the hash algorithm and proto definitions are unchanged. See the root CHANGELOG for regeneration instructions, known limitations and current tool content digests. The 2026-11-13 entry below is retained as history, not current migration instructions.

## V1.0.0 — 2026-11-13 revision

M7 makes same-folder generated SKILL.md mandatory: derived name/description/license and the fixed executor-only bootstrap must match; only five valid launch strings plus the frozen version policy may vary. `agent_skills_bridge` replaces the old marker; missing/legacy/drifted interfaces fail, no opt-out. Default executor is SoulRun, not vendor-bound. There is no host self-execution fallback. Preview then explicitly migrate recognized old generated projections with the existing generator and recheck core/bridge/README. Damaged or unknown content is not silently repaired or reset to defaults.

The V1.0.0 protocol marker deliberately stays unchanged, but old/new conformance is not equivalent. The native Creator example is 1.0.1 after manual M7 migration. SoulRun is a replaceable default executor, not a versioned component of this protocol release; its frozen package requirement is separate from the bundled engine version. The interface uses one version decision: matching versions run directly; proven absence/mismatch requires consent, installation and a matching recheck. Unknown probes and failed/declined installations stop.

The root CHANGELOG records migration details and the reference tool digests for this revision; this page deliberately does not mirror those hashes or maintain another cross-repository status ledger. Format checks, replay fixtures and local engineering regressions do not certify runtime enforcement, all host workflows, or publication readiness. Apply the [release evidence requirements](reference/release-evidence-matrix.md).

## Historical Release

| Version | Date | Summary |
|---------|------|---------|
| [1.0.0](https://github.com/AIXP-Labs/AISP/blob/main/CHANGELOG.md#100--2026-06-19) | 2026-06-19 | First public AISP V1.0.0 specification: skill-package structure, Axiom 0, real-object `aisp_contract`, `enforced_by` binding, conformance standards, schemas, reference tools, examples, generated per-skill README and `SKILL.md` projections, runtime trace evidence, default-but-core-optional bridge validation, and a [release evidence matrix](reference/release-evidence-matrix.md) for publication checks. |

For detailed additions, security notes, and honest boundaries, read the root [CHANGELOG.md](https://github.com/AIXP-Labs/AISP/blob/main/CHANGELOG.md).

The historical optional-interface behavior in that release is superseded by this revision's mandatory M7 interface; it is not the current authoring rule.

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
