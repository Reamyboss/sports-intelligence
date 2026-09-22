"""
Display-only match context: fixture congestion and competition
standings.

These are real computed facts shown to the reader. The single most
important property is that they are NOT scored - adding them must
leave every prediction, probability and confidence value exactly as
it was, so the measured backtest accuracy still describes the engine
that is actually running.
"""

from datetime import datetime, timedelta, timezone

from app.evidence.congestion_evidence import get_fixture_congestion
from app.evidence.evidence_builder import (
    build_context_signals,
    build_evidence,
    build_supporting_evidence,
)
from app.evidence.evidence_models import ContextSignal
from app.evidence.standings_evidence import (
    NON_LEAGUE_COMPETITIONS,
    get_standings_snapshot,
)
from app.knowledge.knowledge_builder import build_match_profile
from app.models.match import Match
from app.prediction.prediction_engine import predict
from app.reasoning.reasoning_engine import build_reasoning
from app.repositories.match_repository import MatchRepository


def _a_played_league_match() -> Match:
    """A finished Premier League match, so both sides are placed."""

    raw = next(
        m
        for m in MatchRepository().get_all_matches()
        if m["competition"] == "Premier League"
        and str(m.get("status", "")).lower() == "finished"
    )

    return Match(**raw)


# --------------------------------------------------------------
# The property that matters most
# --------------------------------------------------------------


def test_context_is_never_scored_and_cannot_change_a_prediction():
    """
    The same reasoning, predicted with and without context, must
    produce identical verdicts, probabilities and confidence. If this
    ever fails, a display-only signal has leaked into the maths and
    the published accuracy figure no longer describes the engine.
    """

    match = _a_played_league_match()
    profile = build_match_profile(match)

    evidence = build_evidence(profile, match_id=match.id, kickoff=match.kickoff)
    supporting = build_supporting_evidence(evidence)
    reasoning = build_reasoning(evidence=evidence, supporting_evidence=supporting)

    context = build_context_signals(
        profile,
        competition=match.competition,
        season=match.season,
        match_id=match.id,
        kickoff=match.kickoff,
    )

    without = predict(reasoning)
    with_context = predict(reasoning, context=context)

    assert with_context.winner == without.winner
    assert with_context.probability == without.probability
    assert with_context.home_probability == without.home_probability
    assert with_context.draw_probability == without.draw_probability
    assert with_context.away_probability == without.away_probability
    assert with_context.confidence == without.confidence


def test_context_signals_carry_no_strength_field():
    """
    Structural guard: _evidence_score sums Evidence.strength. A type
    without that field cannot be fed to it by accident.
    """

    assert "strength" not in ContextSignal.model_fields


def test_context_never_enters_supporting_evidence():
    match = _a_played_league_match()
    profile = build_match_profile(match)

    evidence = build_evidence(profile, match_id=match.id, kickoff=match.kickoff)
    supporting = build_supporting_evidence(evidence)

    titles = {item.title for item in supporting}

    assert "Fixture Congestion" not in titles
    assert "Competition Context" not in titles


# --------------------------------------------------------------
# Fixture congestion
# --------------------------------------------------------------


def test_congestion_counts_only_matches_inside_the_window():
    match = _a_played_league_match()

    narrow = get_fixture_congestion(
        match.home_team,
        before=match.kickoff,
        exclude_match_id=match.id,
        window_days=1,
    )
    wide = get_fixture_congestion(
        match.home_team,
        before=match.kickoff,
        exclude_match_id=match.id,
        window_days=90,
    )

    assert narrow["matches_played"] <= wide["matches_played"]
    assert narrow["window_days"] == 1
    assert wide["window_days"] == 90


def test_congestion_never_counts_the_match_being_predicted():
    match = _a_played_league_match()

    result = get_fixture_congestion(
        match.home_team,
        before=match.kickoff,
        exclude_match_id=match.id,
        window_days=365,
    )

    most_recent = result["most_recent_kickoff"]

    assert most_recent is None or most_recent < match.kickoff


def test_congestion_window_start_tracks_the_window_length():
    match = _a_played_league_match()

    result = get_fixture_congestion(
        match.home_team,
        before=match.kickoff,
        exclude_match_id=match.id,
        window_days=14,
    )

    assert result["window_start"] == match.kickoff - timedelta(days=14)


# --------------------------------------------------------------
# Competition standings
# --------------------------------------------------------------


def test_standings_place_a_team_inside_its_own_table():
    match = _a_played_league_match()

    snapshot = get_standings_snapshot(
        match.home_team,
        match.competition,
        match.season,
        before=match.kickoff,
        exclude_match_id=match.id,
    )

    if snapshot is None:
        return

    assert 1 <= snapshot["position"] <= snapshot["teams_in_table"]
    assert snapshot["played"] >= 0
    assert snapshot["points"] >= 0
    assert (
        snapshot["goal_difference"]
        == snapshot["goals_for"] - snapshot["goals_against"]
    )


def test_standings_are_none_for_competitions_without_a_single_table():
    for competition in NON_LEAGUE_COMPETITIONS:
        assert (
            get_standings_snapshot(
                "Brazil",
                competition,
                2026,
                before=datetime(2026, 10, 1, tzinfo=timezone.utc),
            )
            is None
        )


def test_standings_are_none_before_any_match_has_been_played():
    """
    A season with nothing played has no table. The correct answer is
    no position at all, never a fabricated first place.
    """

    assert (
        get_standings_snapshot(
            "Arsenal FC",
            "Premier League",
            2026,
            before=datetime(1990, 1, 1, tzinfo=timezone.utc),
        )
        is None
    )


def test_standings_are_none_for_a_team_not_in_the_competition():
    assert (
        get_standings_snapshot(
            "A Team That Does Not Exist",
            "Premier League",
            2026,
            before=datetime(2026, 10, 1, tzinfo=timezone.utc),
        )
        is None
    )


# --------------------------------------------------------------
# Assembly
# --------------------------------------------------------------


def test_built_signals_are_well_formed():
    match = _a_played_league_match()
    profile = build_match_profile(match)

    signals = build_context_signals(
        profile,
        competition=match.competition,
        season=match.season,
        match_id=match.id,
        kickoff=match.kickoff,
    )

    for signal in signals:
        assert isinstance(signal, ContextSignal)
        assert signal.title
        assert signal.home_value
        assert signal.away_value
        assert signal.detail
        assert signal.favours in ("HOME", "AWAY", None)


def test_prediction_endpoint_exposes_context(client):
    match = next(
        m
        for m in client.get("/matches/").json()
        if m["competition"] == "Premier League"
    )

    body = client.get(f"/prediction/{match['id']}").json()

    assert "context" in body
    assert isinstance(body["context"], list)

    for signal in body["context"]:
        assert set(signal) == {
            "title",
            "home_value",
            "away_value",
            "detail",
            "favours",
        }
