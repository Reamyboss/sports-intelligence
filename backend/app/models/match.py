from datetime import datetime

from pydantic import BaseModel


class Match(BaseModel):
    """Represents a football match."""

    id: int

    home_team: str
    away_team: str

    competition: str

    kickoff: datetime

    home_score: int | None = None
    away_score: int | None = None

    status: str = "scheduled"
