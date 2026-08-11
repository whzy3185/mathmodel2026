# A 题候选模型审批请求

模型执行前，请人类队员阅读四份 JSON，并将对应哈希原样填入各文件的 `team_approval.plan_hash`，同时填写：

```json
{
  "approved": true,
  "approver": "人类队员姓名或稳定代号",
  "approved_at": "带时区的 ISO-8601 时间，例如 2026-08-11T18:30:00+08:00",
  "plan_hash": "下表对应哈希"
}
```

| 方案 | 文件 | 当前内容哈希 |
|---|---|---|
| Q1 | `Q1.json` | `28c8965b18dbec1f6e7ea3a04d84a40c7e09a6ea61c0e3b680ae91a2d8c65249` |
| Q2 | `Q2.json` | `183ac1caa707c6a6c676f4870f333edebf4cd154f15157113f5e8db4cb073f3f` |
| Q3 | `Q3.json` | `cab4a03c25e6ab7b741c96c1d99a53bf07ca851803fee8bdc737c88ef9e6527a` |
| Q4 | `Q4.json` | `c0e0d78c130b68ae3e90aa4cc6378b8afda6e869b678a2a8610fd78afb33769e` |

推荐由人类审批人直接运行交互脚本（Codex 不得代为输入）：

```powershell
python human_approve_plans.py
```

也可以手工填写。审批后逐份运行：

```powershell
python mathmodel/math-modeling-competition/scripts/check_plan.py mathmodel/runs/huashubei-2024-final-001/problem/tournaments/Q1.json
```

四份均显示 `PASS` 后才允许执行模型。任何候选内容变化都会使哈希失效并要求重新审批。

