from fastapi import APIRouter

from app.models.match import Match
from app.services.match_service import get_matches

router = APIRouter(prefix="/matches", tags=["Matches"])


@router.get("/", response_model=list[Match])
async def list_matches() -> list[Match]:
    return get_matches()
