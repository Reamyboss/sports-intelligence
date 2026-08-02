from app.reasoning.reasoning_models import ReasoningResult


def explain(result: ReasoningResult) -> list[str]:
    """
    Convert structured reasoning into readable explanations.
    """

    explanations = []

    explanations.extend(result.strengths)

    explanations.extend(result.opportunities)

    explanations.extend(result.risks)

    explanations.extend(result.weaknesses)

    explanations.extend(result.contradictions)

    return explanations