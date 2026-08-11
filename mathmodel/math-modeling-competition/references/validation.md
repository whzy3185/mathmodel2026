# Validation System

## Contents

1. Validation is claim-specific
2. Data-driven models
3. Mechanism and optimization
4. Evidence table

## 1. Match validation to the claim

- Prediction: error on unseen future/population, interval coverage, calibration.
- Explanation: residual structure, competing specifications, parameter uncertainty.
- Mechanism: conservation, limits, independent observations, identifiability.
- Optimization: feasibility, objective recomputation, bound/gap, scenario stability.
- Ranking/policy: weight and scenario stability, stakeholder trade-offs.
- Simulation: convergence, event verification, output distribution and face validity.

Keep calibration, model selection, and final evaluation separate. Freeze preprocessing inside the resampling pipeline.

## 2. Data-driven checklist

| Technique | Use | Common trap |
|---|---|---|
| Train/test | independent final estimate | repeated tuning on the test set |
| K-fold CV | exchangeable observations | clustered or temporal leakage |
| Group CV | subjects/sites/groups repeat | group ID leaks into features |
| Time-series split | ordered forecasting | random split or future scaling |
| Nested CV | model/hyperparameter selection | reporting inner-CV score |
| Residual analysis | bias, variance, dependence | showing only R²/accuracy |
| Bootstrap | sampling uncertainty | naive bootstrap under dependence |
| Ablation | contribution of components | removing components while retuning unfairly |
| Baseline comparison | justify complexity | weak straw-man baseline |

Report point metrics plus uncertainty. Choose metrics before seeing the ranking and connect them to the contest decision.

## 3. Mechanism and optimization

Mechanism: unit tests for equations; dimensional analysis; limiting/special cases; manufactured or analytic solutions when available; parameter recovery on synthetic data; calibration on one slice and validation on another; profile likelihood or posterior diagnostics; conservation/positivity checks.

Optimization: independently recompute objective and every constraint; inspect solver status; report primal feasibility, integrality, optimality gap and time limit; compare an exact solution on reduced instances; test infeasibility and missing-constraint cases; re-solve scenarios. A feasible heuristic result is not a proof of optimality.

## 4. Claim–evidence table

For each paper claim record artifact, code command, dataset/version, metric, uncertainty, baseline, failure threshold, and figure/table ID. No conclusion may appear without a row.

