# AISP Protocol Specification

AISP defines the package. AISOP executes it.

This page is the documentation-site entry point for the AISP V1.0.0 specification. The normative Markdown files live in [`specification/`](../specification/); this page points to the authoritative artifacts and explains how to read them.

## Start Here

| Reader | Recommended path |
|--------|------------------|
| New to AISP | Start with the English specification overview, then read §§0-4 |
| Skill author | Read skill structure, contract fields, resources, interoperability, and checklist sections |
| Validator implementer | Read the conformance standards and validator coverage reference |
| Runtime implementer | Read execution/disclosure sections and R-series runtime rules |
| Registry or distribution implementer | Read lifecycle, registry/runtime artifacts, generated README, and provenance sections |

---

## Normative Specification

- **[AISP Skill-Package Specification (English)](../specification/AISP_Protocol.md)** --- The authoritative normative specification
- **[AISP Skill-Package Specification (Chinese)](../specification/AISP_Protocol_cn.md)** --- Chinese translation (non-normative)

---

## Conformance Standards

The conformance rules are distributed across three `AISP_Standard.*` files. Rule codes within a series (e.g. `M`, `R`, `SE`, `EC`) are declared in the file relevant to their domain. The authoritative semantics come from the JSON files themselves, not this table.

| Standard File | Scope | Rule Codes Declared |
|---------------|-------|---------------------|
| [AISP_Standard.core](../specification/standards/AISP_Standard.core.aisop.json) | Core conformance — the baseline every skill must pass | M1-M6 (skill), R1-R7 (runtime) |
| [AISP_Standard.security](../specification/standards/AISP_Standard.security.aisop.json) | Security extension: resource attack surface, mode gating, discovery-script safety, threat taxonomy | SE1-SE8, ST1-ST6 |
| [AISP_Standard.ecosystem](../specification/standards/AISP_Standard.ecosystem.aisop.json) | Ecosystem / lifecycle: the `aisp/` directory contract, index integrity, `_shared/`, the AISP-native tool-agnostic lifecycle, default-but-core-optional `SKILL.md` sidecar bridge, generated skill README | EC1-EC8 |

Conformance series overview:

| Series | Count | Domain |
|--------|-------|--------|
| **M** (Skill conformance) | 6 | A conformant skill is first a legal AISOP program, then M1-M6 |
| **R** (Runtime conformance) | 7 | How a runtime must read, enforce, honor execute_mode, and not hide the contract |
| **SE** (Security) | 8 | Resource attack surface, mode gating, discovery-script safety |
| **ST** (Skill threats) | 6 | Threat taxonomy mapped to SE mitigations |
| **EC** (Ecosystem) | 8 | `aisp/` directory, index integrity, AISP-native lifecycle, default-but-core-optional `SKILL.md` sidecar bridge, generated skill README |

These files together define the AISP conformance framework. A skill is checked against the M rules; a runtime against the R rules; security and ecosystem extensions add SE / EC checks. AISP's generation, evolution, and distribution are AISP-native and tool-agnostic — handled by external tooling of the author's choice; AISP defines the package and the conformance, not the toolchain.

---

## Proto Definition

The [aisp.proto](../specification/aisp.proto) file provides the proto3 definition of AISP data structures (skill, skill contract, discovery, conformance) and service operations. It can be used to generate typed client and server code in any language supported by Protocol Buffers.

Per `AISP_Protocol.md` §1.1 (Normative Artifacts and Their Roles), `aisp.proto` is **authoritative for data-object schemas and service contracts**; `AISP_Protocol.md` itself is authoritative for **rules and skill structure**. When the two appear to conflict, consult §1.1 for the tie-breaker order.

---

> Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
