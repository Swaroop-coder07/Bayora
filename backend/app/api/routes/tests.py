from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.database import get_db
from app.models import User
from app.schemas import TestIn, TestResultOut
from app.services import referee

router = APIRouter(prefix="/tests", tags=["tests"])


@router.post("/run", response_model=TestResultOut)
def run_test(body: TestIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    try:
        outcome = referee.execute_test(db, user, body.prompt, body.category)
    except referee.NoActiveConfig:
        raise HTTPException(409, "No active Blue Team configuration. Ask the Blue Team to activate one.")
    run, b = outcome.run, outcome.budget
    return TestResultOut(
        run_id=run.id, session_id=run.session_id, verdict=referee.visible_verdict(run, user),
        feedback_level=run.feedback_level, response=referee.visible_response(run, user),
        risk_score=b.risk_score, similar_count=b.similar_count, budget_total=b.budget_total,
        budget_remaining=b.budget_remaining, budget_level=b.level, canary_detected=run.canary_hit,
        paused=outcome.paused, model_version=run.model_version,
    )
