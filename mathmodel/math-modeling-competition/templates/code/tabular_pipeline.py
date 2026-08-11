"""Tabular evaluation with preprocessing fitted inside each training split."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.base import BaseEstimator, clone
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import GroupShuffleSplit, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def split_indices(
    n_samples: int,
    *,
    strategy: str = "train_test",
    test_size: float = 0.2,
    groups: np.ndarray | None = None,
    random_state: int = 0,
) -> tuple[np.ndarray, np.ndarray]:
    indices = np.arange(n_samples)
    if not 0 < test_size < 1:
        raise ValueError("test_size must be between zero and one")
    if strategy == "train_test":
        train, test = train_test_split(indices, test_size=test_size, random_state=random_state)
    elif strategy == "group":
        if groups is None or len(groups) != n_samples:
            raise ValueError("group split requires one group label per row")
        train, test = next(
            GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=random_state).split(
                indices, groups=groups
            )
        )
    elif strategy == "time":
        cutoff = int(np.floor(n_samples * (1.0 - test_size)))
        if cutoff < 1 or cutoff >= n_samples:
            raise ValueError("time split produces an empty partition")
        train, test = indices[:cutoff], indices[cutoff:]
    else:
        raise ValueError("strategy must be train_test, group, or time")
    return np.asarray(train), np.asarray(test)


def build_pipeline(estimator: BaseEstimator) -> Pipeline:
    return Pipeline([("scale", StandardScaler()), ("model", clone(estimator))])


def evaluate_regressor(
    X: Any,
    y: Any,
    estimator: BaseEstimator,
    *,
    strategy: str = "train_test",
    test_size: float = 0.2,
    groups: Any = None,
    random_state: int = 0,
) -> dict[str, Any]:
    features = np.asarray(X, dtype=float)
    target = np.asarray(y, dtype=float)
    train, test = split_indices(
        len(target),
        strategy=strategy,
        test_size=test_size,
        groups=None if groups is None else np.asarray(groups),
        random_state=random_state,
    )
    pipeline = build_pipeline(estimator)
    pipeline.fit(features[train], target[train])
    predicted = pipeline.predict(features[test])
    return {
        "status": "ok",
        "split_strategy": strategy,
        "train_indices": train.tolist(),
        "test_indices": test.tolist(),
        "metrics": {
            "rmse": float(np.sqrt(mean_squared_error(target[test], predicted))),
            "mae": float(mean_absolute_error(target[test], predicted)),
        },
        "predicted": np.asarray(predicted).tolist(),
        "pipeline": pipeline,
    }
