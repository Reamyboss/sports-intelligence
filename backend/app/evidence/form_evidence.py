from datetime import datetime

from app.repositories.match_repository import MatchRepository
from app.utils.helpers import parse_kickoff

repository = MatchRepository()


def get_recent_form(
    team: str,
    before: datetime | None = None,
    exclude_match_id: int | None = None,
) -> list[str]:
    """
    Returns the last five completed match results, most recent
    first - ordered by actual kickoff date, not JSON/file order.

    W = Win
    D = Draw
    L = Loss
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

    recent_matches = [match for _, match in dated_matches[:5]]

    results = []

    for match in recent_matches:

        is_home = match["home_team"] == team

        home_score = match["home_score"]
        away_score = match["away_score"]

        if home_score == away_score:
            results.append("D")

        elif is_home:

            results.append(
                "W" if home_score > away_score else "L"
            )

        else:

            results.append(
                "W" if away_score > home_score else "L"
            )

    return results
