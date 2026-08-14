# 数学建模论文 Figure Agent 直接生成工作流

> 目标：让 Agent 直接产出可以进入论文的图表候选，同时把科学正确性、数值一致性、可编辑性和最终版面检查设为硬门槛。  
> 原则：生成可以自动化，科学责任不能外包给生成模型。

## 1. 总体架构

本工作流将“直接生成”定义为从项目真值源自动得到最终图文件、审计记录和入稿版本，而不是从一句提示词得到一张位图。

```text
题意与正文主张
      ↓
Claim–Evidence Contract
      ↓
图形类型路由 ── 数据/几何图 → 代码候选 Agent × 3–5
      │
      └──────── 方法示意图 → 语义图 Agent → SVG/XML 候选 Agent × 3–5
                                      ↓
              数值核验 + 语义核验 + 视觉核验 + 复现核验
                                      ↓
                         盲选、拒绝或定向重绘
                                      ↓
                       SVG/PDF/PNG + 生成脚本/源文件
                                      ↓
                          DOCX/PDF 实际页面终审
```

## 2. 真值源与输入合同

每张图生成前必须填写现有 [`figure-contract.md`](../templates/figure-contract.md)。至少增加以下机器可核验字段：

```yaml
figure_id: C04_q3_bounds_band
claim_id: Q3_MINIMUM_COUNT
claim: 8 根为充分条件且 7 根不足
source_files:
  - outputs/data/final_results.json
  - data/raw/A/attachment.xlsx
source_fields:
  - q3.upper_bound_by_n
  - q3.lower_bound_by_n
transform_function: build_q3_bounds
expected_assertions:
  - upper_bound[7] < 0.90
  - lower_bound[8] >= 0.90
units:
  x: 根数
  y: 概率界
allowed_interpolation: false
output_width_mm: 145
```

没有可定位的 `source_files`、`source_fields` 和 `claim_id` 时，图不得进入候选生成阶段。

## 3. 图形类型路由

### 3.1 数据图与优化图

包括折线、散点、概率界、误差、敏感性、优化前沿、可行域、热力图、三维曲面等。

必须采用代码路线：

1. Planning Agent 读取合同和数据字典，提出 3–5 种图形方案；
2. Code Agent 只从声明的数据字段取值并生成 Python/R 代码；
3. Runner 执行代码，保存 stdout、依赖版本和中间表；
4. Numeric Verifier 对绘图数据与真值源逐点比对；
5. Visual Critic 在最终插入尺寸下检查遮挡、层级、字体和图例；
6. Selector 根据固定量表盲选；
7. Exporter 输出 SVG、PDF、300 dpi PNG，并保存源代码。

严禁使用图像生成模型绘制数据曲线、柱高、误差条、坐标刻度或地图位置。

### 3.2 三维几何与空间路径图

除上述门禁外，必须增加：

- 坐标轴、单位、视角和等比例设置检查；
- 障碍物、机械臂连杆、路径点来自真实模型数据；
- 三维图至少配一个二维投影、距离证书或碰撞余量图；
- 线宽只用于视觉辨识，不可暗示实体半径；
- 透视遮挡不能隐藏关键不可行点或最短距离位置。

### 3.3 方法流程图与机理示意图

可以参考 PaperBanana、AutoFigure、SciFig、Crafter 的结构，但最终必须为可编辑 SVG/XML：

1. Semantic Parser 从正文抽取实体、步骤、输入、输出、约束和关系；
2. Graph Planner 先输出机器可读语义图，而不是直接画图；
3. Layout Agents 并行生成 3–5 个结构不同的 SVG/XML；
4. Edge Verifier 逐条检查源节点、目标节点、方向和标签；
5. Terminology Verifier 将图中文字与论文术语表比较；
6. Visual Critic 检查层级、对齐、箭头路由、留白和字体；
7. Selector 盲选后只做局部修改，不允许无理由整图重生。

推荐中间语义结构：

