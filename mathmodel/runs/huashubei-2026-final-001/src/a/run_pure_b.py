#!/usr/bin/env python3
# AI assistance disclosure: drafted with OpenAI Codex and verified by executable tests.
"""Low-particle pure-B validation for the literal periodic-object model."""

from __future__ import annotations

import argparse
import json
import math
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree
from scipy.stats import norm

from geometry import BOX_HALF, BOX_SIDE, GAP, UnionFind
from mixed import B_B_THRESHOLD, SPHERE_RADIUS


def wilson(k: int, n: int) -> list[float]:
    z = float(norm.ppf(0.975)); p = k / n; den = 1 + z * z / n
    center = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [center - half, center + half]


def critical_b(seed_and_max: tuple[int, int]) -> int:
    seed, max_b = seed_and_max
    rng = np.random.default_rng(seed)
    centers = rng.uniform(-BOX_HALF, BOX_HALF, size=(max_b, 3))
    pairs = cKDTree(centers + BOX_HALF, boxsize=BOX_SIDE).query_pairs(
        B_B_THRESHOLD, output_type="ndarray"
    )
    events: list[list[tuple[int, int]]] = [[] for _ in range(max_b)]
    for i, j in pairs:
        events[int(max(i, j))].append((int(i), int(j)))
    left = centers[:, 0] - SPHERE_RADIUS <= -BOX_HALF + GAP
    right = centers[:, 0] + SPHERE_RADIUS >= BOX_HALF - GAP
    bridge = np.abs(centers[:, 0]) + SPHERE_RADIUS >= BOX_HALF
    left |= bridge; right |= bridge
    source, target = max_b, max_b + 1
    uf = UnionFind(max_b + 2)
    for b in range(max_b):
        if left[b]: uf.union(b, source)
        if right[b]: uf.union(b, target)
        for i, j in events[b]: uf.union(i, j)
        if uf.connected(source, target): return b + 1
    return max_b + 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--replications", type=int, default=50_000)
    parser.add_argument("--max-b", type=int, default=65)
    parser.add_argument("--seed", type=int, default=20260903)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    seeds = [int(x.generate_state(1)[0]) for x in np.random.SeedSequence(args.seed).spawn(args.replications)]
    payloads = [(seed, args.max_b) for seed in seeds]
    if args.workers == 1:
        critical = [critical_b(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            critical = list(pool.map(critical_b, payloads, chunksize=10))
    rows = []
    for count in range(50, args.max_b + 1):
        successes = sum(value <= count for value in critical)
        rows.append({
            "b_count": count,
            "successes": successes,
            "trials": args.replications,
            "probability": successes / args.replications,
            "wilson_95": wilson(successes, args.replications),
        })
    record = {"seed": args.seed, "replications": args.replications, "max_b": args.max_b, "results": rows}
    output = args.output or args.root / "outputs/data/literal_pure_b.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)
    for row in rows:
        if row["b_count"] in {55, 56, 57, 58}:
            print(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
