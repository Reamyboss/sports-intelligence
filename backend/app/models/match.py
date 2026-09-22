from datetime import datetime

from pydantic import BaseModel


class Match(BaseModel):
    """Represents a football match."""

    id: int

    home_team: str
    away_team: str

    competition: str

    # Present on every row in matches.json. Optional so that a Match
    # constructed without one - as much of the test suite does - stays
    # valid, and so a future source that omits it degrades to "unknown"
    # rather than failing to parse.
    season: int | None = None

    kickoff: datetime

    home_score: int | None = None
    away_score: int | None = None

    status: str = "scheduled"
