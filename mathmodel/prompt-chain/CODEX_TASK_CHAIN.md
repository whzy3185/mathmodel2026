# Codex Prompt Task Chain

使用方式：从 Task 00 开始逐条复制给 Codex。默认工作根目录为 `mathmodel/`，目标 Skill 为 `mathmodel/math-modeling-competition/`。若文件已存在，先检查并增量修改；不得覆盖用户改动。每个任务完成后提交给下一任务使用的结构化产物。

## Task 00 — Repository Reconnaissance

```text
背景：我们要在本地建立一个证据优先的数学建模竞赛 Skill，支持 CUMCM、MCM/ICM、研究生数学建模及相近赛事。它不能把关键词直接映射为模型，必须保留状态、执行真实代码并 fail-closed 验证。
当前状态：你刚进入一个可能已有文件的仓库，尚不知道 Git、Python、Skill、依赖和用户改动情况。
输入：当前目录；用户提供的赛题/资料（若有）；现有 AGENTS.md/SKILL.md；Git 状态。
任务：完成只读侦察并建立安全工作分支与环境报告。
文件范围：可读取整个仓库；只允许新建 `mathmodel/research/environment-report.md`，以及在仓库已初始化时新建分支 `research/math-modeling-skill`。不要改业务文件。
实施步骤：确认绝对路径和仓库根；列出关键目录而非全盘扫描；检查 `git status`、当前分支和未跟踪文件；检查 Python 版本及 numpy/pandas/scipy/statsmodels/sklearn/networkx/matplotlib；搜索已有 SKILL.md、AGENTS.md、模板、测试；记录冲突与复用机会；若不是 Git 仓库，初始化前先确认目标就是当前目录；建立研究分支；写环境报告。
禁止事项：禁止删除、reset、checkout 覆盖、安装全局包、改用户文件、提交或推送；禁止把密钥和环境变量写入报告。
验证方法：报告必须包含 cwd、repo root、Git 状态、Python/工具状态、已有 Skill、脏文件、风险和下一步；重新运行 `git status --short --branch` 与报告一致。
输出文件：`mathmodel/research/environment-report.md`。
完成标准：下一任务能从报告明确知道哪些路径可写、哪些文件必须保护、有哪些依赖和复用候选。
```

## Task 01 — Source Manifest

```text
背景：调研发现高价值来源包括 handsomeZR 的状态化 Skill、Lupynow 的 solver/paper 结构、MM-Agent/MM-Bench、scientific-agents、OptiMUS、OptiBench、OptMATH、NEMO、OR-Space、COMAP/UMAP 与 CUMCM 官方来源。许可证和证据等级必须先于复用。
当前状态：Task 00 已生成环境报告；尚未建立统一来源清单。
输入：`mathmodel/research/environment-report.md`；本任务给出的资源线索；已有 `sources/manifest.json`（若有）。
任务：网页核验并建立 30–50 条来源清单，最终标记 15–25 个核心来源。
文件范围：只修改 `mathmodel/math-modeling-competition/sources/manifest.json` 和 `mathmodel/research/search-log.md`。
实施步骤：至少执行 GitHub 五组关键词；分别检查 HF Papers/Models/Datasets/Spaces/Collections 或标签页；检查 COMAP instructions/resources/results、UMAP contest issues、CUMCM 当前规则/格式/论文入口；对 GitHub 记录 repository、commit/release、stars、forks、更新时间、license；对论文记录题名、作者、年份、比赛/奖项/DOI；按 S/A/B/C 分级；填写 `name,type,url,source,license,award_level,year,topic,methods,quality,usage,notes,accessed_at`；标记 no-license 和许可冲突；连续两轮无新高价值资源才停止。
禁止事项：禁止默认 GitHub 内容可复制；禁止把第三方镜像当官方；禁止把版权不明 PDF 放入仓库；禁止编造 stars、奖项、DOI 或许可。
验证方法：JSON 可解析；至少 30 条、GitHub ≥10、Skill/Agent ≥3、论文/源码 ≥3、HF/学术 ≥8、官方论文入口 ≥10；每条都有 URL、quality、usage、accessed_at。
输出文件：`sources/manifest.json`、`research/search-log.md`。
完成标准：下一任务可以仅凭 manifest 选择高价值仓库并明确允许的复用方式。
```

