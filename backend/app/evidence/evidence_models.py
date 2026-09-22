from pydantic import BaseModel


class Evidence(BaseModel):
    """
    Represents one piece of evidence used by the reasoning engine.
    """

    title: str

    supports: str

    strength: float

    reason: str


class ContextSignal(BaseModel):
    """
    A real, computed match fact that is shown to the reader but is
    deliberately NOT scored.

    This type exists to make "display-only" structural rather than a
    convention. It has no `strength` field, so it cannot be fed to
    prediction_rules._evidence_score even by accident, and it travels
    on PredictionResult.context - never in
    ReasoningResult.supporting_evidence, which is the only collection
    the prediction and confidence maths reads.

    `favours` describes which side the fact happens to flatter. It is
    commentary for the reader, not a weight: nothing downstream
    consumes it.
    """

    title: str

    home_value: str

    away_value: str

    detail: str

    # HOME | AWAY | None - None when neither side is favoured, or
    # when the comparison is not meaningful.
    favours: str | None = None
