# 数学建模 AI 竞赛资源深度调研报告

调研日期：2026-08-11；所有 stars、forks、提交和页面状态均为当日快照，后续会变化。

## 1. 搜索范围与检索统计

本次执行了 12 轮主题检索，其中 GitHub 6 轮（完整 Skill、Codex/Claude Skill、端到端 Agent、优秀论文/源码、优化 Agent、模板与 RAG），Hugging Face/学术 4 轮（Papers、Models、Datasets、Spaces、Collections/标签页），官方来源 2 轮（COMAP/UMAP、CUMCM）。另外用 GitHub REST API 对 15 个重点仓库核验 stars、forks、默认分支、最近更新时间、许可证和当前提交。

- 候选资源：40+；写入来源清单：38。
- GitHub 深度对象：15；其中 Skill/Agent 8，论文/源码/模板 4，研究基准 3。
- Hugging Face/论文深度对象：13，覆盖 Paper、Model、Dataset、Space；Collections 的通用搜索噪声较大，最终改用论文关联、标签页和数据卡交叉发现。
- 可靠论文/评论入口：12+，包括 COMAP 结果页、多个 UMAP contest issue、Mathmodels、CUMCM 历年论文展示与期刊链，以及可核验的论文+代码仓库。
- 核心精选：22；证据层级以 S/A 为主，B 级主要作为工程实现参考，C 级只用于发现线索。

停止条件满足：已覆盖任务要求的最低数量，且最后两轮泛化搜索主要返回重复项目、非数学建模的“模型优化”或低证据内容。

### Executive Summary：10 条最重要结论

