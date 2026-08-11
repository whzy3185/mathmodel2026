# Problem B intake — Creating a Moon Colony Using a Space Elevator System

Source: `input/problems/problem_B.pdf` (official COMAP PDF, SHA-256 `bbb6efb6...827ca`).

## Required work and deliverables

1. Compare delivery of 100 million metric tons by three Galactic Harbours alone, rockets alone, and a hybrid.
2. Re-evaluate cost and timeline under imperfect reliability.
3. Estimate one year of water needs for 100,000 residents and apply the delivery model.
4. Compare environmental impacts and adjust the model to reduce them.
5. Write a one-page recommendation letter to the fictional MCM Agency.

## Structured intake

| Item | Extraction |
|---|---|
| Given data | 100 Mt construction mass; 100,000 residents; three harbours; 179,000 t/year stated lift capability; 100–150 t future rocket payload; ten launch-site candidates. |
| External data | Space-elevator throughput interpretation, electricity/cost assumptions, rocket launch cost/rate/emissions, water use and recycling. |
| Task components | Capacity planning, optimization, reliability simulation, environmental accounting, scenario decision. |
| Subquestion DAG | Q1 deterministic scenarios → Q2 reliability → Q3 water operations; Q1+Q2+Q3 → Q4 environment → Q5 letter. |
| Decision variables | Method shares, launch sites, annual launches, harbour allocation, redundancy, delivery schedule. |
| Output variables | Completion year, cost (currency), delivered mass (t), reliability, water mass (t/year), emissions. |
| Key constraints | Capacity, mass balance, nonnegative flows, service start in 2050, facility/launch throughput, reliability. |
| Data scale | Small scenario model but many uncertain external parameters. |
| Most dangerous assumption | Interpreting 179,000 t/year as per harbour/system/elevator without resolving wording. |
| Largest execution risk | Cost and emissions dominate conclusions yet are not supplied and must be defensibly sourced. |
| Largest paper risk | False precision in speculative 2050 costs and technology performance. |
| Expected figures | Cost–time frontier, delivery schedule, reliability bands, water scenarios, emissions trade-off. |
| Solver/packages | SciPy linear programming; Monte Carlo; pandas/numpy/matplotlib. |
| Simplest baseline | Constant-capacity deterministic mass-balance schedule for each of the three specified scenarios. |

Baseline route: deterministic annual flow. Candidate families: linear cost–time allocation;
chance-constrained or reliability-adjusted scheduling; multi-objective cost–time–emissions frontier.
