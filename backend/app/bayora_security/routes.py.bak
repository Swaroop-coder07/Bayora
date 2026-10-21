import csv
import hashlib
import io
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

AUDIT_DIR = Path(os.getenv("AUDIT_LOG_DIR", "./audit_logs"))
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

def canonical_json(record: dict[str, Any]) -> str:
    """Stable JSON representation; hash field is intentionally excluded."""
    body = {k: v for k, v in record.items() if k != "sha256"}
    return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def create_run(payload: dict[str, Any]) -> dict[str, Any]:
    run = {
        "run_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **payload,
    }
    run["sha256"] = hashlib.sha256(canonical_json(run).encode("utf-8")).hexdigest()
    path = AUDIT_DIR / f"{run['run_id']}.json"
    path.write_text(json.dumps(run, indent=2, ensure_ascii=False), encoding="utf-8")
    return run

def get_run(run_id: str) -> dict[str, Any] | None:
    if not re.fullmatch(r"[0-9a-fA-F-]{36}", run_id):
        return None
    path = AUDIT_DIR / f"{run_id}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None

def verify_run(run_id: str) -> dict[str, Any]:
    record = get_run(run_id)
    if record is None:
        return {"run_id": run_id, "exists": False, "valid": False, "message": "Run not found or unreadable"}
    stored = record.get("sha256", "")
    calculated = hashlib.sha256(canonical_json(record).encode("utf-8")).hexdigest()
    valid = bool(stored) and stored == calculated
    return {
        "run_id": run_id,
        "exists": True,
        "valid": valid,
        "stored_sha256": stored,
        "calculated_sha256": calculated,
        "message": "Integrity check passed" if valid else "Integrity mismatch: record may have been modified",
    }

def list_runs(limit: int = 100) -> list[dict[str, Any]]:
    result = []
    for path in sorted(AUDIT_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
        try:
            result.append(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            continue
    return result

def export_json() -> bytes:
    return json.dumps(list_runs(1000), indent=2, ensure_ascii=False).encode("utf-8")

def export_csv() -> bytes:
    runs = list_runs(1000)
    columns = ["run_id", "timestamp", "risk_score", "severity", "status", "sha256", "summary", "findings", "recommended_fixes"]
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    for run in runs:
        row = dict(run)
        row["findings"] = json.dumps(row.get("findings", []), ensure_ascii=False)
        row["recommended_fixes"] = json.dumps(row.get("recommended_fixes", []), ensure_ascii=False)
        writer.writerow(row)
    return stream.getvalue().encode("utf-8-sig")
