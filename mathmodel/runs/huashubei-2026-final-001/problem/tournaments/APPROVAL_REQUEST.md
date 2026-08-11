# 2026 A 题候选模型审批请求

模型执行前，请人类团队成员完整阅读 `Q1.json` 至 `Q4.json`。本次口头“审批通过”发生在这些新计划和哈希生成之前，因此不能替代对下列不可变内容的签署。

| 方案 | 当前内容 SHA-256 |
|---|---|
| Q1 | `575a0a8a5eb22696582726936b9d24dd7255d1464b49c008aae4daa6733d37d9` |
| Q2 | `a9bae499256fa7f678a6ac5f98fa8377ce41801b29bf67ffe026fa8e0dbf10c3` |
| Q3 | `2531e711aaa2a83950878fcc144d780813349ecf14f55bdf1f123e73ec4f4f4d` |
| Q4 | `a20b8c7f2c7d0e94b67809aec9aea6c4c9dbfe2b4ee8e677e29b6252fa41d9af` |

推荐由审批人进入本目录并直接运行交互脚本（Codex 不得代为输入）：

```powershell
python human_approve_plans.py
```

脚本会再次显示实时哈希，要求审批人输入姓名或稳定代号，并键入精确确认短语。审批后应逐份运行：

```powershell
python ..\..\..\..\math-modeling-competition\scripts\check_plan.py Q1.json
python ..\..\..\..\math-modeling-competition\scripts\check_plan.py Q2.json
python ..\..\..\..\math-modeling-competition\scripts\check_plan.py Q3.json
python ..\..\..\..\math-modeling-competition\scripts\check_plan.py Q4.json
```

四份均显示 `PASS` 后才允许执行任何 Q1–Q4 数值模型。计划内容一旦修改，旧审批会自动因哈希不匹配而失效。
