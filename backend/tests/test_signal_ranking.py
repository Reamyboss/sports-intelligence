"""
Evidence must be read by magnitude, not by the order the rules happen
to be written in.

The evidence engine has always attached a `strength` to every signal,
but the explanation quoted `leading_reasons[0]` - the first rule that
fired. A 0.1 goal differential could headline the narrative while a
5.0 streak differential went unmentioned.
"""

from app.evidence.evidence_models import Evidence
from app.prediction.prediction_engine import predict
from app.reasoning.explanation_engine import summarize
from app.reasoning.reasoning_models import ReasoningResult
from app.reasoning.signal_ranking import (
    conflict_level,
    rank_signals,
    side_strength,
    split_by_side,
    strongest,
)


def evidence(supports, strength, title="Signal", reason=None):
    return Evidence(
        title=title,
        supports=supports,
        strength=strength,
        reason=reason or f"{title} favours {supports}.",
    )


def make_reasoning(
    strengths=0,
    weaknesses=0,
    supporting_evidence=None,
):
    return ReasoningResult(
        home_team="Arsenal FC",
        away_team="Coventry City FC",
        strengths=["Home team has stronger recent form."] * strengths,
        weaknesses=["Home team concedes more goals."] * weaknesses,
        risks=[],
        opportunities=[],
        contradictions=[],
        summary="test",
        supporting_evidence=supporting_evidence or [],
    )


# -----------------------------
# Ranking
# -----------------------------


def test_signals_are_ranked_by_strength_not_insertion_order():
    signals = [
        evidence("HOME", 0.55, title="Goals Scored"),
        evidence("HOME", 2.0, title="Head-to-Head"),
        evidence("HOME", 1.0, title="Recent Form"),
    ]

    ranked = rank_signals(signals)

    assert [item.title for item in ranked] == [
        "Head-to-Head",
        "Recent Form",
        "Goals Scored",
    ]


def test_ranking_is_stable_for_equal_strengths():
    """
    Genuine ties keep the evidence builder's order rather than being
    reshuffled arbitrarily.
    """

    signals = [
        evidence("HOME", 2.0, title="Head-to-Head"),
        evidence("HOME", 2.0, title="Current Streak"),
    ]

    assert [item.title for item in rank_signals(signals)] == [
        "Head-to-Head",
        "Current Streak",
    ]


def test_ranking_empty_evidence_is_safe():
    assert rank_signals([]) == []
    assert strongest([]) is None
    assert conflict_level([]) == "NONE"
    assert side_strength([], "HOME") == 0.0


# -----------------------------
# Supporting vs opposing
# -----------------------------


def test_split_separates_supporting_from_opposing_signals():
    ranked = rank_signals(
        [
            evidence("HOME", 2.0, title="Head-to-Head"),
            evidence("AWAY", 3.0, title="Current Streak"),
            evidence("HOME", 1.0, title="Recent Form"),
        ]
    )

    supporting, opposing = split_by_side(ranked, "HOME")

    assert [item.title for item in supporting] == ["Head-to-Head", "Recent Form"]
    assert [item.title for item in opposing] == ["Current Streak"]


def test_split_is_symmetric_between_home_and_away():
    ranked = rank_signals(
        [
            evidence("HOME", 2.0, title="Head-to-Head"),
            evidence("AWAY", 3.0, title="Current Streak"),
        ]
    )

    home_support, home_against = split_by_side(ranked, "HOME")
    away_support, away_against = split_by_side(ranked, "AWAY")

    assert home_support == away_against
    assert home_against == away_support


def test_draw_has_no_supporting_evidence_of_its_own():
    ranked = rank_signals([evidence("HOME", 2.0), evidence("AWAY", 1.0)])

    supporting, opposing = split_by_side(ranked, "DRAW")

    assert supporting == []
    assert len(opposing) == 2


# -----------------------------
# Conflict
# -----------------------------


def test_conflict_is_none_when_all_evidence_agrees():
    ranked = rank_signals([evidence("HOME", 2.0), evidence("HOME", 1.0)])

    assert conflict_level(ranked) == "NONE"


