from pydantic import BaseModel


class MatchProfile(BaseModel):

    home_team: str
    away_team: str

    home_form: list[str]
    away_form: list[str]

    home_advantage: bool

    rest_days_home: int | None
    rest_days_away: int | None

    head_to_head: dict
