#!/usr/bin/env python3
# AI assistance disclosure: drafted with OpenAI Codex and verified by executable tests.
"""Held-out direct comparison of the selected mixed and pure-A candidates."""

from __future__ import annotations

import argparse
import json
import math
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from scipy.stats import norm

from geometry import BOX_HALF, seeded_a_configuration
from mixed import SPHERE_RADIUS, build_mixed_graph, critical_b_for_a_counts


CASES = [
    {"name": "selected_0A_57B", "a_count": 0, "b_count": 57},
    {"name": "cheaper_0A_56B", "a_count": 0, "b_count": 56},
    {"name": "cheaper_1A_48B", "a_count": 1, "b_count": 48},
    {"name": "cheaper_2A_39B", "a_count": 2, "b_count": 39},
    {"name": "pure_8A", "a_count": 8, "b_count": 0},
]
A_VOLUME = math.pi * 30**2 * 5000
B_VOLUME = 4 * math.pi * SPHERE_RADIUS**3 / 3
CUBE_VOLUME = 10_000.0**3


def wilson(k: int, n: int) -> list[float]:
    z = float(norm.ppf(0.975)); p = k / n; den = 1 + z * z / n
    center = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [center - half, center + half]


def replicate(payload: tuple[int, bool]) -> list[bool]:
    seed, inner_spheres = payload
    max_a, max_b = max(x["a_count"] for x in CASES), max(x["b_count"] for x in CASES)
    a_centers, a_directions = seeded_a_configuration(seed, max_a)
    b_seed = np.random.SeedSequence(seed).spawn(3)[2]
    b_rng = np.random.default_rng(b_seed)
    bound = BOX_HALF - SPHERE_RADIUS if inner_spheres else BOX_HALF
    b_centers = b_rng.uniform(-bound, bound, size=(max_b, 3))
    graph = build_mixed_graph(a_centers, a_directions, b_centers)
    a_counts = sorted(set(x["a_count"] for x in CASES))
    critical = dict(zip(a_counts, critical_b_for_a_counts(graph, a_counts, max_b)))
    return [critical[x["a_count"]] <= x["b_count"] for x in CASES]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--replications", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260831)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--inner-spheres", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    seeds = [int(x.generate_state(1)[0]) for x in np.random.SeedSequence(args.seed).spawn(args.replications)]
    payloads = [(seed, args.inner_spheres) for seed in seeds]
    if args.workers == 1:
        raw = [replicate(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            raw = list(pool.map(replicate, payloads, chunksize=1))
    outcomes = np.asarray(raw, dtype=bool)
    results = []
    for index, case in enumerate(CASES):
        successes = int(outcomes[:, index].sum())
        a_fraction = case["a_count"] * A_VOLUME / CUBE_VOLUME
        b_fraction = case["b_count"] * B_VOLUME / CUBE_VOLUME
        results.append({
            **case,
            "a_fraction": a_fraction,
            "b_fraction": b_fraction,
            "cost_cny": 1000 * (1.05 * a_fraction + 0.05 * b_fraction),
            "successes": successes,
            "trials": args.replications,
            "probability": successes / args.replications,
            "wilson_95": wilson(successes, args.replications),
            "confidence_feasible": wilson(successes, args.replications)[0] >= 0.90,
        })
    record = {
        "schema_version": 1,
        "seed": args.seed,
        "replications": args.replications,
        "sphere_boundary_scenario": "inner-center sensitivity" if args.inner_spheres else "uniform-center clipped-cap primary",
        "results": results,
    }
    output = args.output or args.root / "outputs/data/q4_validation.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
