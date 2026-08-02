from app.repositories.match_repository import MatchRepository


repository = MatchRepository()


def get_home_away_statistics(team: str) -> dict:
    matches = repository.get_finished_matches_by_team(team)

    home = {
        "wins": 0,
        "draws": 0,
        "losses": 0,
    }

    away = {
        "wins": 0,
        "draws": 0,
        "losses": 0,
    }

    for match in matches:

        home_team = match["home_team"] == team

        home_score = match["home_score"]
        away_score = match["away_score"]

        if home_team:

            if home_score > away_score:
                home["wins"] += 1

            elif home_score < away_score:
                home["losses"] += 1

            else:
                home["draws"] += 1

        else:

            if away_score > home_score:
                away["wins"] += 1

            elif away_score < home_score:
                away["losses"] += 1

            else:
                away["draws"] += 1

    return {
        "home": home,
        "away": away,
    }