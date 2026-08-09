from app.providers.football_data_provider import FootballDataProvider
from app.repositories.match_repository import MatchRepository


class SyncService:
    def __init__(self):
        self.provider = FootballDataProvider()
        self.repository = MatchRepository()

    def sync_competition(self, competition: str) -> int:
        matches_payload = self.provider.fetch_matches(competition)

        matches = []

        for match in matches_payload:
            matches.append(
                {
                    "id": match["id"],
                    "competition": match["competition"]["name"],
                    "season": int(match["season"]["startDate"][:4]),
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

        return len(matches)

    def sync_premier_league(self) -> int:
        return self.sync_competition("PL")

    def close(self) -> None:
        self.provider.close()