# 2024 华数杯真题闭环实验

本运行使用用户指定的三道题；经官方来源核验，它们属于 2024 第五届华数杯。官方赛题、规范化附件、数据审计、三题筛选、国赛成熟论文方法卡和 A 题候选模型均已落盘。

## 当前状态

- 已完成：官方来源与格式核验、A/B/C 数据审计、选 A、训练语料方法蒸馏、Q1–Q4 候选赛选。
- 当前门禁：`problem/tournaments/APPROVAL_REQUEST.md` 中的人类哈希审批。
- 审批通过后：执行 A 题 Q1–Q4、稳健性分析、图表、中文论文和支撑材料。

## 复现审计

```powershell
python src/common/audit_inputs.py .
```

输出为 `data/eda_summary.json` 和 `data/eda_report.md`。原始输入不被修改。

## 目录约定

- `input/`：官方赛题 PDF 与原始 ZIP；
- `data/raw/`：规范化只读附件；
- `problem/`：审题、依赖关系和候选模型；
- `training/`：国赛成熟论文来源清单与原创方法卡；
- `results/`、`figures/`、`paper/`：审批后生成的机器结果和论文资产。

