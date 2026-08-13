# 国赛与研究生数学建模论文资源扩展清单

更新时间：2026-08-13。本文只做资源发现、证据分级和原创方法摘记，不复制许可证不明的论文正文、图表或代码。

## 1. 当前仓库基线

运行目录原有 `source_manifest.json` 共登记 **3 篇 CUMCM 成熟案例**：2023 A、2020 B、2019 A；本地全文 PDF 为 **0 篇**，仅 URL 为 **3 项**，原创方法卡为 **4 张**。这 3 项的“全国一等奖”均以可识别作者仓库自述为主要证据，未在本次检索中逐队匹配官方获奖名单，因此奖项证据记为 **A（作者自述 + 论文/代码）**，不冒充官方 S 级核验。

技能级 `sources/manifest.json` 另有大量工作流、模板、MCM/ICM 和优化基准资源，但其中直接属于 CUMCM 成熟论文的仍主要是上述 3 项；不能把工具仓库数量当作优秀论文数量。

## 2. 扩展后统计

本次清单共 **15 项**：

- GitHub：13 项；Hugging Face：2 项。
- CUMCM 具体论文/代码案例：6 项（其中原有 3、新增 3）。
- 华为杯/中国研究生数学建模竞赛具体案例：6 项。
- 聚合论文库或格式模板：3 项。
- 许可明确、原则上可公开纳入的仓库：7 项；无许可证或内容来源权利链不清、仅可链接/元数据研究：8 项。
- 当前实际落入 `training/external_repos` 的外部全文快照：**0 项**。曾尝试浅克隆许可明确仓库，但网络中断造成不完整工作树，已全部移除，避免提交残缺或权利边界不清的内容。后续若重新搬运，应固定 commit，并把代码许可与论文版权分开复核。

## 3. 高价值资源表

证据等级沿用技能规范：S=官方结果或官方展示；A=作者自述且有完整论文/代码佐证；B=成熟实现或聚合发现源；C=线索。`可公开纳入` 指许可证层面的初筛，不等于可以把第三方题目附件、数据或论文全文一并转载。

| ID | 平台 | 年份/赛题 | 奖项证据 | 许可证与公开边界 | 建议用途 |
|---|---|---|---|---|---|
| CUMCM-2023-A | GitHub | 2023 A 定日镜场 | A：作者自述国一，含论文/代码/答辩 | MIT 仓库；论文著作权仍单独核验。可借鉴代码并署名，不直接复制论文图文 | 机制模型、蒙特卡洛、分层优化、答辩图表 |
| CUMCM-2020-B | GitHub | 2020 B 沙漠游戏 | A：作者自述国一，含论文源码 | 无许可证；仅链接、元数据和原创方法卡 | 精确动态规划、先基线后扩展、状态审计 |
| CUMCM-2019-A | GitHub | 2019 A 高压油管 | A：作者仓库自述国一 | 无许可证；仅链接和原创笔记 | 守恒律、分段数值求解、稳定性验证 |
| CUMCM-2018-B | GitHub | 2018 B RGV 调度 | A：作者自述国一；未见论文全文 | AGPL-3.0；代码可依许可证纳入，题目附件版权另计 | 贪心基线、遗传改进、随机故障仿真 |
| CUMCM-2025-B | GitHub | 2025 B 薄膜干涉 | A：团队自述国一，含论文、TeX、复现脚本 | MIT 仓库；论文和官方附件仍需文件级确认 | 频域分析、残差图、参数灵敏度、可复现论文 |
| CUMCM-2024-A-TEMPLATE | GitHub | 2024 国一作者排版模板 | A：作者自述其 2024 国一论文采用该模板 | MIT；可适配并保留许可，当前官方格式优先 | 图表统一、标题层级、参考文献、黑白打印 |
| GMCM-2019-F | GitHub | 2019 华为杯 F | A：作者称 F 题第一名，含论文/代码 | MPL-2.0；代码修改文件遵守 MPL，论文版权仍单独核验 | 图网络、动态优化、完整论文结构 |
| GMCM-2021-E | GitHub | 2021 华为杯 E | A：作者自述全国一等奖，含论文/代码/数据包 | MIT 仓库；论文与竞赛数据需单独确认 | 三维定位、去噪、K-means、神经网络、3D 轨迹 |
| GMCM-2021-D | GitHub | 2021 华为杯 D | A：作者自述国二，代码与图像 | Apache-2.0；可按许可研究/改编代码，无论文全文 | 多任务学习、分类指标、模型结构图 |
| GMCM-2021-D-STAR | GitHub | 2021 华为杯 D 乳腺癌 | A：作者自述“数模之星”，资源完整 | 无许可证；只登记链接和原创分析 | 特征工程、模型比较、复现清单 |
| GMCM-2023-C | GitHub | 2023 华为杯 C 自动化评审 | A：作者自述全国一等奖，主要为代码 | 无许可证；仅链接/方法元数据 | 大规模评审、组合优化、模块化代码 |
| GMCM-2024-E | GitHub | 2024 华为杯 E | A：作者自述国二，含论文和图表 | 无许可证；只链接，不复制论文/图片 | 多面板科研图、数据—图—结论组织 |
| GMCM-ARCHIVE | GitHub | 2019–2024 研究生赛聚合 | B：聚合站，奖项需逐篇回到官方核验 | 无许可证且约 3.8 GB；严禁整体搬运，仅作发现索引 | 历年赛题、优秀论文入口、官方模板线索 |
| HF-CUMCM-CORPUS | Hugging Face | 1993–2025 CUMCM Markdown/图像语料 | B：文件名含“优秀论文/一等奖”，未逐篇核奖 | 数据集卡标 Apache-2.0，但底层论文来源权利链未逐篇证明；只作检索索引与少量原创分析 | 章节检索、图表类型抽样、跨年份结构统计 |
| HF-CUMCM-KB | Hugging Face | CUMCM 知识库，约 5.9 GB | C：上传者描述，当前缺少逐项证据 | 无明确许可证；仅链接，不下载/再分发 | 发现线索，不作为训练语料或奖项事实依据 |

