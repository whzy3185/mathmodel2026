#!/usr/bin/env python3
"""Fail closed when claims are not supported by current, hash-matched artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ARTIFACT_TYPES = {"data", "model", "result", "table", "figure", "paper"}
ARTIFACT_STATUSES = {"current", "stale"}
CLAIM_STATUSES = {"draft", "validated", "stale", "rejected"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_path(root: Path, relative: Any) -> Path | None:
    if not isinstance(relative, str) or not relative.strip():
        return None
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def validate_evidence(claim_document: Any, artifact_document: Any, root: Path) -> list[str]:
    errors: list[str] = []
    claims = claim_document.get("claims") if isinstance(claim_document, dict) else None
    artifacts = artifact_document.get("artifacts") if isinstance(artifact_document, dict) else None
    if not isinstance(claims, list):
        errors.append("claim document must contain a claims array")
        claims = []
    if not isinstance(artifacts, list):
        errors.append("artifact document must contain an artifacts array")
        artifacts = []

    artifact_map: dict[str, dict[str, Any]] = {}
    for index, artifact in enumerate(artifacts):
        label = f"artifact[{index}]"
        if not isinstance(artifact, dict):
            errors.append(f"{label}: must be an object")
            continue
        artifact_id = artifact.get("artifact_id")
        if not isinstance(artifact_id, str) or not artifact_id.strip():
            errors.append(f"{label}: artifact_id is empty")
            continue
        if artifact_id in artifact_map:
            errors.append(f"duplicate artifact_id: {artifact_id}")
        artifact_map[artifact_id] = artifact
        if artifact.get("type") not in ARTIFACT_TYPES:
            errors.append(f"{artifact_id}: invalid artifact type")
        if artifact.get("status") not in ARTIFACT_STATUSES:
            errors.append(f"{artifact_id}: invalid artifact status")
        for field in ("content_hash", "created_by", "created_at"):
            if not isinstance(artifact.get(field), str) or not artifact[field].strip():
                errors.append(f"{artifact_id}: {field} is empty")
        source_ids = artifact.get("source_artifacts")
        if not isinstance(source_ids, list):
            errors.append(f"{artifact_id}: source_artifacts must be an array")
        path = _safe_path(root, artifact.get("path"))
        if path is None:
            errors.append(f"{artifact_id}: path is empty or escapes registry root")
        elif not path.is_file():
            errors.append(f"{artifact_id}: artifact file does not exist: {artifact.get('path')}")
        elif artifact.get("content_hash") != sha256_file(path):
            errors.append(f"{artifact_id}: content hash mismatch")

    for artifact_id, artifact in artifact_map.items():
        for source_id in artifact.get("source_artifacts", []):
            if source_id not in artifact_map:
                errors.append(f"{artifact_id}: missing source artifact {source_id}")

    claim_ids: set[str] = set()
    for index, claim in enumerate(claims):
        label = f"claim[{index}]"
        if not isinstance(claim, dict):
            errors.append(f"{label}: must be an object")
            continue
        claim_id = claim.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id.strip():
            errors.append(f"{label}: claim_id is empty")
            claim_id = label
        elif claim_id in claim_ids:
            errors.append(f"duplicate claim_id: {claim_id}")
        claim_ids.add(claim_id)
        if claim.get("status") not in CLAIM_STATUSES:
            errors.append(f"{claim_id}: invalid claim status")
        for field in ("text", "question_id"):
            if not isinstance(claim.get(field), str) or not claim[field].strip():
                errors.append(f"{claim_id}: {field} is empty")
        artifact_ids = claim.get("artifact_ids")
        if not isinstance(artifact_ids, list):
            errors.append(f"{claim_id}: artifact_ids must be an array")
            artifact_ids = []
        if claim.get("value") is not None and (
            not isinstance(claim.get("unit"), str) or not claim["unit"].strip()
        ):
            errors.append(f"{claim_id}: quantitative claim is missing a unit")
        if claim.get("status") == "validated":
            if not artifact_ids:
                errors.append(f"{claim_id}: validated claim has no artifacts")
            for artifact_id in artifact_ids:
                artifact = artifact_map.get(artifact_id)
                if artifact is None:
                    errors.append(f"{claim_id}: referenced artifact does not exist: {artifact_id}")
                elif artifact.get("status") != "current":
                    errors.append(f"{claim_id}: stale artifact supports validated claim: {artifact_id}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("claims", type=Path)
    parser.add_argument("artifacts", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        claim_document = json.loads(args.claims.read_text(encoding="utf-8"))
        artifact_document = json.loads(args.artifacts.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print("FAIL")
        print(f"- cannot read registry: {exc}")
        return 1
    errors = validate_evidence(claim_document, artifact_document, args.root.resolve())
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
