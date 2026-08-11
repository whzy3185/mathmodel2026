"""Reproducible Monte Carlo summaries with confidence and convergence diagnostics."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
from scipy import stats


def run_monte_carlo(
    simulator: Callable[[np.random.Generator], float],
    *,
    replications: int,
    seed: int,
    confidence: float = 0.95,
    batches: int = 10,
) -> dict[str, Any]:
    if replications < 2 or not 0 < confidence < 1 or batches < 2:
        raise ValueError("invalid Monte Carlo configuration")
    rng = np.random.default_rng(seed)
    samples = np.asarray([simulator(rng) for _ in range(replications)], dtype=float)
    if not np.all(np.isfinite(samples)):
        raise ValueError("simulator returned a non-finite value")
    mean = float(np.mean(samples))
    std = float(np.std(samples, ddof=1))
    critical = float(stats.t.ppf((1.0 + confidence) / 2.0, replications - 1))
    half_width = critical * std / np.sqrt(replications)
    boundaries = np.linspace(max(2, replications // batches), replications, batches, dtype=int)
    running_means = [float(np.mean(samples[:end])) for end in boundaries]
    final_scale = max(abs(mean), np.finfo(float).eps)
    tail_change = abs(running_means[-1] - running_means[-2]) / final_scale
    return {
        "status": "ok",
        "seed": seed,
        "replications": replications,
        "mean": mean,
        "standard_deviation": std,
        "confidence": confidence,
        "confidence_interval": [mean - half_width, mean + half_width],
        "convergence": {
            "sample_sizes": boundaries.tolist(),
            "running_means": running_means,
            "relative_tail_change": float(tail_change),
        },
    }
