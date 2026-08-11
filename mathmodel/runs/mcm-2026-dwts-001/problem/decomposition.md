# Selected Problem C decomposition

The supplied votes are secret. Therefore Q1 estimates a compatible distribution/set and its
uncertainty, never a uniquely observed total. Units below are fixed before modeling.

## Q1 — Latent weekly fan support

- Exact deliverable: weekly fan-share estimates, compatibility rate with observed eliminations, and contestant/week uncertainty.
- Inputs: active-roster judge scores, season, week, observed elimination/final result.
- Outputs: fan share (fraction of active weekly vote), lower/upper interval (fraction), elimination compatibility (% weeks).
- Symbols: \(j_{iwt}\) judge share; \(v_{iwt}\) fan share; \(c_{iwt}\) combined score; \(e_{iwt}\) observed elimination indicator.
- Decision variables: \(v_{iwt}\ge0\), \(\sum_i v_{iwt}=1\).
- Unknown parameters: regularization/smoothing strength and numerical elimination margin.
- Estimand/objective: the least-informative vote distribution compatible with observed outcomes.
- Constraints: simplex, method-specific combined-score order, active roster, optional temporal continuity.
- Assumptions: data zeros after elimination are structural; ties use a documented deterministic tolerance.
- External evidence: none required.
- Dependencies: processed contestant-week table; downstream Q2, Q3, Q4.
- Validation: observed-elimination compatibility, feasible-week rate, bootstrap/set width, held-out-season stress test.
- Tables/figures: compatibility by season; vote uncertainty; controversy trajectories.
- Baseline: uniform shares with minimum feasibility adjustment.
- Candidates: maximum entropy; temporally regularized constrained shares; supervised point prediction (expected rejection—no vote labels).

## Q2 — Counterfactual voting rules

- Exact deliverable: rank-vs-percentage counterfactual outcomes across seasons, controversy cases, bottom-two judge-save impact, and recommendation.
- Inputs: Q1 vote distributions/intervals and weekly judge shares.
- Outputs: changed eliminations (count and %), fan-favor index (rank positions), controversy outcomes, uncertainty bands.
- Symbols: \(R^J,R^V\) ranks; \(p^J,p^V\) shares; \(a\) judge weight.
- Decision variables: combination rule, judge/fan weight, bottom-two safeguard.
- Unknown parameters: tie policy and counterfactual judge-save proxy.
- Estimand/objective: rule-induced outcome differences conditional on Q1 uncertainty.
- Constraints: identical active roster and vote draw across compared rules.
- Assumptions: counterfactual vote shares do not change in response to the rule.
- External evidence: none required.
- Dependencies: Q1 results; downstream Q4 and memo.
- Validation: replay reported era rules; repeat over feasible/bootstrap vote draws; controversy case checks.
- Tables/figures: disagreement matrix; fan-favor distribution; named-case paths.
- Baseline: deterministic replay using the Q1 point estimate.
- Candidates: uncertainty-integrated counterfactual simulation; point replay fallback; placement-only comparison (expected rejection—post-outcome leakage).

## Q3 — Partner and celebrity associations

- Exact deliverable: estimates for age, industry, geography and professional-partner associations with judge score and estimated fan support.
- Inputs: contestant metadata, judge outcomes, Q1 fan estimates and uncertainty weights.
- Outputs: standardized effect estimates, grouped-validation errors, stability intervals.
- Symbols: \(y^J,y^V\) outcomes; \(X\) characteristics; season/week/partner effects.
- Decision variables: encoding, regularization, grouped split, reported effect threshold.
- Unknown parameters: ridge penalty and minimum group sample size.
- Estimand/objective: predictive association after season/week adjustment, not causal effects.
- Constraints: split by season; preprocessing fitted inside folds; no placement/future-week features.
- Assumptions: residual association is descriptive and Q1 uncertainty is propagated.
- External evidence: none required.
- Dependencies: Q1 result and processed metadata; informs Q4 discussion.
- Validation: leave-seasons-out/grouped validation; bootstrap stability; ablation.
- Tables/figures: model comparison; top stable associations with intervals.
- Baseline: season/week-adjusted mean and OLS/ridge without partner effects.
- Candidates: grouped ridge with partner/industry features; hierarchical shrinkage approximation; deep model (expected rejection—small data and weak interpretability).

## Q4 — Alternative weekly system

- Exact deliverable: a proposed rule, quantified fairness/excitement criteria, robustness, and producer memo recommendation.
- Inputs: Q1 vote uncertainty, Q2 counterfactuals, Q3 association/stability results.
- Outputs: chosen judge weight (%), safeguard rule, upset/churn/fan-influence metrics and failure boundary.
- Symbols: \(a\in[0,1]\) judge weight; \(L(a)\) multi-criterion loss.
- Decision variables: \(a\), rank/percentage transform, bottom-two safeguard.
- Unknown parameters: normative criterion weights; handled by sensitivity rather than hidden defaults.
- Estimand/objective: robust trade-off between judge quality, fan influence, and rule stability.
- Constraints: transparent weekly computation; no external engagement label; recommendation stable over documented preference ranges.
- Assumptions: historical votes are a useful stress-test population for the new rule.
- External evidence: none required.
- Dependencies: Q1–Q3; downstream paper conclusions and memo.
- Validation: scenario grid, alternative criterion weights, rank reversal, controversy cases, feasible-vote perturbations.
- Tables/figures: rule frontier; sensitivity map; final recommendation table.
- Baseline: current 50/50 percentage combination.
- Candidates: robust judge-weight selection with bottom-two safeguard; trimmed rank fallback; engagement-trained rule (expected rejection—no engagement target).
