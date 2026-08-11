#!/usr/bin/env python3
"""Propagate upstream artifact changes to descendants and supporting claims."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def invalidation_closure(artifacts: list[dict[str, Any]], changed_ids: set[str]) -> set[str]:
    known = {artifact.get("artifact_id") for artifact in artifacts}
    missing = changed_ids - known
    if missing:
        raise ValueError(f"unknown artifact ids: {sorted(missing)}")
    stale = set(changed_ids)
    progressed = True
    while progressed:
        progressed = False
        for artifact in artifacts:
            artifact_id = artifact.get("artifact_id")
            if artifact_id not in stale and stale.intersection(artifact.get("source_artifacts", [])):
                stale.add(artifact_id)
                progressed = True
    return stale


def invalidate(
    artifact_document: dict[str, Any], claim_document: dict[str, Any], changed_ids: set[str]
) -> dict[str, Any]:
    artifacts = artifact_document.get("artifacts")
    claims = claim_document.get("claims")
    if not isinstance(artifacts, list) or not isinstance(claims, list):
        raise ValueError("registries must contain artifacts and claims arrays")
    stale_ids = invalidation_closure(artifacts, changed_ids)
    for artifact in artifacts:
        if artifact.get("artifact_id") in stale_ids:
            artifact["status"] = "stale"
    stale_claims: list[str] = []
    for claim in claims:
        if stale_ids.intersection(claim.get("artifact_ids", [])):
            claim["status"] = "stale"
            stale_claims.append(claim.get("claim_id", ""))
    return {"stale_artifact_ids": sorted(stale_ids), "stale_claim_ids": sorted(stale_claims)}


def _write_json(path: Path, data: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifacts", type=Path)
    parser.add_argument("claims", type=Path)
    parser.add_argument("changed_artifact_ids", nargs="+")
    args = parser.parse_args()
    try:
        artifact_document = json.loads(args.artifacts.read_text(encoding="utf-8"))
        claim_document = json.loads(args.claims.read_text(encoding="utf-8"))
        summary = invalidate(artifact_document, claim_document, set(args.changed_artifact_ids))
        _write_json(args.artifacts, artifact_document)
        _write_json(args.claims, claim_document)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print("FAIL")
        print(f"- cannot invalidate registries: {exc}")
        return 1
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
