from datetime import datetime

from app.repositories.match_repository import MatchRepository


repository = MatchRepository()


def get_goal_statistics(
    team: str,
    before: datetime | None = None,
    exclude_match_id: int | None = None,
) -> dict:
    """
    Calculate goal statistics from historical matches.
    """

    matches = repository.get_finished_matches_by_team(
        team,
        before=before,
        exclude_match_id=exclude_match_id,
    )

    if not matches:
        return {
            "matches": 0,
            "goals_scored": 0,
            "goals_conceded": 0,
            "avg_goals_scored": 0.0,
            "avg_goals_conceded": 0.0,
        }

    goals_scored = 0
    goals_conceded = 0

    for match in matches:

        if match["home_team"] == team:
            goals_scored += match["home_score"]
            goals_conceded += match["away_score"]

        else:
            goals_scored += match["away_score"]
            goals_conceded += match["home_score"]

    total_matches = len(matches)

    return {
        "matches": total_matches,
        "goals_scored": goals_scored,
        "goals_conceded": goals_conceded,
        "avg_goals_scored": round(
            goals_scored / total_matches,
            2,
        ),
        "avg_goals_conceded": round(
            goals_conceded / total_matches,
            2,
        ),
    }