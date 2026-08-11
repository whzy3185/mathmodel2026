#!/usr/bin/env python3
# AI assistance disclosure: drafted with OpenAI Codex and verified by executable tests.
"""Execute Q1 and the coupled pure-A Monte Carlo experiment for Q2-Q3."""

from __future__ import annotations

import argparse
import json
import math
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import norm

from geometry import (
    BOX_HALF,
    BOX_SIDE,
    ROD_LENGTH,
    ROD_RADIUS,
    connectivity,
    critical_prefix,
    infer_periodic_identity_edges,
    seeded_a_configuration,
)


ROD_VOLUME = math.pi * ROD_RADIUS**2 * ROD_LENGTH
CUBE_VOLUME = BOX_SIDE**3
SINGLE_A_PERIODIC_BRIDGE = 0.25 + 2 * ROD_RADIUS * (math.pi / 4) / BOX_SIDE


def wilson(successes: int, trials: int, confidence: float = 0.95) -> list[float]:
    if trials == 0:
        return [float("nan"), float("nan")]
    z = float(norm.ppf((1 + confidence) / 2))
    p = successes / trials
    denominator = 1 + z * z / trials
    center = (p + z * z / (2 * trials)) / denominator
    half = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials)) / denominator
    return [max(0.0, center - half), min(1.0, center + half)]


def rods_for_fraction(fraction: float) -> int:
    return int(math.floor(fraction * CUBE_VOLUME / ROD_VOLUME + 0.5))


def achieved_fraction(rods: int) -> float:
    return rods * ROD_VOLUME / CUBE_VOLUME


def one_replication(payload: tuple[int, int]) -> tuple[int, dict[str, int], list[float]]:
    seed, max_rods = payload
    centers, directions = seeded_a_configuration(seed, max_rods)
    critical, diagnostics = critical_prefix(centers, directions)
    moments = np.concatenate((directions.mean(axis=0), np.mean(directions**2, axis=0))).tolist()
    return critical, diagnostics, moments


def run_q1(root: Path) -> dict[str, Any]:
    workbook = root / "data/raw/A/attachment.xlsx"
    results: list[dict[str, Any]] = []
    for sheet in pd.ExcelFile(workbook).sheet_names:
        frame = pd.read_excel(workbook, sheet_name=sheet, header=None)
        coords = frame.iloc[2:, :6].apply(pd.to_numeric, errors="coerce").dropna().to_numpy(float)
        identity = infer_periodic_identity_edges(coords[:, :3], coords[:, 3:])
        result = connectivity(coords[:, :3], coords[:, 3:], identity_edges=identity)
        broad = connectivity(
            coords[:, :3], coords[:, 3:], use_broadphase=True, identity_edges=identity
        )
        if (result.connected, result.edge_count) != (broad.connected, broad.edge_count):
            raise AssertionError(f"broad phase mismatch in {sheet}")
        results.append({
            "group": sheet,
            "fragment_count": int(len(coords)),
            "connected": result.connected,
            "conductive_path_1_based": result.path,
            "edge_count": result.edge_count,
            "left_contact_count": result.left_contacts,
            "right_contact_count": result.right_contacts,
            "minimum_accepted_edge_threshold_margin_nm": result.minimum_margin_nm,
            "broadphase_match": True,
            "periodic_identity_edge_count": int(len(identity)),
        })
    return {"model": "finite-axis distance graph", "axis_threshold_nm": 61.8, "groups": results}


