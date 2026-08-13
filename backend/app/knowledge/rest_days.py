from datetime import datetime

from app.repositories.match_repository import MatchRepository
from app.utils.helpers import parse_kickoff

repository = MatchRepository()


def get_rest_days(
    team: str,
    before: datetime | None = None,
    exclude_match_id: int | None = None,
) -> int | None:
    """
    Real days-since-last-match, computed from the same temporal-safe
    repository query the evidence layer uses (before=kickoff,
    exclude_match_id=this match). Returns None - not a guessed
    default - when there is no qualifying prior match to compute
    from, or when no temporal boundary was given at all.
    """

    if before is None:
        return None

    matches = repository.get_finished_matches_by_team(
        team,
        before=before,
        exclude_match_id=exclude_match_id,
    )

    kickoffs = [parse_kickoff(match) for match in matches]
    kickoffs = [kickoff for kickoff in kickoffs if kickoff is not None]

    if not kickoffs:
        return None

    most_recent = max(kickoffs)

    return (before - most_recent).days
