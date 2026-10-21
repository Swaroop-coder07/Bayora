from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.database import get_db
from app.isolation.session_manager import SessionManager
from app.models import IsolationSession, User
from app.schemas import SessionOut

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("", response_model=list[SessionOut])
def list_sessions(limit: int = 50, _: User = Depends(current_user), db: Session = Depends(get_db)):
    return list(db.scalars(select(IsolationSession).order_by(IsolationSession.created_at.desc()).limit(min(limit, 200))))


@router.get("/current", response_model=SessionOut | None)
def current_session(_: User = Depends(current_user), db: Session = Depends(get_db)):
    return db.scalar(select(IsolationSession).order_by(IsolationSession.created_at.desc()))


@router.post("/selftest")
def selftest(_: User = Depends(current_user), db: Session = Depends(get_db)):
    return SessionManager(db).run_selftest()
