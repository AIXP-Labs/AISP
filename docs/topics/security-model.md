# Security Model

> AISP Protocol — Conceptual Guide
> Classification: Security Architecture

AISP's security model is built around one observation: a skill's resources and its discovery script are the attack surface. Unlike prose skills, AISP declares every resource, gates how each is used, confines paths, and refuses self-declared trust. This document covers the attack surface, the security rules, the Axiom 0 invariant, and the ST1–ST6 threat taxonomy.

---

## Introduction

A native AISP skill bundles executable and readable resources (scripts, templates, data, sometimes remote URLs) plus a discovery script (`aisp_list.py`). These are exactly where malicious payloads can hide. AISP's defenses are structural: the resource inventory, `mode` gating, path confinement, least authority, no self-declared trust, and the forced-blocking `sys.io.confirm`.

---

## Platform Policy Precedence

> An `aisp_contract` is authoritative only within the AISP execution context. It does NOT override platform-level system, developer, safety, legal, or policy instructions. In the standard message hierarchy (system / developer > user > assistant) the contract sits in the user message and is skill-layer authority, not platform-top authority. The strong `instruction` (`STRICTLY OBEY aisp_contract …`) binds the model to the skill's own rules; it never licenses bypassing platform or safety policy.

The contract is deliberately placed in the user message, which makes it structurally subordinate to the host platform's higher-precedence system/developer layer. Its authority is scoped to *how the skill runs* — which `non_negotiable` red lines hold, which `aisop.main` nodes are mandatory — not to overriding the platform. The strong `instruction` raises adherence to the skill's own rules; it is not a jailbreak token, and a runtime MUST NOT interpret it as permission to ignore platform, safety, legal, or policy instructions.

---

## Read-Only During Execution (SE8)

> An AISP runtime SHOULD treat skill packages (files and resources) as read-only during normal execution. Modifications happen only through a deliberate evolution/edit step.

Normal invocation never rewrites the skill. Reading `data/` and running declared `execute_only` scripts are permitted; writing back into the skill folder is not. Mutation of `aisp.aisop.json` or any declared resource is reserved for a deliberate evolution/edit step (with a changelog entry and a security scan — see [Lifecycle](lifecycle.md)). This keeps the executed artifact identical to the audited/published one and protects the integrity that registry provenance (`contract_sha256` / `resources_sha256`) attests to.

---

## Tool Enforcement: Hard vs Advisory (R6)

> A runtime SHOULD declare whether its tool enforcement is hard (permissions actually enforced) or advisory. If advisory, `enforced_by: tools` MUST NOT be treated as a hard guarantee.

A `non_negotiable` red line bound to `enforced_by: tools` (for example "never place trades", backed by the absence of a trading tool) is only a *hard* guarantee when the runtime truly enforces tool permissions. A runtime whose tool layer is advisory — it merely advertises a tool list the model is asked to respect — provides a soft constraint, equivalent to policy-as-prompt. Such a runtime SHOULD declare its enforcement as advisory, and consumers MUST NOT count `enforced_by: tools` as policy-as-code on it. A runtime's top-level `tool_enforcement: "hard"` declaration is an attestation, not independent proof; strict release gates require event-backed trace evidence or provenance-bearing tool capability evidence. Hard guarantees that do not depend on this distinction use `sys.*` instead (`<node>.stepN:sys.assert`, `sys.io.confirm`).

---

## The Attack Surface

| Surface | Risk |
|---------|------|
| Resources (scripts / templates / data) | Injected payloads, over-broad execution, undeclared files |
| Remote URLs | Indirect prompt injection via fetched content |
| `aisp_list.py` | Running it executes code (discovery poisoning) |
| Trust claims | A skill spoofing `verified` / `safe` to lower a consumer's guard |

---

## Security Rules

