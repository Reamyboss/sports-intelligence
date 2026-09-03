from app.collectors.football_data_co_uk_normalizer import (
    normalize_row,
    parse_csv_rows,
    synthetic_match_id,
)

TEAM_MAP = {
    "Arsenal": "Arsenal FC",
    "Chelsea": "Chelsea FC",
}


def make_row(**overrides):
    row = {
        "Date": "16/08/2024",
        "Time": "20:00",
        "HomeTeam": "Arsenal",
        "AwayTeam": "Chelsea",
        "FTHG": "2",
        "FTAG": "1",
    }
    row.update(overrides)
    return row


def test_normalize_row_maps_a_clean_row():
    record, reason = normalize_row(make_row(), "E0", 2024, TEAM_MAP)

    assert reason is None
    assert record["competition"] == "PL"
    assert record["season"] == 2024
    assert record["home_team"] == "Arsenal FC"
    assert record["away_team"] == "Chelsea FC"
    assert record["home_score"] == 2
    assert record["away_score"] == 1
    assert record["winner"] == "HOME"
    assert record["status"] == "finished"
    assert record["source"] == "football-data.co.uk"
    assert record["utc_date"] == "2024-08-16T20:00:00Z"
    assert record["id"] < 0


def test_normalize_row_draw():
    record, reason = normalize_row(make_row(FTHG="1", FTAG="1"), "E0", 2024, TEAM_MAP)

    assert reason is None
    assert record["winner"] == "DRAW"


def test_normalize_row_missing_score_is_skipped_not_guessed():
    record, reason = normalize_row(make_row(FTHG=""), "E0", 2024, TEAM_MAP)

    assert record is None
    assert reason == "missing_field"


def test_normalize_row_unparseable_date_is_skipped():
    record, reason = normalize_row(make_row(Date="not-a-date"), "E0", 2024, TEAM_MAP)

    assert record is None
    assert reason == "unparseable_date"


def test_normalize_row_unmapped_home_team_is_skipped_not_guessed():
    record, reason = normalize_row(
        make_row(HomeTeam="Some Unmapped Club"), "E0", 2024, TEAM_MAP,
    )

    assert record is None
    assert reason == "unmapped_home_team"


def test_normalize_row_unmapped_away_team_is_skipped_not_guessed():
    record, reason = normalize_row(
        make_row(AwayTeam="Some Unmapped Club"), "E0", 2024, TEAM_MAP,
    )

    assert record is None
    assert reason == "unmapped_away_team"


def test_normalize_row_missing_time_column_falls_back_to_default():
    row = make_row()
    del row["Time"]

    record, reason = normalize_row(row, "E0", 2024, TEAM_MAP)

    assert reason is None
    assert record["utc_date"] == "2024-08-16T15:00:00Z"


def test_synthetic_match_id_is_deterministic_and_negative():
    id_a = synthetic_match_id("football-data.co.uk", "PL", "2024-08-16", "Arsenal FC", "Chelsea FC")
    id_b = synthetic_match_id("football-data.co.uk", "PL", "2024-08-16", "Arsenal FC", "Chelsea FC")

    assert id_a == id_b
    assert id_a < 0


def test_synthetic_match_id_differs_for_different_matches():
    id_a = synthetic_match_id("football-data.co.uk", "PL", "2024-08-16", "Arsenal FC", "Chelsea FC")
    id_b = synthetic_match_id("football-data.co.uk", "PL", "2024-08-17", "Arsenal FC", "Chelsea FC")

    assert id_a != id_b


def test_parse_csv_rows_skips_blank_trailing_lines():
    csv_text = (
        "Date,HomeTeam,AwayTeam,FTHG,FTAG\r\n"
        "16/08/2024,Arsenal,Chelsea,2,1\r\n"
        "\r\n"
    )

    rows = parse_csv_rows(csv_text)

    assert len(rows) == 1
    assert rows[0]["HomeTeam"] == "Arsenal"
