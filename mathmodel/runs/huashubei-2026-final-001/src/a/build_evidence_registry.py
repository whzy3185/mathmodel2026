#!/usr/bin/env python3
"""Build hash-current dependency and claim registries."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[2]; created_at = datetime.now(timezone.utc).isoformat()
    specs = [
        ("official-a", "data", "input/problems/problem_A.pdf", []),
        ("attachment-a", "data", "data/raw/A/attachment.xlsx", ["official-a"]),
        ("requirements", "model", "requirements.txt", []),
        ("geometry-code", "model", "src/a/geometry.py", ["requirements"]),
        ("bounds-code", "model", "src/a/analytic_bounds.py", ["requirements"]),
        ("result-builder", "model", "src/a/build_corrected_results.py", ["geometry-code", "bounds-code"]),
        ("final-results", "result", "outputs/data/final_results.json", ["official-a", "attachment-a", "result-builder"]),
        ("figure-code", "model", "src/a/build_final_artifacts.py", ["requirements"]),
        ("figure-f1", "figure", "outputs/figures/F1_q3_threshold.pdf", ["final-results", "figure-code"]),
        ("figure-f2", "figure", "outputs/figures/F2_q2_failure_scale.pdf", ["final-results", "figure-code"]),
        ("figure-f3", "figure", "outputs/figures/F3_q4_cost_validation.pdf", ["final-results", "figure-code"]),
        ("paper", "paper", "paper/paper.md", ["final-results", "figure-f1", "figure-f2", "figure-f3"]),
        ("paper-full-md", "paper", "paper/paper_full.md", ["final-results", "attachment-a"]),
        ("research-figure-code", "model", "src/a/build_research_figures.py", ["requirements"]),
        ("research-q2", "figure", "outputs/figures_research/C05_q2_failure_lollipop.pdf", ["final-results", "research-figure-code"]),
        ("research-q3", "figure", "outputs/figures_research/C04_q3_bounds_band.pdf", ["final-results", "research-figure-code"]),
        ("research-q4", "figure", "outputs/figures_research/C08_q4_cost_frontier.pdf", ["final-results", "research-figure-code"]),
        ("paper-full-docx", "paper", "paper/华数杯A题完整论文.docx", ["paper-full-md"]),
        ("paper-full-pdf", "paper", "paper/华数杯A题完整论文.pdf", ["paper-full-docx"]),
    ]
    artifacts = []
    for artifact_id, artifact_type, relative, sources in specs:
        path = root / relative
        artifacts.append({"artifact_id": artifact_id, "type": artifact_type, "path": relative, "source_artifacts": sources, "content_hash": digest(path), "created_by": "reproducible project workflow", "created_at": created_at, "status": "current"})
    claims = [
        {"claim_id": "C-Q1", "text": "Group 1 is disconnected; groups 2 and 3 are connected when each attachment row is one A.", "question_id": "Q1", "artifact_ids": ["attachment-a", "geometry-code", "final-results", "paper"], "metric": "connected groups", "value": 2, "unit": "groups", "uncertainty": "deterministic row-level graph; positive paths certified by interior side contacts", "baseline": "all-pairs exact axis broadphase check", "failure_threshold": "path certificate fails or broadphase differs", "status": "validated"},
        {"claim_id": "C-Q2", "text": "All four requested A fractions have failure-probability upper bounds below 1e-45.", "question_id": "Q2", "artifact_ids": ["bounds-code", "final-results", "figure-f2", "paper"], "metric": "largest failure-probability upper bound", "value": 6.35e-46, "unit": "probability", "uncertainty": "analytic direct-bridge sufficient condition", "baseline": "direct bridge only", "failure_threshold": "analytic bound not reproduced", "status": "validated"},
        {"claim_id": "C-Q3", "text": "Eight A are sufficient and seven A are insufficient by analytic lower and upper bounds.", "question_id": "Q3", "artifact_ids": ["bounds-code", "final-results", "figure-f1", "paper"], "metric": "minimum A count", "value": 8, "unit": "conductors", "uncertainty": "deterministic analytic bounds", "baseline": "direct bridge plus terminal-pair union bound", "failure_threshold": "8 lower bound <=0.90 or 7 upper bound >=0.90", "status": "validated"},
        {"claim_id": "C-Q4", "text": "Under the strict both-materials-positive interpretation, 1 A plus 50 B is the least-cost solution; 0 A plus 57 B is the relaxed-domain boundary solution.", "question_id": "Q4", "artifact_ids": ["bounds-code", "final-results", "research-q4", "paper-full-docx"], "metric": "strict-mixture material cost", "value": 0.09861982912029291, "unit": "CNY", "uncertainty": "exhaustive 164-candidate analytic proof conditional on the declared probability model", "baseline": "all lower-cost positive-integer combinations", "failure_threshold": "selected lower bound <=0.90 or any cheaper upper bound >=0.90", "status": "validated"},
    ]
    evidence = root / "evidence"; evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "artifact_registry.json").write_text(json.dumps({"schema_version": "1.0", "artifacts": artifacts}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (evidence / "claim_evidence.json").write_text(json.dumps({"schema_version": "1.0", "claims": claims}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
