"""
The number displayed beside a team must be that team's probability.

Before this suite existed, `probability` was the home-lean index
`clamp(50 + score * 8, 40, 90)` for every outcome - so every AWAY
prediction surfaced as 40-42%, and the UI printed
"Coventry City FC  40% probability" directly beneath a summary saying
Coventry were favoured. These tests are written to fail loudly if that
ever comes back.
"""

import pytest

from app.evidence.evidence_models import Evidence
from app.prediction.prediction_engine import predict
from app.prediction.prediction_rules import match_probabilities
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
        home_team="Arsenal FC",
        away_team="Coventry City FC",
        strengths=["s"] * strengths,
        weaknesses=["w"] * weaknesses,
        risks=["r"] * risks,
        opportunities=["o"] * opportunities,
        contradictions=["c"] * contradictions,
        summary="test",
        supporting_evidence=supporting_evidence or [],
    )


def evidence(supports, strength, title="Signal"):
    return Evidence(
        title=title, supports=supports, strength=strength, reason=f"{title} reason."
    )


# -----------------------------
# The exact production failure
# -----------------------------


def test_away_prediction_does_not_report_the_home_probability():
    """
    The regression guard for the shipped bug. An away call used to
    report ~40% - which was the *home* side's number.
    """

    result = predict(make_reasoning(weaknesses=3))

    assert result.winner == "AWAY"
    assert result.probability == result.away_probability
    assert result.probability > 50.0


def test_away_prediction_is_not_pinned_to_the_old_forty_percent_floor():
    for weaknesses in (2, 3, 5, 10):
        result = predict(make_reasoning(weaknesses=weaknesses))

        assert result.winner == "AWAY"
        assert result.probability != pytest.approx(40.0, abs=2.0)


def test_stronger_away_evidence_raises_the_away_probability():
    """
    Under the old formula every away call clamped to the same 40-42
    band, so a crushing away case and a marginal one were reported
    identically.
    """

    marginal = predict(make_reasoning(weaknesses=2))
    crushing = predict(make_reasoning(weaknesses=8))

    assert crushing.probability > marginal.probability


# -----------------------------
# Semantics: winner <-> probability
# -----------------------------


@pytest.mark.parametrize(
    "reasoning_kwargs, expected_winner",
    [
        ({"strengths": 3}, "HOME"),
        ({"weaknesses": 3}, "AWAY"),
        ({}, "DRAW"),
    ],
)
def test_probability_always_belongs_to_the_predicted_winner(
    reasoning_kwargs, expected_winner
):
    result = predict(make_reasoning(**reasoning_kwargs))

    by_outcome = {
        "HOME": result.home_probability,
        "DRAW": result.draw_probability,
        "AWAY": result.away_probability,
    }

    assert result.winner == expected_winner
    assert result.probability == by_outcome[result.winner]


@pytest.mark.parametrize(
    "reasoning_kwargs",
    [
        {},
        {"strengths": 1},
        {"strengths": 2},
        {"strengths": 6},
        {"weaknesses": 1},
        {"weaknesses": 2},
        {"weaknesses": 6},
        {"risks": 4},
        {"opportunities": 4},
        {"strengths": 3, "risks": 2},
    ],
)
def test_winner_always_holds_the_highest_probability(reasoning_kwargs):
    """
    The verdict and the numbers can never contradict each other on
    screen: whichever outcome is named must also be the one with the
    largest share.
    """

    result = predict(make_reasoning(**reasoning_kwargs))

    assert result.probability >= result.home_probability
    assert result.probability >= result.draw_probability
    assert result.probability >= result.away_probability


# -----------------------------
# Distribution invariants
# -----------------------------


@pytest.mark.parametrize(
    "reasoning_kwargs",
    [
        {},
        {"strengths": 2},
        {"weaknesses": 2},
        {"strengths": 20},
        {"weaknesses": 20},
        {"supporting_evidence": [evidence("HOME", 9.0)]},
        {"supporting_evidence": [evidence("AWAY", 9.0)]},
    ],
)
def test_probabilities_sum_to_one_hundred(reasoning_kwargs):
    home, draw, away = match_probabilities(make_reasoning(**reasoning_kwargs))

    assert home + draw + away == pytest.approx(100.0, abs=0.05)


@pytest.mark.parametrize(
    "reasoning_kwargs",
    [{}, {"strengths": 4}, {"weaknesses": 4}, {"strengths": 50}, {"weaknesses": 50}],
)
def test_no_probability_is_negative_or_above_one_hundred(reasoning_kwargs):
    for value in match_probabilities(make_reasoning(**reasoning_kwargs)):
        assert 0.0 <= value <= 100.0


def test_distribution_is_symmetric_between_home_and_away():
    """
    A home case and its exact mirror must produce mirrored numbers.
    The old clamp of [40, 90] was asymmetric by construction, which is
    what allowed home calls to reach 90 while away calls never left 40.
    """

    home_side = match_probabilities(make_reasoning(strengths=3))
    away_side = match_probabilities(make_reasoning(weaknesses=3))

    assert home_side[0] == pytest.approx(away_side[2])
    assert home_side[2] == pytest.approx(away_side[0])
    assert home_side[1] == pytest.approx(away_side[1])


def test_no_evidence_produces_a_near_even_three_way_split():
    home, draw, away = match_probabilities(make_reasoning())

    assert home == pytest.approx(away)
    assert draw > home


# -----------------------------
# Confidence agrees with the claim being made
# -----------------------------


def test_confidence_is_measured_against_the_predicted_outcome():
    """
    Confidence used to be seeded with the home-lean index, so a
    decisive away call was reported as low confidence purely for not
    being a home win. A strong away case must not score lower than a
    marginal one.
    """

    marginal = predict(make_reasoning(weaknesses=2))
    decisive = predict(make_reasoning(weaknesses=6))

    assert decisive.confidence > marginal.confidence
