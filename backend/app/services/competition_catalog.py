"""
What the product can actually offer, per competition.

The match list alone cannot answer "why is there nothing to analyse
here?". A competition with no upcoming fixtures is not necessarily
empty - the Champions League holds a complete, high-quality 2025/26
record and simply has no 2026/27 fixtures published to us yet.
Reporting that as "no matches" tells the user something false.

This module derives that distinction from the fixtures already on
disk. It invents no fixtures and no schedule.
"""

from datetime import datetime, timezone

from app.repositories.match_repository import MatchRepository
from app.utils.helpers import parse_kickoff

# Has fixtures still to be played.
ACTIVE = "ACTIVE"

# Everything on record has been played. Either the season is over or
# the next one has not been published to us yet - from the fixture
# data alone those are indistinguishable, so the label says only what
# is actually known.
NO_UPCOMING_FIXTURES = "NO_UPCOMING_FIXTURES"

# On record but with nothing in it at all.
EMPTY = "EMPTY"


def _summarise(name: str, matches: list[dict], now: datetime) -> dict:
    played = [m for m in matches if str(m.get("status", "")).lower() == "finished"]

    kickoffs = [k for k in (parse_kickoff(m) for m in matches) if k is not None]
    upcoming = sorted(k for k in kickoffs if k > now)

    seasons = sorted({m["season"] for m in matches if m.get("season") is not None})

    if not matches:
        availability = EMPTY
    elif upcoming:
        availability = ACTIVE
    else:
        availability = NO_UPCOMING_FIXTURES

    return {
        "name": name,
        "season": seasons[-1] if seasons else None,
        "availability": availability,
        "total_matches": len(matches),
        "played_matches": len(played),
        "upcoming_matches": len(upcoming),
        "next_kickoff": upcoming[0] if upcoming else None,
        "last_kickoff": max(kickoffs) if kickoffs else None,
        # A competition with no upcoming fixtures is still valuable:
        # its played matches remain evidence for every team in it.
        "prediction_ready": bool(upcoming),
    }


def list_competitions(now: datetime | None = None) -> list[dict]:
    """
    One summary per competition, most immediately useful first:
    competitions with fixtures to come, ordered by how soon, then
    everything else by name.
    """

    now = now or datetime.now(timezone.utc)

    matches = MatchRepository().get_all_matches()

    grouped: dict[str, list[dict]] = {}

    for match in matches:
        grouped.setdefault(match["competition"], []).append(match)

    summaries = [
        _summarise(name, competition_matches, now)
        for name, competition_matches in grouped.items()
    ]

    with_fixtures = sorted(
        [s for s in summaries if s["next_kickoff"] is not None],
        key=lambda s: (s["next_kickoff"], s["name"]),
    )
    without_fixtures = sorted(
        [s for s in summaries if s["next_kickoff"] is None],
        key=lambda s: s["name"],
    )

    return with_fixtures + without_fixtures
