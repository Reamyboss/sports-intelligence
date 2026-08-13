from app.evidence.evidence_models import Evidence
from app.reasoning.reasoning_models import ReasoningResult


def _evidence_score(supporting_evidence: list[Evidence]) -> float:
    """
    Turn structured Evidence into a signed score.

    Evidence.strength is on a different scale per signal (a goals
    differential and a head-to-head win differential aren't the same
    unit), so raw strengths can't be summed directly without one
    large-scale signal silently dominating. Each item's strength is
    instead saturated into (0, 1) via strength / (strength + 1) -
    small differentials contribute weakly, large ones approach but
    never reach full weight - then signed by which side it supports.

    Returns 0.0 when there is no supporting evidence, so this is a
    pure extension: predictions built from count-only reasoning
    (the case for every match with no real evidence, and for every
    existing test that doesn't set supporting_evidence) are completely
    unaffected.
    """

    total = 0.0

    for item in supporting_evidence:
        magnitude = item.strength / (item.strength + 1.0)
        total += magnitude if item.supports == "HOME" else -magnitude

    return total


def predict_match_winner(
    reasoning: ReasoningResult,
) -> tuple[str, float]:
    """
    Determine the predicted winner using reasoning.
    """

    score = 0

    score += len(reasoning.strengths)

    score += len(reasoning.opportunities)

    score -= len(reasoning.weaknesses)

    score -= len(reasoning.risks)

    score -= len(reasoning.contradictions)

    score += _evidence_score(reasoning.supporting_evidence)

    if score > 1:
        prediction = "HOME"

    elif score < -1:
        prediction = "AWAY"

    else:
        prediction = "DRAW"

    probability = max(
        40.0,
        min(
            90.0,
            50 + (score * 8),
        ),
    )

    return prediction, probability