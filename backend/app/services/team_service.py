from app.models.team import Team
from app.repositories.team_repository import TeamRepository

repository = TeamRepository()


def get_teams() -> list[Team]:
    teams = repository.get_all()

    return [Team(**team) for team in teams]
