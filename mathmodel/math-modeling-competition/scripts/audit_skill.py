#!/usr/bin/env python3
"""Deterministic structural audit for the packaged skill."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED = (
    "SKILL.md", "agents/openai.yaml", "sources/manifest.json",
    "references/problem-taxonomy.md", "references/model-selection.md",
    "references/validation.md", "references/failure-patterns.md",
    "templates/candidate-model-tournament.json", "templates/claim-evidence.json",
    "templates/artifact-registry.json", "templates/code/rolling_forecast.py",
    "templates/code/tabular_pipeline.py", "templates/code/optimization_utils.py",
    "templates/code/ode_utils.py", "templates/code/monte_carlo.py",
    "templates/code/graph_robustness.py", "templates/code/result_io.py",
    "scripts/check_evidence.py", "scripts/invalidate_artifacts.py",
    "benchmarks/benchmark_cases.json"
)
BENCHMARK_CATEGORIES = {"forecasting", "optimization", "evaluation", "network", "mechanism", "spatial", "simulation", "policy"}


def audit(root: Path) -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED:
        path = root / relative
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"missing or empty: {relative}")
    manifest_path = root / "sources" / "manifest.json"
    if manifest_path.is_file():
        items = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(items, list) or len(items) < 30:
            errors.append("manifest must contain at least 30 resources")
        required_fields = {"name", "type", "url", "source", "license", "quality", "usage", "notes", "accessed_at"}
        for index, item in enumerate(items if isinstance(items, list) else []):
            missing = required_fields - item.keys()
            if missing:
                errors.append(f"manifest[{index}] missing {sorted(missing)}")
    benchmark_path = root / "benchmarks" / "benchmark_cases.json"
    if benchmark_path.is_file():
        cases = json.loads(benchmark_path.read_text(encoding="utf-8"))
        found = {case.get("category") for case in cases}
        if not BENCHMARK_CATEGORIES.issubset(found):
            errors.append(f"benchmark categories missing: {sorted(BENCHMARK_CATEGORIES - found)}")
    skill_text = (root / "SKILL.md").read_text(encoding="utf-8") if (root / "SKILL.md").is_file() else ""
    if skill_text.count("---") < 2 or "name: math-modeling-competition" not in skill_text:
        errors.append("invalid SKILL.md frontmatter")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("skill", type=Path)
    args = parser.parse_args()
    errors = audit(args.skill.resolve())
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
