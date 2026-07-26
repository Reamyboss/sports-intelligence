from app.models.team import Team


def get_team(name: str) -> Team:

    teams = {
        "Arsenal": Team(
            id=1,
            name="Arsenal",
            country="England",
            league="Premier League",
            fifa_rating=88,
            attack_rating=90,
            midfield_rating=89,
            defense_rating=87,
            goalkeeper_rating=85,
        ),
        "Chelsea": Team(
            id=2,
            name="Chelsea",
            country="England",
            league="Premier League",
            fifa_rating=84,
            attack_rating=83,
            midfield_rating=84,
            defense_rating=82,
            goalkeeper_rating=83,
        ),
    }

    return teams[name]
