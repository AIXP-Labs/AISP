<!-- generated_from_aisp: true -->
<!-- source: aisp.aisop.json -->
<!-- generator: tools/aisp_readme.py -->

# AISP Creator & Evolution

This README is a deterministic projection of `aisp.aisop.json`. The contract remains the source of truth.

## Identity

| Field | Value |
| --- | --- |
| Skill ID | `aisp_creator_evolution_aisp` |
| Version | `1.0.0` |
| Protocol | `AISP V1.0.0` |
| License | `Apache-2.0` |
| Risk Level | `medium` |
| Category | meta-tooling |
| Tags | skill-creation, skill-evolution, aisp-generator, meta-skill |

## Purpose

Create new conformant AISP skills, evolve existing ones, and adapt existing Agent Skills into native AISP packages from requirements, SOPs, prompts, or evidence.

## When To Use

- create a new AISP skill
- convert a requirement, workflow, SOP, or prompt into an AISP skill
- evolve an existing AISP skill from research, execution evidence, tests, or human feedback

## When Not To Use

- research only, with no skill produced
- generating a non-AISP artifact (e.g. a plain SKILL.md with no AISOP body)
- no user request provided

## How To Run

With an AISOP runtime:

1. Load `aisp.aisop.json`.
2. Read `user.content.aisp_contract` before execution.
3. Run `user.content.aisop.main` exactly as declared.
4. Enforce every `non_negotiable` rule and every referenced `sys.*` mechanism.
5. Treat `sys.io.confirm` and other human-confirmation gates as blocking controls.

With a generic AI or non-AISOP agent:

- Treat this README as bootstrap guidance only.
- Verify external provenance or obtain explicit human approval before executing an untrusted package.
- Load the contract from `aisp.aisop.json`; do not treat this README as authoritative.
- Follow `RUN aisop.main` and the non-negotiable rules on a best-effort basis.
- Hard guarantees such as `sys.assert`, tool gating, and `sys.io.confirm` exist only in a conforming AISOP runtime.

## Non-Negotiable Rules

| Rule | Enforced By |
| --- | --- |
| Follow RUN aisop.main; route by intent and never skip research, validation, or human review. | `aisop.main` |
| Required research MUST run via the research sub-graph, not ad-hoc browsing. | `run_research.step2:sys.assert` |
| Design MUST NOT start until mandatory research has completed. | `assert_research_complete.step1:sys.assert` |
| A delivered skill MUST be a conformant AISP skill (passes M1-M6 and safety checks); reject otherwise. | `validate_candidate.step5:sys.assert` |
| MUST obtain explicit human approval before delivering a candidate. | `review_candidate.step2:sys.io.confirm` |
| Never write outside the resolved candidate root; never publish or perform destructive actions without confirmation. | `tools` |

## Resources

