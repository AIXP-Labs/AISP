# enforced_by Binding Rules (AISP)

How to bind each `non_negotiable` red line to a real mechanism. Hard guarantees require a conforming runtime to enforce the bound operation; a `sys.*` name alone is not proof. Natural-language rules are policy-as-prompt (soft); `enforced_by: tools` is hard only when the runtime actually enforces tool permissions (otherwise advisory, R6).

## Grammar

```
enforced_by := <node>.<step>:<mechanism>   # e.g. interpret.step1:sys.assert
             | aisop.main                    # the graph topology / ordering forces it
             | tools                          # the runtime tool allow-list enforces it
```

The referenced `<node>.<step>` MUST exist in `functions`, and that step MUST begin with a call to the exact named `sys.*` mechanism (`sys.assert_fake` is not `sys.assert`). `aisop.main` MUST be the entry graph. Dangling references fail M4. Static matching does not evaluate an assertion: use AISOP-supported comparisons/boolean operators, not Python methods or comprehensions, and test intended rejection behavior. An undefined value must stop, not be accepted as a successful assertion.

## Choosing a mechanism

| Red line is about… | Bind to | Why |
|--------------------|---------|-----|
| A precondition / postcondition that must hold | `<node>.<stepN>:sys.assert` | Deterministic check; hard fail on violation |
| A human gate before an irreversible action | `<node>.<stepN>:sys.io.confirm` | Forced-blocking confirmation (Axiom 0 / SE7) |
| Required ordering or a mandatory node | `aisop.main` | Graph topology forces the path |
| Capability restriction (no network, no writes outside scope, no trades) | `tools` | The tool allow-list bounds what the runtime can do |
| Reading from a confined resource only | `<node>.<stepN>:sys.io.read` | The system call confines the path |

## Rules

1. Prefer `sys.*` over `tools` over prose whenever a deterministic check exists.
2. Never bind a red line to a node/step that does not exist — generate the step first.
3. A confirmation red line MUST use `sys.io.confirm`, never a prose "ask the user".
4. Keep red lines minimal and machine-checkable; descriptive guidance belongs in `functions` (Tier A), not in `non_negotiable`.
5. Do not weaken an inherited red line during evolution (no removing a constraint, lowering `risk_level`, or expanding `tools`). An intentional policy change requires separate explicit human authorization and a documented decision; supporting evidence alone is not permission.
