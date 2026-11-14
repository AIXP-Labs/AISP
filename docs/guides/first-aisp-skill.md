# First AISP Skill

This tutorial walks you through building a complete AISP skill from scratch. You will create the `yijing_aisp` divination skill — a single, read-only skill that demonstrates every core part of the protocol: the folder, the two-message body, the real-object contract, and red lines bound to real mechanisms.

**What we are building:** an I Ching reading skill.
**Risk level:** low (read-only).
**Estimated time:** 20 minutes.

By the end you will have a conformant `aisp/yijing_aisp/` skill package. It is executable by an AISP/AISOP-compatible runtime; this tutorial focuses on the package, contract, resources, and validation.

This tutorial uses `aisp/...` as the package-root layout. The repository example of the same skill lives at `examples/aisp/yijing_aisp/`.

---

## Step 1: Create the Folder

The folder name **is** the skill `id`, and it **must end with `_aisp`**:

```text
aisp/
└── yijing_aisp/
    ├── aisp.aisop.json
    └── data/
```

This satisfies conformance rule **M2** (folder name == id, ends with `_aisp`, file named `aisp.aisop.json`).

---

## Step 2: Write the System Message (Identity)

The skill body is a 2-message array. The first message is `system` and holds identity metadata:

```json
{
  "role": "system",
  "content": {
    "protocol": "AISP V1.0.0",
    "axiom_0": "Human_Sovereignty_and_Wellbeing",
    "id": "yijing_aisp",
    "name": "Yijing Divination",
    "version": "1.0.0",
    "license": "Apache-2.0",
    "summary": "Cast and interpret an I Ching (Yijing) hexagram for a user's question.",
    "description": "Native AISP skill: clarify the question, cast a hexagram randomly, and interpret it for reflection (not deterministic prediction).",
    "flow_format": "mermaid",
    "loading_mode": "node",
    "tools": ["filesystem", "code"],
    "params": { "question": "string" },
    "system_prompt": ""
  }
}
```

| Field | Value | Purpose |
|-------|-------|---------|
| `protocol` | `AISP V1.0.0` | Declares the file as AISP (still structurally an AISOP program) |
| `id` | `yijing_aisp` | == the folder name; ends with `_aisp` |
| `license` | `Apache-2.0` | Default license (SHOULD) |
| `system_prompt` | `""` | MAY be empty — the contract carries the briefing, not `system_prompt` |

This satisfies **M1** (a legal AISOP program with the required fields).

---

## Step 3: Write the User Message (Instruction + Contract + Flow)

The second message is `user`. It holds the strong `instruction`, the real-object `aisp_contract`, the `aisop.main` graph, and the `functions`.

### The instruction

```json
"instruction": "STRICTLY OBEY aisp_contract; its non_negotiable rules are inviolable; then RUN aisop.main"
```

This is the immutable strong directive: obey the contract, then run the flow.

### The contract (Tier S)

```json
"aisp_contract": {
  "profile": "aisp.skill.v1",
  "invocation": {
    "mode": "auto_or_manual",
    "when_to_use": ["cast an I Ching reading", "interpret a hexagram", "yijing divination for a question"],
    "when_not_to_use": ["medical, legal, or financial decisions needing a professional", "no question provided"]
  },
  "non_negotiable": [
    { "rule": "Follow RUN aisop.main; never interpret before casting.", "enforced_by": "aisop.main" },
    { "rule": "Do not interpret without a cast hexagram.", "enforced_by": "interpret.step1:sys.assert" },
    { "rule": "The reading must state it is for reflection, not deterministic prediction.", "enforced_by": "interpret.step4:sys.assert" }
  ],
  "discovery": { "category": "culture", "tags": ["yijing", "iching", "divination", "hexagram"] },
  "risk_level": "low",
  "resources": [
    { "id": "hexagrams", "path": "data/hexagrams.json", "kind": "data", "mode": "read_only" },
    { "id": "interpretation_guide", "path": "data/interpretation_guide.md", "kind": "reference", "mode": "read_only", "when": "interpreting the hexagram" }
  ]
}
```

The contract is a **real object** (not a string), in the **user message**, so the model reads it directly (M3). Each `enforced_by` will point to a real mechanism (M4) — we wire those in `functions` next.

### The flow (Tier A)

```json
"aisop": {
  "main": "graph TD\n    clarify[Clarify the question] --> cast[Cast hexagram]\n    cast --> interpret[Interpret]\n    interpret --> end_node((End))"
},
"functions": {
  "clarify": { "step1": "Identify the user's question and intent for the reading.", "output_mapping": "question" },
  "cast": {
    "step1": "sys.code.exec('python', 'import random; lines=[random.randint(6,9) for _ in range(6)]') -> lines",
    "step2": "sys.io.read('data/hexagrams.json') -> hexagram_table",
    "step3": "Map lines to the primary and changing hexagram via hexagram_table.",
    "output_mapping": "hexagram"
  },
  "interpret": {
    "step1": "sys.assert('hexagram != null', 'No hexagram has been cast')",
    "step2": "sys.io.read('data/interpretation_guide.md') -> guide",
    "step3": "sys.llm.json('Interpret the hexagram for the question using guide; set disclaimer exactly to: For reflection only, not deterministic prediction.', schema={summary:'string', guidance:'string', changing_lines:'array', disclaimer:'string'}) -> reading",
    "step4": "sys.assert(\"reading.disclaimer == 'For reflection only, not deterministic prediction.'\", 'The required disclaimer must match the declared wording')",
    "step5": "Render reading as Markdown.",
    "constraints": ["Ground the interpretation in the cast hexagram and guide; do not fabricate hexagrams."]
  },
  "end_node": { "step1": "Return the final Markdown reading." }
}
```

