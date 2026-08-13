#!/usr/bin/env python3
"""Build data-faithful research-style figure candidates and select finalists.

Every plotted value is derived from the official Q1 workbook, final_results.json,
or the analytic equations used to produce those results.  No stochastic or
illustrative observations are introduced.
"""

from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm, ListedColormap

from analytic_bounds import (
    A_COST,
    B_COST,
    BOX_SIDE,
    GAP,
    ROD_RADIUS,
    SPHERE_RADIUS,
    conduction_upper_bound,
    direct_bridge_probability,
    material_cost,
)
from geometry import BOX_HALF, segment_distance_certificates


RUN = Path(__file__).resolve().parents[2]
RESULTS_PATH = RUN / "outputs" / "data" / "final_results.json"
WORKBOOK = RUN / "data" / "raw" / "A" / "attachment.xlsx"
CANDIDATES = RUN / "outputs" / "figure_candidates"
FINAL = RUN / "outputs" / "figures_research"

BLUE = "#176B87"
ORANGE = "#D97706"
RED = "#C2412D"
GREEN = "#16835B"
GRAY = "#9AA4AE"
LIGHT = "#E8EEF2"
INK = "#25313C"


def configure() -> None:
    fonts = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "DejaVu Sans"]
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": fonts,
        "axes.unicode_minus": False,
        "font.size": 9,
        "axes.titlesize": 10.5,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "axes.edgecolor": "#66717B",
        "axes.linewidth": 0.75,
        "grid.color": "#D7DEE4",
        "grid.linewidth": 0.55,
        "grid.alpha": 0.8,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })


def load() -> tuple[dict, list[tuple[np.ndarray, np.ndarray]]]:
    results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    groups = []
    book = pd.ExcelFile(WORKBOOK)
    for sheet in book.sheet_names:
        frame = pd.read_excel(WORKBOOK, sheet_name=sheet, header=None)
        xyz = frame.iloc[2:, :6].apply(pd.to_numeric, errors="coerce").dropna().to_numpy(float)
        groups.append((xyz[:, :3], xyz[:, 3:]))
    if [len(item[0]) for item in groups] != [row["row_count"] for row in results["Q1"]]:
        raise AssertionError("Q1 workbook and final_results.json disagree")
    return results, groups


def style_ax(ax, grid=True) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    if grid:
        ax.grid(True, axis="y", zorder=0)
    ax.tick_params(length=3, color="#66717B")


def panel_label(ax, label: str) -> None:
    writer = ax.text2D if hasattr(ax, "text2D") else ax.text
    writer(-0.06, 1.04, label, transform=ax.transAxes, weight="bold", fontsize=10.5,
           va="bottom", ha="left", color=INK)


