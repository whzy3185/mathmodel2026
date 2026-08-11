# Machine Learning Cookbook

ML is a candidate only when prediction or flexible approximation is decision-relevant and data support it.

| Method | Use | Do not use | Assumptions/formulation | Validation/alternative |
|---|---|---|---|---|
| Regularized linear/logistic | strong interpretable baseline | nonlinear residual structure ignored | sparse/shrunk coefficients | nested CV, calibration; GLM/GAM |
| Random forest | tabular nonlinear interactions | extrapolation/very small sample | bagged trees | grouped/time CV, permutation importance; boosted tree |
| XGBoost/LightGBM | strong tabular prediction | leakage and aggressive tuning | gradient-boosted trees | nested/time CV, calibration, SHAP stability; linear/RF |
| SVR | medium nonlinear data | huge dataset/unscaled features | kernel margin regression | pipeline scaling, tuning nested; linear/tree |
| Neural networks | large structured/multimodal data | one small table/time series | learned high-capacity mapping | seeds, learning curves, ablation; simpler model |
| Clustering | exploratory grouping with metric meaning | forced segments as truth | distance/density/mixture structure | stability, silhouette plus domain utility; continuous score |

Create a feature availability table at prediction time. Fit imputation, scaling, selection and resampling inside folds. Use group/time splits when dependence exists. Evaluate calibration, class imbalance, subgroup error, distribution shift and learning curves. Interpretability methods describe model behavior, not causal effects. Report all tuned degrees of freedom and compare a simple baseline.

