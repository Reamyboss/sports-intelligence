from app.models.match import Match
from app.repositories.match_repository import MatchRepository


class MatchService:
    def __init__(self):
        self.repository = MatchRepository()

    def list_matches(self) -> list[Match]:
        return [
            Match(**match)
            for match in self.repository.get_all_matches()
        ]

    def get_match(self, match_id: int) -> Match | None:
        match = self.repository.get_match(match_id)

        if match is None:
            return None

        return Match(**match)