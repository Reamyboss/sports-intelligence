from datetime import datetime

from app.evidence.form_evidence import get_recent_form
from app.evidence.goal_evidence import get_goal_statistics
from app.evidence.h2h_evidence import get_head_to_head
from app.evidence.home_away_evidence import get_home_away_statistics
from app.evidence.rest_evidence import get_rest_information
from app.evidence.streak_evidence import get_current_streak
from app.knowledge.match_profile import MatchProfile


def build_evidence(
    profile: MatchProfile,
    match_id: int,
    kickoff: datetime,
) -> dict:
    """
    `match_id` and `kickoff` scope every evidence query to matches
    strictly before this match, excluding this match itself - so a
    prediction can never use its own result (or a later result) as
    evidence.
    """

    return {
        "home_team": {
            "name": profile.home_team,
            "form": get_recent_form(
                profile.home_team,
                before=kickoff,
                exclude_match_id=match_id,
            ),
            "goals": get_goal_statistics(
                profile.home_team,
                before=kickoff,
                exclude_match_id=match_id,
            ),
            "home_away": get_home_away_statistics(
                profile.home_team,
                before=kickoff,
                exclude_match_id=match_id,
            ),
            "streak": get_current_streak(
                profile.home_team,
                before=kickoff,
                exclude_match_id=match_id,
            ),
            "rest": get_rest_information(
                profile.home_team,
            ),
        },
        "away_team": {
            "name": profile.away_team,
            "form": get_recent_form(
                profile.away_team,
                before=kickoff,
                exclude_match_id=match_id,
            ),
            "goals": get_goal_statistics(
                profile.away_team,
                before=kickoff,
                exclude_match_id=match_id,
            ),
            "home_away": get_home_away_statistics(
                profile.away_team,
                before=kickoff,
                exclude_match_id=match_id,
            ),
            "streak": get_current_streak(
                profile.away_team,
                before=kickoff,
                exclude_match_id=match_id,
            ),
            "rest": get_rest_information(
                profile.away_team,
            ),
        },
        "head_to_head": get_head_to_head(
            profile.home_team,
            profile.away_team,
            before=kickoff,
            exclude_match_id=match_id,
        ),
    }
