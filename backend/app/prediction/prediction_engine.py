from app.confidence.confidence_engine import calculate_confidence
from app.prediction.prediction_models import PredictionResult
from app.prediction.prediction_rules import predict_match_winner
from app.reasoning.explanation_engine import explain, summarize
from app.reasoning.reasoning_models import ReasoningResult


def predict(
    reasoning: ReasoningResult,
) -> PredictionResult:
    """
    Generate a prediction from reasoning.
    """

    prediction, probability = predict_match_winner(
        reasoning,
    )

    confidence = calculate_confidence(
        reasoning,
        probability,
    )

    return PredictionResult(
        market="MATCH_WINNER",
        winner=prediction,
        probability=probability,
        confidence=confidence,
        reasoning=reasoning,
        explanation=explain(reasoning),
        summary=summarize(
            winner=prediction,
            probability=probability,
            confidence=confidence,
            reasoning=reasoning,
        ),
    )