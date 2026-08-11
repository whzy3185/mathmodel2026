# Problem C intake — Data With The Stars

Sources: `input/problems/problem_C.pdf` and `input/attachments/problem_C_data.csv` (official COMAP files).

## Required work and deliverables

1. Estimate latent weekly fan-vote shares; measure whether estimates reproduce eliminations and quantify nonuniform certainty.
2. Apply rank and percentage combination methods across seasons, analyze controversies and bottom-two judge saves, and recommend a method.
3. Estimate effects of professional dancers and celebrity characteristics on judge scores and fan support.
4. Propose and support a fairer/better weekly voting system.
5. Deliver an English PDF of at most 25 pages including a one- to two-page producer memo.

## Structured intake

| Item | Extraction |
|---|---|
| Given data | 421 contestants × 53 columns: identity/partner/industry/geography/age/season/result/placement plus up to four judge scores for weeks 1–11. |
| External data | Optional only; not required for a complete reproducible route. |
| Task components | Partial-identification/inverse problem, constrained estimation, counterfactual simulation, grouped statistical modeling, mechanism design. |
| Subquestion DAG | Q1 latent votes → Q2 method counterfactuals and Q3 effects; Q2+Q3 → Q4 alternative system and memo. |
| Decision variables | Latent fan shares by contestant/week; proposed judge/fan weight and safeguard rule. |
| Output variables | Elimination consistency, vote intervals, counterfactual changes, group/partner effects, recommendation metrics. |
| Key constraints | Fan shares nonnegative and sum to one; observed elimination/bottom status; no true fan-vote labels; zero judge scores after elimination are structural. |
| Data scale | 421 rows, 34 seasons, 44 weekly judge-score columns; compact local computation. |
| Most dangerous assumption | Treating one feasible latent-vote vector as the unknown truth despite set identification. |
| Largest execution risk | Correctly reconstructing active rosters and atypical no-/multi-elimination weeks. |
| Largest paper risk | Causal language for partner/industry associations and overconfident fan-vote point estimates. |
| Expected figures | EDA/active roster, vote intervals, method disagreement, controversy trajectories, effect intervals, fairness frontier. |
| Solver/packages | pandas/numpy/scipy/sklearn/matplotlib; no commercial solver. |
| Simplest baseline | Minimum-deviation feasible fan shares around uniform support subject to observed elimination consistency. |

Baseline route: uniform shares with the smallest constraint-enforcing adjustment. Candidate families:
maximum-entropy constrained shares; temporal regularized constrained shares; Bayesian/bootstrapped
partial-identification intervals. The data identify compatibility sets, not true secret vote totals.
