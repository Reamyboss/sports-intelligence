from datetime import datetime

from app.models.match import Match


def normalize_fixture(data: dict) -> Match:
    """
    Normalize a simple fixture into our internal Match model.
    """

    return Match(
        id=data["id"],
        home_team=data["home"],
        away_team=data["away"],
        competition=data["competition"],
        kickoff=datetime.fromisoformat(data["kickoff"]),
    )


# The match states football-data.org documents. Anything outside this
# set is upstream corruption, not a state we should store.
KNOWN_STATUSES = {
    "scheduled",
    "timed",
    "in_play",
    "paused",
    "finished",
    "postponed",
    "suspended",
    "cancelled",
    "awarded",
}


def normalize_status(raw_status, home_score=None, away_score=None) -> str:
    """
    Guard the ingestion boundary against a malformed upstream `status`.

    football-data.org intermittently returns the fixture's kick-off
    timestamp in this field instead of a state - observed on 54
    Primeira Liga and 1 Brasileirao fixtures, e.g.
    `"status": "2026-08-22 14:30:00Z"`. Re-syncing cannot fix it
    because the defect is in the source payload, so it has to be
    caught here.

    Storing the raw value is the dangerous option: `status` is what
    decides whether a match becomes historical evidence, and a garbage
    value silently means "never finished, never counted" - the result
    would never feed back into the engine even after the match is
    played.

    A full-time score line is the only reliable evidence that a match
    has actually been played, so that (and nothing else) promotes an
    unrecognised status to "finished". Everything else falls back to
    "scheduled", which is the safe direction: a fixture wrongly marked
    scheduled is merely invisible, whereas one wrongly marked finished
    would inject a fabricated result into the evidence base.
    """

    status = str(raw_status or "").strip().lower()

    if status in KNOWN_STATUSES:
        return status

    if home_score is not None and away_score is not None:
        return "finished"

    return "scheduled"


def normalize_match(raw_match: dict) -> dict:
    """
    Normalize a Football-Data.org match into the
    Sports Intelligence internal match format.
    """

    score = raw_match.get("score", {})
    full_time = score.get("fullTime", {})

    home_score = full_time.get("home")
    away_score = full_time.get("away")

    winner = "UNKNOWN"

    if home_score is not None and away_score is not None:

        if home_score > away_score:
            winner = "HOME"

        elif away_score > home_score:
            winner = "AWAY"

        else:
            winner = "DRAW"

    season = int(raw_match["season"]["startDate"][:4])

    return {
        "id": raw_match["id"],
        "competition_id": raw_match["competition"]["id"],
        "competition": raw_match["competition"]["code"],
        "season": season,
        "matchday": raw_match["matchday"],
        "utc_date": raw_match["utcDate"],
        "status": raw_match["status"],
        "home_team_id": raw_match["homeTeam"]["id"],
        "home_team": raw_match["homeTeam"]["name"],
        "away_team_id": raw_match["awayTeam"]["id"],
        "away_team": raw_match["awayTeam"]["name"],
        "home_score": home_score,
        "away_score": away_score,
        "winner": winner,
    }


def normalize_team(raw_team: dict, competition_code: str) -> dict:
    """
    Normalize a Football-Data.org team into the Sports Intelligence
    internal team format (matches app.models.team.Team).
    """

    league_name = competition_code

    for competition in raw_team.get("runningCompetitions", []):
        if competition.get("code") == competition_code:
            league_name = competition.get("name", competition_code)
            break

    coach = raw_team.get("coach") or {}

    return {
        "id": raw_team["id"],
        "name": raw_team["name"],
        "country": raw_team["area"]["name"],
        "league": league_name,
        "stadium": raw_team.get("venue") or "Unknown",
        "manager": coach.get("name") or "Unknown",
    }