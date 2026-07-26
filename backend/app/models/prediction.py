from pydantic import BaseModel


class Prediction(BaseModel):
    """Prediction output."""

    match_id: int

    home_win: float

    draw: float

    away_win: float

    confidence: float