## Task 02 — Existing Skill Reverse Engineering

```text
背景：目标不是抄 README，而是提取 Trigger、Workflow、Stage、State、References、Scripts、Template、Feedback Loop、Validation 和 Failure Handling。
当前状态：Task 01 已建立经过分级和许可标注的 manifest。
输入：`sources/manifest.json`；优先项目 handsomeZR/mathmodel-skill、Lupynow/math-modeling-skills、y351.../route-selection、usail-hkust/LLM-MM-Agent、K-Dense-AI/scientific-agents、Kirito-Elucidator/MathModel-QA-Engine，以及 manifest 中新增的核心项目。
任务：对至少 6 个项目做文件级逆向分析并给出可借鉴/需重做/不应复制清单。
文件范围：只写 `mathmodel/research/existing-skill-analysis.md`；临时克隆放仓库外或 `work/`，不得把第三方源码提交进目标 Skill。
实施步骤：核对 README、SKILL.md、AGENTS.md、references、scripts、templates、tests、prompts；绘制阶段和状态流；记录输入输出 schema、回退、确定性检查和人类批准点；用 100 分七维 rubric 评分；区分维护者自述与可验证实现；核对许可证；特别比较 decision log、Candidate Tournament、HMML、actor-critic、solver feedback、RAG corpus provenance。
禁止事项：禁止仅凭 stars 排名；禁止把自报获奖效果当因果证据；禁止复制无许可证文本或模板；禁止执行第三方未知代码。
验证方法：每个项目都有证据文件/链接、分项评分、强项、缺陷、许可、复用结论；总表与逐项分析一致。
输出文件：`research/existing-skill-analysis.md`。
完成标准：Task 12 能从本报告设计一个简洁入口，而不需重新浏览所有仓库。
```

## Task 03 — Award Paper Knowledge Base

```text
背景：优秀论文用于蒸馏问题分解与证据结构，不能当作语言模板。核心来源优先 COMAP Outstanding、Judges' Commentary、CUMCM 官方优秀论文链，以及论文+代码+数据的 S 级仓库。
当前状态：manifest 和 existing-skill-analysis 已完成。
输入：`sources/manifest.json`、官方结果/论文入口、已许可或 link-only 的代表论文。
任务：建立原创派生的 award-paper pattern library。
文件范围：写 `mathmodel/math-modeling-competition/references/award-paper-patterns.md` 和可选的 `sources/paper-metadata.json`；不保存完整 PDF。
实施步骤：选择至少 10 个可靠入口和若干代表论文；对每篇提取 decomposition、model route、baseline、main model、improvement、validation、sensitivity、robustness、visualization、writing、narrative、innovation、weakness；归纳至少预测+优化、评价+优化、机理+参数估计、网络+鲁棒性、空间+政策、仿真+情景、ML+可解释、多目标+Pareto、动态+控制、数据+机理融合；每个模式绑定 baseline、验证和常见失败。
禁止事项：禁止普通摘要；禁止复制获奖论文措辞、公式布局或完整图；禁止把第三方奖项自述当官方验证；禁止把观察模式写成官方 rubric。
验证方法：每个模式可追溯到来源入口；每条都回答何时适用、关键依赖、baseline、验证和弱点；版权策略明确。
输出文件：`references/award-paper-patterns.md`、可选 `sources/paper-metadata.json`。
完成标准：后续模型选择和论文模块可以引用模式，但不会把模式机械套题。
```

## Task 04 — Problem Taxonomy

