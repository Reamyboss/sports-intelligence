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

    confidence = 0.0

    total_findings = (
        len(strengths)
        + len(opportunities)
        - len(risks)
        - len(weaknesses)
    )

    confidence = max(
        0.0,
        min(
            100.0,
            50 + (total_findings * 10),
        ),
    )

    summary = (
        "Reasoning completed successfully."
    )

    return ReasoningResult(
        strengths=strengths,
        weaknesses=weaknesses,
        risks=risks,
        opportunities=opportunities,
        contradictions=contradictions,
        confidence=confidence,
        summary=summary,
        supporting_evidence=supporting_evidence,
    )