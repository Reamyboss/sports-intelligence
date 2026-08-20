"""
A fixture must contribute to a team's evidence exactly once.

matches.json and historical_matches.json are not disjoint: every
completed Champions League fixture is written to both - to the first
as a current-season fixture, to the second as a completed match. The
evidence pool concatenated them, so all 189 CL results were counted
twice, inflating form, goals, streak and head-to-head evidence for 36
clubs. Up to a quarter of a top side's entire match history was
duplicated, and those clubs are precisely Europe's strongest, so the
distortion landed on the matches that matter most.
"""

import collections

from app.repositories.match_repository import MatchRepository


def test_no_fixture_is_counted_twice_in_a_team_history():
    repository = MatchRepository()

    current = repository.get_all_matches()
    historical = repository.get_all_historical_matches()

    overlapping = {m["id"] for m in current} & {m["id"] for m in historical}

    # Guard the guard: if the two files ever stop overlapping, this
    # test would silently stop testing anything.
    assert overlapping, "expected the two data files to share fixtures"

    duplicated = next(
        m for m in current if m["id"] in overlapping
    )

    for team in (duplicated["home_team"], duplicated["away_team"]):
        history = repository.get_finished_matches_by_team(team)
        counts = collections.Counter(m["id"] for m in history)

        repeated = {i: c for i, c in counts.items() if c > 1}

        assert not repeated, f"{team} has duplicated fixtures: {repeated}"


def test_deduplication_does_not_drop_legitimate_history():
    """
    The fix removes copies, never distinct matches.
    """

    repository = MatchRepository()

    combined = repository.get_all_matches() + repository.get_all_historical_matches()

    finished_ids = {
        m["id"] for m in combined if str(m.get("status", "")).lower() == "finished"
    }

    team = "Arsenal FC"
    history = repository.get_finished_matches_by_team(team)

    expected = {
        m["id"]
        for m in combined
        if str(m.get("status", "")).lower() == "finished"
        and team in (m["home_team"], m["away_team"])
    }

    assert {m["id"] for m in history} == expected
    assert len(history) == len(expected)
    assert expected <= finished_ids


def test_head_to_head_is_not_inflated_by_duplicates():
    """
    Head-to-head is the signal duplication distorted most sharply -
    a two-legged Champions League tie counted as four meetings.
    """

    repository = MatchRepository()

    overlapping = {m["id"] for m in repository.get_all_matches()} & {
        m["id"] for m in repository.get_all_historical_matches()
    }

    duplicated = next(m for m in repository.get_all_matches() if m["id"] in overlapping)

    home = duplicated["home_team"]
    away = duplicated["away_team"]

    history = repository.get_finished_matches_by_team(home)

    meetings = [
        m for m in history if away in (m["home_team"], m["away_team"])
    ]

    assert len(meetings) == len({m["id"] for m in meetings})
