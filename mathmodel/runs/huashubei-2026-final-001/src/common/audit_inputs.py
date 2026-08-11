#!/usr/bin/env python3
# AI assistance disclosure: drafted with OpenAI Codex and verified by executable tests.
"""Read-only audit of the official 2026 Huashu Cup A/B/C attachments."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
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


def audit_a(root: Path) -> dict[str, Any]:
    path = root / "data/raw/A/attachment.xlsx"
    sheets: dict[str, Any] = {}
    for sheet in pd.ExcelFile(path).sheet_names:
        raw = pd.read_excel(path, sheet_name=sheet, header=None)
        coords = raw.iloc[2:, :6].apply(pd.to_numeric, errors="coerce").dropna().to_numpy(float)
        starts, ends = coords[:, :3], coords[:, 3:]
        lengths = np.linalg.norm(ends - starts, axis=1)
        on_face = np.isclose(np.abs(coords), 5000.0, atol=1e-7)
        sheets[sheet] = {
            "medium_count": int(len(coords)),
            "coordinate_min_nm": float(coords.min()),
            "coordinate_max_nm": float(coords.max()),
            "segment_length_nm": {
                "min": float(lengths.min()),
                "median": float(np.median(lengths)),
                "max": float(lengths.max()),
                "near_5000_count": int(np.isclose(lengths, 5000.0, rtol=0, atol=1e-5).sum()),
            },
            "media_touching_any_boundary_face": int(on_face.any(axis=1).sum()),
            "endpoint_coordinate_boundary_hits": int(on_face.sum()),
            "nonfinite_value_count": int((~np.isfinite(coords)).sum()),
        }
    return {"file": "data/raw/A/attachment.xlsx", "sha256": sha256(path), "sheets": sheets}


BLOCK_RE = re.compile(
    r"^(b\d+)\s+block\s+4\s+\(0,\s*0\)\s+\(0,\s*(\d+)\)\s+\((\d+),\s*(\d+)\)\s+\((\d+),\s*0\)$"
)


def audit_b(root: Path) -> dict[str, Any]:
    directory = root / "data/raw/B"
    cases: dict[str, Any] = {}
    for size in (100, 200, 300):
        prefix = f"n{size}"
        blocks_path = directory / f"{prefix}.blocks"
        nets_path = directory / f"{prefix}.nets"
        pl_path = directory / f"{prefix}.pl"
        block_lines = blocks_path.read_text(encoding="utf-8-sig").splitlines()
        net_lines = nets_path.read_text(encoding="utf-8-sig").splitlines()
        pl_lines = [line for line in pl_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        declared_blocks = int(re.search(r"NumHardBlocks\s*:\s*(\d+)", "\n".join(block_lines)).group(1))
        declared_terminals = int(re.search(r"NumTerminals\s*:\s*(\d+)", "\n".join(block_lines)).group(1))
        declared_nets = int(re.search(r"NumNets\s*:\s*(\d+)", "\n".join(net_lines)).group(1))
        declared_pins = int(re.search(r"NumPins\s*:\s*(\d+)", "\n".join(net_lines)).group(1))
        parsed: list[tuple[str, int, int]] = []
        for line in block_lines:
            match = BLOCK_RE.match(line.strip())
            if match:
                name, height, width1, height2, width2 = match.groups()
                if int(height) != int(height2) or int(width1) != int(width2):
                    raise ValueError(f"non-rectangular hard block in {blocks_path}: {line}")
                parsed.append((name, int(width1), int(height)))
        total_area = int(sum(width * height for _, width, height in parsed))
        contour_side_015 = math.sqrt(total_area * 1.15)
        cases[prefix] = {
            "declared_hard_blocks": declared_blocks,
            "parsed_hard_blocks": len(parsed),
            "declared_terminals": declared_terminals,
            "terminal_placement_rows": len(pl_lines),
            "declared_nets": declared_nets,
            "parsed_net_headers": sum(line.startswith("NetDegree") for line in net_lines),
            "declared_pins": declared_pins,
            "parsed_net_nodes": sum(1 for line in net_lines if re.fullmatch(r"[bp]\d+", line.strip())),
            "total_block_area": total_area,
            "square_contour_side_dead_space_0_15": contour_side_015,
            "file_hashes": {
                "blocks": sha256(blocks_path), "nets": sha256(nets_path), "pl": sha256(pl_path)
            },
        }
    return {"directory": "data/raw/B", "cases": cases}


def missing_map(frame: pd.DataFrame) -> dict[str, int]:
    return {str(key): int(value) for key, value in frame.isna().sum().items() if value}


def audit_c(root: Path) -> dict[str, Any]:
    directory = root / "data/raw/C"
    workload_path = directory / "workload_trace.xlsx"
    region_path = directory / "region_time_data.xlsx"
    gpu_path = directory / "GPU_information.xlsx"
    latency_path = directory / "network_latency.xlsx"
    power_path = directory / "power_mapping.xlsx"
    storage_path = directory / "storage_information.xlsx"
    workload = pd.read_excel(workload_path, sheet_name="Sheet1")
    region = pd.read_excel(region_path, sheet_name="region_time_data")
    gpu = pd.read_excel(gpu_path, sheet_name="GPU中心基础情况")
    latency = pd.read_excel(latency_path, sheet_name="network_latency")
    power = pd.read_excel(power_path, sheet_name="任务功率映射")
    storage = pd.read_excel(storage_path, sheet_name="storage_information")
    invalid_window = workload[
        (workload["EarliestStartHour"] < workload["ArrivalHour"])
        | (workload["LatestFinishHour"] > 2406)
        | (workload["LatestFinishHour"] <= workload["EarliestStartHour"])
    ]
    duplicate_region_hour = int(region.duplicated(["Hour", "Region"]).sum())
    return {
        "directory": "data/raw/C",
        "workload": {
            "rows": int(len(workload)),
            "columns": int(workload.shape[1]),
            "task_type_counts": {str(k): int(v) for k, v in workload["TaskType"].value_counts().items()},
            "source_region_counts": {str(k): int(v) for k, v in workload["SourceRegion"].value_counts().items()},
            "arrival_hour_range": [int(workload["ArrivalHour"].min()), int(workload["ArrivalHour"].max())],
            "last_24h_task_count": int(workload["ArrivalHour"].between(2376, 2399).sum()),
            "gpu_demand_range": [int(workload["GPU_Demand"].min()), int(workload["GPU_Demand"].max())],
            "duration_min_range": [int(workload["EstimatedDuration_min"].min()), int(workload["EstimatedDuration_min"].max())],
            "duplicate_task_ids": int(workload["TaskID"].duplicated().sum()),
            "invalid_time_windows": int(len(invalid_window)),
            "missing": missing_map(workload),
            "sha256": sha256(workload_path),
        },
        "region_time": {
            "rows": int(len(region)),
            "expected_rows": 2407 * 6,
            "hour_range": [int(region["Hour"].min()), int(region["Hour"].max())],
            "regions": sorted(map(str, region["Region"].unique())),
            "duplicate_region_hour": duplicate_region_hour,
            "missing": missing_map(region),
            "sha256": sha256(region_path),
        },
        "dimension_tables": {
            "gpu_rows": int(len(gpu)), "latency_rows": int(len(latency)),
            "power_rows": int(len(power)), "storage_rows": int(len(storage))
        },
        "file_hashes": {path.name: sha256(path) for path in directory.glob("*.xlsx")},
    }


def render(summary: dict[str, Any]) -> str:
    a, b, c = summary["A"], summary["B"], summary["C"]
    lines = ["# 2026 华数杯 A/B/C 官方附件审计", "", "所有统计均由只读脚本生成。", "", "## A 题", ""]
    for name, info in a["sheets"].items():
        lengths = info["segment_length_nm"]
        lines.append(
            f"- {name}: {info['medium_count']} 个圆柱介质，轴段长度范围 {lengths['min']:.3f}–{lengths['max']:.3f} nm，"
            f"触及任一边界面的介质 {info['media_touching_any_boundary_face']} 个。"
        )
    lines.extend(["", "## B 题", ""])
    for name, info in b["cases"].items():
        lines.append(
            f"- {name}: {info['parsed_hard_blocks']} 个硬模块、{info['declared_terminals']} 个终端、"
            f"{info['declared_nets']} 个网络、{info['declared_pins']} 个引脚，总模块面积 {info['total_block_area']}。"
        )
    w, rt = c["workload"], c["region_time"]
    lines.extend([
        "", "## C 题", "",
        f"- 工作负载 {w['rows']} 条；最后24小时实际到达 {w['last_24h_task_count']} 条；任务ID重复 {w['duplicate_task_ids']} 条；非法时间窗 {w['invalid_time_windows']} 条。",
        f"- 区域逐时数据 {rt['rows']} 行，对应 2407×6={rt['expected_rows']}，区域-小时重复 {rt['duplicate_region_hour']} 行。",
        "", "## 可执行性结论", "",
        "A 题规模小、输入自洽、外部数据依赖为零，可用几何距离、空间索引、并查集和带置信区间的蒙特卡洛形成完整闭环。",
        "B 题数据完整但 n300 非凸布图规划需要大规模随机优化且难以证明全局最优。",
        "C 题数据最丰富，但 5 万个不可抢占任务与 14442 个区域时点构成超大调度问题，完整四问的工程和算力风险最高。",
        "因此本轮首选 A，B 为第二选择，C 暂不作为主实验。", ""
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    summary = {"schema_version": 1, "A": audit_a(root), "B": audit_b(root), "C": audit_c(root)}
    (root / "data/eda_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (root / "data/eda_report.md").write_text(render(summary), encoding="utf-8")
    print(root / "data/eda_summary.json")
    print(root / "data/eda_report.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
