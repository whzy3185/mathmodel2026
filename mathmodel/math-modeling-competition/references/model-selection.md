# Candidate Model Tournament

## Contents

1. Required record
2. Gates
3. Refutation
4. Selection output

## 1. Start from a claim, not a method

State the decision or claim the model must support, its horizon, population, units, tolerance, and evidence available. Define a transparent baseline before complex candidates. A baseline may be persistence, seasonal naive, mean/rate, linear regression, shortest path, greedy feasible allocation, or a reduced mechanism.

Generate two or three candidates with genuinely different assumptions. For each answer: why suitable; why simpler method is insufficient; assumptions; data and parameter needs; computational cost; validation; what would refute it; fallback.

## 2. Gates

| Gate | Pass evidence | Reject/repair signal |
|---|---|---|
| Assumption | assumptions are explicit and testable | essential assumption contradicts data/domain |
| Data | variables, sample, resolution, order, labels support fit | target unavailable, leakage, scale mismatch |
| Complexity | added degrees of freedom buy measurable value | no gain over baseline; small sample/high variance |
| Identifiability | parameters/features can be learned separately | flat profile, collinearity, equivalent parameter sets |
| Engineering | implementation fits time, compute, libraries | brittle dependency, unbounded run, no solver access |
| Validation | credible out-of-sample or structural test exists | only training fit or circular validation |
| Communication | formulation and results can be explained | black box cannot support requested decision |

Prefer the simplest candidate that clears every applicable gate. Complexity is justified by lower validated error, better feasibility, needed causal/mechanistic structure, improved uncertainty, or a decision-relevant capability—not novelty.

## 3. Refutation before confirmation

Write failure tests before fitting: residual autocorrelation; conservation violation; poor calibration; unstable ranks; infeasibility; sensitivity discontinuity; parameter non-identifiability; out-of-regime extrapolation; performance collapse under rolling splits; heuristic worse than a simple feasible baseline.

If a primary candidate fails, execute the named fallback. Do not silently swap models after seeing results; record the evidence and version.

## 4. Selection output

Use `templates/candidate-model-tournament.json`. The final note must include baseline, candidates, rejected candidates with evidence, primary model, fallback, validation plan, stop conditions, and team approval. Run `scripts/check_plan.py` before implementation.

