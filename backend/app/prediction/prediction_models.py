from pydantic import BaseModel

from app.reasoning.reasoning_models import ReasoningResult


class PredictionResult(BaseModel):
    """
    Final prediction produced by the Prediction Engine.
    """

    winner: str

    probability: float

    confidence: float

    market: str

    reasoning: ReasoningResult

    explanation: list[str]