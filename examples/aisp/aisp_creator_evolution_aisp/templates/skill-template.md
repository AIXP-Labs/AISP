# AISP Skill Scaffold Template

A generated skill is a folder `<id>_aisp/` whose name equals `id` and ends with `_aisp`.
By default it is created as a sibling of this creator skill. If a deployment
has a parent-level `aisp/` registry wrapper, that wrapper is fixed external
infrastructure and is not created or modified by this creator.

```
<id>_aisp/
├── aisp.aisop.json     # the skill — a legal AISOP V1.0.0 program (2-message array)
├── README.md           # generated from aisp.aisop.json
├── SKILL.md            # default same-folder Agent Skills sidecar; core-optional
├── evals/              # behavior evidence
│   ├── script-behavior.json  # required when executable scripts are declared
│   └── behavior-cases.json   # recommended for non-script/model-mediated skills
└── <resources>/        # custom layout, e.g. data/, scripts/, schemas/
```

> Do not create `<id>_aisp/aisp/`. Parent-level discovery/registry files such
> as `aisp/README.md`, `aisp_list.py`, or `aisp_list.json` are outside this
> creator's scope.

## `aisp.aisop.json` skeleton

```json
[
  {
    "role": "system",
    "content": {
      "protocol": "AISP V1.0.0",
      "axiom_0": "Human_Sovereignty_and_Wellbeing",
      "id": "<id>_aisp",
      "name": "<Name>",
      "version": "1.0.0",
      "license": "Apache-2.0",
      "summary": "<one line>",
      "flow_format": "jsonflow",
      "loading_mode": "node",
      "tools": ["<minimal capabilities>"],
      "params": {},
      "system_prompt": ""
    }
  },
  {
    "role": "user",
    "content": {
      "instruction": "STRICTLY OBEY aisp_contract; its non_negotiable rules are inviolable; then RUN aisop.main",
      "user_input": "{user_request}",
      "aisp_contract": {
        "profile": "aisp.skill.v1",
        "invocation": { "mode": "auto_or_manual", "when_to_use": ["..."], "when_not_to_use": ["..."] },
        "non_negotiable": [ { "rule": "...", "enforced_by": "<node>.<step>:sys.assert" } ],
        "discovery": { "category": "...", "tags": ["..."] },
        "risk_level": "low",
        "resources": [ { "id": "...", "path": "data/...", "kind": "data", "mode": "read_only" } ]
      },
      "aisop": { "main": { "start": { "next": ["end_node"] }, "end_node": {} } },
      "functions": {
        "start": { "step1": "...", "execute_mode": "inline" },
        "end_node": { "step1": "Return result.", "execute_mode": "inline" }
      }
    }
  }
]
```

## Checklist (must pass M1–M6)

- [ ] 2-message array; `protocol` == `"AISP V1.0.0"`; `aisop.main` present (M1)
- [ ] folder name == `id` and ends with `_aisp`; file is `aisp.aisop.json` (M2)
- [ ] for third-party Agent Skill conversions, use a neutral adapter `id` / folder / `SKILL.md name`; keep external source or platform identity only in resources/references
- [ ] `user.content.aisp_contract` is a real object; `profile` starts `aisp.skill.` (M3)
- [ ] every `non_negotiable.enforced_by` resolves to a real mechanism (M4)
- [ ] every `resources[].path` is relative, no `..`, confined to the folder or `_shared/` (M5)
- [ ] no self-declared `trusted` / `verified` / `safe` (M6)
- [ ] `system_prompt` empty; contract is NOT JSON-in-string
- [ ] every function either declares `execute_mode: "inline"` or `execute_mode: "agent"`; missing values fall back to inline and warn
- [ ] use `inline` for short routing/classification/confirmation/simple summarization nodes; use `agent` when isolation, source gathering, generation, complex validation, or decision impact justifies it
- [ ] non-agent nodes with more than 10 `step*` entries are reviewed for `execute_mode: "agent"`; this is a review heuristic, not a restriction on shorter `agent` nodes
- [ ] generated root `README.md` matches `aisp.aisop.json`
- [ ] default same-folder `SKILL.md` sidecar unless explicitly opted out — `metadata.aisp_program: aisp.aisop.json`, `metadata.bridge_mode: native_sidecar`, never copies logic; if opted out, record the opt-out and do not claim Agent Skills interop
- [ ] if any script resource is executable (`execute_only` or `read_and_execute`), `evals/script-behavior.json` exists, is declared in `resources`, and replays positive, boundary, and failure cases
- [ ] if no executable script resource exists, `evals/behavior-cases.json` exists, is declared in `resources`, and lists positive, boundary, and failure review cases; this is soft semantic evidence, not a safety proof
- [ ] after any resource, README, SKILL.md, or eval evidence change, regenerate root `README.md` and same-folder `SKILL.md`
- [ ] no internal `aisp/` directory inside the candidate package; parent-level AISP registry infrastructure is external
