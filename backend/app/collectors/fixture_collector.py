from app.collectors.base import BaseCollector


class FixtureCollector(BaseCollector):
    """Collects fixture data."""

    async def collect(self):
        return [
            {
                "id": 1,
                "home": "Arsenal",
                "away": "Chelsea",
                "competition": "Premier League",
                "kickoff": "2026-08-01T17:30:00",
            }
        ]
