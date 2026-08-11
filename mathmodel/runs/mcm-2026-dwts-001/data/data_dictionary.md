# Data dictionary

| Field | Unit | Meaning |
|---|---|---|
| celebrity_name | text | Celebrity contestant |
| ballroom_partner | text | Professional dancer |
| celebrity_industry | category | Profession category |
| celebrity_age_during_season | years | Age during the season |
| season | season index | Seasons 1–34 |
| week | ordinal week | Weeks 1–11 |
| results | text | Final/weekly elimination label; forbidden as a predictive feature |
| placement | rank | Final season placement; forbidden as a weekly predictive feature |
| elimination_week | ordinal week | Parsed from `results`; validation constraint only |
| observed_elimination | boolean | Whether the row matches the reported elimination week |
| active | boolean | At least one positive judge score in that week |
| judge_count | judges/dance records | Non-missing judge columns |
| judge_total | points | Sum of positive scores |
| judge_mean | points | Mean of positive scores |
