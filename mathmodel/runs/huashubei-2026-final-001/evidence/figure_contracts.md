# 最终图 Figure Contracts

## F1：纯 A 粒子数—导通概率

- Figure ID: F1
- Claim supported: 8 根 A 达到 90% 要求，而 7 根明显不足。
- Why this figure is necessary: 显示整数阈值及解析充分条件与完整图模拟的一致性。
- Data and transformation: `literal_q3_final_50000.json` 的临界前缀；解析式 `1-(1-q_A)^N`。
- X axis, unit, range: A 数量，根，1–10。
- Y axis, unit, range: 导通概率，0–1。
- Encoding/legend: 解析直接跨界曲线、模拟点和 95% Wilson 区间。
- Baseline or reference line: `P=0.90`。
- Expected pattern before plotting: 单调上升，在 7 与 8 之间跨过 0.90。
- Uncertainty or variability shown: 50,000 次模拟的 Wilson 区间。
- What the reader should conclude: 8 根是模型支持的最低整数填充量。
- What the figure cannot establish: 不能消除官方“周期片段是否仍视为同一介质”的语义歧义。
- Source/provenance note: 官方题面参数；固定种子 `20260902`。

## F2：Q2 四个体积分数的失败概率

- Figure ID: F2
- Claim supported: 0.50%–1.00% 时，仅直接跨界机制已使不导通概率极小。
- Why this figure is necessary: 普通概率坐标会把四点都显示为 1，无法比较数量级。
- Data and transformation: 按四舍五入粒子数计算 `(1-q_A)^N`，取 `log10`。
- X axis, unit, range: A 体积分数，%，0.50–1.00。
- Y axis, unit, range: `log10(不导通概率)`。
- Encoding/legend: 单条直接跨界充分条件曲线/点。
- Baseline or reference line: 无；纵轴直接标注数量级。
- Expected pattern before plotting: 随填充率增加快速下降。
- Uncertainty or variability shown: 解析式，无采样误差。
- What the reader should conclude: 四个 Q2 概率在报告精度内均为 1。
- What the figure cannot establish: 不分解非直接介质网络的额外贡献。
- Source/provenance note: 官方几何尺寸与各向同性方向假设。

## F3：Q4 候选的概率—成本验证

- Figure ID: F3
- Claim supported: 57B 达到置信约束，所有成本更低的紧邻方案未通过。
- Why this figure is necessary: 同时呈现可行性边界、置信区间和成本比较。
- Data and transformation: `literal_q4_final_100000.json`；成本按官方元/μm³换算。
- X axis, unit, range: 总成本，元，覆盖候选范围。
- Y axis, unit, range: 导通概率，0.87–0.92。
- Encoding/legend: 不同候选标签；水平误差为零，垂直误差为 Wilson 区间；颜色区分可行性。
- Baseline or reference line: `P=0.90`。
- Expected pattern before plotting: 57B 与 8A 通过；更便宜候选低于阈值。
- Uncertainty or variability shown: 100,000 次独立模拟的 95% Wilson 区间。
- What the reader should conclude: 57B 是所枚举的更低成本邻域中最低的置信可行方案。
- What the figure cannot establish: 不是对无限整数域的形式化全局最优证明；结论受周期同一介质解释约束。
- Source/provenance note: 固定种子 `20260904`，官方成本参数。
