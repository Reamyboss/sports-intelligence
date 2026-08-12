import json
from pathlib import Path


class TeamRepository:
    def __init__(self) -> None:
        self.data_file = (
            Path(__file__).parent.parent
            / "data"
            / "teams.json"
        )

    def get_all(self) -> list[dict]:
        with self.data_file.open(encoding="utf-8") as file:
            return json.load(file)

    def get_by_name(self, name: str) -> dict | None:
        teams = self.get_all()

        return next(
            (
                team
                for team in teams
                if team["name"].lower() == name.lower()
            ),
            None,
        )

    def save_teams(self, teams: list[dict]) -> None:
        merged = {
            team["id"]: team
            for team in self.get_all()
        }

        for team in teams:
            merged[team["id"]] = team

        with self.data_file.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                list(merged.values()),
                file,
                indent=2,
                ensure_ascii=False,
            )