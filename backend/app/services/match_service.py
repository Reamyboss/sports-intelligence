from datetime import datetime

from app.models.match import Match


def get_matches() -> list[Match]:
    return [
        Match(
            id=1,
            home_team="Arsenal",
            away_team="Chelsea",
            competition="Premier League",
            kickoff=datetime(2026, 8, 1, 17, 30),
        )
    ]
