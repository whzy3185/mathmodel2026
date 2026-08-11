# Award-Paper Pattern Library

These are derived design patterns, not templates to copy and not official rubrics.

| Pattern | Dependency chain | Essential baseline | Core validation | Common weakness |
|---|---|---|---|---|
| P01 Forecast → optimization | demand distribution feeds decisions | naive forecast + static allocation | rolling backtest + scenario re-solve | forecast uncertainty not propagated |
| P02 Evaluation → optimization | scores become benefits/constraints | equal weights/simple cost | weight/rank stability + Pareto | arbitrary score normalization |
| P03 Mechanism → parameter estimation | laws define states; data fit parameters | reduced/limiting model | units, recovery, holdout trajectory | non-identifiability |
| P04 Network → robustness | topology drives flow/diffusion | degree/random null | edge/node attacks, alternative metrics | hairball interpretation |
| P05 Spatial statistics → policy | local risk estimates allocate policy | non-spatial model | spatial CV, scale/boundary sensitivity | ecological overclaim |
| P06 Simulation → scenarios | rules generate outcome distributions | analytic/simple queue | convergence, seeds, scenario comparison | face validity only |
| P07 ML → explainability | prediction plus decision-relevant drivers | linear/tree baseline | nested CV, calibration, SHAP stability | explanation treated as causation |
| P08 Multi-objective → Pareto | objectives expose trade-offs | single-objective optima | frontier convergence and dominance | weighted sum hides nonconvex trade-off |
| P09 Dynamic system → control | states drive feedback action | uncontrolled system | stability, disturbance and actuator limits | perfect information/control |
| P10 Data–mechanism fusion | residual/data model repairs mechanism | each component alone | ablation and out-of-regime test | double counting |
| P11 Forecast → risk reserve | distribution drives safety margin | point forecast | interval coverage + loss simulation | only mean accuracy |
| P12 Causal estimate → policy | estimand feeds counterfactual choice | descriptive association | placebo/specification/sensitivity | causal language without identification |

## Extraction record for a representative paper

Capture citation/award evidence; Q1–Qn dependency; baseline; model route and rejection reasons; main formulation; improvement; validation; sensitivity; robustness; claim-bearing figures; summary structure; narrative; genuine innovation; weaknesses and a better redesign. Do not store full PDFs when copyright is unclear; store metadata, source link, and original derived notes.

