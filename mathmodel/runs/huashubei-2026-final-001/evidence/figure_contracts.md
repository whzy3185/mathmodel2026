# 最终图 Figure Contracts

## F1：纯 A 粒子数—导通概率

- Figure ID: F1
- Claim supported: 8 根 A 达到 90% 要求，而 7 根明显不足。
- Why this figure is necessary: 显示整数阈值及解析充分条件与完整图模拟的一致性。
- Data and transformation: `final_results.json` 的解析上下界；下界 `1-(1-q_A)^N`，上界再加 `N(N-1)(g/L)^2`。
- X axis, unit, range: A 数量，根，1–10。
- Y axis, unit, range: 导通概率，0–1。
- Encoding/legend: 严格充分下界与严格必要上界。
- Baseline or reference line: `P=0.90`。
- Expected pattern before plotting: 单调上升，在 7 与 8 之间跨过 0.90。
- Uncertainty or variability shown: 无抽样误差；显示解析夹界宽度。
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
- Data and transformation: `final_results.json` 的216个更便宜整数点及7个单调前沿；成本按官方元/μm³换算。
- X axis, unit, range: 总成本，元，覆盖候选范围。
- Y axis, unit, range: 导通概率，0.87–0.92。
- Encoding/legend: 更便宜前沿使用严格上界，57B 使用严格下界。
- Baseline or reference line: `P=0.90`。
- Expected pattern before plotting: 57B 与 8A 通过；更便宜候选低于阈值。
- Uncertainty or variability shown: 无抽样误差；上下界来自解析证明。
- What the reader should conclude: 57B 的下界超过0.90，全部216个更低成本整数方案的上界低于0.90。
- What the figure cannot establish: 不是对无限整数域的形式化全局最优证明；结论受周期同一介质解释约束。
- Source/provenance note: 固定种子 `20260904`，官方成本参数。