```json
{
  "nodes": [
    {"id": "input", "label": "题目附件", "type": "data"},
    {"id": "audit", "label": "数据审计", "type": "process"},
    {"id": "model", "label": "几何与概率模型", "type": "model"},
    {"id": "result", "label": "可复核结果", "type": "evidence"}
  ],
  "edges": [
    {"source": "input", "target": "audit", "relation": "读取"},
    {"source": "audit", "target": "model", "relation": "提供参数"},
    {"source": "model", "target": "result", "relation": "计算"}
  ]
}
```

生成的 SVG 中每条边都必须能回映射到这里的 edge ID。

## 4. Agent 分工

| Agent | 只负责什么 | 明确不能做什么 | 必须留下的产物 |
|---|---|---|---|
| Claim Agent | 把正文主张变成图形合同 | 画图 | contract YAML/JSON |
| Design Planner | 提出候选图型和证据逻辑 | 改数据 | candidate plans |
| Code/Vector Agent | 生成绘图代码或 SVG/XML | 自行补造结果 | source + render |
| Runner | 执行和记录环境 | 修改结论 | logs + versions |
| Numeric Verifier | 核验点、线、区间、单位 | 评价美观 | numeric audit JSON |
| Semantic Verifier | 核验节点、边、公式、术语 | 只凭视觉打分 | semantic audit JSON |
| Visual Critic | 检查排版、遮挡、可读性 | 证明科学正确 | visual audit MD/JSON |
| Adversarial Reviewer | 尝试找误导编码和结论越界 | 参与生成 | attack report |
| Selector | 按固定量表盲选 | 因“更炫”覆盖硬错误 | score sheet |
| Document QA | 检查 DOCX/PDF 实际页面 | 只看单图预览 | page render audit |

生成 Agent 与核验 Agent 不共享候选评分结论；Selector 在评分前不显示候选来源和生成工具。

## 5. 候选生成协议

每个正文图位至少生成 3 个、最多 5 个候选。候选必须在结构上不同，而不是只换配色：

- A：最小充分证据版；
- B：多面板解释版；
- C：面向评委快速发现的直接标注版；
- D：黑白打印优化版；
- E：必要时的三维/交互关系补充版。

候选禁止通过改变坐标范围、裁剪异常值、隐藏失败方案或平滑离散数据来提高观感。

## 6. 硬门禁

### Gate 1：执行门禁

- 脚本退出码为 0；
- 输出文件存在且非空；
- SVG/PDF 可解析；
- 字体和依赖可用；
- 固定种子下重复运行的关键数据一致。

### Gate 2：数值门禁

- 绘图用中间表与结果 JSON 行数、键、数值逐项一致；
- 浮点误差阈值在合同中声明；
- 坐标轴单位、缩放和对数底正确；
- 误差条/置信区间有真实定义和计算来源；
- 离散点不擅自连成连续规律；
- 插值、平滑、归一化和截断全部记录。

任一关键点不一致即拒绝，不允许视觉 Critic 覆盖 Numeric Verifier 的失败。

### Gate 3：语义门禁

- 每个节点能在正文、公式或数据源中定位；
- 每条边的方向与依赖关系正确；
- 图中公式与正文公式逐字符比对；
- 未出现模型自动补造的机构、变量、阶段或因果关系；
- 概率界、估计值、模拟值、最优值用词不混淆。

### Gate 4：视觉门禁

- 在目标宽度和 100% 页面视图下正文、刻度、图例可读；
- 无标签碰撞、裁剪、遮挡和箭头穿字；
- 主次层级明确，网格和阴影不过度；
- 灰度打印仍可区分；
- 色盲模拟下核心编码不丢失；
- 图例不遮挡数据，类别少时优先直接标注；
- 3D 只在第三维承载真实变量时使用。

### Gate 5：论证门禁

- 图题能独立说明对象、条件和主要结论；
- 正文引用该图并解释其证据意义；
- 图不能比数据或模型证明得更多；
- 图与表不机械重复同一信息；
- 删除该图会削弱一个明确论证，否则移入附录或删除。

### Gate 6：成稿门禁

