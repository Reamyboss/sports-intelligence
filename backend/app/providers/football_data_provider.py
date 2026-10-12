import httpx

from app.core.settings import get_settings


class FootballDataProvider:
    BASE_URL = "https://api.football-data.org/v4"

    # Retries transient connection failures only (e.g. DNS/connect
    # errors like [Errno 11002] getaddrinfo failed) - not HTTP error
    # responses, which still raise via raise_for_status() as before.
    CONNECT_RETRIES = 1

    def __init__(self):
        settings = get_settings()

        self.client = httpx.Client(
            headers={
                "X-Auth-Token": settings.FOOTBALL_DATA_API_KEY,
            },
            timeout=30.0,
            transport=httpx.HTTPTransport(retries=self.CONNECT_RETRIES),
        )

    def fetch_matches(
        self,
        competition: str = "PL",
    ) -> list[dict]:
        """
        Fetch current season fixtures.
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
        Fetch matches from a specific historical season.
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

    def fetch_teams(
        self,
        competition: str,
    ) -> list[dict]:
        """
        Fetch all teams currently in a competition.
        """

        response = self.client.get(
            f"{self.BASE_URL}/competitions/{competition}/teams"
        )

        response.raise_for_status()

        payload = response.json()

        return payload["teams"]

    def close(self) -> None:
        self.client.close()