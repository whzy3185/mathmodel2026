# 科研级论文图表 Agent 与 Skill 深度调研

> 调研日期：2026-08-14
>
> 适用范围：数学建模竞赛论文的数据图、空间几何图、优化结果图、方法流程图和机理示意图
>
> 结论口径：区分论文作者自报指标、代码是否公开、社区热度、独立用户复现和当前项目可用性。

## 1. 结论先行

目前没有证据表明某个通用 Skill 能稳定地把论文或数据“一键变成无需复核的投稿级图”。现阶段最可靠的方案不是单一生图模型，而是两条分开的 Agent 流水线：

1. **数据图、优化结果图、灵敏度图、三维几何图**：必须由可执行代码从受控数据生成，Agent 负责规划、写代码、运行、视觉审查和数值审查；不能让图像生成模型绘制柱高、曲线、坐标或误差条。
2. **方法流程图、系统架构图、机理示意图**：可以采用“语义抽取—结构规划—多候选生成—批评—重绘—矢量化”的多 Agent 路线，但必须保留可编辑 SVG/XML，并由独立语义核验器检查节点、边、公式和术语。

值得直接借鉴的是 **PaperBanana、AutoFigure、SciFig、Crafter、MatPlotAgent** 的 Agent 结构，而不是它们对“publication-ready”的宣传用语。它们共同证明了多轮规划与反馈优于一次生成，同时也共同暴露出文本错误、连接错误、数值幻觉、领域外泛化不足和仍需人工微调等问题。

对本项目而言，最优实践是：

> 结果数据/公式作为唯一真值源 → 一张图一个 claim–evidence contract → 生成 3–5 个候选 → 数值与语义双核验 → 盲选 → 最终尺寸渲染 → 嵌入 DOCX/PDF 后再审。

## 2. 什么才算“Agent 直接生成论文级结果”

本调研不把“看起来像论文图”视为论文级。只有同时满足以下条件，才允许进入论文正文：

| 条件 | 可验证要求 |
|---|---|
| 结论支撑 | 图必须对应一个明确主张，并能说明读者应从图中得到什么结论 |
| 数据忠实 | 图中点、线、柱、区间、标签必须能逐项追溯到数据文件、公式或结果 JSON |
| 语义忠实 | 流程图的节点、边、方向、公式和术语与正文一致，不得擅自补造关系 |
| 可编辑 | 数据图保留脚本；示意图优先保留 SVG、PDF、XML 或其他分层矢量源文件 |
| 可复现 | 固定依赖、参数、随机种子和导出命令后可重新生成 |
| 最终尺寸可读 | 在论文实际插入宽度下检查，而不是只看放大预览 |
| 黑白与无障碍 | 灰度打印仍可区分；不能只靠颜色编码 |
| 版面正确 | 图题、编号、单位、字体、页边距和分页在最终 PDF 中正确 |
| 独立审查 | 生成 Agent 不能同时充当唯一验收者；至少有一个独立审查环节 |

只满足“漂亮”和“高清”而不满足数值、语义、复现条件的图，最多是候选草图。

## 3. 主要 Agent 系统的证据核查

### 3.1 PaperBanana：目前社区热度最高，但方法图仍是位图路线

