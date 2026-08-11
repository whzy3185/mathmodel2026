#!/usr/bin/env python3
"""Fail closed on incomplete candidate-model tournaments."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


GATES = ("data_gate", "complexity_gate", "identifiability_gate", "engineering_gate")


def validate(plan: dict) -> list[str]:
    errors: list[str] = []
    for key in ("problem_id", "subquestion", "target_claim", "baseline", "candidates", "primary_model", "fallback_model"):
        if not plan.get(key):
            errors.append(f"missing or empty: {key}")
    candidates = plan.get("candidates", [])
    if len(candidates) < 2:
        errors.append("at least two candidates are required")
    decisions = []
    for index, candidate in enumerate(candidates):
        label = f"candidate[{index}]"
        if not candidate.get("name"):
            errors.append(f"{label}: missing name")
        for gate in GATES:
            if candidate.get(gate) not in {"pass", "fail"}:
                errors.append(f"{label}: {gate} must be pass or fail")
        if not candidate.get("validation_plan"):
            errors.append(f"{label}: validation_plan is empty")
        if not candidate.get("refutation_evidence"):
            errors.append(f"{label}: refutation_evidence is empty")
        decision = candidate.get("decision")
        decisions.append(decision)
        if decision not in {"primary", "fallback", "reject"}:
            errors.append(f"{label}: invalid decision")
        if not candidate.get("decision_reason"):
            errors.append(f"{label}: decision_reason is empty")
    if decisions.count("primary") != 1:
        errors.append("exactly one candidate must be primary")
    if "fallback" not in decisions:
        errors.append("at least one candidate must be fallback")
    if not plan.get("stop_conditions"):
        errors.append("stop_conditions is empty")
    if plan.get("team_approval") is not True:
        errors.append("team_approval must be true before execution")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()
    data = json.loads(args.plan.read_text(encoding="utf-8"))
    errors = validate(data)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

