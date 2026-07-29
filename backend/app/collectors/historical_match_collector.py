from app.providers.football_data_provider import FootballDataProvider
from app.repositories.match_repository import MatchRepository


class HistoricalMatchCollector:
    def __init__(self):
        self.provider = FootballDataProvider()
        self.repository = MatchRepository()

    def collect(self, competition: str = "PL") -> int:
        """
        Download completed historical matches and store them.
        """

        matches = self.provider.fetch_matches(competition)

        historical = [
            match
            for match in matches
            if match["status"] == "FINISHED"
        ]

        self.repository.save_matches(historical)

        return len(historical)