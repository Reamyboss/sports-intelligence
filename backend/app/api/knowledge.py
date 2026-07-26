from fastapi import APIRouter

from app.knowledge.knowledge_builder import build_match_profile
from app.services.match_service import get_matches

router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge"],
)


@router.get("/{match_id}")
def get_match_knowledge(match_id: int):

    matches = get_matches()

    match = next(m for m in matches if m.id == match_id)

    return build_match_profile(match)
