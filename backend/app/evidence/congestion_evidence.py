from datetime import datetime, timedelta

from app.repositories.match_repository import MatchRepository
from app.utils.helpers import parse_kickoff

repository = MatchRepository()

# Two weeks is the window in which a backlog is actually felt: long
# enough to contain a midweek cup run on top of league football,
# short enough that last month's schedule doesn't dilute it.
DEFAULT_WINDOW_DAYS = 14


def get_fixture_congestion(
    team: str,
    before: datetime | None = None,
    exclude_match_id: int | None = None,
    window_days: int = DEFAULT_WINDOW_DAYS,
) -> dict:
    """
    How many matches `team` actually played in the `window_days`
    leading up to `before`.

    This is the density companion to rest days: rest days answer "how
    long since the last match", congestion answers "how much football
    has this side had in its legs recently" - a team can have four
    days' rest and still be in its fifth match in a fortnight.

    Counts only finished matches strictly before `before`, under the
    same boundary every other evidence module uses, so it can never
    see the match being predicted or anything after it. Matches with
    an unparseable kickoff are excluded rather than guessed at.

    `window_start` is None when `before` is None - with no reference
    point there is no window, so the count is over every finished
    match on record and callers should treat it as unbounded.
    """

    matches = repository.get_finished_matches_by_team(
        team,
        before=before,
        exclude_match_id=exclude_match_id,
    )

    window_start = before - timedelta(days=window_days) if before else None

    in_window = []

    for match in matches:
        kickoff = parse_kickoff(match)

        if kickoff is None:
            continue

        if window_start is not None and kickoff < window_start:
            continue

        in_window.append((kickoff, match))

    in_window.sort(key=lambda item: item[0], reverse=True)

    return {
        "window_days": window_days,
        "matches_played": len(in_window),
        "window_start": window_start,
        "most_recent_kickoff": in_window[0][0] if in_window else None,
    }
