from app.confidence.confidence_engine import calculate_confidence
from app.prediction.prediction_models import PredictionResult
from app.prediction.prediction_rules import (
    match_probabilities,
    predict_match_winner,
    probability_of,
)
from app.reasoning.explanation_engine import explain, summarize
from app.reasoning.reasoning_models import ReasoningResult
from app.reasoning.signal_ranking import (
    conflict_level,
    rank_signals,
    split_by_side,
    strongest,
)


def predict(
    reasoning: ReasoningResult,
) -> PredictionResult:
    """
    Generate a prediction from reasoning.
    """

    prediction, _home_lean_index = predict_match_winner(
        reasoning,
    )

    probabilities = match_probabilities(reasoning)
    probability = probability_of(prediction, probabilities)

    home_probability, draw_probability, away_probability = probabilities

    # Rank the evidence the reasoning layer already collected, then
    # split it around the outcome actually predicted - so "what backs
    # this call" and "what argues against it" are answerable per
    # prediction rather than per rule-evaluation order.
    ranked = rank_signals(reasoning.supporting_evidence)
    supporting, opposing = split_by_side(ranked, prediction)

    # Confidence is measured against the probability of the outcome
    # being claimed. Feeding it the home-lean index instead - as the
    # old wiring did - meant a strong away call started from ~40 and
    # was reported as low confidence purely for not being a home win.
    confidence = calculate_confidence(
        reasoning,
        probability,
    )

    return PredictionResult(
        market="MATCH_WINNER",
        winner=prediction,
        probability=probability,
        home_probability=home_probability,
        draw_probability=draw_probability,
        away_probability=away_probability,
        confidence=confidence,
        strongest_support=strongest(supporting),
        strongest_opposition=strongest(opposing),
        conflict=conflict_level(ranked),
        reasoning=reasoning,
        explanation=explain(reasoning),
        summary=summarize(
            winner=prediction,
            probability=probability,
            confidence=confidence,
            reasoning=reasoning,
        ),
    )
