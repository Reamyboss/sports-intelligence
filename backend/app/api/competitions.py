from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.competition_catalog import list_competitions

router = APIRouter(
    prefix="/competitions",
    tags=["Competitions"],
)


class CompetitionSummary(BaseModel):
    """
    What the product can offer for one competition.

    `availability` distinguishes a competition with nothing to analyse
    yet from one that is genuinely empty - the difference between
    "the 2026/27 fixtures aren't published yet" and "we have no data",
    which the match list alone cannot express.
    """

    name: str
    season: int | None

    # ACTIVE | NO_UPCOMING_FIXTURES | EMPTY
    availability: str

    total_matches: int
    played_matches: int
    upcoming_matches: int

    next_kickoff: datetime | None
    last_kickoff: datetime | None

    prediction_ready: bool


@router.get("/", response_model=list[CompetitionSummary])
def get_competitions() -> list[CompetitionSummary]:
    """
    Every competition on record, soonest fixture first.
    """

    return [CompetitionSummary(**summary) for summary in list_competitions()]