## 4. 来源链接与固定版本

- CUMCM 2023 A：https://github.com/linggm3/2023_CUMCM_National-First-Prize ，commit `486768dc1aa6e74622f8b0628ae32db3b51291f4`。
- CUMCM 2020 B：https://github.com/seanys/CUMCM2020-Desert-Game ，commit `d5757bbb41e3435b22278bd36156bd8ba2d6274a`。
- CUMCM 2019 A：https://github.com/ZPZhou-lab/MathematicalModeling ，commit `fc5603f1cda3720dd7f96a137667ff96bc68b4ad`。
- CUMCM 2018 B：https://github.com/Hecate2/CUMCM_2018_ProblemB ，commit `2a5c621d69ca489df62b826ec064b121d7227174`。
- CUMCM 2025 B：https://github.com/CUMCM-2025B-Team/CUMCM-2025-Problem-B ，检索时 HEAD `78c70dad9809828e1de6dd5405bf2e4879aa7316`。
- CUMCM 国一作者模板：https://github.com/Sustainable-Enjoyment/CUMCM-LaTeX-Template ，commit `27e8354a117c90510a770a74b2e98f7d65490465`。
- 华为杯 2019 F：https://github.com/qssxbhxy/2019GMCM ，commit `5b1f8da482b25f4daf6549ad7b7e2a3c43ed1c8c`。
- 华为杯 2021 E：https://github.com/hiyouga/HuaweiCup2021-MCM-ProblemE ，commit `f800024df78f5520ca73355430b37d91be5d23be`。
- 华为杯 2021 D 国二：https://github.com/rnzhiw/HuaweiCupMathModel ，commit `3058563020ca3b3c90eea1f12a8523306f082ca1`。
- 华为杯 2021 D 数模之星：https://github.com/DongZhouGu/MathModel-Pretrain 。
- 华为杯 2023 C：https://github.com/K1XE/Optimized-design-for-large-scale-competition-marking 。
- 华为杯 2024 E：https://github.com/LY-zhang-yi-hao/Huawei_Mathcup_OpenAccess 。
- 研究生赛聚合：https://github.com/zhanwen/MathModel ，commit `cd5be91735ebf11d5ee52eb170e86a6d07131977`。
- Hugging Face CUMCM 语料：https://huggingface.co/datasets/IDEA-FinAI/Mathematical_Modeling_Speciale_Dataset_v0.1 ，revision `da13d6456dee8f3a9387ca17366d7531660ff323`。
- Hugging Face CUMCM 知识库：https://huggingface.co/datasets/Jzx123456789/cumcm-knowledge-base ，revision `982a31054c6a744ed1ed6fb53cfe24d85649b048`。

## 5. 对当前论文最值得迁移的做法

1. **摘要采用“方法—结果—验证—结论”闭环**：每问至少给一个定量结果，不以算法名堆砌代替贡献。
2. **图形围绕主张设计**：机制示意图解释空间关系，阈值图显示上下界，三维图只在确实表达空间方向或路径时使用；每张图必须有单位、图例和一句可检验结论。
3. **基线与改进同图比较**：优秀案例常把解析/简单基线与优化模型并置，再用残差、敏感性或极端场景证明改进不是装饰。
4. **表格承担精确值，图承担趋势**：不要把几十个数字堆在折线图中，也不要用三维柱状图制造透视误差。
5. **格式来源优先级**：当前竞赛官方格式 > 当年官方模板 > 获奖论文习惯 > 通用科研排版。不能因为“国一模板”而覆盖华数杯现行规则。

## 6. 使用边界

- “MIT/Apache/MPL/AGPL 仓库”不自动意味着其中收录的官方赛题、附件、第三方数据和参赛论文都采用同一许可证；必须做文件级判断。
- 无许可证仓库默认保留全部版权：可链接、阅读、用自己的语言总结，但不能复制代码、全文或图表到公开仓库。
- Hugging Face 数据集卡的许可证是上传者声明；面对由历年论文汇编而成的派生语料，若缺乏原作者授权链，不将其作为可再分发全文或直接训练语料。
- 奖项若没有官方名单与队号/作者的精确匹配，只写“作者自述”，不写“官方核验”。
