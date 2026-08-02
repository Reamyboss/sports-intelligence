from app.evidence.form_evidence import get_recent_form
from app.evidence.goal_evidence import get_goal_statistics
from app.evidence.h2h_evidence import get_head_to_head
from app.evidence.home_away_evidence import get_home_away_statistics
from app.evidence.rest_evidence import get_rest_information
from app.evidence.streak_evidence import get_current_streak
from app.knowledge.match_profile import MatchProfile


def build_evidence(profile: MatchProfile) -> dict:
    return {
        "home_team": {
            "name": profile.home_team,
            "form": get_recent_form(profile.home_team),
            "goals": get_goal_statistics(profile.home_team),
            "home_away": get_home_away_statistics(
                profile.home_team,
            ),
            "streak": get_current_streak(
                profile.home_team,
            ),
            "rest": get_rest_information(
                profile.home_team,
            ),
        },
        "away_team": {
            "name": profile.away_team,
            "form": get_recent_form(profile.away_team),
            "goals": get_goal_statistics(profile.away_team),
            "home_away": get_home_away_statistics(
                profile.away_team,
            ),
            "streak": get_current_streak(
                profile.away_team,
            ),
            "rest": get_rest_information(
                profile.away_team,
            ),
        },
        "head_to_head": get_head_to_head(
            profile.home_team,
            profile.away_team,
        ),
    }