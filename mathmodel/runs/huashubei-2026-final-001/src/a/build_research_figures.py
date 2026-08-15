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
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle

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
    # Manuscript target: one CJK-capable family at final insertion size.
    # SVG text stays live and every finalist uses an uncropped physical canvas.
    fonts = ["Microsoft YaHei"]
    mpl.rcParams.update({
        "font.family": fonts,
        "font.sans-serif": fonts,
        "axes.unicode_minus": False,
        "font.size": 9,
        "axes.titlesize": 10.5,
        "axes.labelsize": 9.5,
        "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5,
        "legend.fontsize": 8.2,
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
        "svg.fonttype": "none",
        "savefig.bbox": "standard",
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
    fig.savefig(CANDIDATES / f"{stem}.png", dpi=300)
    fig.savefig(CANDIDATES / f"{stem}.pdf")
    fig.savefig(CANDIDATES / f"{stem}.svg")
    plt.close(fig)


def path_indices(result: dict) -> list[int]:
    return [int(x) - 1 for x in result["conductive_path_1_based"] if isinstance(x, int)]


def s01_problem_geometry() -> None:
    fig, ax = plt.subplots(figsize=(160 / 25.4, 78 / 25.4))
    fig.subplots_adjust(left=.04, right=.98, bottom=.08, top=.96)
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")
    ax.add_patch(Rectangle((1.5, 1.0), 6.4, 4.1, fill=False, ec="#66717B", lw=1.2))
    ax.add_patch(Rectangle((1.5, 1.0), .16, 4.1, fc="#BDE7F3", ec=BLUE, lw=.9))
    ax.add_patch(Rectangle((7.74, 1.0), .16, 4.1, fc="#FAD1C8", ec=RED, lw=.9))
    ax.plot([2.8, 6.4], [1.8, 4.0], color=BLUE, lw=9, solid_capstyle="butt")
    ax.scatter([2.8, 6.4], [1.8, 4.0], s=75, color="#5BC0BE", edgecolor=BLUE, zorder=3)
    ax.add_patch(Circle((5.4, 4.35), .43, fc="#F5C04A", ec=ORANGE, lw=1.0))
    ax.text(.75, 3.05, "左电极\nx = −5000 nm", ha="center", va="center", color=BLUE, fontsize=8.3)
    ax.text(8.65, 3.05, "右电极\nx = 5000 nm", ha="center", va="center", color=RED, fontsize=8.3)
    ax.text(4.55, 2.45, "A：平端圆柱\nH = 5000 nm，r_A = 30 nm", ha="center", va="center", fontsize=8.1, color=INK)
    ax.text(5.4, 4.35, "B", ha="center", va="center", fontsize=8, color=INK)
    ax.annotate("越界片段平移一个边长并保留介质身份", xy=(7.85, 5.35), xytext=(4.2, 5.65),
                ha="center", color=RED, fontsize=7.8,
                arrowprops={"arrowstyle": "->", "color": RED, "lw": .9})
    ax.text(4.7, .35, "接触判据：两实体表面最短距离不超过 1.8 nm", ha="center", color=INK, fontsize=8.2)
    save(fig, "S01_problem_geometry")


def s02_workflow() -> None:
    fig, ax = plt.subplots(figsize=(160 / 25.4, 78 / 25.4))
    fig.subplots_adjust(left=.02, right=.98, bottom=.05, top=.96)
    ax.set_xlim(0, 12); ax.set_ylim(0, 6); ax.axis("off")
    boxes = [
        (0.3, 3.4, 2.0, 1.25, "附件坐标\n数据审计", BLUE),
        (2.8, 3.4, 2.1, 1.25, "确定性几何图\n路径证书", BLUE),
        (5.4, 3.4, 2.2, 1.25, "共享概率模型\n上下界", ORANGE),
        (8.2, 4.25, 1.9, 1.15, "Q2\n给定体积分数", GREEN),
        (8.2, 2.65, 1.9, 1.15, "Q3\n7/8 根夹逼", GREEN),
        (8.2, .95, 1.9, 1.15, "Q4\n整数成本优化", RED),
        (10.55, .95, 1.15, 1.15, "检验\n与敏感性", "#66717B"),
    ]
    for x, y, w, h, label, color in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=.05", fc="white", ec=color, lw=1.2))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=8.1, color=INK)
    arrows = [((2.3,4.03),(2.8,4.03)),((4.9,4.03),(5.4,4.03)),((7.6,4.03),(8.2,4.82)),
              ((7.6,4.03),(8.2,3.22)),((6.5,3.4),(8.2,1.52)),((10.1,1.52),(10.55,1.52))]
    for start, end in arrows:
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="->", mutation_scale=10, lw=1.0, color="#52606B"))
    ax.text(6.5, 2.85, "直接贯通下界\n非直接通路上界", ha="center", va="top", fontsize=7.4, color=ORANGE)
    ax.text(6.0, .35, "同一机器结果源驱动表格、图片与阈值证书", ha="center", fontsize=8, color=INK)
    save(fig, "S02_workflow")


