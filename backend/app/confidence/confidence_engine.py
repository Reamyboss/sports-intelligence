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

    confidence = max(
        0.0,
        min(
            100.0,
            confidence,
        ),
    )

    return round(confidence, 2)