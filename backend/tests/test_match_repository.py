from datetime import datetime, timezone

from app.repositories.match_repository import MatchRepository


def make_repo(tmp_path):
    """
    A repository pointed at a throwaway directory so tests never
    touch the real, live-synced app/data/*.json files.
    """

    repo = MatchRepository()
    repo.matches_file = tmp_path / "matches.json"
    repo.historical_matches_file = tmp_path / "historical_matches.json"

    return repo


def match(
    id,
    competition,
    status="scheduled",
    home_score=None,
    away_score=None,
    kickoff="2026-08-21T19:00:00Z",
):
    return {
        "id": id,
        "competition": competition,
        "season": 2026,
        "matchday": 1,
        "kickoff": kickoff,
        "status": status,
        "home_team": "Team A",
        "away_team": "Team B",
        "home_score": home_score,
        "away_score": away_score,
    }


def test_saving_a_second_competition_does_not_erase_the_first(tmp_path):
    """
    Regression test: save_matches() used to open the file in write
    mode and dump only what was passed in, so syncing league B after
    league A silently destroyed league A's matches.
    """

    repo = make_repo(tmp_path)

    repo.save_matches([match(1, "Premier League")])
    repo.save_matches([match(2, "La Liga")])

    ids = {m["id"] for m in repo.get_all_matches()}

    assert ids == {1, 2}


def test_saving_an_existing_id_updates_it_in_place(tmp_path):
    repo = make_repo(tmp_path)

    repo.save_matches([match(1, "Premier League", status="scheduled")])
    repo.save_matches(
        [match(1, "Premier League", status="finished", home_score=2, away_score=1)]
    )

    all_matches = repo.get_all_matches()

    assert len(all_matches) == 1
    assert all_matches[0]["status"] == "finished"
    assert all_matches[0]["home_score"] == 2


def test_historical_matches_merge_the_same_way(tmp_path):
    repo = make_repo(tmp_path)

    repo.save_historical_matches([match(1, "Premier League", status="FINISHED")])
    repo.save_historical_matches([match(2, "Bundesliga", status="FINISHED")])

    ids = {m["id"] for m in repo.get_all_historical_matches()}

    assert ids == {1, 2}


def test_finished_matches_by_team_are_found_in_historical_file(tmp_path):
    """
    Regression test: get_finished_matches_by_team() used to only read
    matches.json (the upcoming-fixtures file, which can never contain
    a finished match) instead of historical_matches.json, so evidence
    was always empty regardless of how much real history existed.
    """

    repo = make_repo(tmp_path)

    repo.save_matches([match(1, "Premier League", status="scheduled")])
    repo.save_historical_matches(
        [
            {
                **match(2, "Premier League", status="FINISHED", home_score=3, away_score=1),
                "home_team": "Arsenal FC",
                "away_team": "Chelsea FC",
                "utc_date": "2025-01-01T00:00:00Z",
            }
        ]
    )

    finished = repo.get_finished_matches_by_team("Arsenal FC")

    assert len(finished) == 1
    assert finished[0]["home_score"] == 3


def test_finished_matches_by_team_includes_current_season_once_played(tmp_path):
    """
    A team's finished matches should include results from the
    in-progress season (matches.json) as well as prior completed
    seasons (historical_matches.json) - not just one or the other.
    """

    repo = make_repo(tmp_path)

    repo.save_matches(
        [
            {
                **match(1, "Premier League", status="finished", home_score=1, away_score=1),
                "home_team": "Arsenal FC",
                "away_team": "Chelsea FC",
            }
        ]
    )
    repo.save_historical_matches([])

    finished = repo.get_finished_matches_by_team("Arsenal FC")

    assert len(finished) == 1


def test_scheduled_matches_are_excluded_from_finished_lookup(tmp_path):
    repo = make_repo(tmp_path)

    repo.save_matches(
        [
            {
                **match(1, "Premier League", status="scheduled"),
                "home_team": "Arsenal FC",
                "away_team": "Chelsea FC",
            }
        ]
    )
    repo.save_historical_matches([])

    assert repo.get_finished_matches_by_team("Arsenal FC") == []


# -----------------------------
# Temporal boundary (before / exclude_match_id)
# -----------------------------


def test_before_cutoff_excludes_matches_on_or_after_it(tmp_path):
    """
    Only matches strictly earlier than `before` should be returned -
    matches on or after it (including one at the exact same instant)
    must not leak in.
    """

    repo = make_repo(tmp_path)

    repo.save_historical_matches(
        [
            {
                **match(1, "Premier League", status="FINISHED", home_score=1, away_score=0,
                        kickoff="2026-01-01T00:00:00Z"),
                "home_team": "Arsenal FC",
                "away_team": "Chelsea FC",
            },
            {
                **match(2, "Premier League", status="FINISHED", home_score=2, away_score=0,
                        kickoff="2026-06-01T00:00:00Z"),
                "home_team": "Arsenal FC",
                "away_team": "Chelsea FC",
            },
        ]
    )

    cutoff = datetime(2026, 6, 1, tzinfo=timezone.utc)

    finished = repo.get_finished_matches_by_team("Arsenal FC", before=cutoff)

    assert {m["id"] for m in finished} == {1}


def test_exclude_match_id_removes_that_match_regardless_of_date(tmp_path):
    """
    A match must never be able to contribute to its own evidence,
    independent of the date-based cutoff.
    """

    repo = make_repo(tmp_path)

    repo.save_historical_matches(
        [
            {
                **match(1, "Premier League", status="FINISHED", home_score=1, away_score=0,
                        kickoff="2026-01-01T00:00:00Z"),
                "home_team": "Arsenal FC",
                "away_team": "Chelsea FC",
            },
        ]
    )

    cutoff = datetime(2026, 6, 1, tzinfo=timezone.utc)

    finished = repo.get_finished_matches_by_team(
        "Arsenal FC", before=cutoff, exclude_match_id=1,
    )

    assert finished == []


def test_missing_or_invalid_kickoff_is_excluded_not_guessed(tmp_path):
    """
    A match with no parseable date can't be proven to be "before" the
    cutoff, so it must be excluded rather than assumed safe.
    """

    repo = make_repo(tmp_path)

    repo.save_historical_matches(
        [
            {
                **match(1, "Premier League", status="FINISHED", home_score=1, away_score=0),
                "home_team": "Arsenal FC",
                "away_team": "Chelsea FC",
                "kickoff": "not-a-date",
            },
        ]
    )

    cutoff = datetime(2027, 1, 1, tzinfo=timezone.utc)

    finished = repo.get_finished_matches_by_team("Arsenal FC", before=cutoff)

    assert finished == []
