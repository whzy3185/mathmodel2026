# Evaluation and MCDM Cookbook

First decide whether a scalar ranking is scientifically meaningful. Separate measurement construction from stakeholder preference.

| Method | Use | Do not use | Assumptions/formulation | Validation and alternative |
|---|---|---|---|---|
| PCA | reduce correlated numeric indicators | interpret PCs as preferences | orthogonal variance directions | scaling/loadings stability; factor model |
| Factor analysis | latent constructs with multiple indicators | tiny sample or causal ranking | covariance from latent factors + error | fit/reliability/rotation stability; PCA |
| AHP | transparent pairwise expert priorities | many criteria/inconsistent judgments | reciprocal comparison eigenvector | consistency ratio, expert sensitivity; swing weighting |
| Entropy weight | weight dispersion as information | dispersion ≠ importance | normalized entropy inverse | outlier/range sensitivity; equal/CRITIC |
| CRITIC | objective contrast and conflict | correlations unstable | SD × conflict weights | bootstrap weights; equal weights |
| TOPSIS | distance-to-ideal compromise after valid scaling | compensability or ordinal scales invalid | weighted normalized distances | rank reversal/normalization/weight sensitivity; Pareto |
| DEA | relative efficiency with inputs/outputs | too many variables for units | frontier LP efficiency | leave-one-out, returns-to-scale; SFA |
| Fuzzy evaluation | linguistic uncertainty with justified membership | memberships invented post hoc | membership aggregation | membership/weight sensitivity; probabilistic model |

For every index give direction, unit, transformation, missing-data rule, redundancy/double-counting audit, weight provenance and compensability. Compare equal-weight and dominance/Pareto baselines. Report rank intervals, top-k overlap and reversal conditions, not only a final table.

