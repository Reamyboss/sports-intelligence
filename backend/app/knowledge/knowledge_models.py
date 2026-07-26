from pydantic import BaseModel


class MatchKnowledge(BaseModel):
    """Knowledge extracted about a match."""

    home_team: str
    away_team: str

    home_form: list[str]

    away_form: list[str]

    home_advantage: bool

    confidence_inputs: list[str]
