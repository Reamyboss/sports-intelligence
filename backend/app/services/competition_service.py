from app.models.competition import Competition


def get_competition(name: str) -> Competition:

    return Competition(
        id=1,
        name=name,
        country="England",
        season="2026/27",
    )
