from fastapi import APIRouter, HTTPException

from app.models.match import Match
from app.services.match_service import MatchService

router = APIRouter(prefix="/matches", tags=["Matches"])

service = MatchService()


@router.get("/", response_model=list[Match])
def list_matches() -> list[Match]:
    return service.list_matches()


@router.get("/{match_id}", response_model=Match)
def get_match(match_id: int) -> Match:
    match = service.get_match(match_id)

    if match is None:
        raise HTTPException(
            status_code=404,
            detail="Match not found",
        )

    return match