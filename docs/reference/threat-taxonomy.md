# Threat Taxonomy Reference

> Complete reference for the six threat categories (ST1–ST6) in the AISP skill threat model.
> Every AISP skill MUST address the applicable threats; mitigations are enforced by the SE / M conformance rules.

In AISP the attack surface is concentrated in two places: **resources** (scripts, templates, data, remote URLs that a node may read or run) and the **discovery script** (`aisp_list.py`, where running it equals executing code). The threat model targets both. A skill never self-declares trust; trust and provenance are judged by the runtime, registry, user, and scanner.

---

## Resource & Discovery-Script Attack Surface

| Surface | Risk | Primary guard |
|---------|------|---------------|
| `resources[].path` | Traversal / escape outside the skill folder | Path confinement (SE1 / M5) |
| Remote resource URLs | Indirect prompt injection via fetched content | Remote gate + confirm (SE2) |
| `mode` declarations | Executing read-only data; injecting executable scripts into the model | mode gating (SE3) |
| Scripts | Excessive authority; unconfirmed dangerous commands | Least authority + confirm (SE4) |
| `aisp_list.py` | Arbitrary code execution during discovery | Discovery-script safety (SE5) |
| Trust claims | Spoofed verified/trusted status | Trust not self-declared (SE6 / M6) |

**mode-gating decision**: `read_only` → may be read into context, never executed. `execute_only` → may be executed, never injected in full into the model. `read_and_execute` → both permitted. **path-confinement decision**: a path is rejected if it is absolute, contains `..`, or resolves outside the skill folder (`scope:skill`) or `_shared/` (`scope:shared`).

---

## Threat Overview

| ID | Name | Vector | Severity | Primary Mitigation |
|----|------|--------|----------|--------------------|
| **ST1** | Skill Discovery Poisoning | Malicious / tampered discovery script or index | High | SE5 — discovery-script safety |
| **ST2** | Undeclared Resource | Folder file not declared in `resources` | Medium | M5 — validator warns on undeclared files |
| **ST3** | Indirect Injection via Remote Content | Remote resource carries injected payload | High | SE2 — remote gate + confirm |
| **ST4** | Path Traversal / Resource Escape | `path` uses `../` or absolute path | High | SE1 / M5 — path confinement |
| **ST5** | Excessive Authority | Script over-requests tools; unconfirmed dangerous commands | Medium | SE4 — least authority + `sys.io.confirm` |
| **ST6** | Trust Spoofing | Skill claims verified/trusted/safe | Medium | SE6 / M6 — trust not self-declared |

---

## ST1: Skill Discovery Poisoning

| Aspect | Detail |
|--------|--------|
| Description | A malicious `aisp_list.py` (or a tampered `aisp_list.json`) executes code or misrepresents skills during discovery. |
| Attack Surface | `aisp/aisp_list.py` (running it = executing code), `aisp/aisp_list.json`. |
| Detection | Static-analyze `aisp_list.py`: no imports beyond stdlib, no network calls, no subprocess, no deletion; the only write target is `aisp_list.json`. |
| Mitigation | SE5: minimal, auditable, zero-dependency script; prefer reading the index (no execution); trust gate before running the script. |
| Conformance Rules | SE5 (FAIL), R5 (WARNING) |

---

## ST2: Undeclared Resource

| Aspect | Detail |
|--------|--------|
| Description | A file exists in the skill folder but is not declared in `aisp_contract.resources` — an unknown surface a node could read or run. |
| Attack Surface | Any file in the skill folder not listed in `resources`. |
| Detection | Diff the folder contents against the `resources` inventory; warn on any undeclared file. |
| Mitigation | `resources` is the single source of truth for "what is a resource"; a validator SHOULD warn on undeclared files (M5). |
| Conformance Rules | M5 (FAIL on escape; WARNING on undeclared) |

---

## ST3: Indirect Injection via Remote Content

| Aspect | Detail |
|--------|--------|
| Description | A resource references remote content (a URL) that carries an injected instruction payload. |
| Attack Surface | Any `resources[].path` that is a remote URL. |
| Detection | Flag resource paths with a remote scheme (http/https/etc.) not gated by a confirmation step. |
| Mitigation | SE2: remote URLs disabled by default; a `sys.io.confirm` user gate before access. |
| Conformance Rules | SE2 (FAIL) |

---

## ST4: Path Traversal / Resource Escape

| Aspect | Detail |
|--------|--------|
| Description | A `resources[].path` uses `../` or an absolute path to escape the skill folder. |
| Attack Surface | `resources[].path`. |
| Detection | Reject any path that is absolute, contains `..`, or resolves outside the skill folder / `_shared/`. |
| Mitigation | SE1 / M5: path confinement to the skill folder (`scope:skill`) or `_shared/` (`scope:shared`). |
| Conformance Rules | SE1 (FAIL), M5 (FAIL) |

---

## ST5: Excessive Authority

| Aspect | Detail |
|--------|--------|
| Description | A script requests or uses more tools than it needs, or runs dangerous commands without confirmation. |
| Attack Surface | `kind:script` resources, `requires_tools`, the skill `tools` allow-list. |
| Detection | Compare a script's `requires_tools` against its actual needs; verify dangerous operations are gated by `sys.io.confirm`. |
| Mitigation | SE4: minimal `requires_tools`; `sys.io.confirm` on dangerous operations; `sys.io.confirm` is forced-blocking (SE7). |
| Conformance Rules | SE4 (WARNING), SE7 (FAIL) |

---

## ST6: Trust Spoofing

| Aspect | Detail |
|--------|--------|
| Description | A skill claims to be verified / trusted / safe to lower a consumer's guard. |
| Attack Surface | The contract and skill metadata (any self-asserted trust flag). |
| Detection | Reject any self-asserted `trusted` / `verified` / `safe` flag. |
| Mitigation | SE6 / M6: trust is never self-declared; provenance (source / commit / hashes) is recorded by the registry. |
| Conformance Rules | M6 (FAIL), SE6 (FAIL) |

---

## Axiom 0 Invariant

Independent of any threat, every skill inherits Axiom 0: `sys.io.confirm` is **forced-blocking** and MUST NOT be bypassed regardless of `invocation.mode` or `risk_level` (SE7). A runtime cannot auto-approve a `sys.io.confirm` step, and a skill cannot downgrade it to a natural-language confirmation.

---

Align Axiom 0: Human Sovereignty and Wellbeing | Protocol: AISP | Execution: AISOP | Executor: SoulBot
