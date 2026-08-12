from datetime import datetime

from app.repositories.match_repository import MatchRepository
from app.utils.helpers import parse_kickoff

repository = MatchRepository()


def get_current_streak(
    team: str,
    before: datetime | None = None,
    exclude_match_id: int | None = None,
) -> dict:
    """
    Calculates the team's current streaks from matches strictly
    ordered by kickoff date - not JSON/file order.
    """

    matches = repository.get_finished_matches_by_team(
        team,
        before=before,
        exclude_match_id=exclude_match_id,
    )

    dated_matches = [
        (parse_kickoff(match), match) for match in matches
    ]

    dated_matches = [
        (kickoff, match)
        for kickoff, match in dated_matches
        if kickoff is not None
    ]

    dated_matches.sort(key=lambda item: item[0], reverse=True)

    results = []

    for _, match in dated_matches:

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

    # results is already most-recent-first, since dated_matches was
    # sorted that way above.

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
