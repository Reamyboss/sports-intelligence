from app.collectors.normalizer import normalize_status, normalize_team
from app.providers.football_data_provider import FootballDataProvider
from app.repositories.match_repository import MatchRepository
from app.repositories.team_repository import TeamRepository


class SyncService:
    def __init__(self):
        self.provider = FootballDataProvider()
        self.repository = MatchRepository()
        self.team_repository = TeamRepository()

    def sync_competition(self, competition: str) -> int:
        matches_payload = self.provider.fetch_matches(competition)

        matches = []

        for match in matches_payload:
            home_score = match["score"]["fullTime"]["home"]
            away_score = match["score"]["fullTime"]["away"]

            matches.append(
                {
                    "id": match["id"],
                    "competition": match["competition"]["name"],
                    "season": int(match["season"]["startDate"][:4]),
                    "matchday": match.get("matchday"),
                    "kickoff": match["utcDate"],
                    "status": normalize_status(
                        match["status"],
                        home_score,
                        away_score,
                    ),
                    "home_team": match["homeTeam"]["name"],
                    "away_team": match["awayTeam"]["name"],
                    "home_score": home_score,
                    "away_score": away_score,
                }
            )

        self.repository.save_matches(matches)

        return len(matches)

    def sync_premier_league(self) -> int:
        return self.sync_competition("PL")

    def sync_teams(self, competition: str) -> int:
        raw_teams = self.provider.fetch_teams(competition)

        teams = [
            normalize_team(team, competition)
            for team in raw_teams
        ]

        self.team_repository.save_teams(teams)

        return len(teams)

    def close(self) -> None:
        self.provider.close()