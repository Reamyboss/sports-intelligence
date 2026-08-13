"""
The pre-refactor, count-only prediction/confidence formulas, kept
here ONLY so the backtest can compare against them. This is NOT the
production implementation - app/prediction/prediction_rules.py and
app/confidence/confidence_engine.py are. Do not import this module
from production code.
"""

from app.reasoning.reasoning_models import ReasoningResult


def predict_match_winner_baseline(
    reasoning: ReasoningResult,
) -> tuple[str, float]:
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

    probability = max(40.0, min(90.0, 50 + (score * 8)))

    return prediction, probability


def calculate_confidence_baseline(
    reasoning: ReasoningResult,
    probability: float,
) -> float:
    confidence = probability

    confidence += len(reasoning.strengths) * 2
    confidence += len(reasoning.opportunities)
    confidence -= len(reasoning.risks) * 2
    confidence -= len(reasoning.contradictions) * 3

    confidence = max(0.0, min(100.0, confidence))

    return round(confidence, 2)