def run_monte_carlo(replications: int, max_fraction: float, seed: int, workers: int) -> dict[str, Any]:
    max_rods = rods_for_fraction(max_fraction)
    seed_sequence = np.random.SeedSequence(seed)
    child_seeds = [int(child.generate_state(1)[0]) for child in seed_sequence.spawn(replications)]
    started = time.perf_counter()
    payloads = [(child_seed, max_rods) for child_seed in child_seeds]
    if workers == 1:
        raw = [one_replication(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            raw = list(pool.map(one_replication, payloads, chunksize=1))
    elapsed = time.perf_counter() - started
    critical = np.asarray([item[0] for item in raw], dtype=int)
    diagnostics = [item[1] for item in raw]
    moments = np.asarray([item[2] for item in raw])

    requested = [0.005, 0.006, 0.007, 0.010]
    q2 = []
    for fraction in requested:
        count = rods_for_fraction(fraction)
        if count > max_rods:
            log10_failure = count * math.log10(1 - SINGLE_A_PERIODIC_BRIDGE)
            q2.append({
                "requested_volume_fraction": fraction,
                "rod_count": count,
                "achieved_volume_fraction": achieved_fraction(count),
                "simulation_not_run_at_count": True,
                "direct_bridge_probability_lower_bound": 1 - 10**log10_failure,
                "log10_failure_probability_upper_bound": log10_failure,
            })
            continue
        successes = int(np.sum(critical <= count))
        q2.append({
            "requested_volume_fraction": fraction,
            "rod_count": count,
            "achieved_volume_fraction": achieved_fraction(count),
            "successes": successes,
            "trials": replications,
            "probability": successes / replications,
            "wilson_95": wilson(successes, replications),
        })

    threshold_count = None
    threshold_stats = None
    for count in range(1, max_rods + 1):
        successes = int(np.sum(critical <= count))
        interval = wilson(successes, replications)
        if interval[0] >= 0.90:
            threshold_count = count
            threshold_stats = (successes, interval)
            break
    q3: dict[str, Any]
    if threshold_count is None:
        q3 = {"status": "not_reached", "max_fraction": max_fraction}
    else:
        successes, interval = threshold_stats
        lower_count = threshold_count - 1
        lower_successes = int(np.sum(critical <= lower_count)) if lower_count else 0
        q3 = {
            "status": "resolved_on_particle_grid",
            "criterion": "95% Wilson lower bound >= 0.90",
            "rod_count": threshold_count,
            "achieved_volume_fraction": achieved_fraction(threshold_count),
            "reported_percent_2dp": round(100 * achieved_fraction(threshold_count), 2),
            "successes": successes,
            "trials": replications,
            "probability": successes / replications,
            "wilson_95": interval,
            "immediate_lower_neighbor": {
                "rod_count": lower_count,
                "achieved_volume_fraction": achieved_fraction(lower_count),
                "successes": lower_successes,
                "wilson_95": wilson(lower_successes, replications),
            },
        }

    checkpoints = sorted(set(max(2, int(x)) for x in np.linspace(replications / 10, replications, 10)))
    convergence = []
    for n in checkpoints:
        row = {"trials": n}
        for fraction in requested:
            count = rods_for_fraction(fraction)
            successes = int(np.sum(critical[:n] <= count))
            row[f"p_{100*fraction:.2f}pct"] = successes / n
        convergence.append(row)

    return {
        "schema_version": 1,
        "seed": seed,
        "replications": replications,
        "max_fraction": max_fraction,
        "max_rods": max_rods,
        "elapsed_seconds": elapsed,
        "critical_prefix_counts": critical.tolist(),
        "q2": q2,
        "q3": q3,
        "convergence": convergence,
        "orientation_diagnostics": {
            "mean_components": moments[:, :3].mean(axis=0).tolist(),
            "mean_squared_components": moments[:, 3:].mean(axis=0).tolist(),
            "target_mean": [0.0, 0.0, 0.0],
            "target_mean_squared": [1 / 3, 1 / 3, 1 / 3],
        },
        "performance_diagnostics": {
            "mean_fragments": float(np.mean([x["fragments"] for x in diagnostics])),
            "mean_conductive_edges": float(np.mean([x["conductive_edges"] for x in diagnostics])),
            "mean_broadphase_pairs": float(np.mean([x["broadphase_pairs"] for x in diagnostics])),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--replications", type=int, default=200)
    parser.add_argument("--max-fraction", type=float, default=0.015)
    parser.add_argument("--seed", type=int, default=20260811)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output or root / "outputs/data/pure_a_experiment.json"
    record = {
        "q1": run_q1(root),
        "pure_a_monte_carlo": run_monte_carlo(
            args.replications, args.max_fraction, args.seed, args.workers
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)
    for group in record["q1"]["groups"]:
        print(group["group"], group["connected"], group["conductive_path_1_based"])
    print(json.dumps(record["pure_a_monte_carlo"]["q2"], ensure_ascii=False, indent=2))
    print(json.dumps(record["pure_a_monte_carlo"]["q3"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
