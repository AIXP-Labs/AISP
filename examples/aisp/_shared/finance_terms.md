# Finance Terms (shared resource)

A cross-skill `_shared/` resource. It is referenced by `stock_analysis_aisp` with
`scope: "shared"`, so its `path` (`finance_terms.md`) resolves relative to
`aisp/_shared/`, not the skill folder. `_shared/` carries **no** `_aisp` suffix, so
the discovery glob `aisp/*_aisp/aisp.aisop.json` naturally skips it (EC3).

| Term | Plain definition |
|------|------------------|
| Moving average | The mean closing price over the sampled window; smooths short-term noise. |
| Volatility | The standard deviation of closing prices over the window; higher means larger swings. |
| Trend | The direction from the first to the last close in the window: up / down / flat. |
| Signal | A notable pattern in the indicators worth highlighting; descriptive, never a trade instruction. |

> These definitions are informational. Any skill that uses them must state that its
> output is **not financial advice** (a `non_negotiable` red line in
> `stock_analysis_aisp`, enforced by `report.step2:sys.assert`).