- 重新生成 DOCX 和 PDF；
- 逐页渲染检查图题分离、跨页、空白、字体替换和低清晰度；
- PDF 中的 SVG/PDF 矢量元素放大后保持清晰；
- 最终 PDF 的图号、正文交叉引用和目录一致。

## 7. 候选评分量表

先执行硬门禁，再评分。任何硬门禁失败的候选直接淘汰。

| 维度 | 分值 | 评分问题 |
|---|---:|---|
| Claim 支撑 | 0–5 | 能否直接支撑合同中的主张 |
| 数学/数据忠实 | 0–5 | 数据、区间、单位和变换是否可逐项复核 |
| 可读性 | 0–5 | 最终尺寸下是否无需放大即可理解 |
| 信息密度 | 0–5 | 是否在不过载的情况下提供必要证据 |
| 黑白与无障碍 | 0–5 | 灰度和色盲条件下是否仍可区分 |
| 可编辑与复现 | 0–5 | 是否有代码/矢量源、环境和命令 |
| 版面效率 | 0–5 | 占用篇幅是否与论证价值匹配 |
| 攻击审查余量 | 0–5 | 是否难以被误读、质疑或指出越界 |

总分 40。建议正文入选阈值 33，附录阈值 28；但阈值不能豁免硬门禁。

## 8. 目录与审计产物

建议每个 run 使用以下结构：

```text
outputs/
  figure_contracts/
    C04_q3_bounds_band.yaml
  figure_candidates/
    C04_A.svg
    C04_B.svg
    C04_C.svg
  figure_data/
    C04_plot_data.csv
  figure_audits/
    C04_numeric.json
    C04_semantic.json
    C04_visual.md
    C04_adversarial.md
    C04_selection.json
  figures_final/
    C04_q3_bounds_band.svg
    C04_q3_bounds_band.pdf
    C04_q3_bounds_band.png
```

`selection.json` 至少记录候选 hash、各维度得分、拒绝理由、最终选择和人工修改说明。

## 9. 对当前华数杯 A 题项目的落地映射

当前 run 已具备：

- 真值结果：`outputs/data/final_results.json`；
- 候选图：`outputs/figure_candidates/`；
- 最终科研图：`outputs/figures_research/`；
- 生成脚本：`src/a/build_research_figures.py`；
- 现有图形审计：`evidence/research_figure_upgrade.md`；
- Claim–Evidence 与 artifact registry：`evidence/claim_evidence.json`、`evidence/artifact_registry.json`；
- 攻击性审查：`reports/adversarial_*.md`。

下一轮不需要推翻现有代码，应补齐：

1. 把现有 Markdown 图形合同转为每图一份 YAML/JSON；
2. 为候选图保存统一的绘图数据 CSV；
3. 自动比较 CSV 与 `final_results.json`；
4. 将候选评分和淘汰理由写入结构化 JSON；
5. 在最终 DOCX/PDF 构建后执行页面截图审查；
6. 把审查失败设为构建失败，而不是只输出警告。

## 10. 工具使用边界

- `make-sci-data-figures`：用于图形选择、统计规划、可复现绘图和多配色候选；不能替代模型正确性证明。
- `nature-figure`：用于期刊尺寸、字体、样式、导出和视觉 QA；不能把普通图自动变成科学证据。
- `polish-sci-figures`：用于组图、间距、标注、矢量导出和最终审查；不能改变数据或结论。
- PaperBanana/AutoFigure 类工具：只用于非数值方法图候选；必须经 SVG/XML、边和术语核验。
- 图像生成模型：只用于不承载数值证据的图标、纹理或概念素材，且应保存来源并接受许可与竞赛规则检查。

## 11. 终止条件

只有同时满足以下条件，Figure Agent 才能报告“完成”：

1. 所有正文图通过六个 Gate；
2. 每图有可重跑的源文件和命令；
3. 每图有数值或语义审计记录；
4. 最终 PDF 页面渲染已检查；
5. 没有把作者自报、模拟界或视觉趋势写成更强结论；
6. 候选、拒绝和最终选择过程可追溯。

否则只能报告“候选图已生成”或“草图已完成”，不能使用“论文级结果已完成”的表述。