def s03_data_audit(results, groups) -> None:
    counts = np.array([len(s) for s, _ in groups])
    boundary = []
    for starts, ends in groups:
        pts = np.vstack([starts, ends])
        touched = np.any(np.isclose(np.abs(np.hstack([starts, ends])), BOX_HALF, atol=1e-6), axis=1)
        boundary.append(100 * touched.mean())
    fig, ax = plt.subplots(figsize=(160 / 25.4, 78 / 25.4))
    fig.subplots_adjust(left=.11, right=.98, bottom=.20, top=.94)
    x = np.arange(3)
    bars = ax.bar(x, np.log10(counts), width=.52, color=[BLUE, ORANGE, RED], alpha=.92)
    for i, (bar, count, pct) in enumerate(zip(bars, counts, boundary)):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+.06, f"{count} 根", ha="center", fontsize=8.4, color=INK)
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()/2, f"边界触及\n{pct:.1f}%", ha="center", va="center", fontsize=7.8, color="white", weight="bold")
    ax.set(xlabel="附件分组", ylabel="介质数量的常用对数", xticks=x, xticklabels=["组1", "组2", "组3"], ylim=(0, 3.0))
    style_ax(ax)
    ax.text(.01, .97, "轴段中位长度：2566、2677、3697 nm", transform=ax.transAxes, ha="left", va="top", fontsize=7.8, color=INK)
    save(fig, "S03_data_audit")


def s04_flat_cylinder_certificate() -> None:
    fig, ax = plt.subplots(figsize=(160 / 25.4, 68 / 25.4))
    fig.subplots_adjust(left=.04, right=.98, bottom=.10, top=.96)
    ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.axis("off")
    ax.plot([1.2, 4.5], [1.4, 3.5], color=BLUE, lw=11, solid_capstyle="butt")
    ax.plot([5.5, 8.9], [1.1, 3.9], color=ORANGE, lw=11, solid_capstyle="butt")
    p = (3.8, 3.05); q = (6.15, 1.64)
    ax.scatter(*zip(p, q), s=42, color=RED, zorder=4)
    ax.plot([p[0], q[0]], [p[1], q[1]], color=RED, lw=1.2)
    ax.text(5.0, 2.55, "轴段最近距离 d_axis", color=RED, fontsize=8, ha="center", rotation=-29)
    ax.text(2.6, 3.7, "P(s)，0 < s < 1", fontsize=8, color=INK)
    ax.text(7.0, 1.05, "Q(t)，0 < t < 1", fontsize=8, color=INK)
    ax.text(5.0, .28, "内部最近点时，连接向量同时垂直两轴；侧面间隙 = max(0, d_axis − 2r_A) ≤ g",
            ha="center", fontsize=8.2, color=INK)
    save(fig, "S04_flat_cylinder_certificate")


