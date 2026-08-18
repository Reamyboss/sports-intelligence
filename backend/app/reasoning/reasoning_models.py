from pydantic import BaseModel

from app.evidence.evidence_models import Evidence


class ReasoningResult(BaseModel):
    """
    Final reasoning produced from all available evidence.
    This is NOT a prediction.
    """

    home_team: str
    away_team: str

    strengths: list[str]

    weaknesses: list[str]

    risks: list[str]

    opportunities: list[str]

    contradictions: list[str]

    summary: str

    supporting_evidence: list[Evidence]