| Rule | Requirement |
|------|-------------|
| **SE1 — Path Confinement** | Each `resources[].path` is relative and confined to the skill folder or `_shared/`. No `../` escape, no absolute paths (reinforces core M5). |
| **SE2 — Remote Resource Gate** | Remote URLs are disabled by default; access requires a `sys.io.confirm` gate. |
| **SE3 — `mode` Gating** | `execute_only` scripts are not injected in full into the model; `read_only` resources are not executed; `read_and_execute` permits both. `mode` is a closed enum. |
| **SE4 — Least Authority** | `kind:script` resources declare `requires_tools` (minimal); dangerous commands trigger `sys.io.confirm`. |
| **SE5 — Discovery Script Safety** | `aisp_list.py` is minimal, auditable, zero-dependency, and only writes `aisp_list.json`. Prefer reading the index; trust gate before execution. |
| **SE6 — Trust Is Not Self-Declared** | No `trusted` / `verified` / `safe` self-assertion; trust is judged by registry / scanner / user (reinforces core M6). |
| **SE7 — Axiom 0 Confirm Invariant** | `sys.io.confirm` is forced-blocking and MUST NOT be bypassed, regardless of `invocation.mode` or `risk_level`. |
| **SE8 — Read-Only During Execution** | Skill files and resources are read-only during normal execution; modifications happen only through a deliberate evolution/edit step. |

> **`aisp_list.py` guarantees (SE5, explicit).** `aisp_list.py` MUST be zero-dependency (standard library only) and human-auditable. It MUST NOT: access the network; import third-party packages; execute skill scripts; modify any file except `aisp_list.json`; read files outside the `aisp/` directory (except declared `_shared` metadata).

---

## The Axiom 0 Confirm Invariant (SE7)

> `sys.io.confirm` cannot be bypassed.

Every skill inherits Axiom 0 from the AISOP execution layer (and ultimately HSAW). A runtime MUST NOT auto-approve a `sys.io.confirm` step, and a node MUST NOT downgrade it to a natural-language "are you sure?" prompt. This invariant holds at every `risk_level` and in every `invocation.mode` — it is the concrete, runtime locus of Human Sovereignty and Wellbeing. See [Axiom 0](axiom-0.md).

---

## Threat Taxonomy (ST1–ST6)

Each threat maps to the security rule(s) that mitigate it.

### ST1: Skill Discovery Poisoning

A malicious `aisp_list.py` (or a tampered `aisp_list.json`) executes code or misrepresents skills during discovery.

**Mitigation:** SE5 — minimal, auditable, zero-dependency script that only writes `aisp_list.json`; prefer reading the index; trust gate before execution.

### ST2: Undeclared Resource

A file exists in the skill folder but is not declared in `aisp_contract.resources` — an unknown surface a node could read or run.

**Mitigation:** core M5 — `resources` is the single source of truth; a validator SHOULD warn on undeclared files.

### ST3: Indirect Injection via Remote Content

A resource references remote content carrying an injected payload.

**Mitigation:** SE2 — remote URLs disabled by default; user confirmation gate.

### ST4: Path Traversal / Resource Escape

A `resources[].path` uses `../` or an absolute path to escape the skill folder.

**Mitigation:** SE1 / core M5 — path confinement to the skill folder or `_shared/`.

### ST5: Excessive Authority

A script requests or uses more tools than it needs; dangerous commands run without confirmation.

**Mitigation:** SE4 — `requires_tools` least authority; `sys.io.confirm` on dangerous operations.

### ST6: Trust Spoofing

A skill claims to be `verified` / `trusted` / `safe` to lower a consumer's guard.

**Mitigation:** SE6 / core M6 — trust is never self-declared; provenance recorded by the registry.

---

## Registry Provenance

Trust is established **outside** the skill. A registry records provenance over the skill folder — `source` / `commit` / `contract_sha256` / `resources_sha256` — and generates trust / scoring / scanning results (AISP is registry-agnostic). A skill states only facts (its declared `risk_level`, its declared resources); a consumer, registry, or scanner decides whether to trust it. See [Discovery & Registry](discovery-and-registry.md).

---

Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
