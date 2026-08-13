from app.knowledge.head_to_head import get_head_to_head
from app.knowledge.home_advantage import has_home_advantage
from app.knowledge.match_profile import MatchProfile
from app.knowledge.rest_days import get_rest_days
from app.knowledge.team_form import get_team_form
from app.models.match import Match


def build_match_profile(match: Match) -> MatchProfile:

    return MatchProfile(
        home_team=match.home_team,
        away_team=match.away_team,
        home_form=get_team_form(match.home_team),
        away_form=get_team_form(match.away_team),
        home_advantage=has_home_advantage(),
        rest_days_home=get_rest_days(
            match.home_team,
            before=match.kickoff,
            exclude_match_id=match.id,
        ),
        rest_days_away=get_rest_days(
            match.away_team,
            before=match.kickoff,
            exclude_match_id=match.id,
        ),
        head_to_head=get_head_to_head(
            match.home_team,
            match.away_team,
            before=match.kickoff,
            exclude_match_id=match.id,
        ),
    )
