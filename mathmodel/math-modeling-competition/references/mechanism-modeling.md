# Mechanism Modeling Cookbook

Start with a system boundary, state variables, units, conservation relations, characteristic scales and a minimal viable model.

| Method | Use | Do not use | Formulation/assumptions | Validation/alternative |
|---|---|---|---|---|
| ODE | lumped continuous dynamics | spatial gradients dominate | dx/dt=f(x,u,θ) | units, limits, trajectory holdout; difference equation |
| PDE | spatial transport/diffusion/waves | data/compute cannot identify field | ∂u/∂t=L(u)+sources | mesh/time convergence, BC sensitivity; compartment ODE |
| Difference equation | discrete periods/events | step-size artifact ignored | x_{t+1}=F(x_t,u_t) | stability and step sensitivity; ODE |
| SIR/SEIR/compartment | transfers among states | homogeneous mixing unrealistic | mass-balanced transition rates | conservation, identifiability, held-out waves; network/ABM |
| Predator–prey | coupled interaction dynamics | mechanism unsupported | Lotka–Volterra variants | equilibria/phase portrait/data; empirical state model |
| System dynamics | feedback and stocks/flows | causal loops without calibrated equations | stock-flow equations/delays | extreme-condition tests, scenario sensitivity |

Estimate parameters with bounds and sources; separate calibration from validation. Use profile likelihood, Fisher information or posterior diagnostics to detect weak identification. Check positivity, conservation, equilibria, stability, limiting cases, initial/boundary conditions, stiffness, discretization and out-of-regime extrapolation.

