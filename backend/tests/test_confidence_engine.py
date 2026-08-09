from app.confidence.confidence_engine import calculate_confidence
from app.reasoning.reasoning_models import ReasoningResult


def make_reasoning(strengths=0, risks=0, opportunities=0, contradictions=0):
    return ReasoningResult(
        strengths=["s"] * strengths,
        weaknesses=[],
        risks=["r"] * risks,
        opportunities=["o"] * opportunities,
        contradictions=["c"] * contradictions,
        confidence=50.0,
        summary="test",
        supporting_evidence=[],
    )


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
