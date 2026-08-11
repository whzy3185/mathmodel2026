"""Leakage-safe rolling-origin evaluation and seasonal-naive forecasts."""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from typing import Any

import numpy as np


def seasonal_naive(history: Sequence[float], horizon: int, season_length: int = 1) -> np.ndarray:
    values = np.asarray(history, dtype=float)
    if horizon < 1 or season_length < 1 or len(values) < season_length:
        raise ValueError("horizon and season_length must be positive and history must contain one season")
    season = values[-season_length:]
    return np.resize(season, horizon)


def error_metric(actual: Sequence[float], predicted: Sequence[float], metric: str = "rmse") -> float:
    y = np.asarray(actual, dtype=float)
    yhat = np.asarray(predicted, dtype=float)
    if y.shape != yhat.shape or y.size == 0:
        raise ValueError("actual and predicted must have the same non-empty shape")
    errors = y - yhat
    metric = metric.lower()
    if metric == "rmse":
        return float(math.sqrt(np.mean(errors**2)))
    if metric == "mae":
        return float(np.mean(np.abs(errors)))
    if metric == "mape":
        nonzero = np.abs(y) > np.finfo(float).eps
        if not np.any(nonzero):
            raise ValueError("MAPE is undefined when every actual value is zero")
        return float(100.0 * np.mean(np.abs(errors[nonzero] / y[nonzero])))
    raise ValueError("metric must be rmse, mae, or mape")


def rolling_origin_evaluate(
    series: Sequence[float],
    forecaster: Callable[[Sequence[float], int], Sequence[float]],
    *,
    min_train: int,
    horizon: int = 1,
    step: int = 1,
    metric: str = "rmse",
) -> dict[str, Any]:
    values = np.asarray(series, dtype=float)
    if min_train < 1 or horizon < 1 or step < 1 or min_train + horizon > len(values):
        raise ValueError("invalid rolling-origin bounds")
    folds: list[dict[str, Any]] = []
    all_actual: list[float] = []
    all_predicted: list[float] = []
    for origin in range(min_train, len(values) - horizon + 1, step):
        history = values[:origin].copy()
        actual = values[origin : origin + horizon]
        predicted = np.asarray(forecaster(history, horizon), dtype=float)
        if predicted.shape != actual.shape:
            raise ValueError("forecaster returned the wrong horizon")
        folds.append(
            {
                "train_end_exclusive": origin,
                "test_start": origin,
                "test_end_exclusive": origin + horizon,
                "score": error_metric(actual, predicted, metric),
            }
        )
        all_actual.extend(actual.tolist())
        all_predicted.extend(predicted.tolist())
    return {
        "status": "ok",
        "metric": metric.lower(),
        "score": error_metric(all_actual, all_predicted, metric),
        "fold_count": len(folds),
        "folds": folds,
        "actual": all_actual,
        "predicted": all_predicted,
    }
