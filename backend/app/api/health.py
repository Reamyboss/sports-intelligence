# pyrefly: ignore [missing-import]
from fastapi import APIRouter

from app.schemas.health import HealthStatus
from app.services.health_service import get_health

router = APIRouter(tags=["Health"])


@router.get("/", response_model=HealthStatus)
def health() -> HealthStatus:
    return get_health()