def save(fig, stem: str) -> None:
    CANDIDATES.mkdir(parents=True, exist_ok=True)
    fig.savefig(CANDIDATES / f"{stem}.png", dpi=300, bbox_inches="tight", pad_inches=0.04)
    fig.savefig(CANDIDATES / f"{stem}.pdf", bbox_inches="tight", pad_inches=0.04)
    fig.savefig(CANDIDATES / f"{stem}.svg", bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


def path_indices(result: dict) -> list[int]:
    return [int(x) - 1 for x in result["conductive_path_1_based"] if isinstance(x, int)]


def draw_box_3d(ax) -> None:
    b = BOX_HALF
    corners = np.array([[x, y, z] for x in (-b, b) for y in (-b, b) for z in (-b, b)])
    for i, p in enumerate(corners):
        for j, q in enumerate(corners):
            if j > i and np.sum(p != q) == 1:
                ax.plot(*zip(p, q), color="#B8C1C9", lw=0.45, alpha=0.7, zorder=0)


def draw_rods_3d(ax, starts, ends, selected=(), background_cap=None) -> None:
    selected = set(selected)
    ids = np.arange(len(starts))
    if background_cap and len(ids) > background_cap:
        keep = np.linspace(0, len(ids) - 1, background_cap, dtype=int)
    else:
        keep = ids
    for idx in keep:
        if idx in selected:
            continue
        ax.plot(*zip(starts[idx], ends[idx]), color=BLUE, alpha=0.24, lw=0.45, zorder=1)
    for idx in selected:
        ax.plot(*zip(starts[idx], ends[idx]), color=RED, lw=2.3, zorder=4)
        mid = (starts[idx] + ends[idx]) / 2
        ax.text(*mid, str(idx + 1), color=RED, fontsize=7, weight="bold", zorder=5)


def c01_q1_3d_triptych(results, groups) -> None:
    fig = plt.figure(figsize=(10.4, 3.45), constrained_layout=True)
    for k, ((starts, ends), result) in enumerate(zip(groups, results["Q1"]), 1):
        ax = fig.add_subplot(1, 3, k, projection="3d")
        selected = path_indices(result)
        draw_rods_3d(ax, starts, ends, selected, background_cap=None)
        draw_box_3d(ax)
        ax.set(xlim=(-5000, 5000), ylim=(-5000, 5000), zlim=(-5000, 5000),
               xlabel="x / nm", ylabel="y / nm", zlabel="z / nm")
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(elev=22, azim=-58)
        status = "导通" if result["connected"] else "不导通"
        ax.set_title(f"组{k}｜{len(starts)} 根｜{status}", color=GREEN if result["connected"] else INK)
        ax.tick_params(labelsize=6, pad=0)
        panel_label(ax, chr(96 + k))
    fig.suptitle("Q1 三组真实三维构型与显式导通路径（红）", weight="bold", color=INK)
    save(fig, "C01_q1_3d_triptych")


def c02_q1_multiview(results, groups) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(10.4, 6.0), constrained_layout=True)
    projections = [(0, 1, "x / nm", "y / nm"), (0, 2, "x / nm", "z / nm"), (1, 2, "y / nm", "z / nm")]
    for row, group_idx in enumerate((1, 2)):
        starts, ends = groups[group_idx]
        selected = set(path_indices(results["Q1"][group_idx]))
        for col, (u, v, xlabel, ylabel) in enumerate(projections):
            ax = axes[row, col]
            for idx in range(len(starts)):
                active = idx in selected
                ax.plot([starts[idx, u], ends[idx, u]], [starts[idx, v], ends[idx, v]],
                        color=RED if active else BLUE, lw=2.0 if active else 0.38,
                        alpha=1 if active else 0.20, zorder=3 if active else 1)
            ax.set(xlim=(-5100, 5100), ylim=(-5100, 5100), xlabel=xlabel, ylabel=ylabel)
            ax.set_aspect("equal", adjustable="box")
            style_ax(ax, grid=False)
            ax.axvline(-5000, color="#52606B", lw=0.8, ls="--") if u == 0 else None
            ax.axvline(5000, color="#52606B", lw=0.8, ls="--") if u == 0 else None
            if row == 0:
                ax.set_title(("俯视 x-y", "侧视 x-z", "端视 y-z")[col])
            if col == 0:
                ax.text(-0.22, 0.5, f"组{group_idx + 1}", transform=ax.transAxes,
                        rotation=90, weight="bold", va="center", color=INK)
    fig.suptitle("Q1 导通正例的正交三视图：投影一致性与路径可辨识性", weight="bold", color=INK)
    save(fig, "C02_q1_multiview")


def c03_q1_path_certificate(results, groups) -> None:
    fig = plt.figure(figsize=(9.2, 4.2), constrained_layout=True)
    for pos, group_idx in enumerate((1, 2), 1):
        ax = fig.add_subplot(1, 2, pos, projection="3d")
        starts, ends = groups[group_idx]
        ids = path_indices(results["Q1"][group_idx])
        draw_rods_3d(ax, starts, ends, ids)
        for left, right in zip(ids[:-1], ids[1:]):
            dist, s, t = segment_distance_certificates(starts[[left]], ends[[left]], starts[[right]], ends[[right]])
            p = starts[left] + s[0] * (ends[left] - starts[left])
            q = starts[right] + t[0] * (ends[right] - starts[right])
            ax.plot(*zip(p, q), color=GREEN, lw=1.8, ls="--", zorder=6)
            mid = (p + q) / 2
            ax.text(*mid, f"{dist[0]:.1f}", color=GREEN, fontsize=6.5, zorder=7)
        cloud = np.vstack([starts[ids], ends[ids]])
        span = np.ptp(cloud, axis=0)
        center = np.mean(cloud, axis=0)
        radius = max(span.max() * 0.57, 500)
        ax.set(xlim=(center[0]-radius, center[0]+radius), ylim=(center[1]-radius, center[1]+radius),
               zlim=(center[2]-radius, center[2]+radius), xlabel="x / nm", ylabel="y / nm", zlabel="z / nm")
        ax.set_box_aspect((1, 1, 1)); ax.view_init(20, -60); ax.tick_params(labelsize=6, pad=0)
        ax.set_title(f"组{group_idx + 1}：红线为路径介质，绿虚线为最短轴距 / nm")
        panel_label(ax, chr(96 + pos))
    fig.suptitle("Q1 显式路径的三维几何证书", weight="bold", color=INK)
    save(fig, "C03_q1_path_certificate")


