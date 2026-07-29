from dataclasses import dataclass


@dataclass(slots=True)
class Match:
    id: int

    competition: str
    season: int
    matchday: int | None

    kickoff: str

    status: str

    home_team: str
    away_team: str

    home_score: int | None
    away_score: int | None