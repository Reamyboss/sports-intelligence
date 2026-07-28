from app.repositories.match_repository import MatchRepository


class MatchService:
    def __init__(self):
        self.repository = MatchRepository()

    def list_matches(self) -> list[dict]:
        return self.repository.get_all_matches()

    def get_match(self, match_id: int) -> dict | None:
        return self.repository.get_match(match_id)