def c04_q3_bounds_band(results) -> None:
    rows = results["Q3"]["proof_rows"]
    x = np.array([r["a_count"] for r in rows])
    lo = np.array([r["direct_bridge_lower_bound"] for r in rows])
    hi = np.array([r["conduction_upper_bound"] for r in rows])
    fig, ax = plt.subplots(figsize=(7.3, 4.2), constrained_layout=True)
    ax.fill_between(x, lo, hi, color=ORANGE, alpha=0.42, label="解析夹逼区间")
    ax.plot(x, lo, color=BLUE, marker="o", ms=4, lw=1.6, label="直接贯通下界")
    ax.plot(x, hi, color=RED, marker="s", ms=3.5, lw=1.0, ls="--", label="总导通上界")
    ax.axhline(.9, color=INK, lw=1.1, ls=(0, (5, 3)), label="目标 0.90")
    ax.axvspan(7.5, 8.5, color=GREEN, alpha=.08)
    ax.annotate("7 根：上界 0.872279 < 0.90", (7, hi[-2]), xytext=(4.4, .935),
                arrowprops={"arrowstyle": "->", "color": RED}, color=RED)
    ax.annotate("8 根：下界 0.904810 > 0.90", (8, lo[-1]), xytext=(5.1, .82),
                arrowprops={"arrowstyle": "->", "color": GREEN}, color=GREEN)
    ax.set(xlabel="A 介质数量 / 根", ylabel="导通概率", xlim=(1, 8.15), ylim=(.2, .96), xticks=x)
    style_ax(ax); ax.legend(loc="lower right", frameon=False)
    ax.set_title("Q3 阈值的解析夹逼：必要性与充分性在相邻整数处闭合", weight="bold", color=INK)
    save(fig, "C04_q3_bounds_band")


def c05_q2_failure_lollipop(results) -> None:
    rows = results["Q2"]
    x = 100 * np.array([r["requested_fraction"] for r in rows])
    y = np.array([r["log10_failure_probability_upper_bound"] for r in rows])
    n = [r["a_count"] for r in rows]
    fig, ax = plt.subplots(figsize=(7.2, 4.0), constrained_layout=True)
    ax.vlines(x, 0, y, color="#AFC3CE", lw=2)
    ax.scatter(x, y, s=52, c=[BLUE, GREEN, ORANGE, RED], edgecolor="white", lw=.8, zorder=3)
    for xi, yi, ni in zip(x, y, n):
        ax.text(xi, yi + 2.5, f"{ni} 根\n$10^{{{yi:.1f}}}$", ha="center", va="bottom", fontsize=8)
    ax.set(xlabel="A 体积分数 / %", ylabel=r"$\log_{10}$（不导通概率上界）",
           xticks=x, ylim=(-97, 4))
    ax.set_xticklabels([f"{v:.2f}" for v in x])
    style_ax(ax); ax.axhline(0, color=INK, lw=.7)
    ax.set_title("Q2 不导通风险的数量级：普通概率坐标无法分辨的差异", weight="bold", color=INK)
    save(fig, "C05_q2_failure_lollipop")


