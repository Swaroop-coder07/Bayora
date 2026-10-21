from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user, require_blue
from app.db.database import get_db
from app.models import Run, User, now_iso
from app.schemas import RunDetailOut, RunOut, VerifyOut
from app.services import audit_service, referee, verification

router = APIRouter(prefix="/runs", tags=["runs"])

FAILED = ("LEAK", "VIOLATION", "SUSPICIOUS")


def _scope(user: User):
    q = select(Run)
    return q if user.role == "blue" else q.where(Run.user_id == user.id)


def _get_run(db: Session, user: User, run_id: str) -> Run:
    run = db.get(Run, run_id)
    if run is None or (user.role != "blue" and run.user_id != user.id):
        raise HTTPException(404, "Run not found")
    return run


def to_out(run: Run, user: User) -> RunOut:
    return RunOut(
        id=run.id, created_at=run.created_at, category=run.category, user_email=run.user_email,
        verdict=referee.visible_verdict(run, user), feedback_level=run.feedback_level, risk_score=run.risk_score,
        canary_hit=run.canary_hit, guardrail_violation=run.guardrail_violation, prompt_hash=run.prompt_hash,
        config_hash=run.config_hash, config_version=run.config_version, model_version=run.model_version,
        fingerprint=run.fingerprint, session_id=run.session_id,
    )


@router.get("", response_model=list[RunOut])
def list_runs(limit: int = 100, user: User = Depends(current_user), db: Session = Depends(get_db)):
    runs = db.scalars(_scope(user).order_by(Run.created_at.desc()).limit(min(limit, 500)))
    return [to_out(r, user) for r in runs]


@router.get("/stats")
def stats(user: User = Depends(current_user), db: Session = Depends(get_db)):
    runs = list(db.scalars(_scope(user).order_by(Run.created_at.asc())))
    return {
        "total": len(runs),
        "passed": sum(r.verdict == "SAFE" for r in runs),
        "failed": sum(r.verdict in FAILED for r in runs),
        "paused": sum(r.verdict == "PAUSED" for r in runs),
        "leaks": sum(r.canary_hit for r in runs),
        "trend": [{"n": i + 1, "risk": r.risk_score, "leak": r.leak_score} for i, r in enumerate(runs[-30:])],
    }


@router.get("/{run_id}", response_model=RunDetailOut)
def run_detail(run_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    run = _get_run(db, user, run_id)
    log = audit_service.read_log(run.id)
    return RunDetailOut(
        **to_out(run, user).model_dump(), prompt=run.prompt, response=referee.visible_response(run, user),
        leak_score=run.leak_score if user.role == "blue" else 0.0, similar_count=run.similar_count,
        budget_remaining=run.budget_remaining, budget_total=run.budget_total,
        audit_log=log if user.role == "blue" else [], audit_chain_ok=audit_service.verify_chain(log),
    )


@router.post("/{run_id}/verify", response_model=VerifyOut)
def verify_run(run_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    run = _get_run(db, user, run_id)
    result = verification.verify(run)
    status = "Verified" if result.ok else "Verification Failed"
    audit_service.log_event(run.id, "verification", {"status": status, "by": user.email})
    return VerifyOut(run_id=run.id, status=status, expected=result.expected, actual=result.actual, checked_at=now_iso())


@router.get("/{run_id}/export")
def export_run(run_id: str, user: User = Depends(require_blue), db: Session = Depends(get_db)):
    run = _get_run(db, user, run_id)
    log = audit_service.read_log(run.id)
    audit_service.log_event(run.id, "export", {"by": user.email})
    return {
        "record": verification.record_fields(run), "fingerprint": run.fingerprint,
        "prompt": run.prompt, "response_masked": run.response_masked, "verdict": run.verdict,
        "audit_log": log, "audit_chain_ok": audit_service.verify_chain(log),
    }
