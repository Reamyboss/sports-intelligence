from app.evidence.evidence_models import Evidence
from app.prediction.prediction_rules import predict_match_winner
from app.reasoning.reasoning_models import ReasoningResult


def make_reasoning(
    strengths=0,
    weaknesses=0,
    risks=0,
    opportunities=0,
    contradictions=0,
    supporting_evidence=None,
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
        supporting_evidence=supporting_evidence or [],
    )


def evidence(supports, strength, title="Signal"):
    return Evidence(title=title, supports=supports, strength=strength, reason="test")


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


# -----------------------------
# Backward compatibility: empty supporting_evidence must reproduce
# the exact pre-refactor, count-only behavior.
# -----------------------------


def test_empty_supporting_evidence_reproduces_count_only_behavior():
    reasoning = make_reasoning(strengths=2, supporting_evidence=[])

    prediction, probability = predict_match_winner(reasoning)

    assert prediction == "HOME"
    assert probability == 66.0


# -----------------------------
# Real evidence differentials meaningfully influence the prediction
# -----------------------------


def test_strong_agreeing_evidence_can_flip_a_borderline_draw_to_a_win():
    """
    A count-based score of 1 is, on its own, still a DRAW (see
    test_borderline_score_of_one_is_still_draw). Real, strong,
    corroborating evidence should be able to tip a genuinely
    borderline case, not just add noise.
    """

    reasoning = make_reasoning(
        strengths=1,
        supporting_evidence=[
            evidence("HOME", strength=10.0, title="Goals Scored"),
            evidence("HOME", strength=8.0, title="Current Streak"),
        ],
    )

    prediction, _ = predict_match_winner(reasoning)

    assert prediction == "HOME"


def test_evidence_supporting_the_same_side_increases_probability():
    baseline = make_reasoning(strengths=2)
    with_evidence = make_reasoning(
        strengths=2,
        supporting_evidence=[evidence("HOME", strength=5.0)],
    )

    _, baseline_probability = predict_match_winner(baseline)
    _, boosted_probability = predict_match_winner(with_evidence)

    assert boosted_probability > baseline_probability


def test_evidence_opposing_the_count_based_signal_decreases_probability():
    baseline = make_reasoning(strengths=2)
    opposed = make_reasoning(
        strengths=2,
        supporting_evidence=[evidence("AWAY", strength=5.0)],
    )

    _, baseline_probability = predict_match_winner(baseline)
    _, opposed_probability = predict_match_winner(opposed)

    assert opposed_probability < baseline_probability


def test_evidence_strength_is_saturating_not_unbounded():
    """
    A single item's raw strength (however large) saturates toward but
    never reaches 1.0 - so one extreme value from a single signal can
    never, by itself, cross the HOME/AWAY threshold (score > 1) the
    way an unbounded sum could. Two agreeing signals still can (see
    test_strong_agreeing_evidence_can_flip_a_borderline_draw_to_a_win).
    """

    reasoning = make_reasoning(
        supporting_evidence=[evidence("HOME", strength=1_000_000.0)],
    )

    prediction, probability = predict_match_winner(reasoning)

    assert prediction == "DRAW"
    assert probability < 58.0


def test_evidence_alone_with_no_count_based_signal_can_still_move_probability():
    reasoning = make_reasoning(
        supporting_evidence=[
            evidence("AWAY", strength=3.0),
            evidence("AWAY", strength=2.0),
        ],
    )

    prediction, probability = predict_match_winner(reasoning)

    assert probability < 50.0