def s05_direct_bridge_mechanism() -> None:
    fig, axes = plt.subplots(2, 1, figsize=(160 / 25.4, 86 / 25.4))
    fig.subplots_adjust(left=.08, right=.98, bottom=.08, top=.96, hspace=.42)
    for ax in axes:
        ax.set_xlim(0, 10); ax.set_ylim(0, 2.2); ax.axis("off")
        ax.set_xticks([]); ax.set_yticks([])
        ax.add_patch(Rectangle((1.0,.35), 8.0, 1.45, fill=False, ec="#66717B", lw=1.0))
        ax.plot([1.2, 1.2], [.35,1.8], color=RED, lw=1.0); ax.plot([8.8,8.8],[.35,1.8],color=RED,lw=1.0)
    axes[0].plot([.6, 2.3], [.65, 1.35], color=BLUE, lw=8, solid_capstyle="butt")
    axes[0].plot([7.8, 9.5], [.65, 1.35], color=BLUE, lw=8, solid_capstyle="butt")
    axes[0].text(.15, 1.75, "介质 A", fontsize=8.5, weight="bold", color=INK)
    axes[0].text(5.0, 1.12, "同一圆柱跨越周期边界，平移片段保留导体身份", ha="center", fontsize=8, color=INK)
    axes[1].add_patch(Circle((1.15,1.05),.46,fc="#F5C04A",ec=ORANGE,lw=1.0))
    axes[1].add_patch(Circle((8.85,1.05),.46,fc="#F5C04A",ec=ORANGE,lw=1.0))
    axes[1].text(.15, 1.75, "介质 B", fontsize=8.5, weight="bold", color=INK)
    axes[1].text(5.0, 1.12, "同一球越界后在对侧出现，仍视作单体直接贯通", ha="center", fontsize=8, color=INK)
    fig.text(.5, .035, "直接贯通是总导通的充分事件，用于构造可证明的概率下界", ha="center", fontsize=8.2, color=INK)
    save(fig, "S05_direct_bridge_mechanism")


def s06_orientation_support() -> None:
    u = np.linspace(0, 1, 300)
    support = (5000 / 2) * u + ROD_RADIUS * np.sqrt(1 - u**2)
    conditional = 2 * support / BOX_SIDE
    fig, ax = plt.subplots(figsize=(160 / 25.4, 76 / 25.4))
    fig.subplots_adjust(left=.12, right=.98, bottom=.20, top=.94)
    ax.plot(u, conditional, color=BLUE, lw=1.8)
    ax.axhline(.25471238898, color=RED, lw=1.0, ls="--", label="各向同性平均 0.254712")
    ax.fill_between(u, conditional, .25471238898, color=ORANGE, alpha=.18)
    ax.set(xlabel="轴向 x 分量的绝对值 |u_x|", ylabel="固定取向下的直接越界概率", xlim=(0,1), ylim=(0,.52))
    style_ax(ax); ax.legend(frameon=False, loc="upper left")
    ax.annotate("平行 x 轴：0.500", (1, .5), xytext=(-102,-24), textcoords="offset points", fontsize=8, color=BLUE,
                arrowprops={"arrowstyle":"->","color":BLUE,"lw":.8})
    save(fig, "S06_orientation_support")


def s07_event_bounds() -> None:
    fig, ax = plt.subplots(figsize=(160 / 25.4, 72 / 25.4))
    fig.subplots_adjust(left=.03, right=.98, bottom=.08, top=.96)
    ax.set_xlim(0, 12); ax.set_ylim(0, 5); ax.axis("off")
    ax.add_patch(FancyBboxPatch((.4,.55),11.0,3.8,boxstyle="round,pad=.08",fc="#EEF5F8",ec=BLUE,lw=1.2))
    ax.text(.7,4.0,"总导通事件 T",fontsize=8.7,color=BLUE,weight="bold")
    ax.add_patch(FancyBboxPatch((1.25,1.25),3.55,2.25,boxstyle="round,pad=.08",fc="#E6F4ED",ec=GREEN,lw=1.1))
    ax.text(3.0,2.65,"直接贯通 D",ha="center",fontsize=9,color=GREEN,weight="bold")
    ax.text(3.0,2.05,"提供总导通下界",ha="center",fontsize=8,color=INK)
    ax.add_patch(FancyBboxPatch((6.1,1.25),4.2,2.25,boxstyle="round,pad=.08",fc="#FFF0E8",ec=RED,lw=1.1))
    ax.text(8.2,2.65,"N = T 与 D 的补集之交",ha="center",fontsize=9,color=RED,weight="bold")
    ax.text(8.2,2.05,"无直接贯通但仍存在路径",ha="center",fontsize=8,color=INK)
    ax.text(8.2,1.58,"必须由不同终端粒子落入左右 g 薄壳",ha="center",fontsize=7.5,color=RED)
    ax.add_patch(FancyArrowPatch((4.85,2.35),(6.05,2.35),arrowstyle="->",mutation_scale=10,color="#66717B",lw=.9))
    ax.text(6.0,.15,"P(D) ≤ P(T) ≤ P(D) + n(n−1)(g/L)²",ha="center",fontsize=8.4,color=INK)
    save(fig, "S07_event_bounds")