```text
背景：赛题分类必须同时考虑任务、对象、输出、证据、动态/随机/空间结构和不确定性，不能只按题号或关键词。
当前状态：来源、现有 Skill、获奖论文模式库已存在。
输入：`award-paper-patterns.md`、`existing-skill-analysis.md`、官方 CUMCM/MCM/ICM 题型说明及其他赛事官方入口。
任务：创建支持 CUMCM、MCM、ICM、研究生数学建模、MathorCup、华数杯、电工杯的统一 taxonomy 与分解记录。
文件范围：写 `references/problem-taxonomy.md`；可增加 `templates/problem-decomposition.md`。
实施步骤：定义分类轴；给每类列典型 deliverable、数据/机制、建模风险和早期 gate；要求每个 Qi 记录决策变量、输入、未知参数、目标/estimand、约束、依赖、验证和下游表图；建立 Qi 依赖 DAG 规则；把 forecasting/evaluation/optimization/statistics/network/spatial/mechanism/simulation/ML/policy 映射到候选族和验证。
禁止事项：禁止“看到预测就 LSTM”“看到评价就 TOPSIS”；禁止把赛事题号当方法；禁止引用过期规则作为当前事实。
验证方法：用至少 8 个公开历史题的摘要/题型进行人工路由测试；每个都能得到不止一个候选族、baseline 和验证提示。
输出文件：`references/problem-taxonomy.md`、可选模板。
完成标准：Task 05 可用 taxonomy 生成候选而非直接给答案。
```

## Task 05 — Model Selection Engine

```text
背景：目标 Skill 的核心差异是 Candidate Model Tournament：先 baseline，再经 assumption/data/complexity/identifiability/engineering/validation gates 淘汰候选，最后给 primary 与 fallback。
当前状态：taxonomy、论文模式和现有 Skill 分析完成。
输入：`references/problem-taxonomy.md`、`award-paper-patterns.md`、`failure-patterns.md`（若已存在）、用户赛题和数据审计。
任务：建立可人工审查、机器校验的模型选择协议。
文件范围：写 `references/model-selection.md`、`templates/candidate-model-tournament.json`、`scripts/check_plan.py` 及相应测试。
实施步骤：定义 claim；建立透明 baseline；生成 2–3 个不同假设的候选；为每个写适用理由、为何不选更简单方法、假设、数据/参数、复杂度、可辨识性、工程成本、验证和反驳证据；只允许一个 primary，至少一个 fallback；记录 reject 理由、stop conditions 和 team approval；脚本 fail closed 检查必填项。
禁止事项：禁止关键词匹配；禁止先看到结果再无记录换模型；禁止复杂度自带加分；禁止候选没有 refutation；禁止脚本相信 LLM 自报通过。
验证方法：单元测试空计划失败、unknown gate 失败、多 primary 失败、无 fallback 失败、完整计划通过；用 benchmark 的至少 3 类题进行 dry run。
输出文件：`references/model-selection.md`、模板、脚本、测试。
完成标准：没有经过 tournament 的模型不能进入代码实现阶段。
```

## Task 06 — Modeling Cookbooks

