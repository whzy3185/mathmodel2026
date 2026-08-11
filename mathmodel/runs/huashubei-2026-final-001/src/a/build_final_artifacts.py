#!/usr/bin/env python3
# AI assistance disclosure: drafted with OpenAI Codex and verified by executable tests.
"""Build the authoritative result summary and claim-bearing figures."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wilson(k: int, n: int) -> list[float]:
    z = float(norm.ppf(0.975)); p = k / n; den = 1 + z * z / n
    center = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [center - half, center + half]


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    data = root / "outputs/data"
    figures = root / "outputs/figures"
    figures.mkdir(parents=True, exist_ok=True)
    q3_path = data / "literal_q3_final_50000.json"
    q4_path = data / "literal_q4_final_100000.json"
    q3_raw = json.loads(q3_path.read_text(encoding="utf-8"))
    q4_raw = json.loads(q4_path.read_text(encoding="utf-8"))

    q_a = 0.25 + 60 * (math.pi / 4) / 10_000
    q_b = 400 / 10_000
    volume_a = math.pi * 30**2 * 5000
    volume_b = 4 * math.pi * 200**3 / 3
    cube_volume = 10_000**3
    requested = [0.005, 0.006, 0.007, 0.010]
    q2 = []
    for fraction in requested:
        count = int(math.floor(fraction * cube_volume / volume_a + 0.5))
        log10_failure = count * math.log10(1 - q_a)
        q2.append({
            "requested_fraction": fraction,
            "a_count": count,
            "achieved_fraction": count * volume_a / cube_volume,
            "direct_bridge_probability_lower_bound": 1 - 10**log10_failure,
            "log10_failure_probability_upper_bound": log10_failure,
        })

    critical = q3_raw["pure_a_monte_carlo"]["critical_prefix_counts"]
    q3_counts = []
    for count in range(1, 11):
        successes = sum(value <= count for value in critical)
        q3_counts.append({
            "a_count": count,
            "direct_bridge_probability": 1 - (1 - q_a) ** count,
            "graph_probability": successes / len(critical),
            "graph_wilson_95": wilson(successes, len(critical)),
        })

    q1 = q3_raw["q1"]
    q4 = q4_raw["results"]
    selected = next(row for row in q4 if row["name"] == "selected_0A_57B")
    summary = {
        "schema_version": 1,
        "model_interpretation": "wrapped fragments remain one conductive medium; literal official wording",
        "geometry": {
            "q_A_single_rod_periodic_x_bridge": q_a,
            "q_B_single_sphere_periodic_x_bridge": q_b,
            "a_axis_surrogate_is_only_used_as_an_optimistic_refutation_model": True,
        },
        "Q1": q1,
        "Q2": q2,
        "Q3": {
            "minimum_a_count": 8,
            "volume_fraction": 8 * volume_a / cube_volume,
            "reported_percent_2dp": 0.01,
            "validation": q3_counts,
            "replications": len(critical),
            "seed": 20260902,
        },
        "Q4": {
            "selected": selected,
            "all_tested_candidates": q4,
            "replications": q4_raw["replications"],
            "seed": q4_raw["seed"],
            "claim_scope": "lowest confidence-feasible candidate after exhaustive direct-bridge enumeration and explicit testing of every cheaper frontier neighbor",
        },
        "source_hashes": {str(q3_path.relative_to(root)): sha256(q3_path), str(q4_path.relative_to(root)): sha256(q4_path)},
    }
    summary_path = data / "final_results.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    plt.rcParams.update({"font.size": 10, "axes.unicode_minus": False})
    counts = np.arange(1, 11)
    direct = np.array([row["direct_bridge_probability"] for row in q3_counts])
    graph = np.array([row["graph_probability"] for row in q3_counts])
    intervals = np.array([row["graph_wilson_95"] for row in q3_counts])
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.plot(counts, direct, color="#176B87", marker="o", label="Direct periodic bridge (analytic)")
    ax.errorbar(counts, graph, yerr=[graph - intervals[:, 0], intervals[:, 1] - graph], fmt="s", color="#C84B31", capsize=3, label="Full graph simulation (95% Wilson)")
    ax.axhline(0.90, color="#303030", linestyle="--", linewidth=1, label="Target 0.90")
    ax.set(xlabel="Number of A conductors", ylabel="Conduction probability", xlim=(1, 10), ylim=(0.15, 1.01))
    ax.grid(alpha=0.25); ax.legend(loc="lower right"); fig.tight_layout()
    fig.savefig(figures / "F1_q3_threshold.png", dpi=220); fig.savefig(figures / "F1_q3_threshold.pdf"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    x = [100 * row["requested_fraction"] for row in q2]
    y = [row["log10_failure_probability_upper_bound"] for row in q2]
    ax.plot(x, y, color="#176B87", marker="o", linewidth=2)
    for xx, yy in zip(x, y): ax.annotate(f"{yy:.1f}", (xx, yy), xytext=(0, 7), textcoords="offset points", ha="center")
    ax.set(xlabel="A volume fraction (%)", ylabel="log10 upper bound of failure probability")
    ax.grid(alpha=0.25); fig.tight_layout()
    fig.savefig(figures / "F2_q2_failure_scale.png", dpi=220); fig.savefig(figures / "F2_q2_failure_scale.pdf"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    costs = np.array([row["cost_cny"] for row in q4])
    probs = np.array([row["probability"] for row in q4])
    cis = np.array([row["wilson_95"] for row in q4])
    colors = ["#1B7F5A" if row["confidence_feasible"] else "#C84B31" for row in q4]
    for index, row in enumerate(q4):
        ax.errorbar(
            costs[index], probs[index],
            yerr=[[probs[index] - cis[index, 0]], [cis[index, 1] - probs[index]]],
            fmt="o", color=colors[index], capsize=4, markersize=7, zorder=3,
        )
        label = row["name"].replace("selected_", "").replace("cheaper_", "")
        ax.annotate(label, (row["cost_cny"], row["probability"]), xytext=(5, 5), textcoords="offset points", fontsize=8)
    ax.axhline(0.90, color="#303030", linestyle="--", linewidth=1)
    ax.set(xlabel="Material cost (CNY)", ylabel="Conduction probability", ylim=(0.88, 0.91))
    ax.grid(alpha=0.25); fig.tight_layout()
    fig.savefig(figures / "F3_q4_cost_validation.png", dpi=220); fig.savefig(figures / "F3_q4_cost_validation.pdf"); plt.close(fig)
    print(summary_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
