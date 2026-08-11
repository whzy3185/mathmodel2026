# EDA report

- Raw shape: 421 rows × 53 columns.
- Processed shape: 4199 contestant-week rows × 16 columns.
- Exact duplicate raw rows: 0.
- Missing raw cells: 4797; most weekly missingness is structural because seasons have different lengths and usually three judges.
- Age range: 14–82 years. No age values were silently clipped.
- Active contestant-weeks: 2777.
- Elimination-week groups: 232 exactly one, 71 none, 32 multiple. These groups require separate constraints.
- Judge-mean versus final-placement Pearson correlation on active rows: -0.590; repeated contestant weeks make this descriptive, not inferential.
- Fan votes are absent, so supervised fan-vote validation is impossible. Validation must use outcome compatibility and uncertainty/set width.
- Temporal ordering is season then week. Any evaluation across time must hold out entire later weeks/seasons; no random weekly split.
- `results`, `placement`, and future-week scores are leakage for weekly prediction and may only define validation constraints.
- Units: judge scores are points, age is years, placement is rank, and future fan estimates are weekly shares summing to one.
- Spatial CRS: not applicable; geography is categorical only.

Machine-readable counts and the full missing-value profile are in `data/eda_summary.json`.
