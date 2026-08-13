from app.reasoning.reasoning_models import ReasoningResult


def calculate_confidence(
    reasoning: ReasoningResult,
    probability: float,
) -> float:
    """
    Calculate confidence from reasoning quality.
    """

    confidence = probability

    confidence += len(reasoning.strengths) * 2

    confidence += len(reasoning.opportunities)

    confidence -= len(reasoning.risks) * 2

    confidence -= len(reasoning.contradictions) * 3

    supporting_evidence = reasoning.supporting_evidence

    if supporting_evidence:
        home_support = sum(
            1 for item in supporting_evidence if item.supports == "HOME"
        )
        away_support = len(supporting_evidence) - home_support

        # Evidence that agrees with itself (mostly/all one side) is
        # genuine corroboration - real signal, be more confident.
        # Evidence split across both sides is genuine contradiction -
        # be less confident, on top of (not instead of) the existing
        # reasoning.contradictions penalty above, since this catches
        # disagreement reasoning_rules.py's narrow rule doesn't.
        agreement = abs(home_support - away_support)
        disagreement = min(home_support, away_support)

        confidence += agreement * 1.5
        confidence -= disagreement * 2.5

    confidence = max(
        0.0,
        min(
            100.0,
            confidence,
        ),
    )

    return round(confidence, 2)