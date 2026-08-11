from __future__ import annotations

import copy
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_evidence import validate_evidence  # noqa: E402
from invalidate_artifacts import invalidate  # noqa: E402


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        paths = {}
        for artifact_id in ("DATA-001", "MODEL-001", "RESULT-001", "FIG-001", "PAPER-001"):
            path = self.root / f"{artifact_id}.txt"
            path.write_text(artifact_id, encoding="utf-8")
            paths[artifact_id] = path
        self.artifacts = {
            "schema_version": "1.0",
            "artifacts": [
                self.artifact("DATA-001", "data", paths["DATA-001"], []),
                self.artifact("MODEL-001", "model", paths["MODEL-001"], ["DATA-001"]),
                self.artifact("RESULT-001", "result", paths["RESULT-001"], ["MODEL-001"]),
                self.artifact("FIG-001", "figure", paths["FIG-001"], ["RESULT-001"]),
                self.artifact("PAPER-001", "paper", paths["PAPER-001"], ["FIG-001"]),
            ],
        }
        self.claims = {
            "schema_version": "1.0",
            "claims": [
                {
                    "claim_id": "CLAIM-001",
                    "text": "The measured value is 2.0.",
                    "question_id": "Q1",
                    "artifact_ids": ["RESULT-001", "FIG-001"],
                    "metric": "estimate",
                    "value": 2.0,
                    "unit": "items",
                    "uncertainty": "95% CI [1.8, 2.2]",
                    "baseline": "1.5 items",
                    "failure_threshold": "CI crosses zero",
                    "status": "validated",
                }
            ],
        }

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def artifact(self, artifact_id: str, kind: str, path: Path, sources: list[str]) -> dict:
        return {
            "artifact_id": artifact_id,
            "type": kind,
            "path": path.name,
            "source_artifacts": sources,
            "content_hash": digest(path),
            "created_by": "unit test",
            "created_at": "2026-08-11T10:00:00+08:00",
            "status": "current",
        }

    def assert_invalid(self, claims: dict, artifacts: dict, text: str) -> None:
        errors = validate_evidence(claims, artifacts, self.root)
        self.assertTrue(any(text in error for error in errors), errors)

    def test_valid_registry_passes(self) -> None:
        self.assertEqual([], validate_evidence(self.claims, self.artifacts, self.root))

    def test_validated_claim_without_artifact_fails(self) -> None:
        claims = copy.deepcopy(self.claims)
        claims["claims"][0]["artifact_ids"] = []
        self.assert_invalid(claims, self.artifacts, "has no artifacts")

    def test_missing_artifact_fails(self) -> None:
        claims = copy.deepcopy(self.claims)
        claims["claims"][0]["artifact_ids"] = ["RESULT-999"]
        self.assert_invalid(claims, self.artifacts, "does not exist")

    def test_stale_artifact_cannot_support_validated_claim(self) -> None:
        artifacts = copy.deepcopy(self.artifacts)
        artifacts["artifacts"][2]["status"] = "stale"
        self.assert_invalid(self.claims, artifacts, "stale artifact")

    def test_quantitative_claim_requires_unit(self) -> None:
        claims = copy.deepcopy(self.claims)
        claims["claims"][0]["unit"] = ""
        self.assert_invalid(claims, self.artifacts, "missing a unit")

    def test_hash_mismatch_fails(self) -> None:
        artifacts = copy.deepcopy(self.artifacts)
        artifacts["artifacts"][2]["content_hash"] = "0" * 64
        self.assert_invalid(self.claims, artifacts, "content hash mismatch")

    def test_invalidation_propagates_to_paper_and_claim(self) -> None:
        artifacts = copy.deepcopy(self.artifacts)
        claims = copy.deepcopy(self.claims)
        summary = invalidate(artifacts, claims, {"DATA-001"})
        self.assertEqual(
            {"DATA-001", "MODEL-001", "RESULT-001", "FIG-001", "PAPER-001"},
            set(summary["stale_artifact_ids"]),
        )
        self.assertEqual("stale", claims["claims"][0]["status"])
        self.assertTrue(all(item["status"] == "stale" for item in artifacts["artifacts"]))


if __name__ == "__main__":
    unittest.main()