def draw_box_3d(ax) -> None:
    b = BOX_HALF
    corners = np.array([[x, y, z] for x in (-b, b) for y in (-b, b) for z in (-b, b)])
    for i, p in enumerate(corners):
        for j, q in enumerate(corners):
            if j > i and np.sum(p != q) == 1:
                ax.plot(*zip(p, q), color="#B8C1C9", lw=0.45, alpha=0.7, zorder=0)


def draw_rods_3d(ax, starts, ends, selected=(), background_cap=None, annotate=True) -> None:
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
        if annotate:
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
    fig = plt.figure(figsize=(160 / 25.4, 82 / 25.4))
    fig.subplots_adjust(left=.03, right=.97, bottom=.07, top=.97, wspace=.06)
    for pos, group_idx in enumerate((1, 2), 1):
        ax = fig.add_subplot(1, 2, pos, projection="3d")
        starts, ends = groups[group_idx]
        ids = path_indices(results["Q1"][group_idx])
        draw_rods_3d(ax, starts, ends, ids, annotate=False)
        connector_distances = []
        for left, right in zip(ids[:-1], ids[1:]):
            dist, s, t = segment_distance_certificates(starts[[left]], ends[[left]], starts[[right]], ends[[right]])
            p = starts[left] + s[0] * (ends[left] - starts[left])
            q = starts[right] + t[0] * (ends[right] - starts[right])
            ax.plot(*zip(p, q), color=GREEN, lw=1.8, ls="--", zorder=6)
            connector_distances.append(float(dist[0]))
        cloud = np.vstack([starts[ids], ends[ids]])
        span = np.ptp(cloud, axis=0)
        center = np.mean(cloud, axis=0)
        radius = max(span.max() * 0.57, 500)
        ax.set(xlim=(center[0]-radius, center[0]+radius), ylim=(center[1]-radius, center[1]+radius),
               zlim=(center[2]-radius, center[2]+radius))
        ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
        ax.set_box_aspect((1, 1, 1)); ax.view_init(20, -60)
        path_text = "–".join(str(i + 1) for i in ids)
        distance_text = "、".join(f"{d:.1f}" for d in connector_distances)
        ax.text2D(.03, .94, f"组{group_idx + 1}  路径 {path_text}", transform=ax.transAxes,
                  fontsize=8.3, weight="bold", color=INK, va="top")
        ax.text2D(.03, .86, f"相邻轴线距 {distance_text} nm", transform=ax.transAxes,
                  fontsize=7.4, color=GREEN, va="top")
    fig.text(.5, .025, "红色：导通路径；绿色虚线：相邻杆件轴线的最近点连线；坐标单位：nm",
             ha="center", va="bottom", fontsize=7.5, color=INK)
    save(fig, "C03_q1_path_certificate")


