"""Solver-independent integrity checks for optimization results."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np


STATUS_MAP = {
    "optimal": "optimal",
    "opt": "optimal",
    "feasible": "feasible",
    "infeasible": "infeasible",
    "unbounded": "unbounded",
    "time_limit": "limit",
    "timelimit": "limit",
    "iteration_limit": "limit",
    "error": "error",
}


def normalize_solver_status(status: Any) -> str:
    key = str(status).strip().lower().replace(" ", "_")
    return STATUS_MAP.get(key, "unknown")


def recompute_objective(coefficients: Sequence[float], solution: Sequence[float], constant: float = 0.0) -> float:
    c = np.asarray(coefficients, dtype=float)
    x = np.asarray(solution, dtype=float)
    if c.shape != x.shape:
        raise ValueError("objective coefficients and solution shapes differ")
    return float(c @ x + constant)


def check_constraints(
    matrix: Sequence[Sequence[float]],
    rhs: Sequence[float],
    senses: Sequence[str],
    solution: Sequence[float],
    *,
    tolerance: float = 1e-8,
) -> dict[str, Any]:
    A = np.asarray(matrix, dtype=float)
    b = np.asarray(rhs, dtype=float)
    x = np.asarray(solution, dtype=float)
    if A.ndim != 2 or A.shape[1] != x.size or A.shape[0] != b.size or len(senses) != b.size:
        raise ValueError("constraint dimensions do not agree")
    lhs = A @ x
    violations: list[float] = []
    for value, bound, sense in zip(lhs, b, senses):
        if sense == "<=":
            violations.append(max(0.0, float(value - bound)))
        elif sense == ">=":
            violations.append(max(0.0, float(bound - value)))
        elif sense == "==":
            violations.append(abs(float(value - bound)))
        else:
            raise ValueError(f"unknown constraint sense: {sense}")
    maximum = max(violations, default=0.0)
    return {
        "feasible": maximum <= tolerance,
        "max_violation": maximum,
        "violations": violations,
        "lhs": lhs.tolist(),
        "tolerance": tolerance,
    }
