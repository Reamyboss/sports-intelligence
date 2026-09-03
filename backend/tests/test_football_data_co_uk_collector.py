import json

import pytest

from app.collectors.football_data_co_uk_collector import FootballDataCoUkCollector

TEAM_MAP = {
    "E0": {
        "Arsenal": "Arsenal FC",
        "Chelsea": "Chelsea FC",
        "Fulham": "Fulham FC",
    },
}

CSV_HEADER = "Date,Time,HomeTeam,AwayTeam,FTHG,FTAG,FTR"


@pytest.fixture
def collector(tmp_path, monkeypatch):
    matches_file = tmp_path / "matches.json"
    historical_file = tmp_path / "historical_matches.json"
    matches_file.write_text("[]", encoding="utf-8")
    historical_file.write_text("[]", encoding="utf-8")

    instance = FootballDataCoUkCollector(TEAM_MAP)
    monkeypatch.setattr(instance.repository, "matches_file", matches_file)
    monkeypatch.setattr(instance.repository, "historical_matches_file", historical_file)

    return instance


def seed_historical(collector, matches):
    collector.repository.save_historical_matches(matches)


def stub_csv(collector, monkeypatch, csv_text):
    monkeypatch.setattr(collector.provider, "fetch_season_csv", lambda code, season: csv_text)


def test_collect_saves_a_normalized_new_match(collector, monkeypatch):
    csv_text = f"{CSV_HEADER}\n16/08/2024,20:00,Arsenal,Chelsea,2,1,H\n"
    stub_csv(collector, monkeypatch, csv_text)

    result = collector.collect("E0", "2425", 2024)

    assert result.fetched == 1
    assert result.saved == 1
    assert result.skipped_duplicate == 0

    saved = collector.repository.get_all_historical_matches()
    assert len(saved) == 1
    assert saved[0]["home_team"] == "Arsenal FC"
    assert saved[0]["source"] == "football-data.co.uk"


def test_collect_skips_a_match_that_already_exists_from_football_data_org(collector, monkeypatch):
    """
    Reproduces the class of bug that caused the real Champions League
    double-count: the same match must never be counted twice just
    because two sources both have it.
    """

    seed_historical(collector, [
        {
            "id": 555001,
            "competition": "PL",
            "utc_date": "2024-08-16T19:00:00Z",
            "status": "finished",
            "home_team": "Arsenal FC",
            "away_team": "Chelsea FC",
            "home_score": 2,
            "away_score": 1,
            "source": "football-data.org",
        },
    ])

    csv_text = f"{CSV_HEADER}\n16/08/2024,20:00,Arsenal,Chelsea,2,1,H\n"
    stub_csv(collector, monkeypatch, csv_text)

    result = collector.collect("E0", "2425", 2024)

    assert result.saved == 0
    assert result.skipped_duplicate == 1

    saved = collector.repository.get_all_historical_matches()
    assert len(saved) == 1
    assert saved[0]["source"] == "football-data.org"


def test_collect_is_idempotent_across_reruns(collector, monkeypatch):
    csv_text = f"{CSV_HEADER}\n16/08/2024,20:00,Arsenal,Chelsea,2,1,H\n"
    stub_csv(collector, monkeypatch, csv_text)

    collector.collect("E0", "2425", 2024)
    collector.collect("E0", "2425", 2024)

    saved = collector.repository.get_all_historical_matches()
    assert len(saved) == 1


def test_collect_reports_unmatched_team_names_instead_of_guessing(collector, monkeypatch):
    csv_text = f"{CSV_HEADER}\n16/08/2024,20:00,Arsenal,SomeUnmappedClub,2,1,H\n"
    stub_csv(collector, monkeypatch, csv_text)

    result = collector.collect("E0", "2425", 2024)

    assert result.saved == 0
    assert result.skipped_unmapped_away == 1
    assert "SomeUnmappedClub" in result.unmatched_teams
    assert collector.repository.get_all_historical_matches() == []


def test_collect_does_not_touch_a_different_competitions_matches(collector, monkeypatch):
    seed_historical(collector, [
        {
            "id": 555002,
            "competition": "SA",
            "utc_date": "2024-08-16T19:00:00Z",
            "status": "finished",
            "home_team": "Some Italian Club",
            "away_team": "Another Italian Club",
            "home_score": 1,
            "away_score": 0,
            "source": "football-data.org",
        },
    ])

    csv_text = f"{CSV_HEADER}\n16/08/2024,20:00,Arsenal,Chelsea,2,1,H\n"
    stub_csv(collector, monkeypatch, csv_text)

    collector.collect("E0", "2425", 2024)

    saved = collector.repository.get_all_historical_matches()
    assert len(saved) == 2
