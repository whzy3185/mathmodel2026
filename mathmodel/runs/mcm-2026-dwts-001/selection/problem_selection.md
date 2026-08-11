# Three-problem rapid feasibility tournament

Run: `mcm-2026-dwts-001`  
Decision: **select Problem C; keep A as second choice; reject B for this run.**

| Dimension (max) | A | B | C |
|---|---:|---:|---:|
| Problem clarity (10) | 9 | 9 | 9 |
| Data availability (15) | 7 | 6 | 15 |
| External data risk (10) | 5 | 4 | 9 |
| Baseline feasibility (10) | 9 | 9 | 9 |
| Candidate-model quality (15) | 14 | 13 | 14 |
| Validation feasibility (15) | 9 | 8 | 13 |
| Computational feasibility (10) | 9 | 9 | 10 |
| Visualization/evidence (5) | 5 | 5 | 5 |
| Paper narrative (5) | 5 | 5 | 5 |
| Team execution risk (5) | 4 | 3 | 4 |
| **Total (100)** | **76** | **71** | **93** |

The total is not the sole decision rule. C is selected because its official 421-row dataset lets the
team test elimination compatibility, counterfactual voting rules, uncertainty, and characteristic
effects without inventing external values. Its central weakness is also explicit: fan votes are
latent, so the valid object is a feasible set/distribution, not a discovered secret total.

Red team: A may produce a stronger mechanistic paper if a licensed validation trace is found, but
data sourcing is the critical path. B is computationally easy but depends on speculative 2050 cost,
capacity, water, and emissions assumptions. C can fail if irregular elimination weeks prevent
reliable active-roster reconstruction; if fewer than 90% of evaluable weeks are reconstructable,
switch to A. Full per-problem routes, prototype checks, and rejection conditions are machine-readable
in `problem_selection.json`.
