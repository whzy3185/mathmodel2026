# Problem Taxonomy

## Contents

1. Classification axes
2. Contest families
3. Decomposition record
4. Method routing

## 1. Classify on several axes

Do not classify a problem from nouns alone. Record:

- **Task:** describe, explain, estimate, predict, rank, optimize, control, simulate, recommend.
- **Object:** time series, individuals, flows, graph, field, population, physical mechanism, decisions.
- **Output:** number, curve, ranking, allocation, route, policy, scenario range, memo.
- **Evidence:** given data, external data, physical law, expert preference, synthetic scenarios.
- **Structure:** static/dynamic; deterministic/stochastic; discrete/continuous; local/spatial/networked.
- **Uncertainty:** observation, parameter, structural, scenario, implementation.

## 2. Contest families

| Family | Typical emphasis | Early gate |
|---|---|---|
| CUMCM A/B | mechanism, optimization, engineering | units, feasibility, reproducible support material |
| CUMCM C | data analysis and decisions | provenance, leakage, interpretable baseline |
| MCM A | continuous mechanism | conservation, nondimensionalization, parameter identifiability |
| MCM B | discrete structure | proof/complexity, exact-vs-heuristic distinction |
| MCM C | data insights | measurement validity, time/order-aware validation |
| ICM D | operations research/network | objective/constraint completeness, solver verification |
| ICM E | environment/sustainability | scenarios, spatial scale, causal restraint |
| ICM F | policy | stakeholders, uncertainty, actionable memo |
| Graduate contest | domain depth and engineering | literature/parameter traceability |
| MathorCup/华数杯/电工杯 | current rules vary | retrieve official problem-specific rubric |

## 3. Decomposition record

For every Qi write: deliverable; decision variables; known inputs; unknown parameters; objective/estimand; constraints; candidate evidence; dependencies on earlier questions; validation; downstream figure/table. Draw a dependency DAG. A later question may consume an earlier result only through a named artifact with units and uncertainty.

## 4. Route by mathematical need

| Need | Candidate family | Required validation |
|---|---|---|
| extrapolate ordered observations | forecasting | rolling-origin backtest, naive/seasonal baseline, residual diagnostics |
| construct preference score/ranking | evaluation/MCDM | weight perturbation, rank stability, dominance and redundancy checks |
| choose actions under constraints | optimization | feasibility, bounds/gap, constraint audit, scenario re-solve |
| estimate relationships/uncertainty | statistics | residuals, interval calibration, specification checks |
| move or diffuse over links | graph/network | null graph or baseline, perturb edges, held-out links if predictive |
| vary over geography | spatial | spatial autocorrelation, spatial CV, scale sensitivity |
| obey conservation or dynamics | mechanism | dimensions, limiting cases, calibration/validation separation |
| propagate stochastic interactions | simulation | convergence, seeds, event logic, distributional comparison |
| predict flexibly from features | ML | leakage-safe pipeline, nested selection, interpretability and shift checks |
| justify public action | decision/policy | stakeholder objectives, scenarios, uncertainty, implementation constraints |

