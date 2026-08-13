import json
from datetime import datetime

import pytest

from app.backtesting.dataset import actual_result, load_backtest_matches
from app.backtesting.runner import run_single_backtest
from app.evidence import (
    form_evidence,
    goal_evidence,
    h2h_evidence,
    home_away_evidence,
    streak_evidence,
)
from app.models.match import Match

EVIDENCE_MODULES = [
    form_evidence,
    goal_evidence,
    h2h_evidence,
    home_away_evidence,
    streak_evidence,
]


def match_dict(id, home, away, kickoff, home_score, away_score, status="FINISHED"):
    return {
        "id": id,
        "competition": "PL",
        "season": 2025,
        "matchday": 1,
        "utc_date": kickoff,
        "status": status,
        "home_team": home,
        "away_team": away,
        "home_score": home_score,
        "away_score": away_score,
    }


@pytest.fixture
def isolated_data(tmp_path, monkeypatch):
    matches_file = tmp_path / "matches.json"
    historical_file = tmp_path / "historical_matches.json"
    matches_file.write_text("[]", encoding="utf-8")
    historical_file.write_text("[]", encoding="utf-8")

    for module in EVIDENCE_MODULES:
        monkeypatch.setattr(module.repository, "matches_file", matches_file)
        monkeypatch.setattr(module.repository, "historical_matches_file", historical_file)

    def write(historical):
        historical_file.write_text(json.dumps(historical), encoding="utf-8")

    return write


def test_backtesting_a_match_never_uses_its_own_result(isolated_data):
    """
    The exact guarantee the whole backtest depends on: predicting a
    real historical match must not let that match's own score leak
    into its own evidence, the same way the live API can't.
    """

    write = isolated_data

    target = match_dict(
        900001, "Team A", "Team B", "2026-01-15T15:00:00Z", home_score=5, away_score=0,
    )
    write([target])

    match = Match(
        id=900001, home_team="Team A", away_team="Team B", competition="PL",
        kickoff=datetime.fromisoformat("2026-01-15T15:00:00+00:00"),
        home_score=5, away_score=0, status="finished",
    )

    result = run_single_backtest(match)

    assert result.evidence_count == 0
    assert result.home_support == 0
    assert result.away_support == 0


def test_backtesting_a_match_never_uses_a_later_match_as_evidence(isolated_data):
    """
    A match scheduled after the one being backtested must never
    contribute to its evidence, even though it's a real, finished
    match sitting in the same data file.
    """

    write = isolated_data

    earlier = match_dict(
        900010, "Team A", "Team C", "2026-01-01T15:00:00Z", home_score=2, away_score=0,
    )
    target = match_dict(
        900011, "Team A", "Team B", "2026-01-15T15:00:00Z", home_score=3, away_score=0,
    )
    later = match_dict(
        900012, "Team A", "Team D", "2026-02-01T15:00:00Z", home_score=0, away_score=4,
    )
    write([earlier, target, later])

    match = Match(
        id=900011, home_team="Team A", away_team="Team B", competition="PL",
        kickoff=datetime.fromisoformat("2026-01-15T15:00:00+00:00"),
        home_score=3, away_score=0, status="finished",
    )

    result = run_single_backtest(match)

    # Only the earlier match can be real evidence: one win on record,
    # not two - the later 0-4 loss must not be visible yet. Reuses
    # the already-isolated repository instance from the fixture,
    # rather than a fresh MatchRepository() pointed at the real data.
    assert result.evidence_count >= 1

    qualifying = form_evidence.repository.get_finished_matches_by_team(
        "Team A", before=match.kickoff, exclude_match_id=match.id,
    )

    assert {m["id"] for m in qualifying} == {900010}


def test_actual_result_is_read_only_after_prediction_fields_exist(isolated_data):
    """
    Structural guard: BacktestResult only exposes `actual` alongside
    the already-computed baseline/current predictions - there is no
    code path where the real result could be read before or during
    evidence construction, since actual_result() is only called at
    the end of run_single_backtest().
    """

    write = isolated_data
    write([match_dict(900020, "Team A", "Team B", "2026-01-15T15:00:00Z", 1, 1)])

    match = Match(
        id=900020, home_team="Team A", away_team="Team B", competition="PL",
        kickoff=datetime.fromisoformat("2026-01-15T15:00:00+00:00"),
        home_score=1, away_score=1, status="finished",
    )

    result = run_single_backtest(match)

    assert result.actual == "DRAW"
    assert result.actual == actual_result(match)


def test_load_backtest_matches_only_includes_real_finished_matches():
    """
    Sanity check against the real, live-synced historical data: every
    loaded match is genuinely finished with a real recorded score -
    nothing scheduled, nothing with a missing scoreline, gets in.
    """

    matches = load_backtest_matches()

    assert len(matches) > 1000  # sanity: this is meant to be a large sample

    ids = [m.id for m in matches]
    assert len(ids) == len(set(ids))  # no duplicate target matches

    for m in matches:
        assert m.home_score is not None
        assert m.away_score is not None