def c06_probability_evidence_dashboard(results) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(9.8, 3.8), constrained_layout=True)
    q3 = results["Q3"]["proof_rows"]
    x = np.array([r["a_count"] for r in q3]); lo = np.array([r["direct_bridge_lower_bound"] for r in q3]); hi = np.array([r["conduction_upper_bound"] for r in q3])
    axes[0].fill_between(x, lo, hi, color=ORANGE, alpha=.45)
    axes[0].plot(x, lo, color=BLUE, marker="o", ms=3.5)
    axes[0].plot(x, hi, color=RED, ls="--", lw=1)
    axes[0].axhline(.9, color=INK, ls="--", lw=1)
    axes[0].set(xlabel="A 数量 / 根", ylabel="导通概率", xticks=x, ylim=(.2, .96), title="Q3｜整数阈值夹逼")
    style_ax(axes[0]); panel_label(axes[0], "a")
    q2 = results["Q2"]
    xf = 100 * np.array([r["requested_fraction"] for r in q2]); yf = np.array([r["log10_failure_probability_upper_bound"] for r in q2])
    axes[1].plot(xf, yf, color=BLUE, marker="o", ms=4)
    for a, b in zip(xf, yf): axes[1].annotate(f"{b:.1f}", (a, b), xytext=(0, 6), textcoords="offset points", ha="center", fontsize=7)
    axes[1].set(xlabel="A 体积分数 / %", ylabel=r"$\log_{10}$（不导通上界）", xticks=xf, title="Q2｜失败风险数量级")
    axes[1].set_xticklabels([f"{v:.2f}" for v in xf]); style_ax(axes[1]); panel_label(axes[1], "b")
    fig.suptitle("同一解析机制在 Q2 与 Q3 中的证据链", weight="bold", color=INK)
    save(fig, "C06_probability_evidence_dashboard")