```text
背景：详细知识应放 references 并按领域渐进加载。每个方法必须说明适用、不适用、假设、数据、公式、参数、实现、验证、敏感性、失败、替代和论文表达。
当前状态：模型选择协议已定义，能够对 cookbook 候选执行 gates。
输入：`problem-taxonomy.md`、`model-selection.md`、可靠教材/官方库/论文来源、manifest。
任务：建立 forecasting、evaluation、optimization、statistics、graph-network、spatial-modeling、mechanism-modeling、simulation、machine-learning 九个 cookbook。
文件范围：只写 `references/*.md` 对应文件；不把全部内容塞进 SKILL.md。
实施步骤：覆盖任务清单中的 ARIMA/SARIMA/ETS/Prophet/VAR/GM/树模型/SVR/LSTM/Transformer/TSFM；PCA/FA/AHP/entropy/TOPSIS/CRITIC/DEA/fuzzy；LP/MILP/NLP/DP/multiobjective/robust/stochastic/control/GA/SA/PSO/ACO；图、统计、空间、ODE/PDE/compartment、博弈/决策、仿真；每类先给 shared checklist，再给方法表；明确 exact vs heuristic；给 baseline 与 fallback。
禁止事项：禁止宣传式算法介绍；禁止遗漏不适用条件；禁止把 explainability 写成 causality；禁止把商业 solver 当唯一实现。
验证方法：搜索每个必需方法名；抽查每个领域均包含 12 个字段或共享字段+方法行；交叉检查 validation/failure references 无矛盾。
输出文件：九个 cookbook reference。
完成标准：Codex 只加载与当前子问有关的 1–2 个文件即可完成候选论证。
```

## Task 07 — Code Templates

```text
背景：代码模板服务于可复现 baseline 和验证，不为“显得高级”引入深度学习。默认优先 numpy、pandas、scipy、statsmodels、sklearn、networkx、matplotlib；优化按需用 scipy.optimize、PuLP 或 OR-Tools。
当前状态：cookbooks 已定义公式、参数和验证合同。
输入：九个 cookbook、Candidate Tournament、环境报告。
任务：建立一组小而可靠的 Python 起步模板及最小测试。
文件范围：`templates/code/`、`tests/test_templates.py`、可选 `templates/requirements.txt`；不得安装全局依赖。
实施步骤：至少实现 leakage-safe tabular pipeline、rolling forecast backtest、LP/约束验证、graph robustness、ODE integration+conservation、Monte Carlo convergence、Figure Contract plot；每个模板参数化输入、固定/记录 seed、保存结构化结果、检查 NaN/单位/状态；可选依赖缺失时清楚 skip；测试使用小合成数据和已知答案。
禁止事项：禁止硬编码比赛答案；禁止在 import 时执行长任务；禁止网络调用；禁止静默忽略 solver failure；禁止训练深网作为默认模板。
验证方法：`python -m unittest discover -s tests -p 'test_*.py' -v`；compileall；至少一个异常输入测试；结果在两次运行中可复现。
输出文件：代码模板、requirements、测试。
完成标准：所有默认模板在当前环境运行，或因明确 optional dependency 被标记 skip，而不是失败或伪造结果。
```

## Task 08 — Validation System

```text
背景：验证必须与 claim 类型匹配，并分离校准、模型选择和最终评价。研究显示执行式 benchmark 比公式相似度更可靠。
当前状态：模型计划与代码模板可运行。
输入：`model-selection.md`、cookbooks、代码模板、failure patterns、NEMO/OR-Space/OptiBench 的 benchmark 思路。
任务：建立统一验证体系和 claim–evidence schema。
文件范围：写 `references/validation.md`、`references/sensitivity.md`、`templates/claim-evidence.json`，必要时添加测试。
实施步骤：覆盖 train/test、K/Group/Nested CV、time-series split、residual、bootstrap、sensitivity、robustness、ablation、baseline、scenario、solver verification；分别定义 prediction/explanation/mechanism/optimization/ranking/simulation 的证据；优化需重算目标与约束、状态/gap；机理需单位、守恒、极限、参数恢复/可辨识；建立 claim→artifact→command→metric→uncertainty→failure threshold 映射。
禁止事项：禁止用训练拟合作验证；禁止测试集调参；禁止 naive bootstrap 处理依赖数据；禁止仅凭可行解声称最优；禁止一张“效果不错”的图通过验证。
验证方法：对 benchmark 每类题指定适用验证；故意注入 leakage、infeasible solution、non-identifiable parameters，确保 gate 能失败。
输出文件：validation、sensitivity、claim-evidence schema 和测试。
完成标准：每个 headline claim 必须能定位到可复现 artifact 和失败阈值。
```

## Task 09 — Paper Skill

```text
背景：COMAP 官方强调摘要、完整作答、清晰变量/假设、模型动机、测试/误差/灵敏度/稳定性、优缺点和明确结果。CUMCM 规则与 AI 披露会按年变化。
当前状态：执行和验证 artifacts 已可追溯。
输入：`claim-evidence`、`award-paper-patterns.md`、`judges-commentary.md`、当前官方规则、用户指定语言/比赛。
任务：建立 CUMCM 中文论文与 MCM/ICM 英文论文写作模块，包括 Memo/Letter。
文件范围：写 `references/paper-writing.md`、`templates/paper-outline-zh.md`、`templates/paper-outline-en.md`；只生成原创骨架，不复制第三方模板。
实施步骤：要求摘要最后写并逐问给方法/关键数值/验证/结论；章节采用 claim→method/equation→executed result→evidence→interpretation；维护符号单位表、参数来源和图表交叉引用；MCM/ICM 支持 Summary Sheet、Memo/Letter；CUMCM 支持支撑材料与 AI 使用说明；模型变更时使摘要/图表/结论失效并重建。
禁止事项：禁止 AI 套话、奖项预测、公式堆砌、伪造引用、结论越界；禁止把过期模板称官方；禁止在没有结果 artifact 时写数值。
验证方法：摘要中的每个数值在 claim–evidence 中可查；无孤立图表/引用；当前规则逐项 sign-off；人工检查中英文语义一致。
输出文件：paper-writing reference 和两个 outline。
完成标准：可以从结构化结果装配论文，但不会凭空补全模型证据。
```

## Task 10 — Visualization

```text
背景：评委长期批评无标签、无解释、无出处的图。每张图必须承担一个可检查的 claim。
当前状态：论文结构和 claim–evidence 已完成。
输入：结果 artifacts、claim-evidence、paper outline。
任务：建立 Figure Contract 与图表审计规则。
文件范围：写 `references/visualization.md`、`templates/figure-contract.md`，可添加图表测试。
实施步骤：图前填写 claim、必要性、数据变换、横纵轴/单位/范围、编码/图例、baseline、预期模式、不确定性、读者结论、不能证明的内容、来源；建立 claim→图型映射；要求最终尺寸可读、色盲友好、线图优先矢量、结果表和脚本可复现；残差、Pareto、敏感性、空间、网络和机制分别给专用规则。
禁止事项：禁止装饰图、3D 无必要图、截断轴误导、网络 hairball、无 uncertainty 的比较、把 SHAP 当因果、外部图无逐图引用。
验证方法：删除任一图，若不削弱 claim 则应删除；脚本重跑得到相同数据；轴、单位、legend、caption、source 全部通过检查。
输出文件：visualization reference、Figure Contract。
完成标准：论文中每张最终图都有合同和对应 claim-evidence 行。
```

## Task 11 — Anti-AI Modeling Rules

```text
背景：最危险的 AI 建模错误是高置信度地跳过证据：无脑 TOPSIS/AHP/熵权/RF/XGBoost/LSTM、模型堆叠、数据泄漏、随机时间切分、参数无来源、约束漏项、solver 状态不查、无单位、无 baseline/敏感性、结论越界和引用幻觉。
当前状态：前面模块已提供 gates、代码和论文合同。
输入：调研报告、现有 Skill 缺陷、Judges' Commentary、validation、cookbooks。
任务：把失败模式转成检测、修复和阻断规则。
文件范围：写 `references/failure-patterns.md` 和可选 `tests/fixtures/bad_cases/`。
实施步骤：按 selection/formulation、data/computation、validation/writing、compliance 分类；每条给 ID、症状、检测证据、修复、严重度；把 leakage、随机时序切分、solver 未检查、引用不存在、规则违规设为 hard fail；其他高风险需显式 waiver；建立故障注入案例。
禁止事项：禁止泛泛写“注意严谨”；禁止把风格偏好当 hard fail；禁止自动修复后不记录；禁止 AI 自己批准 waiver。
验证方法：至少 20 个模式；每个 hard fail 有 fixture 或可执行检查；报告能列出触发 ID 和受影响 artifact。
输出文件：failure-patterns、bad fixtures/测试。
完成标准：Final Audit 能用稳定 ID 引用问题并阻止提交。
```

## Task 12 — SKILL.md

```text
背景：详细知识已在 references、templates、scripts、benchmarks。入口文件只负责触发、路由、阶段、检查点、状态和加载规则。
当前状态：Task 01–11 的知识与工具已经存在。
输入：所有 references；existing-skill-analysis；environment report；skill-creator 规范。
任务：最后创建或重构 `math-modeling-competition/SKILL.md` 与 `agents/openai.yaml`。
文件范围：只修改 SKILL.md 和 agents/openai.yaml；不得复制 references 内容。
实施步骤：frontmatter 仅 name/description，description 包含所有触发；正文用 imperative；定义 workspace 而非 skill 目录、恢复 decision_log、8 个阶段、9 个领域路由、mandatory gates、artifacts、prohibitions；引用所有按需 reference；保持 <500 行；生成 display_name、25–64 字符 short_description 和显式包含 `$math-modeling-competition` 的 default_prompt；运行 skill-creator quick_validate。
禁止事项：禁止 README、安装指南、更新日志塞入 Skill；禁止复制算法百科；禁止在正文另写 When to Use；禁止遗漏许可证/compliance 路由。
验证方法：`quick_validate.py <skill>`；检查 frontmatter 只有两个字段；所有链接文件存在；用 10 条应触发/不应触发提示做人工测试。
输出文件：SKILL.md、agents/openai.yaml。
完成标准：入口简洁、可发现、可恢复、能按任务加载最少 reference。
```

## Task 13 — Benchmark

```text
背景：MM-Bench 提供真实建模题覆盖；OR-Space 证明多文件 Build/Revise/Explain 比一次性 prompt 更接近 Agent；本项目还必须覆盖竞赛常见反模式。
当前状态：完整 Skill 已可用。
输入：公开历史赛题的原创摘要/元数据、MM-Bench/OR-Space/OptiBench 的设计思想、failure IDs。
任务：构建至少 8 类 benchmark：预测、优化、评价、网络、机理、空间、仿真、政策。
文件范围：`benchmarks/benchmark_cases.json`、`scripts/run_benchmarks.py`、`tests/test_benchmarks.py`；不复制受限完整题面。
实施步骤：每例保存 prompt archetype、expected decomposition、required baseline、reasonable candidates、must-reject conditions、validation、fallback；同时设计 Build、Revise、Explain 模式；评分检查拆题、baseline、候选合理性、验证、模型堆叠、泄漏、fallback；优先确定性规则，开放式部分再用盲审 rubric；记录来源和版权。
禁止事项：禁止训练/测试污染；禁止让评测 Agent看到预期答案；禁止只评最终文风；禁止打包版权不明赛题全文。
验证方法：八类齐全；故障样例能触发对应 failure ID；重复运行确定性分数一致；人工抽查至少 2 例。
输出文件：benchmark JSON、runner、tests、可选 benchmark report。
完成标准：Skill 的关键 gates 有可重复的正/负案例，不只验证 frontmatter。
```

## Task 14 — Final Audit

```text
背景：交付前必须验证目录、来源、许可证、Python、Skill 触发、benchmark、Markdown 与内容质量，并生成可审计报告。
当前状态：Task 00–13 全部完成。
输入：整个 `mathmodel/`、Git 状态、测试和 benchmark 产物。
任务：执行最终审计并只修复范围内的明确问题。
文件范围：可修复 `mathmodel/` 内本任务创建的文件；生成 `mathmodel/audits/FINAL_AUDIT.md`。不要提交/推送，除非用户明确要求。
实施步骤：列目录与 required files；解析 manifest 并检查 ≥30、字段、URL、license/usage；扫描 Markdown 本地链接和核心外链；运行 compileall、unittest、skill quick_validate、audit_skill、check_plan 正负样例、benchmark；核对 SKILL 触发；扫描 TODO、重复段落、AI 套话、奖项预测和无证据数值；核对 COMAP/CUMCM 当前规则链接；检查第三方全文/模板未被打包；记录 git diff/stat。
禁止事项：禁止为了全绿删除失败测试；禁止静默忽略 dead link/无许可证；禁止把网络暂时失败直接判死链；禁止改用户无关文件；禁止伪造测试通过。
验证方法：报告列出每项命令、结果、失败/waiver、已修复和剩余风险；最终 `git status --short` 可解释；所有 hard fail 清零才写 PASS。
输出文件：`audits/FINAL_AUDIT.md`。
完成标准：审计状态为 PASS 或明确 BLOCKED；PASS 时无必需文件缺失、JSON/YAML/Markdown 结构错误、Python 测试失败、许可未知却标可复制、或未处理 hard fail。
```

