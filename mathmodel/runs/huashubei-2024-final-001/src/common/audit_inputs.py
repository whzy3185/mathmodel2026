#!/usr/bin/env python3
"""Audit the official 2024 Huashu Cup A/B/C attachments.

The script is intentionally read-only with respect to raw inputs. It writes a
machine-readable summary plus a concise Markdown report under ``data/``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scalar(value: Any) -> Any:
    if pd.isna(value):
        return None
    if isinstance(value, np.generic):
        return value.item()
    return value


def audit_a(root: Path) -> dict[str, Any]:
    path = root / "data/raw/A/attachment.xlsx"
    book = pd.ExcelFile(path)
    sheets: dict[str, Any] = {}
    for sheet in book.sheet_names:
        frame = pd.read_excel(path, sheet_name=sheet, header=None)
        note = str(frame.iloc[0, 0])
        grid = frame.iloc[1:, :].copy()
        locations: dict[str, list[int]] = {}
        obstacles = 0
        free = 0
        unexpected: list[dict[str, Any]] = []
        for r_idx, row in grid.iterrows():
            for c_idx, value in row.items():
                value = scalar(value)
                if isinstance(value, str):
                    locations[value] = [int(r_idx - 1), int(c_idx)]
                elif value == 1:
                    obstacles += 1
                elif value == 0:
                    free += 1
                else:
                    unexpected.append({"row": int(r_idx - 1), "column": int(c_idx), "value": value})
        sheets[sheet] = {
            "grid_rows": int(grid.shape[0]),
            "grid_columns": int(grid.shape[1]),
            "cell_size_mm": [200, 200],
            "target_z_mm": 200,
            "obstacle_cells": obstacles,
            "free_cells": free,
            "labeled_cells": locations,
            "unexpected_cells": unexpected,
            "note": note,
        }
    return {
        "file": str(path.relative_to(root)).replace("\\", "/"),
        "sha256": sha256(path),
        "sheets": sheets,
    }


GROUP_RE = re.compile(
    r"^(Group\d+),\((.*?)\),\(\((.*?)\)\),(\d+),(\d+)$"
)
CELL_RE = re.compile(
    r"^(Cell\d+),\((\d+),(\d+)\),(\d+),(\d+),\((.*?)\),\(\((.*?)\)\)$"
)
PAIR_RE = re.compile(r"\((\d+),(\d+)\)")


def audit_b(root: Path) -> dict[str, Any]:
    group_path = root / "data/raw/B/附件1.txt"
    cell_path = root / "data/raw/B/附件2.txt"
    group_lines = group_path.read_text(encoding="utf-8-sig").splitlines()
    groups: list[dict[str, Any]] = []
    group_errors: list[str] = []
    for line_no, line in enumerate(group_lines[1:], start=2):
        if not line.strip():
            continue
        match = GROUP_RE.match(line.strip())
        if not match:
            group_errors.append(f"line {line_no}: parse failure")
            continue
        name, pins_raw, coords_raw, hpwl_raw, rsmt_raw = match.groups()
        pins = pins_raw.split(",")
        coords = [(int(x), int(y)) for x, y in PAIR_RE.findall("((" + coords_raw + "))")]
        hpwl = int(hpwl_raw)
        rsmt = int(rsmt_raw)
        hpwl_recomputed = max(x for x, _ in coords) - min(x for x, _ in coords)
        hpwl_recomputed += max(y for _, y in coords) - min(y for _, y in coords)
        groups.append(
            {
                "name": name,
                "pin_count": len(pins),
                "coordinate_count": len(coords),
                "hpwl": hpwl,
                "rsmt": rsmt,
                "hpwl_recomputed": hpwl_recomputed,
                "pin_coordinate_match": len(pins) == len(coords),
            }
        )

    cell_lines = cell_path.read_text(encoding="utf-8-sig").splitlines()
    region = [float(item) for item in cell_lines[1].split(",")]
    cells: list[dict[str, Any]] = []
    cell_errors: list[str] = []
    for line_no, line in enumerate(cell_lines[4:], start=5):
        if not line.strip():
            continue
        match = CELL_RE.match(line.strip())
        if not match:
            cell_errors.append(f"line {line_no}: parse failure")
            continue
        name, x, y, width, height, pin_names_raw, offsets_raw = match.groups()
        pin_names = pin_names_raw.split(",")
        offsets = [(int(px), int(py)) for px, py in PAIR_RE.findall("((" + offsets_raw + "))")]
        cells.append(
            {
                "name": name,
                "x": int(x),
                "y": int(y),
                "width": int(width),
                "height": int(height),
                "pin_count": len(pin_names),
                "offset_count": len(offsets),
            }
        )

    hpwl_errors = [g for g in groups if g["hpwl"] != g["hpwl_recomputed"]]
    pin_errors = [g for g in groups if not g["pin_coordinate_match"]]
    cell_pin_errors = [c for c in cells if c["pin_count"] != c["offset_count"]]
    return {
        "group_file": str(group_path.relative_to(root)).replace("\\", "/"),
        "cell_file": str(cell_path.relative_to(root)).replace("\\", "/"),
        "sha256": {"groups": sha256(group_path), "cells": sha256(cell_path)},
        "layout": {
            "width": int(region[0]),
            "height": int(region[1]),
            "horizontal_bins": int(region[2]),
            "vertical_bins": int(region[3]),
            "density_limit": region[4],
        },
        "group_count": len(groups),
        "cell_count": len(cells),
        "net_pin_count": int(sum(g["pin_count"] for g in groups)),
        "cell_pin_count": int(sum(c["pin_count"] for c in cells)),
        "group_parse_errors": group_errors,
        "cell_parse_errors": cell_errors,
        "hpwl_recompute_mismatches": len(hpwl_errors),
        "group_pin_coordinate_mismatches": len(pin_errors),
        "cell_pin_offset_mismatches": len(cell_pin_errors),
        "hpwl_total": int(sum(g["hpwl"] for g in groups)),
        "rsmt_total": int(sum(g["rsmt"] for g in groups)),
        "rsmt_minus_hpwl": int(sum(g["rsmt"] - g["hpwl"] for g in groups)),
        "pin_count_distribution": {
            str(k): int(v) for k, v in pd.Series([g["pin_count"] for g in groups]).value_counts().sort_index().items()
        },
    }


def audit_c(root: Path) -> dict[str, Any]:
    data_dir = root / "data/raw/C"
    files = sorted(data_dir.glob("*.csv"))
    records: list[pd.DataFrame] = []
    schema_variants: dict[str, int] = {}
    row_counts: dict[str, int] = {}
    read_errors: list[str] = []
    hashes: dict[str, str] = {}
    for path in files:
        try:
            frame = pd.read_csv(path)
        except Exception as exc:  # pragma: no cover - evidence capture
            read_errors.append(f"{path.name}: {exc}")
            continue
        city = path.stem
        frame["城市"] = city
        records.append(frame)
        row_counts[city] = int(len(frame))
        signature = "|".join(map(str, frame.columns[:-1]))
        schema_variants[signature] = schema_variants.get(signature, 0) + 1
        hashes[path.name] = sha256(path)
    combined = pd.concat(records, ignore_index=True) if records else pd.DataFrame()
    score = pd.to_numeric(combined.get("评分"), errors="coerce")
    best_score = float(score.max()) if score.notna().any() else None
    best = combined.loc[score.eq(best_score), ["城市", "名字"]] if best_score is not None else pd.DataFrame()
    top_city_counts = (
        best.groupby("城市").size().sort_values(ascending=False).head(10).astype(int).to_dict()
        if not best.empty
        else {}
    )
    duplicate_keys = int(combined.duplicated(subset=["城市", "名字", "链接"], keep=False).sum())
    missing_by_column = {str(k): int(v) for k, v in combined.isna().sum().items()}
    return {
        "directory": str(data_dir.relative_to(root)).replace("\\", "/"),
        "city_file_count": len(files),
        "read_errors": read_errors,
        "schema_variant_count": len(schema_variants),
        "schema_variants": schema_variants,
        "row_count": int(len(combined)),
        "expected_row_count_from_problem": 35200,
        "minimum_city_rows": int(min(row_counts.values())) if row_counts else None,
        "maximum_city_rows": int(max(row_counts.values())) if row_counts else None,
        "cities_with_exactly_100_rows": int(sum(value == 100 for value in row_counts.values())),
        "duplicate_city_name_url_rows": duplicate_keys,
        "missing_by_column": missing_by_column,
        "score_observed_count": int(score.notna().sum()),
        "score_min": float(score.min()) if score.notna().any() else None,
        "score_max": best_score,
        "best_score_attraction_count": int(len(best)),
        "best_score_top_city_counts": top_city_counts,
        "file_hashes": hashes,
    }


def render_report(summary: dict[str, Any]) -> str:
    a = summary["A"]
    b = summary["B"]
    c = summary["C"]
    lines = [
        "# 2024 华数杯 A/B/C 官方附件审计",
        "",
        "本报告由 `src/common/audit_inputs.py` 从只读原始附件生成。所有统计均可复现。",
        "",
        "## A 题",
        "",
        f"- Excel 工作表：{', '.join(a['sheets'])}。",
    ]
    for name, sheet in a["sheets"].items():
        labels = ", ".join(f"{key}={value}" for key, value in sheet["labeled_cells"].items())
        lines.append(
            f"- {name}: {sheet['grid_rows']}×{sheet['grid_columns']}，障碍 {sheet['obstacle_cells']} 格，"
            f"自由格 {sheet['free_cells']} 格，标记 {labels}。"
        )
    lines.extend(
        [
            "",
            "## B 题",
            "",
            f"- {b['cell_count']} 个电路单元、{b['group_count']} 个连接组、{b['net_pin_count']} 个网络端点。",
            f"- 原布局 HPWL 总和 {b['hpwl_total']}，RSMT 总和 {b['rsmt_total']}，差值 {b['rsmt_minus_hpwl']}。",
            f"- HPWL 复算不一致 {b['hpwl_recompute_mismatches']} 组；网络端点/坐标不一致 "
            f"{b['group_pin_coordinate_mismatches']} 组；单元端口/偏移不一致 {b['cell_pin_offset_mismatches']} 个。",
            "",
            "## C 题",
            "",
            f"- 城市文件 {c['city_file_count']} 个，实际景点记录 {c['row_count']} 条；题面宣称 35200 条。",
            f"- 仅 {c['cities_with_exactly_100_rows']} 个城市恰有 100 条；单城范围 "
            f"{c['minimum_city_rows']}–{c['maximum_city_rows']} 条。",
            f"- 可用评分 {c['score_observed_count']} 条，范围 {c['score_min']}–{c['score_max']}；"
            f"最高评分景点 {c['best_score_attraction_count']} 个。",
            f"- 同城名称与网址重复行（包含重复组全部成员）{c['duplicate_city_name_url_rows']} 条。",
            "",
            "## 可执行性结论",
            "",
            "A 题附件结构最完整且外部数据依赖最低；B 题数据结构严整但四问实现和求解规模较高；"
            "C 题原始记录数与题面不一致，且第 2–5 问必须补充城市评价、高铁时刻与票价等外部数据。",
            "因此当前完整实验首选 A 题，B 题为第二选择，C 题不作为本轮主实验。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    summary = {"schema_version": 1, "A": audit_a(root), "B": audit_b(root), "C": audit_c(root)}
    summary_path = root / "data/eda_summary.json"
    report_path = root / "data/eda_report.md"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(render_report(summary), encoding="utf-8")
    print(summary_path)
    print(report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
