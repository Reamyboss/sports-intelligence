"""
A competition with no upcoming fixtures is not the same as an empty
one - telling a user "no matches" when real results exist is false.

The Champions League was the original case: in August 2026 it held a
complete 2025/26 record and no published 2026/27 fixtures. Those
fixtures have since been synced, so that exact situation no longer
exists in the data. The distinction it exposed still has to hold, so
it is asserted here as a rule rather than pinned to whichever
competition happens to lack fixtures today.
"""

from datetime import datetime, timezone

from app.services.competition_catalog import (
    ACTIVE,
    NO_UPCOMING_FIXTURES,
    list_competitions,
)

NOW = datetime(2026, 8, 20, tzinfo=timezone.utc)


def test_competitions_endpoint_lists_every_competition(client):
    response = client.get("/competitions/")

    assert response.status_code == 200

    body = response.json()

    assert len(body) > 0

    names = {item["name"] for item in body}

    assert "Premier League" in names
    assert "UEFA Champions League" in names


def test_every_competition_reports_a_known_availability(client):
    for item in client.get("/competitions/").json():
        assert item["availability"] in (ACTIVE, NO_UPCOMING_FIXTURES, "EMPTY")


def test_premier_league_is_active_with_fixtures_to_come(client):
    body = client.get("/competitions/").json()

    premier_league = next(i for i in body if i["name"] == "Premier League")

    assert premier_league["availability"] == ACTIVE
    assert premier_league["upcoming_matches"] > 0
    assert premier_league["next_kickoff"] is not None
    assert premier_league["prediction_ready"] is True


def test_la_liga_is_present_and_active(client):
    """
    La Liga is stored under its football-data.org name, "Primera
    Division". Searching for the string "La Liga" finds nothing, which
    is exactly how it can look absent while being fully populated.
    """

    body = client.get("/competitions/").json()

    la_liga = next(i for i in body if i["name"] == "Primera Division")

    assert la_liga["availability"] == ACTIVE
    assert la_liga["upcoming_matches"] > 0


def test_a_competition_with_history_but_no_fixtures_is_never_reported_empty():
    """
    The regression guard for the false "no Champions League games"
    message, expressed as the rule it actually protects rather than
    as a fact about one competition.

    Evaluated at a point past every fixture on record (the latest is
    in May 2027), so every competition holding real results is in the
    "played everything, nothing to come" state at once. None of them
    may report EMPTY - and unlike the original Champions League
    assertion, a later fixture resync cannot invalidate this.
    """

    after_every_fixture = datetime(2030, 1, 1, tzinfo=timezone.utc)

    summaries = list_competitions(now=after_every_fixture)

    assert summaries

    with_history = [s for s in summaries if s["played_matches"] > 0]

    assert with_history

    for summary in with_history:
        assert summary["availability"] == NO_UPCOMING_FIXTURES
        assert summary["upcoming_matches"] == 0
        assert summary["prediction_ready"] is False
        assert summary["total_matches"] > 0


def test_champions_league_holds_real_history_and_is_never_empty():
    """
    The Champions League specifically - the competition the false
    "no matches" message was originally reported against - must
    always carry real played matches, whatever its fixture state
    happens to be after the most recent sync.
    """

    champions_league = next(
        s
        for s in list_competitions(now=NOW)
        if s["name"] == "UEFA Champions League"
    )

    assert champions_league["availability"] in (ACTIVE, NO_UPCOMING_FIXTURES)
    assert champions_league["played_matches"] > 0
    assert champions_league["total_matches"] > 0


def test_competitions_with_fixtures_are_listed_before_those_without():
    summaries = list_competitions(now=NOW)

    availabilities = [s["availability"] for s in summaries]
    without = [i for i, a in enumerate(availabilities) if a != ACTIVE]
    active = [i for i, a in enumerate(availabilities) if a == ACTIVE]

    if without and active:
        assert max(active) < min(without)


def test_active_competitions_are_ordered_by_soonest_kickoff():
    summaries = [s for s in list_competitions(now=NOW) if s["availability"] == ACTIVE]

    kickoffs = [s["next_kickoff"] for s in summaries]

    assert kickoffs == sorted(kickoffs)


def test_counts_are_internally_consistent():
    for summary in list_competitions(now=NOW):
        assert summary["played_matches"] <= summary["total_matches"]
        assert summary["upcoming_matches"] <= summary["total_matches"]
        assert summary["prediction_ready"] == (summary["upcoming_matches"] > 0)
