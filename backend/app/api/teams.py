from fastapi import APIRouter

from app.models.team import Team
from app.services.team_service import get_teams

router = APIRouter(
    prefix="/teams",
    tags=["Teams"],
)


@router.get("/", response_model=list[Team])
def list_teams() -> list[Team]:
    return get_teams()