def q4_lattice(reference_cost: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    aa, bb, pp, cc = [], [], [], []
    max_a = int(math.floor(reference_cost / A_COST)) + 1
    max_b = int(math.floor(reference_cost / B_COST)) + 2
    for a in range(max_a + 1):
        for b in range(max_b + 1):
            cost = material_cost(a, b)
            if cost <= reference_cost * 1.08:
                aa.append(a); bb.append(b); pp.append(conduction_upper_bound(a, b)); cc.append(cost)
    return map(np.asarray, (aa, bb, pp, cc))


def c07_q4_integer_domain(results) -> None:
    selected = results["Q4"]["selected"]
    a, b, p, cost = q4_lattice(selected["cost_cny"])
    fig, ax = plt.subplots(figsize=(7.6, 5.2), constrained_layout=True)
    cheaper = cost < selected["cost_cny"] - 1e-15
    sc = ax.scatter(a[cheaper], b[cheaper], c=p[cheaper], cmap="viridis", vmin=.55, vmax=.90,
                    s=28, marker="s", linewidths=0, alpha=.9, label="更低成本整数候选")
    ax.scatter(a[~cheaper], b[~cheaper], facecolors="none", edgecolors=GRAY, s=25, marker="s", lw=.6, label="不低于选定成本")
    frontier = results["Q4"]["cheaper_frontier"]
    fa = [r["a_count"] for r in frontier]; fb = [r["b_count"] for r in frontier]
    ax.plot(fa, fb, color=RED, marker="o", ms=4, lw=1.5, label="更低成本前沿")
    ax.scatter([0], [57], s=110, marker="*", color=GREEN, edgecolor="white", lw=.8, zorder=6, label="最优 0A+57B")
    ax.scatter([1], [50], s=80, marker="D", color=ORANGE, edgecolor="white", lw=.8, zorder=6, label="正混合最优 1A+50B")
    cb = fig.colorbar(sc, ax=ax, pad=.015); cb.set_label("总导通概率上界")
    ax.set(xlabel="A 数量 / 根", ylabel="B 数量 / 个", xlim=(-.35, max(a)+.35), ylim=(-1, max(b)+2))
    style_ax(ax); ax.legend(loc="upper right", frameon=True, framealpha=.95)
    ax.set_title("Q4 完整低成本整数域：216 个候选、排除前沿与两种最优口径", weight="bold", color=INK)
    save(fig, "C07_q4_integer_domain")


def c08_q4_cost_frontier(results) -> None:
    selected = results["Q4"]["selected"]
    a, b, p, cost = q4_lattice(selected["cost_cny"])
    lower = np.array([direct_bridge_probability(int(x), int(y)) for x, y in zip(a, b)])
    fig, ax = plt.subplots(figsize=(7.6, 4.7), constrained_layout=True)
    sc = ax.scatter(cost, p, c=a, cmap="cividis", s=25, alpha=.58, edgecolor="none", label="整数候选（上界）")
    frontier = results["Q4"]["cheaper_frontier"]
    fx = np.array([r["cost_cny"] for r in frontier]); fy = np.array([r["conduction_upper_bound"] for r in frontier])
    order = np.argsort(fx); ax.plot(fx[order], fy[order], color=RED, marker="o", ms=4, lw=1.6, label="更低成本前沿")
    ax.vlines(selected["cost_cny"], selected["direct_bridge_lower_bound"], conduction_upper_bound(0, 57), color=GREEN, lw=4, alpha=.35)
    ax.scatter([selected["cost_cny"]], [selected["direct_bridge_lower_bound"]], marker="*", s=130, color=GREEN, zorder=6, label="0A+57B 下界")
    ax.axhline(.9, color=INK, ls="--", lw=1, label="目标 0.90")
    ax.axvline(selected["cost_cny"], color=GREEN, ls=":", lw=1)
    cb = fig.colorbar(sc, ax=ax, pad=.015); cb.set_label("A 数量 / 根")
    ax.set(xlabel="材料成本 / 元", ylabel="导通概率界", ylim=(max(.5, p.min()-.02), .925))
    style_ax(ax); ax.legend(loc="lower right", frameon=False)
    ax.set_title("Q4 成本—概率前沿：最优点以充分下界越过约束", weight="bold", color=INK)
    save(fig, "C08_q4_cost_frontier")


def required_count(q: np.ndarray) -> np.ndarray:
    return np.ceil(np.log(.1) / np.log(1 - q)).astype(int)


def c09_sensitivity_threshold_counts() -> None:
    heights = np.linspace(3500, 6500, 121)
    q_a = heights / (2 * BOX_SIDE) + 2 * ROD_RADIUS * (math.pi / 4) / BOX_SIDE
    radii = np.linspace(120, 280, 161)
    q_b = 2 * radii / BOX_SIDE
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.9), constrained_layout=True)
    axes[0].step(heights, required_count(q_a), where="mid", color=BLUE, lw=1.8)
    axes[0].scatter([5000], [required_count(np.array([5000/(2*BOX_SIDE)+2*ROD_RADIUS*(math.pi/4)/BOX_SIDE]))[0]], color=RED, s=35, zorder=3)
    axes[0].axvline(5000, color=RED, ls=":", lw=.8)
    axes[0].set(xlabel="A 高度 H / nm", ylabel="达到 90% 所需 A 数量 / 根", title="A 几何高度敏感性")
    style_ax(axes[0]); panel_label(axes[0], "a")
    axes[1].step(radii, required_count(q_b), where="mid", color=ORANGE, lw=1.8)
    axes[1].scatter([SPHERE_RADIUS], [required_count(np.array([2*SPHERE_RADIUS/BOX_SIDE]))[0]], color=RED, s=35, zorder=3)
    axes[1].axvline(SPHERE_RADIUS, color=RED, ls=":", lw=.8)
    axes[1].set(xlabel="B 半径 R / nm", ylabel="达到 90% 所需 B 数量 / 个", title="B 半径敏感性")
    style_ax(axes[1]); panel_label(axes[1], "b")
    fig.suptitle("设计情景敏感性：整数阈值的阶梯响应", weight="bold", color=INK)
    save(fig, "C09_sensitivity_threshold_counts")


