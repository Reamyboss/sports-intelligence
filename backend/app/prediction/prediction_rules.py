from app.reasoning.reasoning_models import ReasoningResult


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