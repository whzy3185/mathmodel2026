"""Canonical, hash-aware JSON result records."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def make_result(
    *,
    model: str,
    version: str,
    status: str,
    metrics: dict[str, Any],
    data_path: Path,
    seed: int | None = None,
    artifact_id: str = "",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not data_path.is_file():
        raise FileNotFoundError(data_path)
    record = {
        "schema_version": "1.0",
        "artifact_id": artifact_id,
        "model": model,
        "model_version": version,
        "seed": seed,
        "data": {"path": str(data_path), "sha256": sha256_file(data_path)},
        "metrics": metrics,
        "status": status,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if extra:
        record["extra"] = extra
    return record


def write_result(path: Path, record: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
