from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user, require_blue
from app.db.database import get_db
from app.models import Alert, User
from app.schemas import AlertOut

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertOut])
def list_alerts(limit: int = 100, _: User = Depends(current_user), db: Session = Depends(get_db)):
    return list(db.scalars(select(Alert).order_by(Alert.id.desc()).limit(min(limit, 500))))


@router.post("/{alert_id}/ack", response_model=AlertOut)
def acknowledge(alert_id: int, _: User = Depends(require_blue), db: Session = Depends(get_db)):
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(404, "Alert not found")
    alert.acknowledged = True
    db.commit()
    return alert
