# Sensitivity and Robustness

Distinguish local sensitivity, global sensitivity, robustness, and scenario analysis.

- **Local:** finite differences or elasticities near the fitted point; vary step size and scale by units.
- **Global:** Morris screening or Sobol indices over justified distributions; ensure Monte Carlo convergence.
- **Robustness:** perturb data, seeds, preprocessing, graph edges, initial conditions, objective weights, and solver tolerances.
- **Scenario:** coherent alternative futures; do not vary parameters independently when their joint structure matters.

Prioritize uncertain and decision-relevant parameters. Cite each range or label it as a designed scenario. Refit when the perturbation would affect estimation; otherwise the analysis understates uncertainty.

For rankings report rank reversal, top-k overlap and dominance stability. For forecasts report error by horizon and rolling window. For optimization report objective regret, feasibility rate, active constraints and solution turnover. For mechanisms report state trajectories, thresholds, equilibria and bifurcations.

Conclude with: stable conclusions; fragile conclusions; tipping parameters; applicable range; fallback decision.

