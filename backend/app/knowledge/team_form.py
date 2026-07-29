from app.repositories.match_repository import MatchRepository


repository = MatchRepository()


def get_team_form(team_name: str) -> list[str]:
    matches = repository.get_finished_matches_by_team(team_name)

    matches.sort(
        key=lambda match: match["kickoff"],
        reverse=True,
    )

    recent_matches = matches[:5]

    form = []

    for match in recent_matches:

        home = match["home_team"] == team_name

        home_score = match["home_score"]
        away_score = match["away_score"]

        if home:

            if home_score > away_score:
                form.append("W")

            elif home_score < away_score:
                form.append("L")

            else:
                form.append("D")

        else:

            if away_score > home_score:
                form.append("W")

            elif away_score < home_score:
                form.append("L")

            else:
                form.append("D")

    return form