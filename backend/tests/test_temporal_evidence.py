import json
from datetime import datetime, timezone

import pytest

from app.evidence import (
    form_evidence,
    goal_evidence,
    h2h_evidence,
    home_away_evidence,
    streak_evidence,
)
from app.evidence.evidence_builder import build_evidence
from app.knowledge.match_profile import MatchProfile

EVIDENCE_MODULES = [
    form_evidence,
    goal_evidence,
    h2h_evidence,
    home_away_evidence,
    streak_evidence,
]


def match(id, home_team, away_team, kickoff, home_score=1, away_score=0, status="finished"):
    return {
        "id": id,
        "competition": "Premier League",
        "season": 2026,
        "matchday": 1,
        "kickoff": kickoff,
        "status": status,
        "home_team": home_team,
        "away_team": away_team,
        "home_score": home_score,
        "away_score": away_score,
    }


@pytest.fixture
def isolated_data(tmp_path, monkeypatch):
    """
    Every evidence module owns its own MatchRepository() instance.
    Point all of them at the same throwaway files so a test can set
    up one consistent dataset, without ever touching the real,
    live-synced app/data/*.json files.
    """

    matches_file = tmp_path / "matches.json"
    historical_file = tmp_path / "historical_matches.json"
    matches_file.write_text("[]", encoding="utf-8")
    historical_file.write_text("[]", encoding="utf-8")

    for module in EVIDENCE_MODULES:
        monkeypatch.setattr(module.repository, "matches_file", matches_file)
        monkeypatch.setattr(module.repository, "historical_matches_file", historical_file)

    def write(current=None, historical=None):
        matches_file.write_text(json.dumps(current or []), encoding="utf-8")
        historical_file.write_text(json.dumps(historical or []), encoding="utf-8")

    return write


def make_profile(home="Home FC", away="Away FC"):
    return MatchProfile(
        home_team=home,
        away_team=away,
        home_form=[],
        away_form=[],
        rest_days_home=0,
        rest_days_away=0,
        head_to_head={},
    )


# -----------------------------
# A. Self-leakage
# -----------------------------


def test_predicting_an_already_finished_match_cannot_use_its_own_result(isolated_data):
    """
    Reproduces the Cambuur case from the investigation: a team whose
    only finished match on record is the very match being predicted
    must not have that match's result appear in its own evidence.
    """

    write = isolated_data

    target = match(
        558214, "SC Cambuur-Leeuwarden", "SBV Excelsior",
        "2026-08-07T18:00:00Z", home_score=0, away_score=4,
    )
    write(current=[target])

    profile = make_profile("SC Cambuur-Leeuwarden", "SBV Excelsior")
    kickoff = datetime.fromisoformat("2026-08-07T18:00:00+00:00")

    evidence = build_evidence(profile, match_id=558214, kickoff=kickoff)

    home = evidence["home_team"]
    assert home["form"] == []
    assert home["goals"]["matches"] == 0
    assert home["streak"]["last_10_results"] == []
    assert home["home_away"]["home"] == {"wins": 0, "draws": 0, "losses": 0}

    # With no real evidence, supporting_evidence must be an honest
    # empty list, not fabricated Evidence objects.
    from app.evidence.evidence_builder import build_supporting_evidence

    assert build_supporting_evidence(evidence) == []


def test_finished_match_used_for_evidence_of_a_later_match_but_not_itself(isolated_data):
    """
    The same finished match IS legitimate evidence for a later
    prediction - only for its own prediction is it out of bounds.
    """

    write = isolated_data

    played = match(
        1, "Arsenal FC", "Chelsea FC", "2026-08-07T18:00:00Z",
        home_score=2, away_score=0,
    )
    write(current=[played])

    later_kickoff = datetime.fromisoformat("2026-08-21T19:00:00+00:00")

    evidence = build_evidence(
        make_profile("Arsenal FC", "Everton FC"),
        match_id=999,
        kickoff=later_kickoff,
    )

    assert evidence["home_team"]["form"] == ["W"]


# -----------------------------
# C. Sorting
# -----------------------------


def test_recent_form_is_chronological_not_file_order(isolated_data):
    write = isolated_data

    # Deliberately stored out of chronological order.
    historical = [
        match(3, "Arsenal FC", "X", "2026-03-01T00:00:00Z", home_score=1, away_score=0),
        match(1, "Arsenal FC", "X", "2026-01-01T00:00:00Z", home_score=0, away_score=1),
        match(2, "Arsenal FC", "X", "2026-02-01T00:00:00Z", home_score=0, away_score=0),
    ]
    write(historical=historical)

    form = form_evidence.get_recent_form("Arsenal FC")

    # Most recent first: March (W), February (D), January (L).
    assert form == ["W", "D", "L"]


def test_current_streak_is_chronological_not_file_order(isolated_data):
    write = isolated_data

    historical = [
        match(3, "Arsenal FC", "X", "2026-03-01T00:00:00Z", home_score=1, away_score=0),
        match(1, "Arsenal FC", "X", "2026-01-01T00:00:00Z", home_score=1, away_score=0),
        match(2, "Arsenal FC", "X", "2026-02-01T00:00:00Z", home_score=1, away_score=0),
    ]
    write(historical=historical)

    streak = streak_evidence.get_current_streak("Arsenal FC")

    assert streak["last_10_results"] == ["W", "W", "W"]
    assert streak["winning_streak"] == 3


# -----------------------------
# D. Newly promoted / no qualifying history
# -----------------------------


def test_no_qualifying_history_returns_honest_empty_evidence(isolated_data):
    write = isolated_data
    write(current=[], historical=[])

    assert form_evidence.get_recent_form("Newly Promoted FC") == []
    assert goal_evidence.get_goal_statistics("Newly Promoted FC")["matches"] == 0
    assert streak_evidence.get_current_streak("Newly Promoted FC")["last_10_results"] == []
    assert h2h_evidence.get_head_to_head("Newly Promoted FC", "Another FC")["matches"] == 0


def test_only_future_dated_history_still_counts_as_no_qualifying_history(isolated_data):
    """
    A team with matches on record, none of which are before kickoff,
    must behave the same as a team with no matches at all - not fall
    back to using them anyway.
    """

    write = isolated_data

    future_match = match(
        5, "Newly Promoted FC", "X", "2026-09-01T00:00:00Z", home_score=3, away_score=0,
    )
    write(current=[future_match])

    kickoff = datetime.fromisoformat("2026-08-07T18:00:00+00:00")

    evidence = build_evidence(
        make_profile("Newly Promoted FC", "X"),
        match_id=999,
        kickoff=kickoff,
    )

    assert evidence["home_team"]["form"] == []
    assert evidence["home_team"]["goals"]["matches"] == 0
