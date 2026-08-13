# 最终图 Figure Contracts

> 2026-08-13 研究型图件升级：下列 RF 合同对应 `outputs/figures_research`。完整候选对照与评分见 `evidence/research_figure_upgrade.md`。

## RF1：Q1 三组真实三维构型
- Figure ID: RF1 / `C01_q1_3d_triptych`
- Claim supported: 官方附件组1不导通，组2和组3存在显式导通路径，且三组空间密度差异显著。
- Why necessary: 单一二维投影可能产生伪相交，三维 xyz 图保留真实空间关系。
- Data/transformation: `attachment.xlsx` 六列端点坐标；路径编号取自 `final_results.json`；无随机抽样、无几何扰动。
- Axes/units: x、y、z 均为 nm，范围 -5000 至 5000。
- Encoding: 蓝色细线为全部轴段，红色粗线为显式路径；线宽仅为视觉编码。
- Expected pattern: 组1稀疏且无红色跨域路径；组2、3显示红色路径。
- Reader conclusion: 连通结论对应真实三维附件构型而非二维投影视觉判断。
- Cannot establish: 图本身不能替代逐边平端圆柱接触证书。
- Provenance: 官方附件、`final_results.json`、`build_research_figures.py`。

## RF2：Q1 三维路径接触证书
- Figure ID: RF2 / `C03_q1_path_certificate`
- Claim supported: 组2、组3显式路径的相邻介质均满足轴距阈值，最短点位于轴段内部。
- Why necessary: 将路径结构与逐边数值证书放在同一空间上下文中。
- Data/transformation: 官方端点；绿色虚线由 `segment_distance_certificates` 计算；标注单位 nm。
- Axes/units: x、y、z，nm；视窗按路径包围盒等比例缩放。
- Encoding: 红线为介质轴段，绿虚线为相邻轴段最近点连线。
- Expected pattern: 每条绿虚线距离不超过 61.8 nm。
- Reader conclusion: 正例路径具备平端圆柱侧面接触的充分证书。
- Cannot establish: 非路径边未逐一呈现；视觉线宽不是实际半径。
- Provenance: 官方附件、`geometry.py`、`final_results.json`。

## RF3：Q3 解析概率夹逼带
- Figure ID: RF3 / `C04_q3_bounds_band`
- Claim supported: 7 根 A 的总导通上界低于 0.90，8 根 A 的直接贯通下界高于 0.90，故整数最小值为 8。
- Why necessary: 同时展示相邻整数处的必要性和充分性。
- Data/transformation: `final_results.json.Q3.proof_rows`；带宽为严格上下界之差，不是抽样置信区间。
- Axes/units: A 数量/根；导通概率 0-1。
- Encoding: 蓝实线下界、红虚线上界、橙色夹逼带；0.90 水平参考线。
- Expected pattern: 7 的上界在阈值下，8 的下界在阈值上。
- Reader conclusion: 8 根结论由解析界闭合证明，而非图形插值。
- Cannot establish: 不估计上下界之间的真实概率位置。
- Provenance: `final_results.json`、`analytic_bounds.py`。

## RF4：Q2 不导通风险数量级
- Figure ID: RF4 / `C05_q2_failure_lollipop`
- Claim supported: 四个规定体积分数下的不导通上界分别达到约 10^-45、10^-54、10^-63、10^-90 数量级。
- Why necessary: 普通概率轴会把四点都压在 1，且折线会暗示未观测的连续工况。
- Data/transformation: `final_results.json.Q2.log10_failure_probability_upper_bound`。
- Axes/units: A 体积分数/%；log10(不导通概率上界)。
- Encoding: 独立棒棒糖和点标记；直接标注数量与数量级。
- Expected pattern: 体积分数增加时风险上界快速下降。
- Reader conclusion: 四个题设工况在报告精度内导通概率均为 1。
- Cannot establish: 四点间不代表经验拟合曲线，也不包含非直接网络贡献。
- Provenance: `final_results.json`。

## RF5：Q4 完整低成本整数域
- Figure ID: RF5 / `C07_q4_integer_domain`
- Claim supported: 216 个比 0A+57B 更便宜的非负整数候选均不能达到 0.90；同时标出正混合口径 1A+50B。
- Why necessary: 避免只画七个前沿点而隐藏已检查的整数域规模。
- Data/transformation: 由 `analytic_bounds.py` 的成本和概率上界公式重新枚举；前沿及选定点与 `final_results.json` 核对。
- Axes/units: A/根，B/个；色标为总导通概率上界。
- Encoding: 实心方格为更低成本点，空心方格为显示窗内较高成本点，红线为排除前沿，星/菱形为两种最优口径。
- Expected pattern: 更低成本前沿整体位于 0.90 以下；选定点紧邻成本边界。
- Reader conclusion: 最优性不是从一条连续曲线推断，而是整数候选穷举排除。
- Cannot establish: 颜色较依赖彩色显示；正式黑白版应保留轮廓、标记和前沿线。
- Provenance: `final_results.json`、`analytic_bounds.py`。

## RF6：Q4 成本—概率前沿
- Figure ID: RF6 / `C08_q4_cost_frontier`
- Claim supported: 0A+57B 是第一个用充分下界越过 0.90、且所有更便宜候选上界均低于阈值的方案。
- Why necessary: 最直观表达目标函数和概率约束的共同作用。
- Data/transformation: 整数枚举；散点纵坐标为上界，选定星点纵坐标为下界。
- Axes/units: 材料成本/元；导通概率界。
- Encoding: 点颜色为 A 数量，红线为更低成本前沿，绿星为选定下界，虚线为 0.90。
- Expected pattern: 红前沿止于阈值下方，绿星刚过阈值。
- Reader conclusion: 结论具有可行性证书与更低成本排除证书。
- Cannot establish: 上界散点不能当作真实导通概率。
- Provenance: `final_results.json`、`analytic_bounds.py`。

## RF7：设计情景下的整数阈值敏感性
- Figure ID: RF7 / `C09_sensitivity_threshold_counts`
- Claim supported: 在保持其余模型条件不变时，A 高度或 B 半径改变会使达到 90% 的直接贯通充分数量呈阶梯响应。
- Why necessary: 直接展示离散阈值对几何参数的结构敏感性，并保留题设基准点。
- Data/transformation: H=3500-6500 nm、R=120-280 nm 为作者设计情景；逐点代入单粒子直接贯通公式并向上取整。
- Axes/units: A 高度 H/nm 与阈值 A 数量/根；B 半径 R/nm 与阈值 B 数量/个。
- Encoding: 阶梯线表示整数阈值，红点表示题设 H=5000 nm、R=200 nm。
- Expected pattern: 单粒子跨界概率随尺寸上升，所需粒子数量分段下降。
- Reader conclusion: 8A 与 57B 对几何尺寸并非连续稳定，而存在整数跳变边界。
- Cannot establish: 参数范围不是实测误差、制造可行区间或概率分布；图中阈值只证明直接贯通充分性。
- Provenance: 题设几何公式、`analytic_bounds.py`、`build_research_figures.py`。

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
