# Decision Log

## 2026-09-07 / Problem selection

从压缩包的 A/B/C 三题中选择 A“煤矿巷道支护问题”。理由：数据规模适中、四问共享清晰的力学依赖链，能够完成从数据识别到工程约束、偏心强度和分区优化的闭环验证。

## Model tournament

### Q1.1
- Baseline：题设物理形式 T=KPd 的过原点 OLS。
- Robust check：Huber 回归。
- Rejected：高阶多项式/黑箱回归，因为没有增加决策能力且破坏物理可解释性。
- Result：OLS 与 Huber 接近，保留 OLS。

### Q1.2
- Primary：等效扭矩系数 Kij=T/(dPij) 的后缀稳定化判据（尾段相对偏差≤5%、后缀 CV≤5%）。
- Validation：5000 次测点 Bootstrap。
- Risk：岩石阈值对空间测点较敏感，因此区分统计起点 125 N·m 与保守施工阈值约 200 N·m；煤体 175 N·m 更稳定。

### Q2
- Primary：把屈服、粘结、压陷统一为 P 上限后取最小值。
- Steel-belt extension：把钢带作用等效为提高荷载扩散宽度 b_eff。
- Solver：解析计算，无需数值优化器。

### Q3
- Baseline：附录 3 名义截面 Von Mises。
- Correction：应力集中 κ 与偏心接触压力放大 1+6e/b。
- Risk：κ 无题内标定，参考 1.20 仅为情景；Monte Carlo 在 1.10–1.30 扰动。

### Q4
- Missing link：题目只给 f=σc/10，未给 E(f)。
- Primary bridge：显式引入模量比 Rm=E/σc，E_GPa=0.01 Rm f。
- Reference：Rm=155，η=0.90；Rm 在 120–220 扰动。
- Claim limit：分区数值是参考情景，不应替代现场 E/UCS 试验。
