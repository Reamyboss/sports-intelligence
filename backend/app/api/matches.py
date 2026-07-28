from fastapi import APIRouter, HTTPException

from app.services.match_service import MatchService

router = APIRouter(prefix="/matches", tags=["Matches"])

service = MatchService()


@router.get("/")
def list_matches():
    return service.list_matches()


@router.get("/{match_id}")
def get_match(match_id: int):
    match = service.get_match(match_id)

    if match is None:
        raise HTTPException(
            status_code=404,
            detail="Match not found",
        )

    return match