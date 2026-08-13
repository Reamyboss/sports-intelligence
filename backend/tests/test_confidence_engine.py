from app.confidence.confidence_engine import calculate_confidence
from app.evidence.evidence_models import Evidence
from app.reasoning.reasoning_models import ReasoningResult


def make_reasoning(
    strengths=0,
    risks=0,
    opportunities=0,
    contradictions=0,
    supporting_evidence=None,
):
    return ReasoningResult(
        home_team="Home Team",
        away_team="Away Team",
        strengths=["s"] * strengths,
        weaknesses=[],
        risks=["r"] * risks,
        opportunities=["o"] * opportunities,
        contradictions=["c"] * contradictions,
        confidence=50.0,
        summary="test",
        supporting_evidence=supporting_evidence or [],
    )


def evidence(supports, strength=1.0, title="Signal"):
    return Evidence(title=title, supports=supports, strength=strength, reason="test")


def test_confidence_rewards_strengths_and_opportunities():
    reasoning = make_reasoning(strengths=2, opportunities=1)

    confidence = calculate_confidence(reasoning, probability=50.0)

    assert confidence == 55.0  # 50 + 2*2 + 1


def test_confidence_penalises_risks_and_contradictions():
    reasoning = make_reasoning(risks=1, contradictions=1)

    confidence = calculate_confidence(reasoning, probability=50.0)

    assert confidence == 45.0  # 50 - 1*2 - 1*3


def test_confidence_clamped_at_one_hundred():
    reasoning = make_reasoning(strengths=10)

    confidence = calculate_confidence(reasoning, probability=95.0)

    assert confidence == 100.0


def test_confidence_clamped_at_zero():
    reasoning = make_reasoning(risks=5, contradictions=5)

    confidence = calculate_confidence(reasoning, probability=10.0)

    assert confidence == 0.0


# -----------------------------
# Backward compatibility
# -----------------------------


def test_empty_supporting_evidence_reproduces_original_confidence():
    reasoning = make_reasoning(strengths=2, opportunities=1, supporting_evidence=[])

    confidence = calculate_confidence(reasoning, probability=50.0)

    assert confidence == 55.0  # identical to test_confidence_rewards_strengths_and_opportunities


# -----------------------------
# Real evidence differentials meaningfully influence confidence
# -----------------------------


def test_agreeing_supporting_evidence_increases_confidence():
    reasoning = make_reasoning(
        supporting_evidence=[evidence("HOME"), evidence("HOME"), evidence("HOME")],
    )

    confidence = calculate_confidence(reasoning, probability=50.0)

    assert confidence == 54.5  # 50 + agreement(3) * 1.5


def test_contradictory_supporting_evidence_decreases_confidence():
    """
    Distinct from reasoning.contradictions (one narrow rule about
    wins-vs-goals) - this catches supporting_evidence items that
    disagree with each other, which that rule doesn't see.
    """

    reasoning = make_reasoning(
        supporting_evidence=[evidence("HOME"), evidence("AWAY")],
    )

    confidence = calculate_confidence(reasoning, probability=50.0)

    assert confidence == 47.5  # 50 - disagreement(1) * 2.5


def test_genuine_low_evidence_case_has_lower_confidence_than_real_corroboration():
    """
    Same count-based signal (one strength), but one case has real,
    agreeing supporting evidence behind it and the other has none -
    the genuinely low-evidence case must not receive the same
    confidence as the well-corroborated one.
    """

    low_evidence = make_reasoning(strengths=1, supporting_evidence=[])
    corroborated = make_reasoning(
        strengths=1,
        supporting_evidence=[evidence("HOME"), evidence("HOME")],
    )

    low_confidence = calculate_confidence(low_evidence, probability=58.0)
    high_confidence = calculate_confidence(corroborated, probability=58.0)

    assert high_confidence > low_confidence


def test_confidence_still_clamped_at_one_hundred_with_heavy_agreement():
    reasoning = make_reasoning(
        strengths=10,
        supporting_evidence=[evidence("HOME")] * 10,
    )

    confidence = calculate_confidence(reasoning, probability=95.0)

    assert confidence == 100.0
