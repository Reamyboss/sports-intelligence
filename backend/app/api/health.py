# pyrefly: ignore [missing-import]
from fastapi import APIRouter

from app.services.health_service import get_health

router = APIRouter()


@router.get("/")
def health():
    return get_health()
