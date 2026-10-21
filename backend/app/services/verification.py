"""C. Verifiable Run Records.

The fingerprint proves the *recorded data* was not changed after the run.
It does NOT prove the model output is reproducible or deterministic.
"""
import hashlib
import json
from dataclasses import dataclass


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical(fields: dict) -> str:
    return json.dumps(fields, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def record_fields(run) -> dict:
    """Recomputed from the stored columns each time, so any edited column changes the result."""
    return {
        "run_id": run.id,
        "created_at": run.created_at,
        "prompt_sha256": sha256_hex(run.prompt),
        "response_sha256": sha256_hex(run.response_masked),
        "config_version": run.config_version,
        "config_hash": run.config_hash,
        "model_version": run.model_version,
        "verdict": run.verdict,
    }


def fingerprint(run) -> str:
    return sha256_hex(canonical(record_fields(run)))


@dataclass
class VerifyResult:
    ok: bool
    expected: str
    actual: str


def verify(run) -> VerifyResult:
    actual = fingerprint(run)
    return VerifyResult(actual == run.fingerprint, run.fingerprint, actual)
