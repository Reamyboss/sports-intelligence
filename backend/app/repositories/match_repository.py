import json
from pathlib import Path


class MatchRepository:
    def __init__(self) -> None:
        self.data_file = Path(__file__).parent.parent / "data" / "matches.json"

    def get_all(self) -> list[dict]:
        with self.data_file.open(encoding="utf-8") as file:
            return json.load(file)
