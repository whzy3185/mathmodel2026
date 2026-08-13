#!/usr/bin/env python3
"""Build corrected authoritative Q1-Q4 results after adversarial review."""

from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd

from analytic_bounds import A_VOLUME, B_VOLUME, CUBE_VOLUME, Q_A, Q_B, prove_q3, prove_q4
from geometry import connectivity, path_certificates


def run_q1(root: Path) -> list[dict]:
    workbook = root / "data/raw/A/attachment.xlsx"
    output = []
    for sheet in pd.ExcelFile(workbook).sheet_names:
        frame = pd.read_excel(workbook, sheet_name=sheet, header=None)
        coords = frame.iloc[2:, :6].apply(pd.to_numeric, errors="coerce").dropna().to_numpy(float)
        result = connectivity(coords[:, :3], coords[:, 3:])
        broad = connectivity(coords[:, :3], coords[:, 3:], use_broadphase=True)
        if (result.connected, result.edge_count) != (broad.connected, broad.edge_count):
            raise AssertionError(f"Q1 broadphase mismatch: {sheet}")
        output.append({
            "group": sheet,
            "row_count": len(coords),
            "each_row_is_one_A": True,
            "connected": result.connected,
            "conductive_path_1_based": result.path,
            "edge_count": result.edge_count,
            "left_contact_count": result.left_contacts,
            "right_contact_count": result.right_contacts,
            "broadphase_match": True,
            "path_certificates": path_certificates(coords[:, :3], coords[:, 3:], result.path),
        })
    return output


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    requested = [0.005, 0.006, 0.007, 0.010]
    q2 = []
    for fraction in requested:
        count = int(math.floor(fraction * CUBE_VOLUME / A_VOLUME + 0.5))
        log10_failure = count * math.log10(1 - Q_A)
        q2.append({
            "requested_fraction": fraction,
            "a_count": count,
            "achieved_fraction": count * A_VOLUME / CUBE_VOLUME,
            "direct_bridge_probability_lower_bound_expression": f"1 - 10^({log10_failure:.12f})",
            "direct_bridge_probability_lower_bound_float": None,
            "log10_failure_probability_upper_bound": log10_failure,
            "float_note": "The lower bound is strictly below 1; binary64 rounds it to 1, so the log10 failure bound is authoritative.",
        })
    q3 = prove_q3()
    q3["volume_fraction"] = q3["selected_a_count"] * A_VOLUME / CUBE_VOLUME
    q3["reported_percent_2dp"] = round(100 * q3["volume_fraction"], 2)
    q4 = prove_q4()
    q4["selected"]["a_fraction"] = 0.0
    q4["selected"]["b_fraction"] = 57 * B_VOLUME / CUBE_VOLUME
    record = {
        "schema_version": 2,
        "proof_strategy": "direct periodic bridge lower bound plus opposite-electrode contact union upper bound",
        "assumptions": [
            "each attachment row is one A conductor",
            "centers are independent and uniform",
            "A orientations are independent and isotropic",
            "a translated periodic portion remains electrically connected to its parent conductor",
            "only material portions that actually cross a boundary are translated",
        ],
        "geometry": {"q_A": Q_A, "q_B": Q_B, "electrode_gap_layer_probability_per_particle_per_side": 1.8 / 10000},
        "Q1": run_q1(root),
        "Q2": q2,
        "Q3": q3,
        "Q4": q4,
    }
    output = root / "outputs/data/final_results.json"
    output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
