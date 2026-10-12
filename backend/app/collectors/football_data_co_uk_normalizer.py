import csv
import hashlib
import io
from datetime import datetime

# football-data.co.uk file code -> this platform's competition code
# (the same codes historical_matches.json already stores under
# "competition" - see app/collectors/normalizer.py).
COMPETITION_CODE_MAP = {
    "E0": "PL",
    "E1": "ELC",
    "SP1": "PD",
    "D1": "BL1",
    "I1": "SA",
    "F1": "FL1",
    "N1": "DED",
    "P1": "PPL",
}

SOURCE = "football-data.co.uk"

# Older seasons' CSVs have no Time column at all. 15:00 is the
# long-standing standard British Saturday kickoff - used only as a
# last resort, and only affects sub-day precision (which nothing in
# this pipeline currently uses; rest-days is already day-granularity).
DEFAULT_KICKOFF_TIME = "15:00"


def parse_csv_rows(csv_text: str) -> list[dict]:
    """
    Tolerant of trailing blank lines and stray columns -
    csv.DictReader handles both natively.
    """

    reader = csv.DictReader(io.StringIO(csv_text))

    return [
        row
        for row in reader
        if row.get("HomeTeam") and row.get("AwayTeam")
    ]


def _parse_date(date_str: str) -> str | None:
    """
    football-data.co.uk dates are DD/MM/YYYY (DD/MM/YY in a few very
    old files, outside the window this collector uses, kept as a
    defensive fallback). Returns None - never a guess - if the value
    doesn't parse as either.
    """

    for fmt in ("%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).date().isoformat()
        except (ValueError, AttributeError):
            continue

    return None


def synthetic_match_id(
    source: str,
    competition: str,
    date_iso: str,
    home_team: str,
    away_team: str,
) -> int:
    """
    Deterministic and always negative, so it can never collide with
    football-data.org's real, always-positive ids when both are
    merged by id in MatchRepository.save_historical_matches().
    Deterministic also means re-running this collector on the same
    source data is idempotent - never creates a duplicate row.
    """

    key = f"{source}|{competition}|{date_iso}|{home_team}|{away_team}"
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()

    return -(int(digest[:12], 16) % 900_000_000 + 100_000_000)


def normalize_row(
    row: dict,
    code: str,
    season_start_year: int,
    team_map: dict[str, str],
) -> tuple[dict | None, str | None]:
    """
    Returns (record, None) on success, or (None, reason) when the row
    must be skipped - never a guessed value. `reason` is one of:
    "missing_field", "unparseable_date", "unparseable_score",
    "unmapped_home_team", "unmapped_away_team".

    Kickoff time is stored as if it were UTC even though
    football-data.co.uk's Time column is UK/local kickoff time, not
    UTC - a several-hour offset only matters here if it shifts the
    calendar date across midnight, which standard kickoff times
    (roughly midday to late evening) never do. Every consumer of this
    field in the pipeline only compares/sorts by date, so this is an
    accepted, documented simplification, not a silent one.
    """

    home_short = (row.get("HomeTeam") or "").strip()
    away_short = (row.get("AwayTeam") or "").strip()
    fthg = (row.get("FTHG") or "").strip()
    ftag = (row.get("FTAG") or "").strip()
    date_raw = (row.get("Date") or "").strip()

    if not (home_short and away_short and fthg and ftag and date_raw):
        return None, "missing_field"

    date_iso = _parse_date(date_raw)

    if date_iso is None:
        return None, "unparseable_date"

    try:
        home_score = int(fthg)
        away_score = int(ftag)
    except ValueError:
        return None, "unparseable_score"

    home_full = team_map.get(home_short)

    if home_full is None:
        return None, "unmapped_home_team"

    away_full = team_map.get(away_short)

    if away_full is None:
        return None, "unmapped_away_team"

    time_raw = (row.get("Time") or "").strip()
    kickoff_time = time_raw if len(time_raw) == 5 and ":" in time_raw else DEFAULT_KICKOFF_TIME

    competition = COMPETITION_CODE_MAP[code]

    if home_score > away_score:
        winner = "HOME"
    elif away_score > home_score:
        winner = "AWAY"
    else:
        winner = "DRAW"

    record = {
        "id": synthetic_match_id(SOURCE, competition, date_iso, home_full, away_full),
        "competition": competition,
        "season": season_start_year,
        "utc_date": f"{date_iso}T{kickoff_time}:00Z",
        "status": "finished",
        "home_team": home_full,
        "away_team": away_full,
        "home_score": home_score,
        "away_score": away_score,
        "winner": winner,
        "source": SOURCE,
    }

    return record, None
