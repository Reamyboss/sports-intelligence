import httpx


class FootballDataCoUkProvider:
    """
    Free, public CSV downloads - no API key, no documented rate
    limit. Unlike FootballDataProvider, this has no dependency on
    app.core.settings.
    """

    BASE_URL = "https://www.football-data.co.uk"

    CONNECT_RETRIES = 1

    def __init__(self):
        self.client = httpx.Client(
            timeout=30.0,
            transport=httpx.HTTPTransport(retries=self.CONNECT_RETRIES),
        )

    def fetch_season_csv(self, code: str, season: str) -> str:
        """
        Fetch one competition's one-season CSV as raw text.

        `season` is football-data.co.uk's own format, e.g. "2425" for
        2024/25. These files are not reliably UTF-8 across eras, so
        decoding falls back through cp1252/latin-1 rather than
        raising - both are strict supersets of ASCII, so this never
        corrupts the columns this collector actually reads
        (Date/HomeTeam/AwayTeam/FTHG/FTAG/FTR/Time), only ever a
        stray character in a field this code doesn't use (e.g.
        Referee).
        """

        response = self.client.get(
            f"{self.BASE_URL}/mmz4281/{season}/{code}.csv"
        )

        response.raise_for_status()

        for encoding in ("utf-8", "cp1252", "latin-1"):
            try:
                return response.content.decode(encoding)
            except UnicodeDecodeError:
                continue

        return response.content.decode("latin-1", errors="replace")

    def close(self) -> None:
        self.client.close()
