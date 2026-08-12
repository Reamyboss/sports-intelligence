import json
from datetime import datetime
from pathlib import Path

from app.utils.helpers import parse_kickoff


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
        before: datetime | None = None,
        exclude_match_id: int | None = None,
    ) -> list[dict]:
        """
        Finished matches involving `team`.

        `before`, when given, excludes any match whose kickoff is not
        strictly earlier than it - and excludes matches with a
        missing/unparseable kickoff entirely, rather than guessing.
        `exclude_match_id` always excludes that match by id, regardless
        of its date, so a match can never contribute evidence to its
        own prediction.
        """

        combined = (
            self.get_all_matches()
            + self.get_all_historical_matches()
        )

        finished = [
            match
            for match in combined
            if match["status"].lower() == "finished"
            and (
                match["home_team"] == team
                or match["away_team"] == team
            )
        ]

        for match in finished:
            match.setdefault("kickoff", match.get("utc_date"))

        if exclude_match_id is not None:
            finished = [
                match
                for match in finished
                if match.get("id") != exclude_match_id
            ]

        if before is not None:
            bounded = []

            for match in finished:
                kickoff = parse_kickoff(match)

                if kickoff is not None and kickoff < before:
                    bounded.append(match)

            finished = bounded

        return finished

    def save_matches(
        self,
        matches: list[dict],
    ) -> None:
        merged = {
            match["id"]: match
            for match in self.get_all_matches()
        }

        for match in matches:
            merged[match["id"]] = match

        with self.matches_file.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                list(merged.values()),
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
        merged = {
            match["id"]: match
            for match in self.get_all_historical_matches()
        }

        for match in matches:
            merged[match["id"]] = match

        with self.historical_matches_file.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                list(merged.values()),
                file,
                indent=2,
                ensure_ascii=False,
            )