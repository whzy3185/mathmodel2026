#!/usr/bin/env python3
# AI assistance disclosure: drafted with OpenAI Codex and verified by executable tests.
"""Render claim-bearing figures strictly from final_results.json."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    results = json.loads((root / "outputs/data/final_results.json").read_text(encoding="utf-8"))
    figures = root / "outputs/figures"; figures.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 10, "axes.unicode_minus": False})

    rows = results["Q3"]["proof_rows"]
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.plot([r["a_count"] for r in rows], [r["direct_bridge_lower_bound"] for r in rows], color="#176B87", marker="o", label="Sufficient lower bound")
    ax.plot([r["a_count"] for r in rows], [r["conduction_upper_bound"] for r in rows], color="#C84B31", marker="s", linestyle="--", label="Necessary upper bound")
    ax.axhline(0.90, color="#303030", linestyle=":", label="Target 0.90")
    ax.set(xlabel="Number of A conductors", ylabel="Conduction probability bound", xlim=(1, 8), ylim=(0.2, 0.93))
    ax.grid(alpha=0.25); ax.legend(loc="lower right"); fig.tight_layout()
    fig.savefig(figures / "F1_q3_threshold.png", dpi=220); fig.savefig(figures / "F1_q3_threshold.pdf"); plt.close(fig)

    q2 = results["Q2"]; fig, ax = plt.subplots(figsize=(6.8, 4.2))
    x = [100 * row["requested_fraction"] for row in q2]; y = [row["log10_failure_probability_upper_bound"] for row in q2]
    ax.plot(x, y, color="#176B87", marker="o", linewidth=2)
    for xx, yy in zip(x, y): ax.annotate(f"{yy:.1f}", (xx, yy), xytext=(0, -16), textcoords="offset points", ha="center")
    ax.set(xlabel="A volume fraction (%)", ylabel="log10 upper bound of failure probability")
    ax.margins(y=0.12); ax.grid(alpha=0.25); fig.tight_layout()
    fig.savefig(figures / "F2_q2_failure_scale.png", dpi=220); fig.savefig(figures / "F2_q2_failure_scale.pdf"); plt.close(fig)

    frontier = results["Q4"]["cheaper_frontier"]; selected = results["Q4"]["selected"]
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    ax.scatter([row["cost_cny"] for row in frontier], [row["conduction_upper_bound"] for row in frontier], color="#C84B31", s=55, label="All cheaper frontier: rigorous upper bound")
    for row in frontier:
        ax.annotate(f"{row['a_count']}A+{row['b_count']}B", (row["cost_cny"], row["conduction_upper_bound"]), xytext=(4, 5), textcoords="offset points", fontsize=8)
    ax.scatter([selected["cost_cny"]], [selected["direct_bridge_lower_bound"]], color="#1B7F5A", s=75, label="57B: rigorous lower bound", zorder=3)
    ax.annotate("0A+57B", (selected["cost_cny"], selected["direct_bridge_lower_bound"]), xytext=(5, 5), textcoords="offset points", fontsize=9)
    ax.axhline(0.90, color="#303030", linestyle=":")
    ax.set(xlabel="Material cost (CNY)", ylabel="Conduction probability bound", ylim=(0.84, 0.91))
    ax.grid(alpha=0.25); ax.legend(loc="lower right"); fig.tight_layout()
    fig.savefig(figures / "F3_q4_cost_validation.png", dpi=220); fig.savefig(figures / "F3_q4_cost_validation.pdf"); plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
