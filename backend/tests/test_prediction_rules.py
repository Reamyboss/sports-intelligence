from app.prediction.prediction_rules import predict_match_winner
from app.reasoning.reasoning_models import ReasoningResult


def make_reasoning(
    strengths=0,
    weaknesses=0,
    risks=0,
    opportunities=0,
    contradictions=0,
):
    return ReasoningResult(
        home_team="Home Team",
        away_team="Away Team",
        strengths=["s"] * strengths,
        weaknesses=["w"] * weaknesses,
        risks=["r"] * risks,
        opportunities=["o"] * opportunities,
        contradictions=["c"] * contradictions,
        confidence=50.0,
        summary="test",
        supporting_evidence=[],
    )


def test_clear_home_advantage_predicts_home():
    reasoning = make_reasoning(strengths=2)

    prediction, probability = predict_match_winner(reasoning)

    assert prediction == "HOME"
    assert probability == 66.0


def test_clear_away_advantage_predicts_away():
    reasoning = make_reasoning(weaknesses=2)

    prediction, probability = predict_match_winner(reasoning)

    assert prediction == "AWAY"


def test_no_signal_predicts_draw_at_50_percent():
    reasoning = make_reasoning()

    prediction, probability = predict_match_winner(reasoning)

    assert prediction == "DRAW"
    assert probability == 50.0


def test_borderline_score_of_one_is_still_draw():
    reasoning = make_reasoning(strengths=1)

    prediction, probability = predict_match_winner(reasoning)

    assert prediction == "DRAW"


def test_probability_never_exceeds_ninety():
    reasoning = make_reasoning(strengths=10)

    _, probability = predict_match_winner(reasoning)

    assert probability == 90.0


def test_probability_never_drops_below_forty():
    reasoning = make_reasoning(weaknesses=10)

    _, probability = predict_match_winner(reasoning)

    assert probability == 40.0
