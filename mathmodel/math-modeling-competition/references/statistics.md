# Statistics and Inference Cookbook

Define the estimand and data-generating unit before selecting a test or model.

| Method | Use | Do not use | Key assumptions/formulation | Validation/alternative |
|---|---|---|---|---|
| Linear regression | conditional mean, interpretable effects | nonlinear/heteroskedastic structure ignored | y=Xβ+ε | residuals, influence, intervals; robust/GAM |
| GLM | non-Gaussian exponential-family outcome | arbitrary link/distribution | g(Ey)=Xβ | deviance/calibration; nonparametric |
| Logistic | binary probability | rare separation/unmodeled dependence | logit(p)=Xβ | calibration, ROC/PR, separation; penalized |
| Mixed effects | clustered/repeated data | clusters too few/ignored | fixed + random effects | ICC/residuals; cluster-robust/GEE |
| Survival | censored time-to-event | censoring informative/unchecked | hazard/survival models | PH check/calibration; AFT |
| Hypothesis tests | prespecified contrast | fishing/multiple unplanned tests | null distribution/error control | effect size/CI/multiplicity; bootstrap |
| Bootstrap | sampling uncertainty | dependent data resampled naively | empirical resampling | block/cluster bootstrap; analytic CI |
| Bayesian | prior knowledge/full uncertainty | prior hidden or weak identification | posterior ∝ likelihood × prior | prior/posterior predictive, R-hat/ESS; frequentist |
| Monte Carlo | propagate uncertainty/integrate | too few/cherry-picked draws | sample from stated distribution | convergence/MC error; quadrature |
| MCMC | complex posterior | diagnostics absent | Markov chain target posterior | R-hat, ESS, divergences, SBC; simpler model |

Missingness, sampling frame, clustering, censoring, multiplicity, measurement error and selection are modeling decisions. Report effect sizes and uncertainty rather than p-values alone. Association is not causation; causal claims require a defensible identification design and sensitivity to unmeasured confounding.