| ID | Path | Kind | Mode | Scope | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| skill_design_schema | schemas/skill-design.schema.json | schema | read_only | skill |  |
| research_request_schema | schemas/research-request.schema.json | schema | read_only | skill |  |
| research_result_schema | schemas/research-result.schema.json | schema | read_only | skill |  |
| evolution_evidence_schema | schemas/evolution-evidence.schema.json | schema | read_only | skill |  |
| binding_rules | references/binding-rules.md | reference | read_only | skill |  |
| readme_cn | README_CN.md | documentation | read_only | skill |  |
| package_ignore | .gitignore | packaging | read_only | skill |  |
| aisop_specification_index | aisop_specification/README.md | spec_index | read_only | skill |  |
| aisop_specification_manifest | aisop_specification/MANIFEST.sha256.json | manifest | read_only | skill |  |
| aisop_specification_en | aisop_specification/aisop-spec.md | spec | read_only | skill |  |
| aisop_specification_cn | aisop_specification/aisop-spec_CN.md | spec | read_only | skill |  |
| aisp_specification_index | aisp_specification/README.md | spec_index | read_only | skill |  |
| aisp_specification_manifest | aisp_specification/MANIFEST.sha256.json | manifest | read_only | skill |  |
| aisp_specification_en | aisp_specification/AISP_Protocol.md | spec | read_only | skill |  |
| aisp_specification_cn | aisp_specification/AISP_Protocol_cn.md | spec | read_only | skill |  |
| aisp_proto | aisp_specification/aisp.proto | spec | read_only | skill |  |
| aisp_standard_core | aisp_specification/standards/AISP_Standard.core.aisop.json | standard | read_only | skill |  |
| aisp_standard_ecosystem | aisp_specification/standards/AISP_Standard.ecosystem.aisop.json | standard | read_only | skill |  |
| aisp_standard_security | aisp_specification/standards/AISP_Standard.security.aisop.json | standard | read_only | skill |  |
| aisp_protocol_schemas_index | aisp_protocol_schemas/README.md | schema_index | read_only | skill |  |
| aisp_protocol_schemas_manifest | aisp_protocol_schemas/MANIFEST.sha256.json | manifest | read_only | skill |  |
| aisp_contract_schema | aisp_protocol_schemas/aisp-contract-v1.schema.json | schema | read_only | skill |  |
| runtime_trace_schema | aisp_protocol_schemas/runtime-trace-v1.schema.json | schema | read_only | skill |  |
| tool_capabilities_schema | aisp_protocol_schemas/tool-capabilities-v1.schema.json | schema | read_only | skill |  |
| registry_manifest_schema | aisp_protocol_schemas/registry-manifest-v1.schema.json | schema | read_only | skill |  |
| aisp_reference_tools_index | aisp_reference_tools/README.md | tool_index | read_only | skill |  |
| aisp_reference_tools_manifest | aisp_reference_tools/MANIFEST.sha256.json | manifest | read_only | skill |  |
| aisp_reference_validator | aisp_reference_tools/aisp_validate.py | script | execute_only | skill |  |
| aisp_reference_hash | aisp_reference_tools/aisp_hash.py | script | execute_only | skill |  |
| aisp_reference_readme | aisp_reference_tools/aisp_readme.py | script | execute_only | skill |  |
| aisp_reference_skill_md | aisp_reference_tools/aisp_skill_md.py | script | execute_only | skill |  |
| aisp_reference_runtime_trace | aisp_reference_tools/aisp_check_runtime_trace.py | script | execute_only | skill |  |
| aisp_reference_agent_skill_bridge | aisp_reference_tools/aisp_validate_agent_skill_bridge.py | script | execute_only | skill |  |
| aisp_reference_doc_sync | aisp_reference_tools/check_doc_sync.py | reference | read_only | skill |  |
| aisp_reference_markdown_links | aisp_reference_tools/check_markdown_links.py | reference | read_only | skill |  |
| aisp_reference_tools_package | aisp_reference_tools/__init__.py | reference | read_only | skill |  |
| skill_template | templates/skill-template.md | template | read_only | skill |  |
| validator | scripts/validate_aisp_skill.py | script | execute_only | skill |  |
| simulate_aisp_flow | scripts/simulate_aisp_flow.py | script | execute_only | skill |  |
| generated_candidate_checker | scripts/check_generated_candidate.py | script | execute_only | skill |  |
| evals | evals/evals.json | eval | read_only | skill |  |
| script_behavior_evidence | evals/script-behavior.json | eval | read_only | skill |  |
| runtime_trace_hard_pass_fixture | evals/runtime-traces/hard-pass.json | eval | read_only | skill |  |
| runtime_trace_attested_warning_fixture | evals/runtime-traces/hard-attested-no-event.json | eval | read_only | skill |  |
| runtime_trace_bad_shape_fixture | evals/runtime-traces/bad-shape.json | eval | read_only | skill |  |

## Integrity

| Hash | Value | Meaning |
| --- | --- | --- |
| `contract_sha256` | `6c56f0b2a8f64438736867a9011eb4722600a7abf01fc29f636d48dfe8e06f8f` | Recomputable hash of `user.content.aisp_contract` |
| `resources_sha256` | `cedfb34fe097c794564763dfc173f7518f2cd0a2885585acc1b7466be13a520f` | Recomputable hash of declared resource records |

`package_sha256` is intentionally not embedded here because a README is part of the distributed package and package-level hashes belong in external registry/provenance artifacts. Recompute it with `tools/aisp_hash.py` at publication time.

These hashes show local integrity only. They do not prove trust, safety, or registry approval.

## Source Of Truth

`aisp.aisop.json` is authoritative. A successful README check proves only that this file matches the contract-derived projection; it does not prove that the skill is safe or trustworthy.
