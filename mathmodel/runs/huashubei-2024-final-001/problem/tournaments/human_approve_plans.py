#!/usr/bin/env python3
"""Interactive human-only approval helper for Q1-Q4 tournaments.

This script must be run by the human reviewer. It prints each immutable plan
hash and requires an explicit confirmation before writing approval metadata.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path


HERE = Path(__file__).resolve().parent
CHECK_PLAN_DIR = HERE.parents[3] / "math-modeling-competition" / "scripts"
sys.path.insert(0, str(CHECK_PLAN_DIR))

from check_plan import compute_plan_hash, validate  # noqa: E402


def main() -> int:
    plans: list[tuple[Path, dict, str]] = []
    print("请先完整阅读 Q1.json 至 Q4.json。当前不可变内容哈希：")
    for name in ("Q1", "Q2", "Q3", "Q4"):
        path = HERE / f"{name}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        digest = compute_plan_hash(data)
        plans.append((path, data, digest))
        print(f"  {name}: {digest}")

    approver = input("人类审批人姓名或稳定代号：").strip()
    if not approver:
        print("未填写审批人，未修改任何文件。")
        return 2
    confirmation = input("若已审阅并批准四份方案，请键入 APPROVE Q1-Q4：").strip()
    if confirmation != "APPROVE Q1-Q4":
        print("确认短语不匹配，未修改任何文件。")
        return 3

    approved_at = datetime.now().astimezone().isoformat(timespec="seconds")
    for path, data, digest in plans:
        data["team_approval"] = {
            "approved": True,
            "approver": approver,
            "approved_at": approved_at,
            "plan_hash": digest,
        }
        errors = validate(data)
        if errors:
            print(f"{path.name} 校验失败：")
            for error in errors:
                print(f"- {error}")
            return 4
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"PASS {path.name}")
    print("四份方案已由人类审批并通过哈希校验。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

