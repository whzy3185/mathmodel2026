from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

import networkx as nx
import numpy as np
from sklearn.linear_model import LinearRegression

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "templates" / "code"))

from graph_robustness import compare_failure_modes  # noqa: E402
from monte_carlo import run_monte_carlo  # noqa: E402
from ode_utils import conservation_check, positivity_check, solve_ode  # noqa: E402
from optimization_utils import check_constraints, normalize_solver_status, recompute_objective  # noqa: E402
from result_io import make_result, write_result  # noqa: E402
from rolling_forecast import rolling_origin_evaluate, seasonal_naive  # noqa: E402
from tabular_pipeline import evaluate_regressor, split_indices  # noqa: E402


class ExecutionTemplateTests(unittest.TestCase):
    def test_rolling_forecast_is_ordered(self) -> None:
        series = np.tile([2.0, 4.0, 6.0, 8.0], 6)
        result = rolling_origin_evaluate(
            series,
            lambda history, horizon: seasonal_naive(history, horizon, 4),
            min_train=8,
            horizon=2,
            metric="rmse",
        )
        self.assertEqual(0.0, result["score"])
        self.assertTrue(all(f["train_end_exclusive"] == f["test_start"] for f in result["folds"]))

    def test_tabular_pipeline_and_split_strategies(self) -> None:
        X = np.arange(80, dtype=float).reshape(40, 2)
        y = 3 * X[:, 0] - 2 * X[:, 1]
        result = evaluate_regressor(X, y, LinearRegression(), strategy="time", test_size=0.25)
        self.assertLess(result["metrics"]["rmse"], 1e-8)
        self.assertLess(max(result["train_indices"]), min(result["test_indices"]))
        groups = np.repeat(np.arange(10), 4)
        train, test = split_indices(40, strategy="group", groups=groups)
        self.assertFalse(set(groups[train]) & set(groups[test]))
        train, test = split_indices(40, strategy="train_test")
        self.assertEqual(40, len(train) + len(test))

    def test_optimization_integrity(self) -> None:
        self.assertEqual("optimal", normalize_solver_status("OPTIMAL"))
        self.assertEqual(5.0, recompute_objective([1, 2], [1, 2]))
        check = check_constraints([[1, 1], [1, 0]], [3, 0], ["<=", ">="], [1, 2])
        self.assertTrue(check["feasible"])

    def test_ode_physical_checks(self) -> None:
        def exchange(_time, state, params):
            rate = params["rate"]
            return [-rate * state[0], rate * state[0]]

        result = solve_ode(exchange, (0, 4), [1, 0], parameters={"rate": 0.5}, evaluation_times=np.linspace(0, 4, 20))
        self.assertEqual("ok", result["status"])
        self.assertTrue(positivity_check(result["state"])["passed"])
        self.assertTrue(conservation_check(result["state"])["passed"])

    def test_monte_carlo_records_seed_ci_and_convergence(self) -> None:
        result = run_monte_carlo(lambda rng: float(rng.normal()), replications=1000, seed=17)
        self.assertEqual(17, result["seed"])
        self.assertEqual(1000, result["replications"])
        self.assertLess(result["confidence_interval"][0], result["confidence_interval"][1])
        self.assertEqual(10, len(result["convergence"]["running_means"]))

    def test_graph_targeted_failure_is_measured(self) -> None:
        graph = nx.star_graph(9)
        result = compare_failure_modes(graph, [0.0, 0.1, 0.3], seed=4)
        random_lcc = result["random"]["trajectory"][1]["largest_component_fraction"]
        targeted_lcc = result["targeted"]["trajectory"][1]["largest_component_fraction"]
        self.assertLessEqual(targeted_lcc, random_lcc)

    def test_result_io_hashes_data(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data.csv"
            data.write_text("x,y\n1,2\n", encoding="utf-8")
            result = make_result(
                model="linear", version="1.0", status="ok", metrics={"rmse": 0.1},
                data_path=data, seed=9, artifact_id="RESULT-001"
            )
            output = write_result(root / "result.json", result)
            loaded = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(64, len(loaded["data"]["sha256"]))
            self.assertEqual("RESULT-001", loaded["artifact_id"])


if __name__ == "__main__":
    unittest.main()
