# Changelog

The authoritative changelog is maintained in the repository root: [CHANGELOG.md](https://github.com/AIXP-Labs/AISP/blob/main/CHANGELOG.md).

This documentation-site page is intentionally short. It points readers to the source of truth instead of duplicating release notes that can drift.

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
