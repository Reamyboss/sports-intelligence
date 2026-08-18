from app.evidence.evidence_models import Evidence
from app.reasoning.reasoning_models import ReasoningResult
from app.reasoning.reasoning_rules import (
    evaluate_contradictions,
    evaluate_opportunities,
    evaluate_risks,
    evaluate_strengths,
    evaluate_weaknesses,
)


def build_reasoning(
    evidence: dict,
    supporting_evidence: list[Evidence],
) -> ReasoningResult:
    """
    Transform evidence into structured reasoning.
    """

    strengths = evaluate_strengths(evidence)

    weaknesses = evaluate_weaknesses(evidence)

    risks = evaluate_risks(evidence)

    opportunities = evaluate_opportunities(evidence)

    contradictions = evaluate_contradictions(evidence)

    summary = (
        "Reasoning completed successfully."
    )

    return ReasoningResult(
        home_team=evidence["home_team"]["name"],
        away_team=evidence["away_team"]["name"],
        strengths=strengths,
        weaknesses=weaknesses,
        risks=risks,
        opportunities=opportunities,
        contradictions=contradictions,
        summary=summary,
        supporting_evidence=supporting_evidence,
    )