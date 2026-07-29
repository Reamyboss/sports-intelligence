import json
from pathlib import Path


class MatchRepository:
    def __init__(self):
        data_dir = Path(__file__).parent.parent / "data"

        self.matches_file = data_dir / "matches.json"

        self.historical_matches_file = (
            data_dir / "historical_matches.json"
        )

    # -----------------------------
    # Current Season Matches
    # -----------------------------

    def get_all_matches(self) -> list[dict]:
        if not self.matches_file.exists():
            return []

        with self.matches_file.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    def get_match(
        self,
        match_id: int,
    ) -> dict | None:
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
            if match["status"].lower() == "finished"
        ]

    def save_matches(
        self,
        matches: list[dict],
    ) -> None:
        with self.matches_file.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                matches,
                file,
                indent=2,
                ensure_ascii=False,
            )

    # -----------------------------
    # Historical Matches
    # -----------------------------

    def get_all_historical_matches(self) -> list[dict]:
        if not self.historical_matches_file.exists():
            return []

        with self.historical_matches_file.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    def save_historical_matches(
        self,
        matches: list[dict],
    ) -> None:
        with self.historical_matches_file.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                matches,
                file,
                indent=2,
                ensure_ascii=False,
            )