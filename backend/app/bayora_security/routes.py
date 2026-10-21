
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from . import audit_service, regression_suite

router = APIRouter(prefix="/api/security", tags=["Bayora Security"])


class RiskRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=20000)
    canary_leaked: bool = False
    prompt_injection: bool = False


@router.get("/health")
def security_health():
    return {"status": "ok", "module": "bayora_security"}


@router.post("/score")
def score_risk(payload: RiskRequest):
    # Confirm the scorer's actual API before wiring it in.
    try:
        from . import risk_scorer
        result = risk_scorer.score_risk(
            payload.text,
            canary_leaked=payload.canary_leaked,
            prompt_injection=payload.prompt_injection,
        )
        return result
    except (ImportError, AttributeError, TypeError) as exc:
        raise HTTPException(
            status_code=501,
            detail=f"Risk scorer integration needs adjustment: {exc}",
        )


@router.post("/regression")
def run_regression():
    try:
        result = regression_suite.run_regression_suite()
        return audit_service.create_run(result)
    except AttributeError as exc:
        raise HTTPException(status_code=501, detail=str(exc))


@router.get("/runs")
def get_runs(limit: int = 100):
    return audit_service.list_runs(max(1, min(limit, 1000)))


@router.get("/runs/{run_id}/verify")
def verify_run(run_id: str):
    return audit_service.verify_run(run_id)


@router.get("/runs/{run_id}")
def get_run(run_id: str):
    result = audit_service.get_run(run_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return result


@router.get("/report.json")
def report_json():
    return Response(
        content=audit_service.export_json(),
        media_type="application/json",
        headers={"Content-Disposition": 'attachment; filename="bayora-security-report.json"'},
    )


@router.get("/report.csv")
def report_csv():
    return Response(
        content=audit_service.export_csv(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="bayora-security-report.csv"'},
    )
