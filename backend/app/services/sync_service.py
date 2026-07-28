from app.providers.football_data_provider import FootballDataProvider
from app.repositories.match_repository import MatchRepository


class SyncService:
    def __init__(self):
        self.provider = FootballDataProvider()
        self.repository = MatchRepository()

    def sync_premier_league(self) -> int:
        payload = self.provider.fetch_matches("PL")

        competition = payload["competition"]["name"]

        matches = []

        for match in payload["matches"]:
            matches.append(
                {
                    "id": match["id"],
                    "competition": competition,
                    "season": int(payload["filters"]["season"]),
                    "matchday": match.get("matchday"),
                    "kickoff": match["utcDate"],
                    "status": match["status"].lower(),
                    "home_team": match["homeTeam"]["name"],
                    "away_team": match["awayTeam"]["name"],
                    "home_score": match["score"]["fullTime"]["home"],
                    "away_score": match["score"]["fullTime"]["away"],
                }
            )

        self.repository.save_matches(matches)

        self.provider.close()

        return len(matches)