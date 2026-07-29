import httpx

from app.core.settings import get_settings


class FootballDataProvider:
    BASE_URL = "https://api.football-data.org/v4"

    def __init__(self):
        settings = get_settings()

        self.client = httpx.Client(
            headers={
                "X-Auth-Token": settings.FOOTBALL_DATA_API_KEY,
            },
            timeout=30.0,
        )

    def fetch_matches(
        self,
        competition: str = "PL",
    ) -> list[dict]:
        """
        Fetch current season matches.
        """

        response = self.client.get(
            f"{self.BASE_URL}/competitions/{competition}/matches"
        )

        response.raise_for_status()

        payload = response.json()

        return payload["matches"]

    def fetch_season_matches(
        self,
        competition: str,
        season: int,
    ) -> list[dict]:
        """
        Fetch matches for a specific historical season.
        """

        response = self.client.get(
            f"{self.BASE_URL}/competitions/{competition}/matches",
            params={
                "season": season,
            },
        )

        response.raise_for_status()

        payload = response.json()

        return payload["matches"]

    def close(self) -> None:
        self.client.close()