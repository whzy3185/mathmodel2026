# Example: Forecast-to-Optimization Route

## Claim

Choose next-week order quantities that control stockout risk without excessive waste. Demand is daily, seasonal, promotion-sensitive and ordered in time.

## Baseline

Seasonal-naive forecast plus a transparent safety-stock rule. It is executable, interpretable and hard to beat on short seasonal histories.

## Candidate tournament

1. SARIMA/ETS: primary candidate if seasonality and residual diagnostics are stable.
2. Gradient-boosted trees: candidate only when lags, calendar and known-future promotion features provide enough examples; preprocessing stays inside rolling folds.
3. LSTM: reject unless many comparable series and a learning curve justify capacity.

The primary is the lowest rolling-origin decision loss, not the lowest training RMSE. The fallback is the seasonal-naive rule. Refutation evidence includes residual dependence, interval undercoverage, unstable promotion effects and worse inventory regret than baseline.

## Validation

Backtest several forecast origins; report error by horizon, interval coverage, waste and stockout cost. Propagate forecast samples into the inventory decision and stress promotion magnitude. The final figure must connect forecast uncertainty to order-quantity or regret, not merely show a decorative fitted curve.

