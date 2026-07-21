import asyncio

from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app.api.dependencies import db_dependency
from app.schemas.health import HealthCheckComponent, LivenessResponse, ReadinessResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/live", summary="Liveness Probe", response_model=LivenessResponse)
async def liveness_check(response: Response) -> LivenessResponse:

    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return LivenessResponse(status="pass")


@router.get("/ready", summary="Readiness Probe", response_model=ReadinessResponse)
async def readiness_check(response: Response, db: db_dependency) -> ReadinessResponse:

    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"

    components: dict[str, HealthCheckComponent] = {}
    is_ready = True

    try:
        await asyncio.wait_for(db.execute(text("SELECT 1")), timeout=2.0)
        components["database"] = HealthCheckComponent(status="pass")
    except Exception as e:
        components["database"] = HealthCheckComponent(status="fail", detail=str(e))
        is_ready = False

    payload = ReadinessResponse(
        status="pass" if is_ready else "fail",
        checks=components,
    )

    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return payload
