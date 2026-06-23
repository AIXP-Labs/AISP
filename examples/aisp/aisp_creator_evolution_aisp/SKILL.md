---
name: "aisp-creator-evolution"
description: "AISP-backed bridge for Create new conformant AISP skills, evolve existing ones, and adapt existing Agent Skills into native AISP packages from requirements, SOPs, prompts, or evidence. Use when create a new AISP skill; convert a requirement, workflow, SOP, or prompt into an AISP skill. Do not use when research only, with no skill produced; generating a non-AISP artifact (e.g. a plain SKILL.md with no AISOP body)."
license: "Apache-2.0"
metadata:
  generated_from_aisp: "true"
  aisp_program: "aisp.aisop.json"
  protocol: "AISP V1.0.0"
  bridge_mode: "native_sidecar"
---

# AISP Creator & Evolution (AISP-backed Agent Skill)

<!-- generated_from_aisp: true -->
<!-- source: aisp.aisop.json -->
<!-- generator: tools/aisp_skill_md.py -->

This `SKILL.md` is a thin Agent Skills discovery bridge, not the source of truth. The executable source of truth is the same-folder `aisp.aisop.json` AISP program.

Deleting this file does not change the native AISP skill. A conforming AISP/AISOP runtime should load `aisp.aisop.json`, read `user.content.aisp_contract`, and run `user.content.aisop.main` exactly as declared.

## How to use

1. Load `aisp.aisop.json` from this folder.
2. Read `user.content.aisp_contract` before following any workflow.
3. Follow `user.content.instruction`: `STRICTLY OBEY aisp_contract; its non_negotiable rules are inviolable; then RUN aisop.main`.
4. Load declared resources only when the AISP graph reaches the node that needs them.
5. Enforce every non-negotiable rule through the mechanism named by `enforced_by`.

## Declared resources

- `schemas/skill-design.schema.json` (schema, read_only)
- `schemas/research-request.schema.json` (schema, read_only)
- `schemas/research-result.schema.json` (schema, read_only)
- `schemas/evolution-evidence.schema.json` (schema, read_only)
- `references/binding-rules.md` (reference, read_only)
- `README_CN.md` (documentation, read_only)
- `.gitignore` (packaging, read_only)
- `aisop_specification/README.md` (spec_index, read_only)
- `aisop_specification/MANIFEST.sha256.json` (manifest, read_only)
- `aisop_specification/aisop-spec.md` (spec, read_only)
- `aisop_specification/aisop-spec_CN.md` (spec, read_only)
- `aisp_specification/README.md` (spec_index, read_only)
- `aisp_specification/MANIFEST.sha256.json` (manifest, read_only)
- `aisp_specification/AISP_Protocol.md` (spec, read_only)
- `aisp_specification/AISP_Protocol_cn.md` (spec, read_only)
- `aisp_specification/aisp.proto` (spec, read_only)
- `aisp_specification/standards/AISP_Standard.core.aisop.json` (standard, read_only)
- `aisp_specification/standards/AISP_Standard.ecosystem.aisop.json` (standard, read_only)
- `aisp_specification/standards/AISP_Standard.security.aisop.json` (standard, read_only)
- `aisp_protocol_schemas/README.md` (schema_index, read_only)
- `aisp_protocol_schemas/MANIFEST.sha256.json` (manifest, read_only)
- `aisp_protocol_schemas/aisp-contract-v1.schema.json` (schema, read_only)
- `aisp_protocol_schemas/runtime-trace-v1.schema.json` (schema, read_only)
- `aisp_protocol_schemas/tool-capabilities-v1.schema.json` (schema, read_only)
- `aisp_protocol_schemas/registry-manifest-v1.schema.json` (schema, read_only)
- `aisp_reference_tools/README.md` (tool_index, read_only)
- `aisp_reference_tools/MANIFEST.sha256.json` (manifest, read_only)
- `aisp_reference_tools/aisp_validate.py` (script, execute_only)
- `aisp_reference_tools/aisp_hash.py` (script, execute_only)
- `aisp_reference_tools/aisp_readme.py` (script, execute_only)
- `aisp_reference_tools/aisp_skill_md.py` (script, execute_only)
- `aisp_reference_tools/aisp_check_runtime_trace.py` (script, execute_only)
- `aisp_reference_tools/aisp_validate_agent_skill_bridge.py` (script, execute_only)
- `aisp_reference_tools/check_doc_sync.py` (reference, read_only)
- `aisp_reference_tools/check_markdown_links.py` (reference, read_only)
- `aisp_reference_tools/__init__.py` (reference, read_only)
- `templates/skill-template.md` (template, read_only)
- `scripts/validate_aisp_skill.py` (script, execute_only)
- `scripts/simulate_aisp_flow.py` (script, execute_only)
- `scripts/check_generated_candidate.py` (script, execute_only)
- `evals/evals.json` (eval, read_only)
- `evals/script-behavior.json` (eval, read_only)
- `evals/runtime-traces/hard-pass.json` (eval, read_only)
- `evals/runtime-traces/hard-attested-no-event.json` (eval, read_only)
- `evals/runtime-traces/bad-shape.json` (eval, read_only)

## Non-negotiable boundaries

- Follow RUN aisop.main; route by intent and never skip research, validation, or human review. (`aisop.main`)
- Required research MUST run via the research sub-graph, not ad-hoc browsing. (`run_research.step2:sys.assert`)
- Design MUST NOT start until mandatory research has completed. (`assert_research_complete.step1:sys.assert`)
- A delivered skill MUST be a conformant AISP skill (passes M1-M6 and safety checks); reject otherwise. (`validate_candidate.step5:sys.assert`)
- MUST obtain explicit human approval before delivering a candidate. (`review_candidate.step2:sys.io.confirm`)
- Never write outside the resolved candidate root; never publish or perform destructive actions without confirmation. (`tools`)

## Runtime boundary

Agent Skills platforms can use this bridge to discover and inspect the package. Hard guarantees such as `sys.assert`, `sys.io.confirm`, tool gating, dispatch behavior, and path confinement require a conforming AISP/AISOP runtime. A generic non-AISOP agent can only follow the contract on a best-effort basis.

Passing `SKILL.md` generation or bridge validation proves only projection consistency and bridge shape. It does not prove external trust, safety, registry approval, or hard execution on a non-AISOP platform.

Align Axiom 0: Human Sovereignty and Wellbeing. AISP - AI Skill Protocol V1.0.0. www.aisp.dev
