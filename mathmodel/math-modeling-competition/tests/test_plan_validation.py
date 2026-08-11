from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_plan import compute_plan_hash, validate  # noqa: E402


def valid_plan() -> dict:
    common = {
        "formulation": "y = f(x; theta)",
        "assumptions": ["measurement process is stable"],
        "parameter_sources": ["training fold only"],
        "assumption_gate": "pass",
        "data_gate": "pass",
        "complexity_gate": "pass",
        "identifiability_gate": "pass",
        "engineering_gate": "pass",
        "validation_gate": "pass",
        "validation_plan": ["rolling holdout"],
        "refutation_evidence": ["worse holdout loss than baseline"],
        "expected_failure_modes": ["distribution shift"],
        "rejection_evidence": [],
    }
    primary = dict(common, name="Model A", decision="primary", decision_reason="best holdout loss")
    fallback = dict(common, name="Model B", decision="fallback", decision_reason="lower complexity")
    plan = {
        "problem_id": "demo",
        "subquestion": "Q1",
        "target_claim": "forecast error",
        "baseline": {
            "name": "seasonal naive",
            "reason": "transparent reference",
            "implementation": "baseline.py",
            "validation": "rolling origin MAE",
        },
        "candidates": [primary, fallback],
        "primary_model": "Model A",
        "fallback_model": "Model B",
        "stop_conditions": ["validation gate fails"],
        "team_approval": {
            "approved": True,
            "approver": "Team Member 1",
            "approved_at": "2026-08-11T10:00:00+08:00",
            "plan_hash": "",
        },
    }
    plan["team_approval"]["plan_hash"] = compute_plan_hash(plan)
    return plan


class PlanValidationTests(unittest.TestCase):
    def assert_invalid(self, plan: dict, text: str) -> None:
        errors = validate(plan)
        self.assertTrue(any(text in error for error in errors), errors)

    def test_valid_plan_passes(self) -> None:
        self.assertEqual([], validate(valid_plan()))

    def test_empty_plan(self) -> None:
        self.assert_invalid({}, "non-empty object")

    def test_unknown_gate(self) -> None:
        plan = valid_plan()
        plan["candidates"][0]["data_gate"] = "unknown"
        self.assert_invalid(plan, "data_gate must be pass or fail")

    def test_failed_gate_primary(self) -> None:
        plan = valid_plan()
        plan["candidates"][0]["validation_gate"] = "fail"
        self.assert_invalid(plan, "primary has non-passing gates")

    def test_multiple_primary(self) -> None:
        plan = valid_plan()
        plan["candidates"][1]["decision"] = "primary"
        self.assert_invalid(plan, "exactly one candidate must be primary")

    def test_missing_fallback(self) -> None:
        plan = valid_plan()
        plan["candidates"][1]["decision"] = "rejected"
        plan["candidates"][1]["rejection_evidence"] = ["fails accuracy threshold"]
        self.assert_invalid(plan, "exactly one candidate must be fallback")

    def test_primary_name_mismatch(self) -> None:
        plan = valid_plan()
        plan["primary_model"] = "wrong"
        self.assert_invalid(plan, "primary_model does not match")

    def test_fallback_name_mismatch(self) -> None:
        plan = valid_plan()
        plan["fallback_model"] = "wrong"
        self.assert_invalid(plan, "fallback_model does not match")

    def test_empty_validation(self) -> None:
        plan = valid_plan()
        plan["candidates"][0]["validation_plan"] = []
        self.assert_invalid(plan, "primary validation_plan is empty")

    def test_empty_refutation(self) -> None:
        plan = valid_plan()
        plan["candidates"][0]["refutation_evidence"] = []
        self.assert_invalid(plan, "primary refutation_evidence is empty")

    def test_malformed_baseline(self) -> None:
        plan = valid_plan()
        del plan["baseline"]["implementation"]
        self.assert_invalid(plan, "baseline.implementation is empty")

    def test_rejected_candidate_requires_evidence(self) -> None:
        plan = valid_plan()
        rejected = copy.deepcopy(plan["candidates"][1])
        rejected.update(name="Model C", decision="rejected", rejection_evidence=[])
        plan["candidates"].append(rejected)
        self.assert_invalid(plan, "requires rejection_evidence")

    def test_stale_approval_hash(self) -> None:
        plan = valid_plan()
        plan["target_claim"] = "changed after approval"
        self.assert_invalid(plan, "plan_hash is stale")

    def test_ai_cannot_approve(self) -> None:
        plan = valid_plan()
        plan["team_approval"]["approver"] = "Codex"
        plan["team_approval"]["plan_hash"] = compute_plan_hash(plan)
        self.assert_invalid(plan, "authorizing user or human team member")

    def test_explicit_user_message_approval_passes(self) -> None:
        plan = valid_plan()
        plan["team_approval"].update(
            method="user_message",
            authorization_text="继续",
            approver="Repository owner",
        )
        plan["team_approval"]["plan_hash"] = compute_plan_hash(plan)
        self.assertEqual([], validate(plan))

    def test_unsupported_user_message_fails(self) -> None:
        plan = valid_plan()
        plan["team_approval"].update(
            method="user_message",
            authorization_text="maybe later",
            approver="Repository owner",
        )
        plan["team_approval"]["plan_hash"] = compute_plan_hash(plan)
        self.assert_invalid(plan, "not an accepted explicit user authorization")


if __name__ == "__main__":
    unittest.main()
