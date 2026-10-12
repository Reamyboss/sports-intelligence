from datetime import datetime

from app.repositories.match_repository import MatchRepository
from app.utils.helpers import parse_kickoff


repository = MatchRepository()


def get_head_to_head(
    home_team: str,
    away_team: str,
    before: datetime | None = None,
    exclude_match_id: int | None = None,
) -> dict:
    """
    Returns historical head-to-head record.
    """

    matches = repository.get_all_historical_matches()

    home_wins = 0
    away_wins = 0
    draws = 0

    for match in matches:

        if (
            exclude_match_id is not None
            and match.get("id") == exclude_match_id
        ):
            continue

        teams = {
            match["home_team"],
            match["away_team"],
        }

        if teams != {home_team, away_team}:
            continue

        if before is not None:
            kickoff = parse_kickoff(match)

            if kickoff is None or kickoff >= before:
                continue

        home_score = match["home_score"]
        away_score = match["away_score"]

        if home_score == away_score:
            draws += 1

        elif match["home_team"] == home_team:

            if home_score > away_score:
                home_wins += 1
            else:
                away_wins += 1

        else:

            if home_score > away_score:
                away_wins += 1
            else:
                home_wins += 1

    return {
        "matches": home_wins + away_wins + draws,
        "home_wins": home_wins,
        "draws": draws,
        "away_wins": away_wins,
    }