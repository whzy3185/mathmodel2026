# Graph and Network Cookbook

Define node/edge meaning, direction, weights, time, missing edges and construction threshold. A force-directed picture is not analysis.

| Method | Use | Do not use | Assumptions/formulation | Validation/alternative |
|---|---|---|---|---|
| Shortest path | additive path cost | negative cycles/uncertain costs ignored | minimize sum of edge weights | path feasibility, perturb weights; k-shortest |
| Max flow/min cut | capacity-limited transfer | flow conservation invalid | conservation + capacity | cut certificate; min-cost flow |
| Min-cost flow | flow with linear cost | nonlinear congestion matters | flow balance/capacity/cost | dual/feasibility; nonlinear network |
| MST | connect all nodes cheaply | redundancy/reliability required | minimum spanning tree | compare alternatives; survivable network |
| TSP/VRP | routing/assignment | time windows/capacities omitted | tour/vehicle constraints | exact small cases, bounds; MILP/heuristic |
| Community detection | mesoscale groups | one algorithm treated as truth | modularity/SBM/flow partitions | null models, resolution/algorithm stability |
| Centrality | specific influence/access definition | “important” without mechanism | degree, betweenness, eigenvector, PageRank | compare metrics/null graph; diffusion test |
| Robustness | failure/attack resilience | only random deletion | efficiency/connectivity under perturbation | random/targeted/scenario attacks |
| Diffusion | contagion/information processes | static centrality substitutes dynamics | SI/SIR/threshold/random walk | synthetic recovery, held-out cascade; ABM |

For predictive link tasks split edges without leaking future topology. Test edge uncertainty, threshold choice, disconnected components and degree-preserving nulls. Report algorithms, complexity, seeds and whether results survive alternative graph construction.

