#!/usr/bin/env python3
# AI assistance disclosure: drafted with OpenAI Codex and verified by executable tests.
"""Execute the coupled A/B cost-frontier experiment for question 4."""

from __future__ import annotations

import argparse
import json
import math
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import norm

from geometry import BOX_HALF, BOX_SIDE, ROD_LENGTH, ROD_RADIUS, seeded_a_configuration
from mixed import SPHERE_RADIUS, build_mixed_graph, critical_b_for_a_counts


CUBE_VOLUME = BOX_SIDE**3
A_VOLUME = math.pi * ROD_RADIUS**2 * ROD_LENGTH
B_VOLUME = 4 * math.pi * SPHERE_RADIUS**3 / 3


def count_for_fraction(fraction: float, particle_volume: float) -> int:
    return int(math.floor(fraction * CUBE_VOLUME / particle_volume + 0.5))


def fraction_for_count(count: int, particle_volume: float) -> float:
    return count * particle_volume / CUBE_VOLUME


def wilson(successes: int, trials: int) -> list[float]:
    z = float(norm.ppf(0.975))
    p = successes / trials
    den = 1 + z * z / trials
    center = (p + z * z / (2 * trials)) / den
    half = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials)) / den
    return [max(0.0, center - half), min(1.0, center + half)]


def one_replication(payload: tuple[int, int, int, list[int], bool]) -> list[int]:
    seed, max_a, max_b, a_counts, inner_spheres = payload
    a_centers, a_directions = seeded_a_configuration(seed, max_a)
    b_seed = np.random.SeedSequence(seed).spawn(3)[2]
    b_rng = np.random.default_rng(b_seed)
    b_bound = BOX_HALF - SPHERE_RADIUS if inner_spheres else BOX_HALF
    b_centers = b_rng.uniform(-b_bound, b_bound, size=(max_b, 3))
    graph = build_mixed_graph(a_centers, a_directions, b_centers)
    return critical_b_for_a_counts(graph, a_counts, max_b)


def run(
    replications: int,
    seed: int,
    workers: int,
    max_b_fraction: float,
    inner_spheres: bool,
) -> dict[str, Any]:
    a_counts = list(range(590, 625))
    max_a = max(a_counts)
    max_b = count_for_fraction(max_b_fraction, B_VOLUME)
    child_seeds = [
        int(child.generate_state(1)[0])
        for child in np.random.SeedSequence(seed).spawn(replications)
    ]
    payloads = [(s, max_a, max_b, a_counts, inner_spheres) for s in child_seeds]
    started = time.perf_counter()
    if workers == 1:
        rows = [one_replication(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            rows = list(pool.map(one_replication, payloads, chunksize=1))
    critical = np.asarray(rows, dtype=int)

    frontier: list[dict[str, Any]] = []
    for column, a_count in enumerate(a_counts):
        b_count = None
        stats = None
        for candidate_b in range(max_b + 1):
            successes = int(np.sum(critical[:, column] <= candidate_b))
            interval = wilson(successes, replications)
            if interval[0] >= 0.90:
                b_count = candidate_b
                stats = (successes, interval)
                break
        if b_count is None:
            frontier.append({"a_count": a_count, "status": "not_reached"})
            continue
        a_fraction = fraction_for_count(a_count, A_VOLUME)
        b_fraction = fraction_for_count(b_count, B_VOLUME)
        successes, interval = stats
        frontier.append({
            "a_count": a_count,
            "b_count": b_count,
            "a_fraction": a_fraction,
            "b_fraction": b_fraction,
            "cost_cny": 1000 * (1.05 * a_fraction + 0.05 * b_fraction),
            "successes": successes,
            "trials": replications,
            "probability": successes / replications,
            "wilson_95": interval,
            "status": "confidence_feasible",
        })
    feasible = [row for row in frontier if row["status"] == "confidence_feasible"]
    best = min(feasible, key=lambda row: row["cost_cny"]) if feasible else None
    return {
        "schema_version": 1,
        "seed": seed,
        "replications": replications,
        "max_b_fraction": max_b_fraction,
        "max_a": max_a,
        "max_b": max_b,
        "a_counts": a_counts,
        "sphere_boundary_scenario": "centers constrained inside by radius" if inner_spheres else "uniform centers; outside caps clipped and not reinserted",
        "elapsed_seconds": time.perf_counter() - started,
        "critical_b_counts_by_replication": critical.tolist(),
        "frontier": frontier,
        "best": best,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--replications", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20260821)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--max-b-fraction", type=float, default=0.12)
    parser.add_argument("--inner-spheres", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output or root / "outputs/data/mixed_experiment.json"
    record = run(args.replications, args.seed, args.workers, args.max_b_fraction, args.inner_spheres)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)
    print(json.dumps(record["best"], ensure_ascii=False, indent=2))
    for row in record["frontier"]:
        if row["status"] == "confidence_feasible":
            print(f"A={100*row['a_fraction']:.4f}% B={100*row['b_fraction']:.4f}% cost={row['cost_cny']:.4f}")
        else:
            print(f"A_count={row['a_count']} not reached")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
