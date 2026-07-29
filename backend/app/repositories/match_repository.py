import json
from pathlib import Path


class MatchRepository:
    def __init__(self):
        self.data_file = (
            Path(__file__).parent.parent
            / "data"
            / "matches.json"
        )

    def get_all_matches(self) -> list[dict]:
        if not self.data_file.exists():
            return []

        with self.data_file.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    def get_match(self, match_id: int) -> dict | None:
        for match in self.get_all_matches():
            if match["id"] == match_id:
                return match

        return None

    def get_matches_by_competition(
        self,
        competition: str,
    ) -> list[dict]:
        return [
            match
            for match in self.get_all_matches()
            if match["competition"] == competition
        ]

    def get_matches_by_team(
        self,
        team: str,
    ) -> list[dict]:
        return [
            match
            for match in self.get_all_matches()
            if match["home_team"] == team
            or match["away_team"] == team
        ]
    def get_finished_matches_by_team(
        self,
        team: str,
    ) -> list[dict]:
       return [
        match
        for match in self.get_matches_by_team(team)
        if match["status"] == "finished"
    ]

    def save_matches(
        self,
        matches: list[dict],
    ) -> None:
        with self.data_file.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                matches,
                file,
                indent=2,
                ensure_ascii=False,
            )
        