[PaperBanana 论文](https://arxiv.org/abs/2601.23265)采用 Retriever、Planner、Stylist、Visualizer、Critic 五类 Agent。Retriever 找参考图，Planner 把方法文本压缩为视觉蓝图，Stylist 提炼论文图风格，Visualizer 出图，Critic 多轮反馈。其核心不是一句提示词，而是参考驱动的协作链。

论文在 292 个 NeurIPS 2025 方法图案例上报告相对基线的总体提升，并在 50 个案例的盲测中报告 72.7% / 20.7% / 6.6% 的胜/平/负结果。但需要注意：

- 论文明确承认其方法示意图主要是 raster 输出，不具备真正的分层矢量编辑能力。
- 作者报告的主要失败模式是冗余连线、源—目标节点错配，且 Critic 有时无法发现这些错误。
- 对统计图，论文明确指出图像生成模型会出现数值幻觉和元素重复，因此改用可执行 Matplotlib 代码。
- 截至调研日，[官方仓库](https://github.com/dwzhu-pku/PaperBanana)仍把“上传统计图代码”列为 TODO，不能把论文中展示的统计图能力等同于官方开源实现已完整可用。
- 官方仓库约 6.9k stars、520 forks，且列出多个社区复现，说明传播和二次开发明显强于一般科研绘图 Skill；但 stars 不是论文级正确率。

独立社区反馈呈两极化：[Reddit 生物学用户的实测讨论](https://www.reddit.com/r/biology/comments/1syv9ik/pi_recently_had_me_evaluate_several_ai_figure/)称结果经常不连贯；另有[生物信息学讨论](https://www.reddit.com/r/bioinformatics/comments/1toaaig/graphic_tools_for_paper/)认为它适合示意图但成本较高，而数据图仍普遍使用 ggplot2、Matplotlib 等代码工具。

**判断**：适合用作方法图候选生成器和 Agent 架构参考；不适合直接承担数学建模数据图，也不能跳过连接关系检查和矢量重绘。

### 3.2 AutoFigure：专家认可并非 100%，最有价值的是 Reasoned Rendering

[AutoFigure 论文](https://arxiv.org/abs/2602.03828)把生成分为结构规划与最终渲染，并通过 designer–critic 循环反复修正。其 FigureBench 包含 3,300 个长文本—图形样本。论文的人类评测规模是 10 位相关论文第一作者、21 篇论文：

- AutoFigure 相对其他 AI 方法的强制排序 win rate 为 83.3%；
- 只有 66.7% 的专家表示愿意把其结果用于自己论文的 camera-ready 版本；
- 论文仍报告小字体、密集布局、复杂背景下的字符级错误，以及领域知识、细粒度分类关系不足等失败模式。

[开源仓库](https://github.com/ResearAI/AutoFigure)提供从文本或 PDF 生成 SVG/XML 的 SDK、0–10 分 Critic 和最多 5 轮 refinement；README 默认质量阈值为 9.0，并估计一次运行约 20 分钟、30k tokens、0.50 美元。调研日仓库约 1.8k stars、136 forks。

需要特别警惕“Agent 自己打 9 分”的循环：Critic 与生成器依赖相近模型时，可能共享盲区。因此仓库的 `final_score` 只能作为候选排序信号，不能代替数值或专家核验。

**判断**：方法图工作流参考价值高；66.7% camera-ready 采用意愿同时说明仍有约三分之一结果未达作者使用门槛。

### 3.3 AutoFigure-Edit：编辑性显著增强，但论文明确要求人工调整和专家核验

[AutoFigure-Edit 论文](https://arxiv.org/abs/2603.06674)增加参考图风格控制、显式结构骨架和组件级 SVG 编辑。其部署式用户研究收集了 217 位用户的 262 份评价，PNG 结果在语义正确、信息完整、视觉质量、风格一致方面的均分约为 4.04、4.11、3.95、4.09（5 分制）。

论文自己的限制部分更重要：

- 依赖闭源视觉和视觉语言模型，存在成本、隐私和复现问题；
- 中间位图的分割错误会传播到 SVG，需要用户在编辑器中人工调整；
- 用户研究主要是可用性研究，跨专业领域的严格专家正确性核验仍是未来工作；
- 系统声明自己是辅助工具，不能替代专家验证。

[仓库](https://github.com/ResearAI/AutoFigure-Edit)调研日约 4.1k stars、266 forks，MIT 许可。可编辑性和社区关注度都强于早期 AutoFigure，但“可编辑”不等于“语义一定正确”。

**判断**：当前较适合作为流程图/示意图的可编辑候选生成器；最终仍要检查连接、术语和公式。

### 3.4 SciFig：评测设计最完整之一，但代码公开状态存在矛盾

[SciFig 论文](https://arxiv.org/abs/2601.04390)的新版采用 Planning、Layout、Component、Feedback 四类 Agent，以可编辑 XML 为最终结构，并保存中间渲染和反馈记录。论文报告：

- SciFig-Bench 覆盖 435 个以 AI/ML 为中心的方法图；
- 60 位参与者完成 10,000 次成对比较；
- 论文报告 SciFig 的 Elo 为 1327、win rate 为 81.4%；
- 生成约 10 分钟、API 成本约 1.2 美元；
- 评估框架与人类判断的 Pearson 相关最高报告为 0.92。

但论文也明确展示了组件内部错误：缺失图节点、公式含义画错、变量标签错误。反馈循环擅长修复重叠、对齐和箭头路由，却不可靠地验证组件内部的科学语义。

截至调研日，[项目页](https://shramanpramanick.github.io/SciFig/)仍显示代码和 benchmark “Coming Soon”，与论文新版“代码可用”的描述存在公开状态差异，故当前不能把它视为已经可独立复现的成熟 Skill。另需避免把商业网站 `scifig.ai` 与该研究项目混为一谈。

**判断**：评测和 Agent 分工非常值得借鉴；当前公开可运行性不足，且评测领域以 AI/ML 为主，不能直接外推到机械臂、VLSI 或旅游规划。

### 3.5 Crafter：最新的“多候选—校正—验证”范式，独立验证仍少

[Crafter 论文](https://arxiv.org/abs/2605.30611)把科学图生成视为 harness 问题：先进行 diversity-driven plan exploration，再做 structured corrective layer，最后通过 directive critic 执行 verify-then-refine；CraftEditor 再把位图转换为可编辑 SVG。论文报告其在 CraftBench 与 PaperBanana-Bench 上超过基线，并报告 CraftEditor 总分 8.04，高于 AutoFigure-Edit 的 6.91。

这项工作的关键启发是：不要只迭代同一张图，而要先并行探索多个结构差异明显的方案，再进入局部修正。它更接近本项目“先生成更多备选，再盲选最终图”的要求。

但该工作发表于 2026 年 5 月，仍很新；当前指标主要来自作者自己的 benchmark 和 VLM judge，独立社区复现不足。

**判断**：适合吸收到本项目 Agent 编排中，不宜仅凭论文自报分数替换数值校验和人工终审。

### 3.6 MatPlotAgent 与 PlotGen：数据图应该走代码 Agent，而不是生图 Agent

[MatPlotAgent 论文](https://arxiv.org/abs/2402.11453)由 Query Expansion、Code Agent、Visual Agent 组成。MatPlotBench 含 100 个经人工核验的任务，其中 75 个源于 Matplotlib Gallery，25 个源于 OriginLab Gallery。主要结果包括：

- GPT-4 直接生成得分 48.86，使用 MatPlotAgent 后为 61.16；
- 去掉 Visual Feedback 后为 53.44，说明“运行后看图再改代码”确有增益；
- 自动评分与人类评分相关为 `r=0.876`（GPT-4）和 `r=0.836`（GPT-3.5）；
- 论文明确承认最困难案例仍无法正确生成，通用 benchmark 也不能覆盖全部专业要求。

[开源仓库](https://github.com/thunlp/MatPlotAgent)调研日约 117 stars、14 forks。热度不高，但它比纯图像生成路线更符合数学建模结果图的真实性要求，因为最终产物是可执行代码。

[PlotGen 论文](https://arxiv.org/abs/2502.00988)进一步把反馈拆成数值、词法和视觉层，并同样使用 Python/Matplotlib 代码。其启发是：视觉 Agent 只能发现“看起来不对”，数值 Agent 才能核查“数据到底有没有画对”。

**判断**：数据图的正确路线。当前项目应采用这一范式，并增加结果 JSON 的逐点比对、单位检查和 Claim–Evidence Gate。

## 4. 通用 Skill 的社区验证情况

### 4.1 `nature-figure`：安装量大，但不等于稳定投稿级

[skills.sh 页面](https://www.skills.sh/yuan1z0825/nature-skills/nature-figure)显示约 7.4k installs；其所属仓库约 32.6k stars，并通过页面列出的三类安全扫描。这说明它传播很广、安装链路较成熟，但仓库星数是整个技能集合的指标，不是该绘图 Skill 的论文正确率。

独立中文社区存在明确负面复现：

- [LINUX DO 讨论一](https://linux.do/t/topic/2176729)：用户称输出“怪怪的”、不如 GitHub 示例、复杂图不可用，与 Nature 审美差距较大；
- [LINUX DO 讨论二](https://linux.do/t/topic/2456658)：用户认为大而全 Skill 在工程领域不适配，Matplotlib 结果像“抽卡”；
- [AI 科研绘图求助](https://linux.do/t/topic/1936803)：用户指出局部修复可能导致整图错位，说明仅靠生成 Agent 很难执行最小编辑。

因此，它适合作为期刊风格、尺寸、字体、调色板和导出 QA 的“规范路由器”，不应被当成科学正确性生成器。

### 4.2 当前已安装的三个本地 Skill

本机已安装：

- `nature-figure`
- `make-sci-data-figures`
- `polish-sci-figures`

本地文件结构和基本脚本已验证可读取，但独立社区验证强度有限。前两者和第三者更适合承担“图形选择、代码生成规范、统一样式、导出、组图与视觉 QA”，不能单独证明图中的数值、模型或科学关系正确。

此前考察的 `Icarus-Figures` 没有安装：其说明引用了缺失的 `_style.py` 与 `critique.py`，安装后也无法按文档完整运行。这个案例说明，Skill 是否“能安装”必须核查引用脚本是否真实存在，而不能只读 README。

## 5. 中国社区、Reddit 与教程信号如何解释

社区材料只能辅助判断可用性，不能替代受控实验。当前信号如下：

- Bilibili 出现多条 Nature Figure、Sci 绘图 Skill 教程，播放和收藏说明需求强，但教程演示通常只展示成功样例，不能估计失败率。
- [LINUX DO 的科研绘图流程分享](https://linux.do/t/topic/1917914)建议先出整体图、再拆分子图、最后进入绘图软件人工完善；这与论文系统的多阶段架构一致，也反证了“一次生成直接交稿”并不现实。
- [PaperBanana 中文社区最佳实践报告](https://linux.do/uploads/short-url/cOoaNtv7CUglkS46D9EC1p6lOCn.pdf)强调 caption、用途和参考风格的重要性；另一份[实验报告](https://linux.do/uploads/short-url/z3obykcgqcGSsijQRH6yjh3nrWO.pdf)指出 NeurIPS 数据偏向 CS/AI、领域外缺少先例且文字标签可能乱码。
- Reddit 上既有正面体验，也有“结果不连贯”的负面实测；样本量都很小，只能说明稳定性尚未形成共识。

综合判断：**目前真正被社区验证的是“这些工具能提高草图效率”，而不是“它们能稳定替代研究者完成最终论文图”。**

## 6. 对数学建模论文的最终选型

| 图形任务 | 推荐主路线 | 可用辅助工具 | 禁止作为最终证据的路线 |
|---|---|---|---|
| 数据分布、误差、灵敏度 | Python/R 代码 Agent + 数值核验 | `make-sci-data-figures`、`nature-figure` | 文生图模型直接画曲线或柱形 |
| 优化前沿、可行域、整数域 | 代码 Agent + 约束/候选逐点校验 | MatPlotAgent/PlotGen 范式 | 只凭视觉看起来像前沿 |
| 三维机械臂、空间路径、障碍物 | 几何代码 + 多视图 + 碰撞证书 | `polish-sci-figures` 做组图与导出 | 纯 3D 渲染且无二维/数值证据 |
| VLSI 布局与连线 | 真实坐标代码绘图 + HPWL/RSMT 数值叠加 | 矢量后处理 | 生成模型虚构单元或连线 |
| 旅游路径地图 | 真实 GIS/坐标/路网绘制 | 版式和配色 Skill | 生成式地图替代真实地理关系 |
| 方法流程图 | 多 Agent 语义规划 + SVG/XML + 边核验 | AutoFigure-Edit/Crafter/PaperBanana 思路 | 位图直接入稿且无法修订 |
| 装饰性概念插图 | 可用图像生成模型做候选 | 人工重绘/矢量化 | 把装饰图包装成结果证据 |

## 7. 可迁移的 Agent 设计原则

从上述系统中可以稳定提取出七条规律：

1. **先定义图要证明什么，再画图。** 没有 claim 的图容易沦为装饰。
2. **结构与渲染解耦。** 先生成语义图或绘图规范，再决定布局和样式。
3. **先产生多样候选，再局部精修。** 同一路径反复自我修正容易收敛到同一个错误结构。
4. **生成者与审查者分离。** 最好使用不同提示词、不同上下文，必要时不同模型。
5. **数值审查与视觉审查分离。** 视觉好看不能证明数据正确。
6. **最终产物必须可编辑、可重跑。** 数据图保留代码，示意图保留 SVG/XML 和组件层。
7. **最终 PDF 才是验收对象。** SVG 单独好看，不代表缩放、分页、字体嵌入后仍然合格。

## 8. 可信度分级

| 结论 | 可信度 | 原因 |
|---|---|---|
| 多轮视觉反馈优于单次代码生成 | 高 | MatPlotAgent 有消融实验，多个系统得到一致结论 |
| 数据图应使用可执行代码 | 高 | PaperBanana 自身也承认图像生成会数值幻觉；科研复现原则一致 |
| SVG/XML 可编辑输出优于纯位图 | 高 | 便于局部修复、重排、字体和标签校正 |
| AutoFigure/PaperBanana 可稳定直接投稿 | 低 | 作者自己的评测也存在未采用比例和明确失败模式 |
| `nature-figure` 已被广泛验证为投稿级 | 低 | 安装量高但独立复现评价明显分化，缺少标准 benchmark |
| SciFig 当前可直接安装复现 | 低 | 项目页仍显示代码 Coming Soon，公开状态与论文表述不一致 |
| 只增加更多 Critic 轮数会持续提高质量 | 低 | 多个系统显示收益饱和；共享盲区和错误传播仍存在 |

## 9. 本项目下一步

不建议继续盲目安装更多“Nature 风格”Skill。下一步应基于现有数据和绘图脚本实现项目专用 Figure Agent Harness：

1. 从 `final_results.json`、原始附件和公式生成图形合同；
2. 每张目标图并行生成 3–5 个结构不同的代码候选；
3. 自动抽取候选图使用的数据，与结果 JSON 逐项比对；
4. 运行独立视觉、数学、物理/业务语义三类审查；
5. 盲选后导出 SVG/PDF/300 dpi PNG；
6. 重建 DOCX/PDF，在实际页面尺寸下做终审；
7. 保存候选、评分、拒绝理由和最终选择，形成可追溯证据。

具体执行规范见 [`figure-agent-workflow.md`](../math-modeling-competition/references/figure-agent-workflow.md)。
