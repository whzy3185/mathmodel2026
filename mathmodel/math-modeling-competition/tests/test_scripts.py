from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_plan import validate  # noqa: E402
from init_workspace import initialize  # noqa: E402


class WorkspaceTests(unittest.TestCase):
    def test_initialize_is_non_destructive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = initialize(root, "cumcm")
            first = state.read_text(encoding="utf-8")
            state.write_text(first.replace('"decisions": []', '"decisions": ["keep"]'), encoding="utf-8")
            initialize(root, "mcm")
            self.assertIn('"keep"', state.read_text(encoding="utf-8"))

    def test_incomplete_plan_fails(self) -> None:
        self.assertTrue(validate({}))

    def test_complete_plan_passes(self) -> None:
        candidate = {
            "name": "A", "data_gate": "pass", "complexity_gate": "pass",
            "identifiability_gate": "pass", "engineering_gate": "pass",
            "validation_plan": ["holdout"], "refutation_evidence": ["residual drift"],
            "decision": "primary", "decision_reason": "beats baseline"
        }
        fallback = dict(candidate, name="B", decision="fallback", decision_reason="simpler")
        plan = {
            "problem_id": "demo", "subquestion": "Q1", "target_claim": "forecast",
            "baseline": {"name": "naive"}, "candidates": [candidate, fallback],
            "primary_model": "A", "fallback_model": "B", "stop_conditions": ["deadline"],
            "team_approval": True
        }
        self.assertEqual([], validate(plan))


if __name__ == "__main__":
    unittest.main()

