# Optimization Cookbook

Define sets, indices, parameters with units, variables/domains, objective, constraints, uncertainty and status checks. Recompute feasibility and objective independently.

| Method | Use | Do not use | Formulation/assumptions | Validation/fallback |
|---|---|---|---|---|
| LP | continuous linear choices | discreteness/nonlinearity matters | min cᵀx, Ax≤b | duals, feasibility; MILP/NLP |
| MILP/CP-SAT | logical, assignment, scheduling | loose big-M or enormous unstructured model | linear constraints + integer domains | gap, bound, reduced instances; heuristic feasible |
| Convex NLP | smooth convex nonlinear relations | nonconvexity ignored | min f(x), g(x)≤0 | KKT + solver status; conic reformulation |
| Nonconvex NLP | genuine nonlinear physics | local solution called global | nonlinear equations/bounds | multi-start/bounds; simplified convex model |
| Dynamic programming | separable staged state/action | state explosion | Bellman recursion | small-instance enumeration; approximation |
| Multi-objective | irreducible trade-offs | arbitrary weighted sum only | Pareto dominance/ε-constraint | frontier convergence; single-objective extremes |
| Robust optimization | bounded/adversarial uncertainty | uncertainty set unjustified | min worst-case objective/constraints | out-of-set scenarios; stochastic model |
| Stochastic optimization | known scenario probabilities | fabricated distributions | expected/risk objective over scenarios | out-of-sample regret; robust fallback |
| Optimal control | dynamic action with state law | static decision suffices | state ODE + control objective | stability/constraints/disturbance; discretized NLP |
| GA/SA/PSO/ACO | hard combinatorial/nonconvex best-found solution | exact model tractable | population/trajectory heuristic | seeds, time budget, feasible baseline, lower bound |

Exact vs heuristic is a reporting boundary. LP/MILP/convex solvers can provide certificates or bounds under conditions. Metaheuristics usually cannot; report best-found feasible, distribution across seeds, runtime, stopping rule, and comparison with exact solutions on small instances.

Test objective weights, big-M, penalty terms, capacity/demand scenarios, integrality tolerances and solution turnover. If infeasible, obtain an IIS/conflict where available and audit missing or contradictory constraints before relaxing them.

