from app.collectors.normalizer import normalize_match
from app.providers.football_data_provider import FootballDataProvider
from app.repositories.match_repository import MatchRepository


class HistoricalMatchCollector:
    """
    Downloads completed historical matches
    and stores them using the Sports Intelligence
    internal match format.
    """

    def __init__(self):
        self.provider = FootballDataProvider()
        self.repository = MatchRepository()

    def collect(
        self,
        competition: str = "PL",
        season: int = 2025,
    ) -> int:

        matches = self.provider.fetch_season_matches(
            competition=competition,
            season=season,
        )

        finished_matches = [
            normalize_match(match)
            for match in matches
            if match["status"] == "FINISHED"
        ]

        self.repository.save_historical_matches(
            finished_matches
        )

        return len(finished_matches)