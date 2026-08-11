# Simulation Cookbook

Specify entities/states/events, random distributions and sources, time advance, initialization, warm-up, termination, replications and outputs.

| Method | Use | Do not use | Formulation/assumptions | Validation/alternative |
|---|---|---|---|---|
| Monte Carlo | propagate uncertainty or estimate probabilities | distributions invented/no convergence | iid or structured draws | MC error, convergence, variance reduction; analytic bound |
| Agent-based | heterogeneous local interactions create emergence | simple aggregate law suffices | rules, network, schedules | unit tests, pattern/parameter validation; system dynamics |
| Discrete-event | queues/resources/event processes | continuous state dominates | event calendar and resource logic | event traces, Little's law, warm-up; queueing model |
| Cellular automata | local grid rules/spatial emergence | grid/rules arbitrary | neighborhood transition rule | resolution/rule sensitivity; PDE/ABM |

Use common random numbers for scenario comparisons when appropriate. Report seeds, replications, confidence intervals, warm-up choice and convergence. Verify implementation on degenerate cases and conservation identities. “Looks realistic” is not validation; compare distributions, moments, event rates or spatial patterns with evidence.

