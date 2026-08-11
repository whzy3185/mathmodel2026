#!/usr/bin/env python3
# AI assistance disclosure: drafted with OpenAI Codex and verified by check_evidence.py.
"""Build hash-current claim and artifact registries for the final paper."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    created_at = datetime.now(timezone.utc).isoformat()
    specs = [
        ("official-a", "data", "input/problems/problem_A.pdf", []),
        ("q3-mc", "result", "outputs/data/literal_q3_final_50000.json", ["official-a"]),
        ("q4-mc", "result", "outputs/data/literal_q4_final_100000.json", ["official-a"]),
        ("final-results", "result", "outputs/data/final_results.json", ["q3-mc", "q4-mc"]),
        ("figure-f1", "figure", "outputs/figures/F1_q3_threshold.pdf", ["final-results"]),
        ("figure-f2", "figure", "outputs/figures/F2_q2_failure_scale.pdf", ["final-results"]),
        ("figure-f3", "figure", "outputs/figures/F3_q4_cost_validation.pdf", ["final-results"]),
        ("paper", "paper", "paper/paper.md", ["final-results", "figure-f1", "figure-f2", "figure-f3"]),
    ]
    artifacts = []
    for artifact_id, artifact_type, relative, sources in specs:
        path = root / relative
        artifacts.append({
            "artifact_id": artifact_id,
            "type": artifact_type,
            "path": relative,
            "source_artifacts": sources,
            "content_hash": digest(path),
            "created_by": "reproducible project workflow",
            "created_at": created_at,
            "status": "current",
        })
    claims = [
        {"claim_id": "C-Q1", "text": "All three supplied groups conduct under periodic fragment identity.", "question_id": "Q1", "artifact_ids": ["final-results", "paper"], "metric": "connected groups", "value": 3, "unit": "groups", "uncertainty": "deterministic graph", "baseline": "fragment-independent graph", "failure_threshold": "any missing left-right path", "status": "validated"},
        {"claim_id": "C-Q2", "text": "All four requested A fractions have conduction probability indistinguishable from one at reporting precision.", "question_id": "Q2", "artifact_ids": ["final-results", "figure-f2", "paper"], "metric": "largest failure-probability upper bound", "value": 6.35e-46, "unit": "probability", "uncertainty": "analytic direct-bridge bound", "baseline": "direct periodic bridge only", "failure_threshold": "bound not negligible", "status": "validated"},
        {"claim_id": "C-Q3", "text": "Eight A conductors are sufficient and seven are insufficient under the stated confidence rule.", "question_id": "Q3", "artifact_ids": ["q3-mc", "final-results", "figure-f1", "paper"], "metric": "minimum A count", "value": 8, "unit": "conductors", "uncertainty": "50000 replications; Wilson intervals", "baseline": "analytic direct bridge", "failure_threshold": "7-count upper interval reaches 0.90 or 8-count lower interval falls below 0.90", "status": "validated"},
        {"claim_id": "C-Q4", "text": "The lowest confidence-feasible tested cost is 57 B spheres and no A cylinders.", "question_id": "Q4", "artifact_ids": ["q4-mc", "final-results", "figure-f3", "paper"], "metric": "material cost", "value": 0.09550441666912972, "unit": "CNY", "uncertainty": "100000 replications; 95% Wilson interval [0.90095, 0.90462]", "baseline": "56 B and every cheaper frontier neighbor", "failure_threshold": "selected lower interval below 0.90 or cheaper candidate lower interval at least 0.90", "status": "validated"}
    ]
    evidence_dir = root / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "artifact_registry.json").write_text(json.dumps({"schema_version": "1.0", "artifacts": artifacts}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (evidence_dir / "claim_evidence.json").write_text(json.dumps({"schema_version": "1.0", "claims": claims}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(evidence_dir / "artifact_registry.json")
    print(evidence_dir / "claim_evidence.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