def c04_q3_bounds_band(results) -> None:
    rows = results["Q3"]["proof_rows"]
    x = np.array([r["a_count"] for r in rows])
    lo = np.array([r["direct_bridge_lower_bound"] for r in rows])
    hi = np.array([r["conduction_upper_bound"] for r in rows])
    fig, axes = plt.subplots(1, 2, figsize=(160 / 25.4, 82 / 25.4),
                             gridspec_kw={"width_ratios": [1.28, 1]})
    fig.subplots_adjust(left=.09, right=.98, bottom=.18, top=.94, wspace=.29)
    ax = axes[0]
    ax.fill_between(x, lo, hi, color=ORANGE, alpha=.34, label="解析界差")
    ax.plot(x, lo, color=BLUE, marker="o", ms=3.7, lw=1.45, label="直接贯通下界")
    ax.plot(x, hi, color=RED, marker="s", ms=3.2, lw=1.0, ls="--", label="总导通上界")
    ax.axhline(.9, color=INK, lw=1.0, ls=(0, (5, 3)), label="目标 0.90")
    ax.set(xlabel="A 介质数量 / 根", ylabel="导通概率", xlim=(1, 8.12), ylim=(.2, .96), xticks=x)
    style_ax(ax); ax.legend(loc="lower right", frameon=False)

    zoom = axes[1]
    zoom.fill_between(x[-2:], lo[-2:], hi[-2:], color=ORANGE, alpha=.34)
    zoom.scatter([7], [hi[-2]], marker="s", s=45, facecolor="white", edgecolor=RED, lw=1.4, zorder=4)
    zoom.scatter([8], [lo[-1]], marker="o", s=47, color=BLUE, edgecolor="white", lw=.7, zorder=4)
    zoom.axhline(.9, color=INK, lw=1.0, ls=(0, (5, 3)))
    zoom.set(xlabel="A 介质数量 / 根", ylabel="阈值附近的概率界",
             xlim=(6.72, 8.28), ylim=(.865, .91), xticks=[7, 8])
    zoom.annotate("上界 0.872279", (7, hi[-2]), xytext=(7.08, .876), color=RED,
                  arrowprops={"arrowstyle": "-", "color": RED, "lw": .8}, fontsize=8)
    zoom.annotate("下界 0.904810", (8, lo[-1]), xytext=(7.06, .9065), color=BLUE,
                  arrowprops={"arrowstyle": "-", "color": BLUE, "lw": .8}, fontsize=8)
    style_ax(zoom)
    save(fig, "C04_q3_bounds_band")


def c05_q2_failure_lollipop(results) -> None:
    rows = results["Q2"]
    x = 100 * np.array([r["requested_fraction"] for r in rows])
    y = np.array([r["log10_failure_probability_upper_bound"] for r in rows])
    n = [r["a_count"] for r in rows]
    fig, ax = plt.subplots(figsize=(160 / 25.4, 78 / 25.4))
    fig.subplots_adjust(left=.13, right=.98, bottom=.20, top=.94)
    ax.vlines(x, 0, y, color="#AFC3CE", lw=1.7)
    ax.scatter(x, y, s=48, c=BLUE, marker="o", edgecolor="white", lw=.8, zorder=3)
    for xi, yi, ni in zip(x, y, n):
        ax.text(xi, yi + 2.5, f"{ni} 根\n{yi:.1f}", ha="center", va="bottom", fontsize=8.2)
    ax.set(xlabel="A 体积分数 / %", ylabel="以 10 为底的对数（不导通概率上界）",
           xticks=x, ylim=(-97, 4))
    ax.set_xticklabels([f"{v:.2f}" for v in x])
    style_ax(ax); ax.axhline(0, color=INK, lw=.7)
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
    q4 = results["Q4"]
    relaxed = q4["selected"]
    formal = q4["strictly_positive_mixture"]["selected"]
    a, b, upper, cost = q4_lattice(formal["cost_cny"])
    positive_cheaper = (a >= 1) & (b >= 1) & (cost < formal["cost_cny"] - 1e-15)
    relaxed_cheaper = cost < relaxed["cost_cny"] - 1e-15

    fig, ax = plt.subplots(figsize=(160 / 25.4, 86 / 25.4))
    fig.subplots_adjust(left=.12, right=.98, bottom=.18, top=.94)
    ax.scatter(cost[positive_cheaper], upper[positive_cheaper], s=23, marker="o",
               facecolor="white", edgecolor=GRAY, lw=.7, alpha=.72,
               label="更低成本正混合点（总上界）")
    ax.scatter(cost[relaxed_cheaper & ~positive_cheaper], upper[relaxed_cheaper & ~positive_cheaper],
               s=18, marker="x", color="#8C6D31", lw=.8, alpha=.6,
               label="放宽域边界点（总上界）")

    bad_pos = q4["strictly_positive_mixture"]["maximum_upper_bound_among_cheaper"]
    bad_rel = q4["maximum_upper_bound_among_cheaper"]
    ax.scatter([bad_pos["cost_cny"]], [bad_pos["conduction_upper_bound"]],
               marker="^", s=58, color=RED, edgecolor="white", lw=.6, zorder=6)
    ax.annotate("1A+49B：上界 0.899244", (bad_pos["cost_cny"], bad_pos["conduction_upper_bound"]),
                xytext=(-128, -23), textcoords="offset points", color=RED, fontsize=8,
                arrowprops={"arrowstyle": "->", "color": RED, "lw": .8})
    ax.scatter([bad_rel["cost_cny"]], [bad_rel["conduction_upper_bound"]],
               marker="v", s=48, color="#8C6D31", edgecolor="white", lw=.6, zorder=6)

    ax.scatter([formal["cost_cny"]], [formal["direct_bridge_lower_bound"]],
               marker="D", s=65, color=ORANGE, edgecolor="white", lw=.8, zorder=7,
               label="1A+50B（主口径下界）")
    ax.scatter([relaxed["cost_cny"]], [relaxed["direct_bridge_lower_bound"]],
               marker="*", s=110, color=GREEN, edgecolor="white", lw=.8, zorder=7,
               label="0A+57B（放宽域下界）")
    ax.axhline(.9, color=INK, ls=(0, (5, 3)), lw=1, label="目标 0.90")
    ax.set(xlabel="材料成本 / 元", ylabel="导通概率界", xlim=(.08, .1003), ylim=(.835, .908))
    style_ax(ax); ax.legend(loc="lower left", frameon=False, ncol=2, columnspacing=1.0)
    save(fig, "C08_q4_cost_frontier")