def test_conflict_is_high_when_both_sides_are_equally_strong():
    ranked = rank_signals([evidence("HOME", 2.0), evidence("AWAY", 2.0)])

    assert conflict_level(ranked) == "HIGH"


def test_conflict_is_low_when_the_counter_signal_is_token():
    ranked = rank_signals([evidence("HOME", 9.0), evidence("AWAY", 0.1)])

    assert conflict_level(ranked) == "LOW"


# -----------------------------
# The explanation actually uses the ranking
# -----------------------------


def test_explanation_leads_with_the_strongest_supporting_evidence():
    """
    The headline defect: a weak signal listed first must not outrank a
    strong one listed later.
    """

    reasoning = make_reasoning(
        strengths=1,
        supporting_evidence=[
            evidence(
                "HOME", 0.1, title="Goals Scored", reason="Arsenal FC average 0.1 more goals."
            ),
            evidence(
                "HOME", 5.0, title="Current Streak", reason="Arsenal FC are on a five-match winning run."
            ),
        ],
    )

    summary = summarize(
        winner="HOME", probability=70.0, confidence=70.0, reasoning=reasoning
    )

    assert "five-match winning run" in summary
    assert "0.1 more goals" not in summary


def test_weaker_first_listed_evidence_does_not_override_stronger_evidence():
    reasoning = make_reasoning(
        weaknesses=1,
        supporting_evidence=[
            evidence("AWAY", 0.2, title="Goals Scored", reason="A marginal goals edge."),
            evidence("AWAY", 4.0, title="Head-to-Head", reason="A commanding head-to-head record."),
        ],
    )

    summary = summarize(
        winner="AWAY", probability=60.0, confidence=55.0, reasoning=reasoning
    )

    assert "commanding head-to-head record" in summary
    assert "marginal goals edge" not in summary


def test_explanation_names_the_strongest_opposing_signal():
    reasoning = make_reasoning(
        supporting_evidence=[
            evidence("HOME", 3.0, title="Current Streak", reason="Arsenal FC are in strong form."),
            evidence("AWAY", 0.3, title="Goals Scored", reason="A slim away goals edge."),
            evidence("AWAY", 2.5, title="Head-to-Head", reason="Coventry City FC own the head-to-head."),
        ],
    )

    summary = summarize(
        winner="HOME", probability=55.0, confidence=50.0, reasoning=reasoning
    )

    assert "However" in summary
    assert "own the head-to-head" in summary


def test_high_conflict_is_communicated_in_the_narrative():
    reasoning = make_reasoning(
        supporting_evidence=[
            evidence("HOME", 2.0, title="Head-to-Head", reason="Arsenal FC lead the head-to-head."),
            evidence("AWAY", 2.0, title="Current Streak", reason="Coventry City FC are on a strong run."),
        ],
    )

    summary = summarize(
        winner="HOME", probability=45.0, confidence=40.0, reasoning=reasoning
    )

    assert "could reasonably go the other way" in summary


def test_explanation_without_evidence_still_produces_a_summary():
    """
    Matches with no real evidence must degrade to the rule-based
    narrative rather than losing their explanation entirely.
    """

    summary = summarize(
        winner="HOME",
        probability=44.0,
        confidence=50.0,
        reasoning=make_reasoning(strengths=1),
    )

    assert "Arsenal FC are" in summary
    assert "stronger recent form" in summary.lower()


# -----------------------------
# The ranking reaches the API contract
# -----------------------------


def test_prediction_exposes_strongest_support_and_opposition():
    result = predict(
        make_reasoning(
            strengths=2,
            supporting_evidence=[
                evidence("HOME", 0.4, title="Goals Scored"),
                evidence("HOME", 3.0, title="Current Streak"),
                evidence("AWAY", 1.5, title="Head-to-Head"),
            ],
        )
    )

    assert result.winner == "HOME"
    assert result.strongest_support.title == "Current Streak"
    assert result.strongest_opposition.title == "Head-to-Head"
    assert result.conflict in ("NONE", "LOW", "MODERATE", "HIGH")


def test_prediction_with_no_evidence_reports_no_support_or_opposition():
    result = predict(make_reasoning(strengths=2))

    assert result.strongest_support is None
    assert result.strongest_opposition is None
    assert result.conflict == "NONE"
