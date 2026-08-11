# Problem A intake — Modeling Smartphone Battery Drain

Source: `input/problems/problem_A.pdf` (official COMAP PDF, SHA-256 `1afb2971...83744`).

## Required work and deliverables

1. Build an explicit continuous-time lithium-ion battery model for state of charge (SOC).
2. Predict time-to-empty under several initial charges and usage scenarios; quantify uncertainty and explain rapid-drain drivers.
3. Test sensitivity to assumptions, parameters, and fluctuating use.
4. Recommend user and operating-system power-saving actions; discuss aging and transfer to other devices.
5. Deliver equations, assumptions, parameter estimation, validation, limitations, extensions, and an executive-style summary in an English PDF of at most 25 pages.

## Structured intake

| Item | Extraction |
|---|---|
| Given data | No attached dataset. Lithium-ion chemistry and named load classes are given qualitatively. |
| External data | Open-licensed battery capacity, voltage, device-component power, temperature, and aging measurements/specifications. |
| Task components | Mechanism modeling, ODE, parameter estimation, scenario simulation, uncertainty, recommendations. |
| Subquestion DAG | Q1 continuous model → Q2 time-to-empty → Q3 sensitivity → Q4 recommendations. |
| Decision variables | User/OS settings: brightness, duty cycles, network mode, GPS/background activity. |
| Output variables | SOC (%), time-to-empty (h), component energy shares (%), uncertainty intervals. |
| Key constraints | Continuous-time physical model; SOC bounds; nonnegative load; explicit physical reasoning; open and documented data. |
| Data scale | Not supplied; depends on external test traces/specifications. |
| Most dangerous assumption | Treating component draws as additive and independent of voltage, temperature, and battery state. |
| Largest execution risk | Obtaining an open validation trace with compatible units and realistic usage labels. |
| Largest paper risk | Presenting a fitted discharge curve as a mechanism despite the explicit prohibition. |
| Expected figures | SOC trajectories, component contribution, observed-vs-predicted time-to-empty, sensitivity/tornado, failure envelope. |
| Solver/packages | SciPy ODE/integration and optimization; pandas/numpy/matplotlib. |
| Simplest baseline | Constant-power Coulomb/energy-counting ODE with scenario-fixed load. |

Baseline route: constant total power and effective capacity. Candidate families: load-state ODE;
temperature/aging-adjusted equivalent-circuit energy model; stochastic usage-state hybrid model.
