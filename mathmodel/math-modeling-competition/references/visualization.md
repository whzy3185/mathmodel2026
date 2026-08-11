# Visualization and Figure Contract

Complete `templates/figure-contract.md` before coding a final figure.

## Match chart to claim

| Claim | Preferred figure | Required evidence |
|---|---|---|
| trend/forecast | time plot with backtest boundary and interval | units, horizon, observed vs predicted |
| model comparison | paired errors or interval plot | folds/seeds and uncertainty, not one bar |
| residual validity | residual-vs-fit, QQ/ACF as applicable | reference line and diagnostic interpretation |
| trade-off | Pareto/scenario frontier | dominance, feasible region, selected point |
| sensitivity | tornado, partial dependence, Sobol/Morris | parameter ranges and uncertainty |
| spatial pattern | map plus scale/legend | CRS/aggregation/source; avoid misleading area |
| network mechanism | metric distribution/subgraph | null/reference; avoid decorative hairball |
| mechanism | state trajectory/phase plot | initial conditions, units, limiting behavior |

Use accessible colors, direct labels where possible, readable type at final size, vector output for line art, and consistent units. Preserve data-to-figure scripts and machine-readable tables. Never use a truncated axis without explicit reason. A chart is removed if deleting it does not weaken a claim.