These bindings point to existing mechanisms: `interpret.step1` and `interpret.step4` start with `sys.assert`, and the graph orders casting before interpretation. This satisfies static reference checks, not runtime certification. The disclaimer now compares exact declared wording, not merely a non-null field; the runtime still has to evaluate it against the actual output. Use runtime-supported expressions and test the intended failure behavior; do not count unsupported or unverified assertions as hard checks.

---

## Step 4: Add the Resources

Create the two declared resources under `data/`:

- `data/hexagrams.json` — a `read_only` data resource (a hexagram lookup table).
- `data/interpretation_guide.md` — a `read_only` reference resource.

Any file a node reads or runs SHOULD be declared in `resources`; an undeclared file is an unknown surface a validator SHOULD warn about (threat ST2). (Path confinement of declared resources is the MUST — see M5.)

---

## Step 5: Verify Your Skill

First generate the required same-folder compatibility interface (from the repository root, using the example path here):

```bash
python -B tools/aisp_skill_md.py examples/aisp/yijing_aisp --write
python -B tools/aisp_skill_md.py examples/aisp/yijing_aisp --check
```

Use your own skill path when authoring elsewhere. The fixed bootstrap delegates to a conforming executor, SoulRun by default; no executor means no execution, not a best-effort host fallback.

Generation freezes the default lower bound once, or accepts an explicit `--executor-version-requirement '>=X.Y.Z'` / `'==X.Y.Z'`. Runtime uses one version condition: matching versions run directly; proven absence/mismatch prompts for installation, followed by a matching recheck. The generator does not install an executor, and normal regeneration does not refresh an existing valid bound.

### Checklist

| Check | Expected | How to Verify |
|-------|----------|---------------|
| M1 | Legal AISOP program | 2-message array; required fields; `aisop.main` present |
| M2 | Folder/file/suffix | folder == `yijing_aisp`, ends `_aisp`, file `aisp.aisop.json` |
| M3 | Contract present | `user.content.aisp_contract` is a real object; `profile` has versioned form `aisp.skill.v<major>` |
| M4 | enforced_by real | each `enforced_by` points to an existing node, numeric execution step, and mechanism |
| M5 | Resource paths | relative, no `../`; declared files match folder |
| M6 | No self-trust | no `trusted`/`verified`/`safe` flags |
| M7 | Required generated interface | same-folder SKILL.md; derived header and fixed bootstrap match, five launch strings plus the frozen version policy valid |

### Common Mistakes

1. Putting the contract in `system_prompt` as a JSON-in-string — use `user.content.aisp_contract` (a real object).
2. `enforced_by` pointing to a step that does not exist, or to metadata such as `step_note` (a phantom guarantee) — wire a real numeric `sys.*` step.
3. Folder name not ending in `_aisp`, or not equal to `id`.
4. Reading a file not declared in `resources`.

---

## Register the Skill

Run the discovery script to (re)generate the index:

```bash
cd aisp
python -B aisp_list.py --json
```

You should see `yijing_aisp` listed, and `aisp_list.json` updated.

For this repository's examples, run from the repository root:

```bash
python -B examples/aisp/aisp_list.py --json
```

---

## Generate the Skill README

Generate the portable bootstrap README from the contract:

```bash
python -B tools/aisp_readme.py examples/aisp/yijing_aisp --write
python -B tools/aisp_readme.py examples/aisp/yijing_aisp --check
```

The generated README helps a human or generic AI understand how to load the independent skill folder. It is not authoritative and does not prove the skill is safe or trusted; `aisp.aisop.json` and external provenance remain the source of truth.

---

## What You Built

A complete, conformant AISP skill: a self-contained folder, a 2-message body, a real-object contract in the user message, and three red lines bound to real mechanisms. The skill is the program; trust is never self-declared.

---

## Next Steps

- Add a second skill with `data/` + `scripts/`: see [`examples/aisp/stock_analysis_aisp/`](https://github.com/AIXP-Labs/AISP/tree/main/examples/aisp/stock_analysis_aisp).
- Run a full conformance check: [Conformance Walkthrough](conformance-walkthrough.md).
- Review the required interface, executor configuration and regeneration rules: [Interoperability with Agent Skills](../topics/interoperability-with-agent-skills.md).

---

> Align Axiom 0: Human Sovereignty and Wellbeing. AISP — AI Skill Protocol V1.0.0. www.aisp.dev
