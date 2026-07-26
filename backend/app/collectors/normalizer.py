from datetime import datetime

from app.models.match import Match


def normalize_fixture(data: dict) -> Match:
    """Convert raw fixture data into our internal Match model."""

    return Match(
        id=data["id"],
        home_team=data["home"],
        away_team=data["away"],
        competition=data["competition"],
        kickoff=datetime.fromisoformat(data["kickoff"]),
    )
