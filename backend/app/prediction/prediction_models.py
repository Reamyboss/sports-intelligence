from pydantic import BaseModel

from app.evidence.evidence_models import ContextSignal, Evidence
from app.reasoning.reasoning_models import ReasoningResult


class PredictionResult(BaseModel):
    """
    Final prediction produced by the Prediction Engine.
    """

    winner: str

    # The probability of `winner` specifically - HOME's chance for a
    # HOME call, AWAY's for an AWAY call, DRAW's for a draw. It is
    # always one of the three fields below, never a separate quantity.
    probability: float

    home_probability: float
    draw_probability: float
    away_probability: float

    confidence: float

    # The single strongest signal behind the call, and the single
    # strongest signal against it. Both are ranked by the magnitude
    # the evidence engine already computed, not by rule order.
    strongest_support: Evidence | None = None
    strongest_opposition: Evidence | None = None

    # NONE / LOW / MODERATE / HIGH - how genuinely the evidence
    # disagrees with itself.
    conflict: str = "NONE"

    market: str

    # Real computed match context, shown to the reader but never
    # scored. Deliberately a separate field of a separate type from
    # supporting_evidence: nothing in prediction_rules or
    # confidence_engine reads this, so it cannot move a probability
    # or a confidence value.
    context: list[ContextSignal] = []

    reasoning: ReasoningResult

    explanation: list[str]

    summary: str