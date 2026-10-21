"""JSON audit logs: one hash-chained JSONL file per run. Never write secrets into `data`."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings

GENESIS = "0" * 64


def _path(run_id: str, base: str | None = None) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9_]+", run_id):
        raise ValueError("invalid run id")
    return Path(base or settings.audit_log_dir) / f"{run_id}.jsonl"


def _entry_hash(entry: dict) -> str:
    body = {k: v for k, v in entry.items() if k != "hash"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def log_event(run_id: str, event: str, data: dict, base: str | None = None) -> dict:
    path = _path(run_id, base)
    path.parent.mkdir(parents=True, exist_ok=True)
    prev = GENESIS
    if path.exists():
        lines = path.read_text().strip().splitlines()
        if lines:
            prev = json.loads(lines[-1])["hash"]
    entry = {"ts": datetime.now(timezone.utc).isoformat(timespec="microseconds"), "event": event, "data": data, "prev": prev}
    entry["hash"] = _entry_hash(entry)
    with path.open("a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def read_log(run_id: str, base: str | None = None) -> list:
    path = _path(run_id, base)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def verify_chain(entries: list) -> bool:
    prev = GENESIS
    for e in entries:
        if e.get("prev") != prev or e.get("hash") != _entry_hash(e):
            return False
        prev = e["hash"]
    return True