def optimum_for_geometry(height: float, radius: float, positive: bool = False) -> tuple[float, int, int]:
    qa = height / (2 * BOX_SIDE) + 2 * ROD_RADIUS * (math.pi / 4) / BOX_SIDE
    qb = 2 * radius / BOX_SIDE
    a_cost = 1.05 * math.pi * ROD_RADIUS**2 * height / 1e9
    b_cost = .05 * (4 * math.pi * radius**3 / 3) / 1e9
    best = (float("inf"), -1, -1)
    for a in range(1 if positive else 0, 16):
        residual = .1 / ((1 - qa) ** a)
        b = max(1 if positive else 0, int(math.ceil(math.log(residual) / math.log(1 - qb)))) if residual < 1 else (1 if positive else 0)
        value = a * a_cost + b * b_cost
        if value < best[0]: best = (value, a, b)
    return best


def c10_sensitivity_cost_phase() -> None:
    heights = np.linspace(4000, 6000, 41)
    radii = np.linspace(150, 250, 41)
    costs = np.empty((len(radii), len(heights)))
    types = np.empty_like(costs, dtype=int)
    for j, r in enumerate(radii):
        for i, h in enumerate(heights):
            value, a, b = optimum_for_geometry(h, r, positive=False)
            costs[j, i] = value; types[j, i] = 0 if a == 0 else 2 if b == 0 else 1
    fig, axes = plt.subplots(1, 2, figsize=(9.8, 4.0), constrained_layout=True)
    im = axes[0].contourf(heights, radii, costs, levels=14, cmap="viridis")
    axes[0].contour(heights, radii, costs, levels=7, colors="white", linewidths=.45, alpha=.8)
    axes[0].scatter([5000], [200], marker="*", s=85, color=RED, edgecolor="white", lw=.7)
    cb = fig.colorbar(im, ax=axes[0], pad=.015); cb.set_label("最小材料成本 / 元")
    axes[0].set(xlabel="A 高度 H / nm", ylabel="B 半径 R / nm", title="最优成本响应面")
    panel_label(axes[0], "a")
    cmap = ListedColormap([ORANGE, GREEN, BLUE]); norm = BoundaryNorm([-.5, .5, 1.5, 2.5], cmap.N)
    axes[1].pcolormesh(heights, radii, types, cmap=cmap, norm=norm, shading="nearest")
    axes[1].contour(heights, radii, types, levels=[.5, 1.5], colors="white", linewidths=1)
    axes[1].scatter([5000], [200], marker="*", s=85, color=RED, edgecolor="white", lw=.7)
    axes[1].set(xlabel="A 高度 H / nm", ylabel="B 半径 R / nm", title="最优配方相区")
    handles = [mpl.lines.Line2D([], [], marker="s", ls="", color=c, label=t) for c, t in zip([ORANGE, GREEN, BLUE], ["纯 B", "A+B", "纯 A"])]
    axes[1].legend(handles=handles, loc="upper right", frameon=True)
    panel_label(axes[1], "b")
    fig.suptitle("双参数灵敏度：几何变化如何改变成本与最优材料类型", weight="bold", color=INK)
    save(fig, "C10_sensitivity_cost_phase")


SELECTED = [
    "C01_q1_3d_triptych",
    "C03_q1_path_certificate",
    "C04_q3_bounds_band",
    "C05_q2_failure_lollipop",
    "C07_q4_integer_domain",
    "C08_q4_cost_frontier",
    "C09_sensitivity_threshold_counts",
]


def select_finalists() -> None:
    FINAL.mkdir(parents=True, exist_ok=True)
    for old in FINAL.glob("*"):
        if old.is_file(): old.unlink()
    for stem in SELECTED:
        for suffix in (".png", ".pdf", ".svg"):
            shutil.copy2(CANDIDATES / f"{stem}{suffix}", FINAL / f"{stem}{suffix}")


def main() -> int:
    configure()
    results, groups = load()
    builders = [c01_q1_3d_triptych, c02_q1_multiview, c03_q1_path_certificate]
    for fn in builders: fn(results, groups)
    c04_q3_bounds_band(results)
    c05_q2_failure_lollipop(results)
    c06_probability_evidence_dashboard(results)
    c07_q4_integer_domain(results)
    c08_q4_cost_frontier(results)
    c09_sensitivity_threshold_counts()
    c10_sensitivity_cost_phase()
    select_finalists()
    print(f"generated 10 candidates in {CANDIDATES}")
    print(f"selected {len(SELECTED)} finalists in {FINAL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