def required_count(q: np.ndarray) -> np.ndarray:
    return np.ceil(np.log(.1) / np.log(1 - q)).astype(int)


def c09_sensitivity_threshold_counts() -> None:
    heights = np.linspace(3500, 6500, 121)
    q_a = heights / (2 * BOX_SIDE) + 2 * ROD_RADIUS * (math.pi / 4) / BOX_SIDE
    radii = np.linspace(120, 280, 161)
    q_b = 2 * radii / BOX_SIDE
    fig, axes = plt.subplots(1, 2, figsize=(160 / 25.4, 82 / 25.4))
    fig.subplots_adjust(left=.09, right=.98, bottom=.20, top=.94, wspace=.30)
    axes[0].step(heights, required_count(q_a), where="mid", color=BLUE, lw=1.8)
    axes[0].scatter([5000], [required_count(np.array([5000/(2*BOX_SIDE)+2*ROD_RADIUS*(math.pi/4)/BOX_SIDE]))[0]], color=RED, s=35, zorder=3)
    axes[0].axvline(5000, color=RED, ls=":", lw=.8)
    axes[0].set(xlabel="A 高度 H / nm", ylabel="达到 90% 所需 A 数量 / 根")
    axes[0].annotate("基准：8 根", (5000, 8), xytext=(5100, 9.2), fontsize=7.8, color=RED,
                     arrowprops={"arrowstyle":"-","color":RED,"lw":.7})
    style_ax(axes[0])
    axes[1].step(radii, required_count(q_b), where="mid", color=ORANGE, lw=1.8)
    axes[1].scatter([SPHERE_RADIUS], [required_count(np.array([2*SPHERE_RADIUS/BOX_SIDE]))[0]], color=RED, s=35, zorder=3)
    axes[1].axvline(SPHERE_RADIUS, color=RED, ls=":", lw=.8)
    axes[1].set(xlabel="B 半径 R / nm", ylabel="达到 90% 所需 B 数量 / 个")
    axes[1].annotate("基准：57 个", (200, 57), xytext=(210, 66), fontsize=7.8, color=RED,
                     arrowprops={"arrowstyle":"-","color":RED,"lw":.7})
    style_ax(axes[1])
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
    "S01_problem_geometry",
    "S02_workflow",
    "S03_data_audit",
    "S04_flat_cylinder_certificate",
    "C03_q1_path_certificate",
    "S05_direct_bridge_mechanism",
    "S06_orientation_support",
    "S07_event_bounds",
    "C04_q3_bounds_band",
    "C05_q2_failure_lollipop",
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
    s01_problem_geometry()
    s02_workflow()
    s03_data_audit(results, groups)
    s04_flat_cylinder_certificate()
    s05_direct_bridge_mechanism()
    s06_orientation_support()
    s07_event_bounds()
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
    print(f"generated 17 candidates in {CANDIDATES}")
    print(f"selected {len(SELECTED)} finalists in {FINAL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
