#!/usr/bin/env python3
"""Create an immutable-data manifest, tidy contestant-week table, and EDA report."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def elimination_week(value: object) -> float:
    match = re.search(r"Eliminated Week (\d+)", str(value), flags=re.IGNORECASE)
    return float(match.group(1)) if match else np.nan


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.run_root.resolve()
    raw = args.raw.resolve()
    data = pd.read_csv(raw, na_values=["N/A"])
    score_columns = [column for column in data.columns if re.fullmatch(r"week\d+_judge\d+_score", column)]

    rows: list[dict] = []
    metadata = [
        "celebrity_name", "ballroom_partner", "celebrity_industry", "celebrity_homestate",
        "celebrity_homecountry/region", "celebrity_age_during_season", "season", "results", "placement"
    ]
    for _, contestant in data.iterrows():
        eliminated = elimination_week(contestant["results"])
        for week in range(1, 12):
            columns = [f"week{week}_judge{judge}_score" for judge in range(1, 5)]
            scores = pd.to_numeric(contestant[columns], errors="coerce")
            observed = scores.dropna()
            if observed.empty:
                continue
            positive = observed[observed > 0]
            active = not positive.empty
            row = {key: contestant[key] for key in metadata}
            row.update(
                {
                    "week": week,
                    "elimination_week": eliminated,
                    "observed_elimination": bool(not np.isnan(eliminated) and week == eliminated),
                    "active": active,
                    "judge_count": int(observed.size),
                    "judge_total": float(positive.sum()) if active else 0.0,
                    "judge_mean": float(positive.mean()) if active else 0.0,
                }
            )
            rows.append(row)
    tidy = pd.DataFrame(rows).sort_values(["season", "week", "placement", "celebrity_name"])
    processed = root / "data" / "processed" / "contestant_weeks.csv"
    tidy.to_csv(processed, index=False)

    duplicates = int(data.duplicated().sum())
    missing = {column: int(data[column].isna().sum()) for column in data.columns}
    age = pd.to_numeric(data["celebrity_age_during_season"], errors="coerce")
    active = tidy[tidy["active"]].copy()
    active["judge_share"] = active.groupby(["season", "week"])["judge_total"].transform(
        lambda values: values / values.sum() if values.sum() else np.nan
    )
    evaluable = active.groupby(["season", "week"])["observed_elimination"].sum()
    correlation = float(active[["judge_mean", "placement"]].corr().iloc[0, 1])
    eda = {
        "raw_shape": [int(data.shape[0]), int(data.shape[1])],
        "processed_shape": [int(tidy.shape[0]), int(tidy.shape[1])],
        "exact_duplicate_rows": duplicates,
        "missing_cells": int(data.isna().sum().sum()),
        "missing_by_column": missing,
        "age_range": [float(age.min()), float(age.max())],
        "seasons": [int(data["season"].min()), int(data["season"].max())],
        "active_contestant_weeks": int(active.shape[0]),
        "weeks_with_exactly_one_reported_elimination": int((evaluable == 1).sum()),
        "weeks_with_no_reported_elimination": int((evaluable == 0).sum()),
        "weeks_with_multiple_reported_eliminations": int((evaluable > 1).sum()),
        "judge_mean_placement_correlation": correlation,
        "fan_vote_target_available": False,
        "leakage_fields_forbidden_in_weekly_prediction": ["results", "placement", "future-week scores"],
        "spatial_crs": "not applicable"
    }
    eda_json = root / "data" / "eda_summary.json"
    eda_json.write_text(json.dumps(eda, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "generated_by": "src/common/prepare_data.py",
        "datasets": [
            {
                "dataset_id": "DATA-RAW-C",
                "source": "official COMAP 2026 Problem C attachment",
                "url": "https://contest.comap.com/undergraduate/contests/mcm/contests/2026/problems/2026_MCM_Problem_C_Data.csv",
                "access_date": "2026-08-11",
                "license": "COMAP page states problems may be reproduced for academic/research purposes; dataset-specific license not separately stated",
                "original_filename": "2026_MCM_Problem_C_Data.csv",
                "stored_path": str(raw.relative_to(root)).replace("\\", "/"),
                "sha256": sha256(raw),
                "rows": int(data.shape[0]), "columns": int(data.shape[1]),
                "units": {"judge_score": "points (1–10 per judge/dance average)", "age": "years", "placement": "rank"},
                "time_range": "seasons 1–34, weeks 1–11",
                "geography": "contestant home state/country fields",
                "missing_values": int(data.isna().sum().sum()),
                "transformations": []
            },
            {
                "dataset_id": "DATA-PROCESSED-C",
                "source": "DATA-RAW-C",
                "stored_path": str(processed.relative_to(root)).replace("\\", "/"),
                "sha256": sha256(processed),
                "rows": int(tidy.shape[0]), "columns": int(tidy.shape[1]),
                "units": {"judge_total": "points", "judge_mean": "points", "week": "ordinal week"},
                "time_range": "seasons 1–34, weeks 1–11",
                "geography": "copied contestant metadata; no spatial calculation",
                "missing_values": int(tidy.isna().sum().sum()),
                "transformations": ["wide weekly scores reshaped to contestant-week rows", "structural post-elimination zeros flagged inactive", "judge totals and means calculated from observed positive scores"]
            }
        ]
    }
    manifest_path = root / "data" / "provenance" / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    dictionary = """# Data dictionary\n\n| Field | Unit | Meaning |\n|---|---|---|\n| celebrity_name | text | Celebrity contestant |\n| ballroom_partner | text | Professional dancer |\n| celebrity_industry | category | Profession category |\n| celebrity_age_during_season | years | Age during the season |\n| season | season index | Seasons 1–34 |\n| week | ordinal week | Weeks 1–11 |\n| results | text | Final/weekly elimination label; forbidden as a predictive feature |\n| placement | rank | Final season placement; forbidden as a weekly predictive feature |\n| elimination_week | ordinal week | Parsed from `results`; validation constraint only |\n| observed_elimination | boolean | Whether the row matches the reported elimination week |\n| active | boolean | At least one positive judge score in that week |\n| judge_count | judges/dance records | Non-missing judge columns |\n| judge_total | points | Sum of positive scores |\n| judge_mean | points | Mean of positive scores |\n"""
    (root / "data" / "data_dictionary.md").write_text(dictionary, encoding="utf-8")
    report = f"""# EDA report\n\n- Raw shape: {data.shape[0]} rows × {data.shape[1]} columns.\n- Processed shape: {tidy.shape[0]} contestant-week rows × {tidy.shape[1]} columns.\n- Exact duplicate raw rows: {duplicates}.\n- Missing raw cells: {eda['missing_cells']}; most weekly missingness is structural because seasons have different lengths and usually three judges.\n- Age range: {age.min():.0f}–{age.max():.0f} years. No age values were silently clipped.\n- Active contestant-weeks: {active.shape[0]}.\n- Elimination-week groups: {(evaluable == 1).sum()} exactly one, {(evaluable == 0).sum()} none, {(evaluable > 1).sum()} multiple. These groups require separate constraints.\n- Judge-mean versus final-placement Pearson correlation on active rows: {correlation:.3f}; repeated contestant weeks make this descriptive, not inferential.\n- Fan votes are absent, so supervised fan-vote validation is impossible. Validation must use outcome compatibility and uncertainty/set width.\n- Temporal ordering is season then week. Any evaluation across time must hold out entire later weeks/seasons; no random weekly split.\n- `results`, `placement`, and future-week scores are leakage for weekly prediction and may only define validation constraints.\n- Units: judge scores are points, age is years, placement is rank, and future fan estimates are weekly shares summing to one.\n- Spatial CRS: not applicable; geography is categorical only.\n\nMachine-readable counts and the full missing-value profile are in `data/eda_summary.json`.\n"""
    (root / "data" / "eda_report.md").write_text(report, encoding="utf-8")
    print(json.dumps({"processed": str(processed), "sha256": sha256(processed), "eda": eda}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