1. **最佳架构不是一个巨型“算法百科 Prompt”**，而是一个主 Skill 管阶段与状态，若干按需 reference 管领域知识，脚本管确定性检查。
2. **现有 Skill 中最值得借鉴的是 `mathmodel-skill` 的状态与 fail-closed 工程**：共享 decision log、阶段回退、评分重算、论文装配和 AI 使用台账；其经验分位并非官方门槛，且 MCM/电工杯经验样本仍有限。[项目说明](https://github.com/handsomeZR-netizen/mathmodel-skill)
3. **`math-modeling-skills` 的强项是覆盖面和 solver/paper 拆分**，但固定决策矩阵、95+ 场景和大量模板容易诱导“匹配即选择”；必须加入 baseline、反驳和候选淘汰。[项目说明](https://github.com/Lupynow/math-modeling-skills)
4. **MM-Agent 提供了最完整的研究级端到端参照**：问题分析、结构化建模、计算求解、报告生成和 111 道 MCM/ICM 题的 MM-Bench；但其 README 写 CC BY-NC 4.0，GitHub License 区显示 GPL-3.0，复用前必须解决许可证冲突。[论文](https://arxiv.org/abs/2505.14148) / [代码](https://github.com/usail-hkust/LLM-MM-Agent)
5. **优化建模研究的共同进展是执行式验证**：OptiBench、OptMATH、NEMO、OR-Space 不再只比较公式文本，而是逐步引入可执行代码、求解结果、修订任务和多文件工作区。[OptiBench](https://arxiv.org/abs/2407.09887) / [OptMATH](https://huggingface.co/papers/2502.11102) / [OR-Space](https://arxiv.org/abs/2605.28158)
6. **评委评论长期稳定地重视完整作答、摘要、假设、清晰表达、可测试性和可靠来源**。COMAP 当前说明明确要求讨论测试、误差、灵敏度/稳定性、优缺点，并强调摘要的重要性。[COMAP Instructions](https://www.contest.comap.com/undergraduate/contests/mcm/instructions.php)
7. **获奖论文不能当作可复制模板**。最高价值是蒸馏 Q1→Qn 依赖、baseline、模型路线、验证、敏感性、图表论证和局限；无许可证仓库只能保存链接、元数据和原创笔记。
8. **最危险的 AI 失败不是“模型不够高级”，而是数据泄漏、时间序列随机切分、目标/约束漏项、求解器状态不检查、参数不可辨识、单位错误和结论越界**。
9. **比赛工作流必须把规则当动态依赖**。COMAP 和 CUMCM 的页数、AI 披露、文件结构与模板会更新；缓存只能是基线，提交前必须回到官方页面复核。[COMAP](https://www.contest.comap.com/undergraduate/contests/mcm/instructions.php) / [CUMCM](https://www.mcm.edu.cn/)
10. **推荐“一个入口 Skill + 领域 reference 模块”，暂不拆成多个独立 Skill**。原因是规则、状态、模型选择、验证、写作具有强依赖；等 benchmark 显示上下文路由或维护边界成为瓶颈，再将 optimization、paper 或 compliance 独立出去。

## 2. 关键资源表

| 资源 | 类型 | 证据级 | 核心价值 | 复用边界 |
|---|---|---:|---|---|
| [handsomeZR mathmodel-skill](https://github.com/handsomeZR-netizen/mathmodel-skill) | Skill | A | 10 阶段、decision log、反馈、脚本、fail-closed 装配 | MIT；经验统计不是官方 rubric |
| [Lupynow math-modeling-skills](https://github.com/Lupynow/math-modeling-skills) | 双 Skill | B/A | solver/paper 拆分、cookbook、代码模板 | MIT；需防决策矩阵机械匹配 |
| [MM-Agent](https://github.com/usail-hkust/LLM-MM-Agent) | Agent+论文 | A | HMML、actor-critic、执行与报告、MM-Bench | 许可证冲突，先只研究架构 |
| [scientific-agents](https://github.com/K-Dense-AI/scientific-agents) | 专家 profile | B/A | 可辨识性、V&V、量纲、OR/统计失败模式 | MIT；不是竞赛全流程 |
| [route-selection](https://github.com/y3519712124-ui/math-modeling-contest-route-selection) | 专项 Skill | B | 选题与路线前置筛选 | MIT；范围窄 |
| [MathModel-QA-Engine](https://github.com/Kirito-Elucidator/MathModel-QA-Engine) | 论文 RAG | B | 年份/题号/章节过滤，方法与写作结构检索 | 代码 MIT；语料权利逐项核验 |
| [2024 ICM E O+INFORMS](https://github.com/ydchen0806/24ICM_E_O_Award_Paper_code) | 论文+源码 | S | 同时有论文和源码，适合做模式提取 | 无许可证：link/metadata/notes only |
| [2023 CUMCM 国一](https://github.com/linggm3/2023_CUMCM_National-First-Prize) | 论文+代码+数据 | S | 机理→仿真→优化链条完整 | 仓库 MIT；论文著作权仍需确认 |
| [OptiMUS](https://github.com/teshnizi/OptiMUS) | 优化 Agent | A | 变量/目标/约束分解，代码执行与反思 | 代码与 NLP4LP 数据许可分开 |
| [OptiBench/ReSocratic](https://github.com/yangzhch6/ReSocratic) | Benchmark | A | 端到端优化求解、执行正确性 | Apache-2.0 |
| [OptMATH](https://huggingface.co/papers/2502.11102) | Paper+Dataset | A | 双向合成、正向建模拒绝采样 | 核对具体数据卡许可 |
| [NEMO artifacts](https://huggingface.co/datasets/c3aiia3c/nemo-icml2026) | Dataset | A | 多候选抽取、代码工作区、验证轨迹 | CC-BY-4.0 |
| [OR-Space](https://huggingface.co/datasets/Chenyu-Zhou/OR-Space) | Workspace benchmark | A | Build/Revise/Explain 全生命周期 | CC-BY-NC-4.0 |
| [COMAP Instructions](https://www.contest.comap.com/undergraduate/contests/mcm/instructions.php) | 官方规则 | S | 评审关注、摘要、测试、AI 与提交 | 只链接/引用/释义 |
| [UMAP 45.4](https://www.comap.org/membership/member-resources/item/umap-journal-45-4-winter-2024-edition) | 官方竞赛刊 | S | 2024 MCM Outstanding 摘要与 Judges' Commentary | 会员/版权内容不打包 |
| [CUMCM 官方](https://www.mcm.edu.cn/) | 官方规则/结果 | S | 当届规则、格式、论文与期刊入口 | 只链接/引用/释义 |

## 3. GitHub 深度分析

### 3.1 评分方法

总分 100：内容完整度 20、技术质量 20、建模质量 20、论文能力 15、Agent/Skill 设计 15、可维护性 5、来源可信度 5。分数是本次调研的工程判断，不是项目质量的绝对排名；stars 只作辅助信号。

| 项目（2026-08-11 快照） | 类型 | Stars/Forks | 最近提交 | License | 分项 C/T/M/P/A/Mt/S | 总分 | 最值得借鉴 | 主要缺陷 | 建议 |
|---|---|---:|---|---|---|---:|---|---|---|
| [mathmodel-skill](https://github.com/handsomeZR-netizen/mathmodel-skill) | Skill | 190/5 | d3941e14d869 | MIT | 19/18/18/14/15/5/4 | **93** | 可恢复状态、局部回退、确定性工具、披露/装配门 | 经验分位非官方；竞赛样本不均衡 | 吸收架构，不复制统计阈值 |
| [LLM-MM-Agent](https://github.com/usail-hkust/LLM-MM-Agent) | Agent | 638/46 | 8abc1300e378 | GPL/CC-NC 冲突 | 18/18/18/13/15/4/5 | **91** | 四阶段、HMML、actor-critic、MM-Bench | 许可冲突；自动选择透明度和复现实验成本 | 研究级参照，暂不代码复用 |
| [math-modeling-skills](https://github.com/Lupynow/math-modeling-skills) | Skill 套件 | 185/7 | 3a9428c006cc | MIT | 19/16/14/14/13/4/3 | **83** | solver/paper 分离、知识路由、代码/写作覆盖 | 模型矩阵可能变成关键词匹配；实证来源需细查 | 选择性吸收 references 组织 |
| [XiaoMa math-modeling-skill](https://github.com/XiaoMaColtAI/math-modeling-skill) | Skill | 664/34 | ccfaeb0612bb | 无 | 19/16/14/14/13/4/2 | **82** | Python/MATLAB、DOCX/LaTeX、阶段反馈 | 无许可证；宽而重；独立门禁质量需实测 | 只研究，不复制内容 |
| [scientific-agents](https://github.com/K-Dense-AI/scientific-agents) | Profiles | 128/15 | 48dedd20b82c | MIT | 10/16/19/7/11/5/4 | **72** | 量纲、可辨识性、数值 V&V、领域失败模式 | 无竞赛状态、执行和论文装配 | 吸收严谨性清单 |
| [OptiMUS](https://github.com/teshnizi/OptiMUS) | OR Agent | 270/48（搜索快照） | 多版本分支 | 代码/数据分离 | 12/18/17/5/13/4/4 | **73** | 变量-约束-目标分工、执行反馈、规模化 | 只覆盖优化；商业 solver/数据许可 | 吸收优化阶段协议 |
| [route-selection](https://github.com/y3519712124-ui/math-modeling-contest-route-selection) | Skill | 28/1 | bb15e079e6e4 | MIT | 7/12/15/4/14/4/3 | **59** | 把选题和路线变成独立门 | 不覆盖执行、验证、论文 | 作为 Stage 0/2 参考 |
| [MathModel-QA-Engine](https://github.com/Kirito-Elucidator/MathModel-QA-Engine) | RAG | 10/0 | 32bcbcbcd233 | MIT | 8/14/10/12/10/3/3 | **60** | section-level 检索和过滤 | 依赖语料来源；RAG 不能证明论文规律 | 作为知识库接口参考 |
| [math-modeling-single](https://github.com/Yoki-cmd/math-modeling-single) | Skill | 9/0 | ccbf76dcaa96 | 无 | 13/13/11/14/11/3/2 | **67** | 不可信赛题输入与代码执行边界 | 无许可证；LaTeX-only；窄工作流 | 借鉴安全边界概念 |
| [2024 ICM E O 源码](https://github.com/ydchen0806/24ICM_E_O_Award_Paper_code) | 获奖论文 | 82/4 | 8194d982ff80 | 无 | 8/15/18/14/2/2/5 | **64** | 可追溯论文-代码关系 | 无许可证；单题过拟合风险 | 核心论文知识库，link-only |
| [2023 CUMCM 国一](https://github.com/linggm3/2023_CUMCM_National-First-Prize) | 获奖论文 | 44/5 | 486768dc1aa6 | MIT | 10/16/18/12/2/3/5 | **66** | 论文、数据、代码、答辩；逐问递进 | 单一案例；不要推广成通用公式 | 核心案例与 benchmark 灵感 |
| [dick20/MCM-ICM](https://github.com/dick20/MCM-ICM) | 论文档案 | 2269/380 | e9a060887be6 | 无 | 12/5/9/13/1/2/3 | **45** | 大规模发现入口 | 无许可证；奖项和版本逐篇验证 | 线索库，不打包 PDF |
| [CUMCMThesis](https://github.com/latexstudio/CUMCMThesis) | LaTeX 模板 | 992/216 | 90d3e854534a | 无 | 4/13/2/13/1/3/2 | **38** | 排版工程和用户基础 | 2023 适配声明已过时；无 detected license | 不作为 2026 官方模板 |
| [OptiBench/ReSocratic](https://github.com/yangzhch6/ReSocratic) | Benchmark | 36/2 | 27ff7ecb3c6a | Apache-2.0 | 8/18/16/2/9/4/5 | **62** | 执行式评分和合成方法 | 优化专域，非完整竞赛 | 吸收 benchmark 设计 |
| [Mamo](https://github.com/FreedomIntelligence/Mamo) | Benchmark | 15/2 | 2c91069dee5c | CC-BY-SA-4.0 | 7/16/15/2/7/4/4 | **55** | solver-grounded 评价 | 优化专域；share-alike | 用作许可清晰的测试来源 |

### 3.2 可直接借鉴、需重做、不值得复制

可直接借鉴：`decision_log` 的连续记忆；阶段进入/退出条件；脚本重算而不是让 LLM 自报分数；Figure Contract；模型/结果变更后的下游失效；候选模型和拒绝理由；执行/求解器状态检查；论文与规则的 fail-closed 审计。

需要重做：统一的 Candidate Model Tournament；跨领域 baseline 库；可辨识性门；数据泄漏/时间顺序门；精确优化与启发式的报告边界；claim–evidence 映射；赛题 benchmark 的反模式判分；来源/许可证 manifest。

不值得复制：按关键词直接推荐模型；把模型数量当创新；未经官方核验的页数/格式；以少量论文样本估计“获奖概率”；无许可证论文/模板整包镜像；把 RAG 回答当成获奖规律；自动生成后不运行的代码。

## 4. Hugging Face / Papers 深度分析

| 项目/论文 | 解决的问题 | 方法 | 对竞赛的价值 | 可转化内容 |
|---|---|---|---|---|
| [MM-Agent/MM-Bench](https://huggingface.co/papers/2505.14148) | 开放式真实建模端到端评价 | 四阶段 Agent、HMML、actor-critic、111 题 | 最接近 MCM/ICM 全流程 | 阶段化、分层方法库、benchmark 题型覆盖 |
| [OptMATH](https://huggingface.co/papers/2502.11102) | 优化建模数据稀缺与泛化 | 可控实例生成、反向语言化、正向建模拒绝采样 | 说明生成知识必须执行/一致性过滤 | 生成案例的 rejection gate |
| [OptiBench](https://arxiv.org/abs/2407.09887) | 自然语言优化的端到端求解 | formulation+code+solution benchmark | 防止“公式看起来对” | 可执行指标、分难度测试 |
| [OptiMUS](https://github.com/teshnizi/OptiMUS) | 大规模 LP/MILP 自动建模 | conductor、变量/约束/目标模块、反思 | 适合 ICM D、排程、分配 | 分工协议、solver feedback |
| [IndustryOR](https://huggingface.co/datasets/CardinalOperations/IndustryOR) | 工业 OR 真实题 | 100 题、5 类优化 | 基准与 small exact tests | 题型与难度标签；非商业许可门 |
| [OR-LLM-Agent/BWOR](https://huggingface.co/papers/2503.10009) | 自动建模、代码和调试 | 3 个专门子代理；批评旧 benchmark | 强化调试是独立阶段 | 建模→代码→debug 门，benchmark 质量审计 |
| [NEMO](https://huggingface.co/datasets/c3aiia3c/nemo-icml2026) | 执行感知优化 Agent | 多候选抽取、模拟器/优化器、验证 | 可直接研究失败轨迹 | 保存候选与执行 artifacts |
| [OR-Space](https://arxiv.org/abs/2605.28158) | 一次性 prompt 忽略真实工作区生命周期 | Build/Revise/Explain，多文件 evaluator | 与 Codex 工作模式最匹配 | 持久 workspace、修改保持旧逻辑、解释可溯源 |
| [JOR-Bench](https://huggingface.co/datasets/cyberagent/JOR-Bench) | 跨语言 OR 评价 | 5 个数据集英/日双语 | 提醒中文化不能只翻译表面 | 语言变体、原许可证传播 |
| [LogiOR](https://huggingface.co/datasets/Georgeay/LogiOR) | 物流供应链优化 | 92 个专家题，公式+Gurobi+解 | 适合作为确定性小测试 | 公式-代码-最优值三联验证 |
| [ORQA](https://huggingface.co/papers/2412.17874) | OR 专家推理泛化 | 专家构造多步题 | 证明通用数学推理不等于建模能力 | 专业知识 slice 评价 |
| [OptiMind-SFT](https://huggingface.co/microsoft/OptiMind-SFT) | NL→可执行优化模型 | 优化类别错误分析与专门训练 | “错误类型反馈”可转为 Skill gate | class-aware failure taxonomy |
| [MathematicalModelingAgent Space](https://huggingface.co/spaces/MathematicalModelingAgent/MathematicalModelingAgent) | 交互演示 | Web Agent | 可做行为检查 | 不把演示当复现证据 |

综合判断：Hugging Face 最有价值的不是下载一个“数模模型”，而是取得 benchmark schema、数据卡、执行轨迹、许可证和失败分布。优化类资源多，预测/空间/机理/论文写作的端到端 benchmark 明显不足，必须自建跨域赛题 benchmark。

## 5. 优秀论文资源

### 5.1 可靠入口（至少 10 个）

1. [COMAP 2025 结果与 Outstanding paper 入口](https://www.contest.comap.com/undergraduate/contests/mcm/contests/2025/results/)（S）。
2. [COMAP MCM/ICM Resources](https://contest.comap.com/undergraduate/contests/resources/index.html)（S）。
3. [Mathmodels.org](https://www.mathmodels.org/)（S，部分内容可能需会员）。
4. [UMAP Journal 46.4：2025 MCM issue](https://www.comap.com/component/finder/search?Itemid=0&q=Outstanding+Papers)（S，官方搜索入口）。
5. [UMAP Journal 46.3：2025 ICM issue](https://www.comap.com/component/finder/search?Itemid=0&q=Outstanding+Papers)（S）。
6. [UMAP Journal 45.4：2024 MCM](https://www.comap.org/membership/member-resources/item/umap-journal-45-4-winter-2024-edition)（S）。
7. [UMAP Journal 44.3/44.4：2023 ICM/MCM 官方搜索入口](https://www.comap.com/component/finder/search?Itemid=0&q=Outstanding+Papers)（S）。
8. [CUMCM 历年结果与论文展示入口](https://www.mcm.edu.cn/html_cn/block/018500ec1a6bd8c7e9997133def2b590.html)（S）。
9. [CUMCM 优秀论文/命题评阅人点评期刊链](https://www.mcm.edu.cn/html_cn/block/0d24174bfce844efa33374cbe64d1845.html)（S）。
10. [2024 ICM E O+INFORMS 论文与源码](https://github.com/ydchen0806/24ICM_E_O_Award_Paper_code)（S，许可不明）。
11. [2023 CUMCM A 国一论文+代码+数据](https://github.com/linggm3/2023_CUMCM_National-First-Prize)（S/B：奖项自述可与官方名单再交叉核验）。
12. [dick20/MCM-ICM 2004–2020 O 论文索引](https://github.com/dick20/MCM-ICM)（A 级线索库；逐篇回到官方核验）。

### 5.2 提取方式

每篇代表论文不做普通摘要，而做 13 字段卡：Problem Decomposition、Model Route、Baseline、Main Model、Improvement、Validation、Sensitivity、Robustness、Claim-bearing Visualization、Summary/Writing、Narrative、Innovation、Weakness/Redesign。优先选“官方奖项 + 论文 + 完整代码/数据”的 S 级样本；版权不明时只存 metadata、source link 和原创派生笔记。

### 5.3 代表模式

最终模式库包含预测+优化、评价+优化、机理+参数估计、网络+鲁棒性、空间+政策、仿真+情景、ML+可解释性、多目标+Pareto、动态系统+控制、数据+机理融合，以及风险储备和因果估计+政策两种扩展。每个模式都强制绑定 baseline、验证和常见薄弱点，见 Skill 的 `references/award-paper-patterns.md`。

## 6. Judges' Commentary 总结

COMAP 当前说明称评委主要关注团队的思考过程、问题分析、建模路线和数学方法，并要求讨论模型如何测试，包括误差、敏感性和稳定性；还要说明优缺点、明确结果和引用来源。[官方说明](https://www.contest.comap.com/undergraduate/contests/mcm/instructions.php)

2009 年官方 Problem B 评论把评价概括为：主要问题覆盖的广度/深度、模型有效性、解答清晰度；它批评只重述题目的摘要、无理由的假设、无标签图和未正确记录的资源。[官方 PDF](https://www.contest.comap.com/undergraduate/contests/mcm/contests/2009/results/2009_MCM_Judges_Commentary_Problem_B.pdf) 2022 Problem B 评论进一步说明 triage 中每篇至少由两位评委阅读；若没有覆盖所有要求、摘要不清楚，即使局部工作不错也难进入下一轮。[UMAP 内容镜像](https://www.shumo.com/nudtdb/2023MCM/2022_MCM_B_JC.pdf)

可执行结论：

- 摘要是检索界面，不是装饰。必须最后写，给路线、具体结果和答案。
- 全题覆盖是 triage 门；高级模型不能补偿漏问。
- 假设要解释“为什么”和“在哪里进入模型”。
- 图表必须有标签、单位、出处和读者应看到的结论。
- 可靠数据与引用必须在事实出现的位置连接，而非只列文末。
- 模型、结果和表达不可分离；无法清楚交流的好模型不会得到高评价。

## 7. 方法知识地图

| 赛题信号 | 首选候选 | 必须 baseline | 验证/反驳 | 禁止捷径 |
|---|---|---|---|---|
| 有序预测 | ETS/SARIMA/回归树，按数据选择 | naive/seasonal naive | rolling split、残差、coverage | 随机切分、无脑 LSTM |
| 综合评价 | PCA/FA 用于测量；AHP/TOPSIS 用于偏好 | equal weights/Pareto | 权重、归一化、rank reversal | 熵权=客观真理 |
| 约束决策 | LP/MILP/NLP/DP | 简单可行解 | status、gap、约束重算、场景 | 启发式称全局最优 |
| 多目标 | ε-constraint/Pareto | 单目标极值 | frontier 收敛、dominance | 只给任意加权和 |
| 路由网络 | flow/TSP/VRP/robustness | shortest/greedy/random failure | 小实例精确解、边扰动、null | 中心性即因果 |
| 统计关系 | GLM/mixed/survival/Bayes | 描述统计/简单 GLM | residual、interval、specification | 只报 p/R² |
| 空间风险 | spatial regression/kriging | 非空间模型 | spatial CV、尺度/边界/权重矩阵 | 随机 CV、GWR 因果化 |
| 机理动力学 | ODE/PDE/compartment | reduced/limiting model | 量纲、守恒、可辨识性、holdout | 参数多即真实 |
| 仿真系统 | MC/ABM/DES/CA | 解析/队列/规则基线 | 收敛、多 seed、event trace | “看起来合理” |
| 政策建议 | scenario+multiobjective/robust | 透明规则 | stakeholder、regret、equity | 单一黑箱指数 |

详细的适用、不适用、假设、数据、公式、参数、实现、验证、敏感性、失败、替代和论文表达已分到 Skill 的 9 个领域 reference。

## 8. Failure Pattern Library

最高严重度（直接阻断提交）：数据泄漏；时间序列随机切分；求解器状态/约束不检查；引用不存在；违反当届规则或隐瞒 AI 使用。

高严重度：无 baseline；目标函数随意；约束遗漏；量纲错误；参数来源不明；不可辨识却做点预测；启发式冒充精确最优；一粒随机种子；测试集反复调参；结论把相关写成因果。

中严重度：无脑 TOPSIS/AHP/熵权；无脑 RF/XGBoost/LSTM；模型堆叠；只有精度无残差/校准；无敏感性；图表无论证；摘要为 AI 套话；公式堆砌；没有 limitations。

每个模式的检测与修复规则已经落入 `references/failure-patterns.md`；F09/F10/F14/F25 与 compliance failure 是 fail-closed 项。

## 9. 现有 Skill 对比

| 能力 | Lupynow | handsomeZR | route-selection | MM-Agent | scientific-agents | 本项目 |
|---|---:|---:|---:|---:|---:|---:|
| 完整生命周期 | 强 | 强 | 弱 | 强 | 弱 | 强 |
| 可恢复状态 | 弱/中 | **强** | 中 | 中 | 无 | **强** |
| 候选淘汰/反驳 | 中 | 中/强 | 强（路线） | actor-critic | 领域级强 | **强制** |
| 执行/solver 验证 | 中 | 强 | 弱 | 强 | 指南级 | **fail-closed** |
| 数据泄漏/可辨识性 | 中 | 已修复若干边界 | 弱 | 研究级但需审计 | **强** | **强制门** |
| 论文装配 | 强 | **强** | 无 | 强 | 弱 | 模板+证据矩阵 |
| 规则/AI 披露 | 中 | **强** | 弱 | 弱 | 无 | 动态官方复核 |
| benchmark | 示例/playbook | tests/样本统计 | 局部 | **MM-Bench** | 无 | 8 类反模式 benchmark |
| 许可证策略 | MIT | MIT+third-party notice | MIT | 冲突 | MIT | manifest+link-only |

本项目避免复制任何现有 Skill 文本或模板；只吸收抽象工程原则，并把不足重新实现为 Candidate Tournament、claim–evidence、许可证清单和跨域 benchmark。

## 10. 最终架构建议

### 决策

当前做 **一个大型入口 Skill，但内部模块化**，而不是多个互相调用的 Skill。

理由：赛题分类、模型选择、执行、验证、图表、论文和合规共享同一状态；分成多个独立 Skill 会增加交接丢失和触发歧义。真正需要按需加载的是领域知识，因此放入 references；真正需要稳定执行的是结构检查、计划检查和 workspace 初始化，因此放入 scripts。

### 目录

```text
mathmodel/
├── research/数学建模AI竞赛资源深度调研报告.md
├── prompt-chain/CODEX_TASK_CHAIN.md
├── audits/FINAL_AUDIT.md
└── math-modeling-competition/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── references/        # 21 个按需模块
    ├── templates/         # 候选赛、Figure Contract、中英论文结构
    ├── scripts/           # 初始化、模型计划验证、结构审计
    ├── benchmarks/        # 8 类反模式测试
    ├── examples/
    ├── tests/
    └── sources/manifest.json
```

### 何时再拆 Skill

当 benchmark 证明以下任一事实时再拆：优化 reference 每次加载造成明显上下文浪费；paper/compliance 由不同维护者独立发布；某一模块有独立触发和稳定输入输出；跨 Skill 状态可以通过 schema 自动验证。优先拆 `math-modeling-paper` 或 `math-modeling-optimization`，主 Skill 保留 orchestrator 和 state ownership。

## 11. 资源引用与许可证策略

1. GitHub 条目记录 repository、commit/release、license、accessed date、reused content、modification。无许可证视为保留全部权利。
2. 论文记录标题、作者、年份、比赛、题目、奖项、DOI/官方来源、方法和原创模式笔记。会员/付费/版权不明 PDF 不进入公开仓库。
3. COMAP/UMAP 仅保存官方链接、书目信息和原创释义；不把会员期刊或第三方镜像 PDF 打包。
4. 数据集按 data card 逐个执行许可；组合数据集如 JOR-Bench 必须继承子集原许可。
5. 许可证冲突优先从 LICENSE 文件、release 和维护者说明解决；MM-Agent 当前冲突未解，因此标为 architecture study only。
6. manifest 的 `usage` 明确限定：link-only、metadata/notes、evaluation data 或 permitted adaptation。

完整机器可读清单见 `math-modeling-competition/sources/manifest.json`。

## 12. 完整 Codex Prompt Task Chain

已生成 15 条可独立复制、连续执行的完整提示词，严格对应 Task 00–14；每条都含背景、当前状态、输入、任务、文件范围、实施步骤、禁止事项、验证方法、输出文件和完成标准。Task N 的输出被 Task N+1 显式列为输入。见 `prompt-chain/CODEX_TASK_CHAIN.md`。

任务链不是泛化标题：它引用本次核验的资源、许可证风险、Candidate Tournament、OR-Space 式 workspace benchmark、COMAP/CUMCM 动态规则、Figure Contract 和 fail-closed 审计。

## 13. 最终结论

### A. 值得直接借鉴

`mathmodel-skill` 的状态/反馈/确定性脚本；MM-Agent 的四阶段和分层方法库；OptiMUS 的优化分解与 solver feedback；OR-Space 的 Build/Revise/Explain workspace benchmark；OptMATH 的拒绝采样；scientific-agents 的量纲、可辨识性和领域失败模式。

### B. 应重新实现

候选模型反驳机制、baseline 门、数据/复杂度/可辨识性/工程/验证 gate、claim–evidence、下游失效传播、统一许可证 manifest、跨域 benchmark 与官方规则动态复核。

### C. 只适合论文知识库

COMAP/UMAP Outstanding 论文与 commentary、CUMCM 优秀论文期刊链、dick20 档案、单题 O/国一仓库。它们用于提取结构和方法，不用于复制措辞、公式编排或数据结论。

### D. 同质化/可靠性风险

大量项目都提供“算法大全+论文模板+一键生成”，但缺乏 baseline、反驳、执行证据和可辨识性；无许可证仓库不可复用；自报奖项/样本规律应回到官方结果；搜索引擎和 HF Collections 容易把模型压缩/推理优化误判为数学优化。

### E. 最终方案

保留一个 `math-modeling-competition` 入口，以 falsifiability、state、execution、validation 和 compliance 为主轴；知识用 references 渐进加载，机械检查交给脚本。这个架构比“更多模型”更能降低比赛失败概率，也比黑箱自动成文更符合 COMAP 对思考过程、分析、模型与表达的长期要求。

