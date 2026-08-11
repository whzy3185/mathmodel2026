#!/usr/bin/env python3
"""Fail closed on incomplete or unapproved candidate-model tournaments."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any


GATES = (
    "assumption_gate",
    "data_gate",
    "complexity_gate",
    "identifiability_gate",
    "engineering_gate",
    "validation_gate",
)
DECISIONS = {"primary", "fallback", "rejected"}
NON_HUMAN_APPROVERS = {"codex", "openai", "chatgpt", "ai", "ai assistant", "llm"}


def _nonempty(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return value is not None


def approval_payload(plan: dict[str, Any]) -> dict[str, Any]:
    """Return the immutable content that a human approval signs."""
    payload = copy.deepcopy(plan)
    payload.pop("team_approval", None)
    return payload


def compute_plan_hash(plan: dict[str, Any]) -> str:
    canonical = json.dumps(
        approval_payload(plan), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _valid_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def validate(plan: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(plan, dict) or not plan:
        return ["plan must be a non-empty object"]

    for key in (
        "problem_id",
        "subquestion",
        "target_claim",
        "baseline",
        "candidates",
        "primary_model",
        "fallback_model",
        "stop_conditions",
        "team_approval",
    ):
        if not _nonempty(plan.get(key)):
            errors.append(f"missing or empty: {key}")

    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        errors.append("baseline must be an object")
    else:
        for field in ("name", "reason", "implementation", "validation"):
            if not _nonempty(baseline.get(field)):
                errors.append(f"baseline.{field} is empty")

    candidates = plan.get("candidates")
    if not isinstance(candidates, list):
        errors.append("candidates must be an array")
        candidates = []
    if len(candidates) < 2:
        errors.append("at least two candidates are required")

    names: list[str] = []
    decisions: list[str] = []
    for index, candidate in enumerate(candidates):
        label = f"candidate[{index}]"
        if not isinstance(candidate, dict):
            errors.append(f"{label}: must be an object")
            continue

        name = candidate.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{label}: missing name")
        else:
            names.append(name)

        for field in (
            "formulation",
            "assumptions",
            "parameter_sources",
            "validation_plan",
            "refutation_evidence",
            "expected_failure_modes",
            "decision",
            "decision_reason",
        ):
            if field not in candidate:
                errors.append(f"{label}: missing {field}")

        for gate in GATES:
            if candidate.get(gate) not in {"pass", "fail"}:
                errors.append(f"{label}: {gate} must be pass or fail")

        decision = candidate.get("decision")
        decisions.append(decision)
        if decision not in DECISIONS:
            errors.append(f"{label}: decision must be primary, fallback, or rejected")
        if not _nonempty(candidate.get("decision_reason")):
            errors.append(f"{label}: decision_reason is empty")

        if decision == "primary":
            failed = [gate for gate in GATES if candidate.get(gate) != "pass"]
            if failed:
                errors.append(f"{label}: primary has non-passing gates: {', '.join(failed)}")
            for field in ("formulation", "validation_plan", "refutation_evidence"):
                if not _nonempty(candidate.get(field)):
                    errors.append(f"{label}: primary {field} is empty")

        if decision == "rejected" and not _nonempty(candidate.get("rejection_evidence")):
            errors.append(f"{label}: rejected candidate requires rejection_evidence")

    if len(names) != len(set(names)):
        errors.append("candidate names must be unique")
    if decisions.count("primary") != 1:
        errors.append("exactly one candidate must be primary")
    if decisions.count("fallback") != 1:
        errors.append("exactly one candidate must be fallback")

    primary_names = [
        candidate.get("name") for candidate in candidates
        if isinstance(candidate, dict) and candidate.get("decision") == "primary"
    ]
    fallback_names = [
        candidate.get("name") for candidate in candidates
        if isinstance(candidate, dict) and candidate.get("decision") == "fallback"
    ]
    if len(primary_names) == 1 and plan.get("primary_model") != primary_names[0]:
        errors.append("primary_model does not match the unique primary candidate")
    if len(fallback_names) == 1 and plan.get("fallback_model") != fallback_names[0]:
        errors.append("fallback_model does not match the unique fallback candidate")

    approval = plan.get("team_approval")
    if not isinstance(approval, dict):
        errors.append("team_approval must be an object")
    else:
        expected_fields = {"approved", "approver", "approved_at", "plan_hash"}
        missing = expected_fields - approval.keys()
        if missing:
            errors.append(f"team_approval missing fields: {sorted(missing)}")
        if approval.get("approved") is not True:
            errors.append("team_approval.approved must be true before execution")
        approver = approval.get("approver")
        if not isinstance(approver, str) or not approver.strip():
            errors.append("team_approval.approver is empty")
        elif approver.strip().lower() in NON_HUMAN_APPROVERS:
            errors.append("team_approval.approver must identify a human team member")
        if not _valid_timestamp(approval.get("approved_at")):
            errors.append("team_approval.approved_at must be an ISO-8601 timestamp with timezone")
        expected_hash = compute_plan_hash(plan)
        if approval.get("plan_hash") != expected_hash:
            errors.append("team_approval.plan_hash is stale or invalid")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=Path)
    parser.add_argument(
        "--print-hash",
        action="store_true",
        help="print the hash a human approver must copy into team_approval.plan_hash",
    )
    args = parser.parse_args()
    try:
        data = json.loads(args.plan.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print("FAIL")
        print(f"- cannot read plan: {exc}")
        return 1
    if args.print_hash:
        print(compute_plan_hash(data))
        return 0
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
