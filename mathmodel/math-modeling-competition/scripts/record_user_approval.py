#!/usr/bin/env python3
# AI assistance disclosure: drafted with OpenAI Codex and covered by skill tests.
"""Record an explicit repository-owner chat authorization on model plans."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from check_plan import USER_MESSAGE_AUTHORIZATIONS, compute_plan_hash, validate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("plans", nargs="+", type=Path)
    parser.add_argument("--approver", required=True)
    parser.add_argument("--authorization", required=True)
    parser.add_argument("--reason", default="initial run-scoped user authorization")
    args = parser.parse_args()

    authorization = args.authorization.strip()
    if authorization.lower() not in USER_MESSAGE_AUTHORIZATIONS:
        print("FAIL")
        print("- authorization must be one of: 继续, approve, 批准, 同意执行")
        return 2
    if not args.approver.strip():
        print("FAIL")
        print("- approver is empty")
        return 2

    approved_at = datetime.now().astimezone().isoformat(timespec="seconds")
    staged: list[tuple[Path, dict]] = []
    for path in args.plans:
        data = json.loads(path.read_text(encoding="utf-8"))
        data["team_approval"] = {
            "approved": True,
            "approver": args.approver.strip(),
            "approved_at": approved_at,
            "plan_hash": compute_plan_hash(data),
            "method": "user_message",
            "authorization_text": authorization,
            "record_reason": args.reason,
        }
        errors = validate(data)
        if errors:
            print(f"FAIL {path}")
            for error in errors:
                print(f"- {error}")
            return 3
        staged.append((path, data))

    for path, data in staged:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"PASS {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
