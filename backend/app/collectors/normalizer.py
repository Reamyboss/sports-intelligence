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