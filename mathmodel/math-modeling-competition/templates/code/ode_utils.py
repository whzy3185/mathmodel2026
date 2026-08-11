"""ODE solving plus physical consistency diagnostics."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp


def solve_ode(
    rhs: Callable,
    t_span: tuple[float, float],
    initial_state: Sequence[float],
    *,
    parameters: dict[str, Any] | None = None,
    evaluation_times: Sequence[float] | None = None,
    method: str = "RK45",
    rtol: float = 1e-7,
    atol: float = 1e-9,
) -> dict[str, Any]:
    params = parameters or {}
    solution = solve_ivp(
        lambda t, y: rhs(t, y, params),
        t_span,
        np.asarray(initial_state, dtype=float),
        t_eval=None if evaluation_times is None else np.asarray(evaluation_times, dtype=float),
        method=method,
        rtol=rtol,
        atol=atol,
    )
    return {
        "status": "ok" if solution.success else "failed",
        "message": solution.message,
        "time": solution.t.tolist(),
        "state": solution.y.tolist(),
        "nfev": solution.nfev,
    }


def positivity_check(state: Sequence[Sequence[float]], tolerance: float = 1e-9) -> dict[str, Any]:
    values = np.asarray(state, dtype=float)
    minimum = float(np.min(values))
    return {"passed": minimum >= -tolerance, "minimum": minimum, "tolerance": tolerance}


def conservation_check(
    state: Sequence[Sequence[float]],
    weights: Sequence[float] | None = None,
    *,
    tolerance: float = 1e-6,
) -> dict[str, Any]:
    values = np.asarray(state, dtype=float)
    if values.ndim != 2:
        raise ValueError("state must have shape variables by time")
    w = np.ones(values.shape[0]) if weights is None else np.asarray(weights, dtype=float)
    if w.size != values.shape[0]:
        raise ValueError("one conservation weight is required per state variable")
    total = w @ values
    scale = max(1.0, abs(float(total[0])))
    maximum = float(np.max(np.abs(total - total[0])) / scale)
    return {"passed": maximum <= tolerance, "relative_drift": maximum, "tolerance": tolerance}
