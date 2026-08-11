#!/usr/bin/env python3
"""Create a recoverable modeling workspace without overwriting user files."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


DIRS = ("state", "data", "src", "results", "figures", "paper_workspace", "paper_output", "support_materials")


def initialize(root: Path, competition: str) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    for name in DIRS:
        (root / name).mkdir(exist_ok=True)
    state = root / "state" / "decision_log.json"
    if state.exists():
        return state
    payload = {
        "schema_version": 1,
        "competition": competition,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "current_stage": "rules-and-intake",
        "official_rules_checked_at": None,
        "problem_id": None,
        "decisions": [],
        "assumptions": [],
        "parameters": [],
        "artifacts": [],
        "open_risks": [],
        "ai_usage": []
    }
    state.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--competition", required=True)
    args = parser.parse_args()
    print(initialize(args.workspace.resolve(), args.competition))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

