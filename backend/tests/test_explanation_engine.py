from app.reasoning.explanation_engine import explain, summarize
from app.reasoning.reasoning_models import ReasoningResult


def make_reasoning(
    strengths=None,
    weaknesses=None,
    risks=None,
    opportunities=None,
    contradictions=None,
):
    return ReasoningResult(
        home_team="Arsenal FC",
        away_team="Chelsea FC",
        strengths=strengths or [],
        weaknesses=weaknesses or [],
        risks=risks or [],
        opportunities=opportunities or [],
        contradictions=contradictions or [],
        confidence=50.0,
        summary="test",
        supporting_evidence=[],
    )


def test_explain_labels_each_category():
    reasoning = make_reasoning(
        strengths=["Stronger form."],
        weaknesses=["Concedes more."],
        risks=["Away team hot streak."],
        opportunities=["Good head-to-head record."],
        contradictions=["Wins more, scores less."],
    )

    explanations = explain(reasoning)

    assert "Strength: Stronger form." in explanations
    assert "Weakness: Concedes more." in explanations
    assert "Risk: Away team hot streak." in explanations
    assert "Opportunity: Good head-to-head record." in explanations
    assert "Contradiction: Wins more, scores less." in explanations


def test_explain_empty_reasoning_gives_empty_list():
    assert explain(make_reasoning()) == []


def test_summarize_names_the_favoured_home_team():
    reasoning = make_reasoning(
        strengths=["Stronger recent form."],
        opportunities=["Historical head-to-head favors the home team."],
    )

    summary = summarize(
        winner="HOME",
        probability=66.0,
        confidence=60.0,
        reasoning=reasoning,
    )

    assert summary.startswith("Arsenal FC are")
    assert "stronger recent form" in summary.lower()


def test_summarize_names_the_favoured_away_team():
    reasoning = make_reasoning(
        weaknesses=["Home team concedes more goals."],
        risks=["Away team arrives in strong form."],
    )

    summary = summarize(
        winner="AWAY",
        probability=66.0,
        confidence=60.0,
        reasoning=reasoning,
    )

    assert summary.startswith("Chelsea FC are")


def test_summarize_draw_mentions_both_teams_without_favouring_either():
    reasoning = make_reasoning()

    summary = summarize(
        winner="DRAW",
        probability=50.0,
        confidence=50.0,
        reasoning=reasoning,
    )

    assert "Arsenal FC" in summary
    assert "Chelsea FC" in summary
    assert "evenly matched" in summary


def test_summarize_mentions_counter_evidence_when_present():
    reasoning = make_reasoning(
        strengths=["Stronger recent form."],
        weaknesses=["Concedes more goals at home."],
    )

    summary = summarize(
        winner="HOME",
        probability=58.0,
        confidence=50.0,
        reasoning=reasoning,
    )

    assert "however" in summary.lower()


def test_summarize_flags_contradictions_explicitly():
    reasoning = make_reasoning(
        strengths=["Stronger recent form."],
        contradictions=["Wins more often but scores fewer goals."],
    )

    summary = summarize(
        winner="HOME",
        probability=58.0,
        confidence=50.0,
        reasoning=reasoning,
    )

    assert "contradictory" in summary.lower()


def test_summarize_always_states_a_confidence_level():
    reasoning = make_reasoning()

    summary = summarize(
        winner="DRAW",
        probability=50.0,
        confidence=82.0,
        reasoning=reasoning,
    )

    assert "82%" in summary
    assert "confidence" in summary.lower()
