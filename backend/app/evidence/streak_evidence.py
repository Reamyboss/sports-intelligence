from app.repositories.match_repository import MatchRepository


repository = MatchRepository()


def get_current_streak(team: str) -> dict:
    """
    Calculates the team's current streaks.
    """

    matches = repository.get_finished_matches_by_team(team)

    results = []

    for match in matches:

        if match["home_team"] == team:

            if match["home_score"] > match["away_score"]:
                results.append("W")

            elif match["home_score"] < match["away_score"]:
                results.append("L")

            else:
                results.append("D")

        else:

            if match["away_score"] > match["home_score"]:
                results.append("W")

            elif match["away_score"] < match["home_score"]:
                results.append("L")

            else:
                results.append("D")

    results.reverse()

    winning_streak = 0
    unbeaten_streak = 0
    losing_streak = 0
    winless_streak = 0

    for result in results:
        if result == "W":
            winning_streak += 1
        else:
            break

    for result in results:
        if result in ("W", "D"):
            unbeaten_streak += 1
        else:
            break

    for result in results:
        if result == "L":
            losing_streak += 1
        else:
            break

    for result in results:
        if result in ("L", "D"):
            winless_streak += 1
        else:
            break

    return {
        "winning_streak": winning_streak,
        "unbeaten_streak": unbeaten_streak,
        "losing_streak": losing_streak,
        "winless_streak": winless_streak,
        "last_10_results": results[:10],
    }