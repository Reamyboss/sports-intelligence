from fastapi import APIRouter, HTTPException

from app.knowledge.knowledge_builder import build_match_profile
from app.services.match_service import MatchService

router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge"],
)

service = MatchService()


@router.get("/{match_id}")
def get_match_knowledge(match_id: int):
    match = service.get_match(match_id)

    if match is None:
        raise HTTPException(
            status_code=404,
            detail="Match not found",
        )

    return build_match_profile(match)