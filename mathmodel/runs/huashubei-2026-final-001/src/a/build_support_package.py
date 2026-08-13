#!/usr/bin/env python3
"""Build the clean paper support package and its hash manifest."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path


RUN = Path(__file__).resolve().parents[2]
PAPER = RUN / "paper"
PACKAGE = PAPER / "华数杯A题论文_支撑材料包.zip"
MANIFEST = PAPER / "support_package_manifest.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_files() -> list[tuple[Path, str]]:
    fixed = [
        (PAPER / "华数杯A题完整论文.docx", "paper/华数杯A题完整论文.docx"),
        (PAPER / "华数杯A题完整论文.pdf", "paper/华数杯A题完整论文.pdf"),
        (PAPER / "paper_full.md", "paper/paper_full.md"),
        (RUN / "input/attachments/official_problem_bundle.zip", "official/official_problem_bundle.zip"),
        (RUN / "input/problems/problem_A.pdf", "official/problem_A.pdf"),
        (RUN / "data/raw/A/attachment.xlsx", "official/attachment_A.xlsx"),
        (RUN / "rules/official_format_rules.pdf", "official/official_format_rules.pdf"),
        (RUN / "outputs/data/final_results.json", "results/final_results.json"),
        (RUN / "requirements.txt", "reproduction/requirements.txt"),
        (RUN / "evidence/artifact_registry.json", "evidence/artifact_registry.json"),
        (RUN / "evidence/claim_evidence.json", "evidence/claim_evidence.json"),
        (RUN / "evidence/figure_contracts.md", "evidence/figure_contracts.md"),
        (RUN / "evidence/research_figure_upgrade.md", "evidence/research_figure_upgrade.md"),
        (RUN / "training/award_paper_writing_visual_guide.md", "training/award_paper_writing_visual_guide.md"),
        (RUN / "training/expanded_paper_sources.md", "training/expanded_paper_sources.md"),
        (RUN / "training/source_manifest_expanded.json", "training/source_manifest_expanded.json"),
        (RUN / "training/cumcm_high_score_papers_catalog.json", "training/cumcm_high_score_papers_catalog.json"),
        (RUN / "training/cumcm_high_score_papers_catalog.csv", "training/cumcm_high_score_papers_catalog.csv"),
        (RUN / "training/cumcm_high_score_papers_catalog.md", "training/cumcm_high_score_papers_catalog.md"),
        (RUN / "training/scripts/build_cumcm_reference_catalog.py", "training/scripts/build_cumcm_reference_catalog.py"),
    ]
    dynamic: list[tuple[Path, str]] = []
    for path in sorted((RUN / "outputs/figures_v2").glob("*.png")):
        dynamic.append((path, f"figures/{path.name}"))
    for path in sorted((RUN / "outputs/figures_research").glob("*")):
        if path.is_file():
            dynamic.append((path, f"figures_selected/{path.name}"))
    for path in sorted((RUN / "outputs/figure_candidates").glob("*")):
        if path.is_file():
            dynamic.append((path, f"figure_candidates/{path.name}"))
    for path in sorted((RUN / "reports").glob("*.md")):
        dynamic.append((path, f"review_reports/{path.name}"))
    for path in sorted((RUN / "src/a").glob("*.py")):
        dynamic.append((path, f"src/a/{path.name}"))
    for path in sorted((RUN / "tests").glob("test_*.py")):
        dynamic.append((path, f"tests/{path.name}"))
    return fixed + dynamic


def main() -> int:
    files = package_files()
    missing = [str(path) for path, _ in files if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing package files: " + ", ".join(missing))

    records = [
        {
            "archive_path": archive,
            "source_path": path.relative_to(RUN).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": digest(path),
        }
        for path, archive in files
    ]
    manifest = {
        "schema_version": "1.0",
        "run_id": "huashubei-2026-final-001",
        "description": "Full paper, figure candidates, selected figures, references, review reports and reproducibility files",
        "file_count": len(records),
        "files": records,
    }
    MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    with zipfile.ZipFile(PACKAGE, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        archive.write(MANIFEST, "PACKAGE_MANIFEST.json")
        for path, archive_path in files:
            archive.write(path, archive_path)

    with zipfile.ZipFile(PACKAGE) as archive:
        bad = archive.testzip()
        if bad is not None:
            raise RuntimeError(f"corrupt member: {bad}")
        expected = {"PACKAGE_MANIFEST.json", *(archive for _, archive in files)}
        if set(archive.namelist()) != expected:
            raise RuntimeError("package member set mismatch")

    print(PACKAGE)
    print(digest(PACKAGE))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
