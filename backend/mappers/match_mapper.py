from app.domain.match import Match


class MatchMapper:

    @staticmethod
    def from_dict(data: dict) -> Match:
        return Match(
            id=data["id"],
            competition=data["competition"],
            season=data["season"],
            matchday=data["matchday"],
            kickoff=data["kickoff"],
            status=data["status"],
            home_team=data["home_team"],
            away_team=data["away_team"],
            home_score=data["home_score"],
            away_score=data["away_score"],
        )