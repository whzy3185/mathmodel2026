# Mathematical Modeling Failure Pattern Library

## Selection and formulation

| ID | Failure | Detection | Repair |
|---|---|---|---|
| F01 | keyword → TOPSIS/AHP/entropy | no decision semantics or alternatives | define preference model and challenge need for ranking |
| F02 | keyword → RF/XGBoost/LSTM | no baseline or data-capacity argument | run simple baseline and learning curve |
| F03 | model stacking as decoration | components have no causal/data dependency | keep only components with ablation value |
| F04 | equations without meaning | symbols lack units/mechanism | symbol-unit table and verbal interpretation |
| F05 | arbitrary objective | weights lack source/trade-off | normalize meaningfully; elicit or analyze Pareto front |
| F06 | missing constraints | solution violates real operation | stakeholder/process constraint audit |
| F07 | exact/heuristic confusion | “optimal” without bound/status | report gap/bound or say best-found feasible |
| F08 | unidentifiable mechanism | many parameter sets fit equally | profile likelihood, reduce/reparameterize |

## Data and computation

| ID | Failure | Detection | Repair |
|---|---|---|---|
| F09 | data leakage | preprocessing/target info crosses split | fit pipeline inside split; provenance diagram |
| F10 | random time split | future samples train the past | rolling/expanding-window evaluation |
| F11 | deep learning on small data | parameter count dwarfs information | regularized/classical baseline or transfer with evidence |
| F12 | overfitting | large train–validation gap/unstable folds | simplify, regularize, nested selection |
| F13 | parameter source missing | value appears only in code/prose | parameter ledger with source/range/unit |
| F14 | unchecked solver result | status/gap/violations absent | fail closed on solver status; recompute constraints |
| F15 | no unit/scale check | inconsistent magnitudes/signs | dimensional analysis and nondimensionalization |
| F16 | stochastic cherry-pick | one favorable seed | fixed seed set, distribution and uncertainty |

## Validation and writing

| ID | Failure | Detection | Repair |
|---|---|---|---|
| F17 | accuracy only | no residual/calibration/decision metric | claim-specific diagnostics and baseline |
| F18 | no sensitivity/robustness | conclusion rests on fixed inputs | perturb high-uncertainty inputs and scenarios |
| F19 | weak baseline | complex method compared with nothing | domain-credible naive/reduced baseline |
| F20 | AI-style summary | generic process, no numbers | write last; methods + concrete results + limits |
| F21 | formula dump | equations not used later | connect each equation to parameter/result/claim |
| F22 | decorative figures | no claim, units, or takeaway | Figure Contract; delete if claim unchanged |
| F23 | conclusion overreach | causal/policy claim exceeds design | calibrate verbs and state scope/uncertainty |
| F24 | missing limitations | paper presents universal certainty | list structural, data, computational limits |
| F25 | citation hallucination | source cannot be opened/located | verify DOI/official URL and quoted fact |
| F26 | rules/template drift | cached page limits or formats | re-check official current notice at submission |

Any F09, F10, F14, F25 or compliance failure blocks submission. Other failures require an explicit waiver with rationale.

