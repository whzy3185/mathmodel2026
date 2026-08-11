# Forecasting Cookbook

For every method report: use/not-use, assumptions, data/horizon, formulation, parameters, implementation, rolling validation, sensitivity, failure, alternative, and paper presentation.

| Method | Use | Do not use | Formulation/assumptions | Validation and fallback |
|---|---|---|---|---|
| Naive/seasonal naive | mandatory baseline | never as sole long-horizon policy | last/seasonal observation; stable local level | rolling error; drift/ETS |
| ARIMA | autocorrelated stationary series | regime shifts, very short data | differenced ARMA; stable coefficients | ACF/residuals, rolling CV; ETS |
| SARIMA | stable known seasonality | changing/multiple seasonality | seasonal differencing and ARMA | horizon-wise backtest; ETS/TBATS-like alternative |
| ETS | level/trend/seasonality | strong exogenous drivers | exponential state updates | rolling CV and interval coverage; ARIMA |
| Prophet | calendar effects, quick robust baseline | used as automatic oracle | additive trend/season/holidays | compare naive/ETS; inspect changepoints |
| VAR | several interacting stationary series | many variables, few observations | vector autoregression | lag stability, residual tests; separate AR models |
| Grey GM(1,1) | very small monotone series as baseline | oscillatory/seasonal or long extrapolation | accumulated series and first-order grey ODE | posterior error, rolling check; regression/ETS |
| Regression/RF/XGBoost/LightGBM/SVR | exogenous features and nonlinear mapping | leakage-prone lag construction, weak sample | supervised f(X); preserve forecast availability | time split, pipeline, SHAP/permutation stability; regularized linear |
| LSTM/Transformer | long, multi-series data with justified capacity | one short contest series | learned sequence mapping; heavy regularization | multiple seeds, rolling test, ablation; boosted tree/ETS |
| Time-series foundation model | cold-start/zero-shot benchmark across many series | domain shift or unverifiable black box | pretrained probabilistic/point forecaster | compare local baseline, calibrate intervals; ETS/ARIMA |

Always define forecast origin, horizon, available covariates, update cadence, loss tied to the decision, and uncertainty propagation. Fit scalers/imputers only on past training windows. Report error by horizon and regime, residual dependence, coverage, and why added complexity beats seasonal naive.

