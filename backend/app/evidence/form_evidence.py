from app.repositories.match_repository import MatchRepository


repository = MatchRepository()


def get_recent_form(team: str) -> list[str]:
    """
    Returns the last five completed match results.

    W = Win
    D = Draw
    L = Loss
    """

    matches = repository.get_finished_matches_by_team(team)

    results = []

    for match in reversed(matches[-5:]):

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