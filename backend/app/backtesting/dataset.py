"""
Loads real, completed historical matches for backtesting.

Source is exclusively historical_matches.json via the real
MatchRepository - the same repository production code uses. Records
that don't parse into a valid Match (missing/invalid kickoff, etc.)
are skipped rather than guessed at.
"""

from app.models.match import Match
from app.repositories.match_repository import MatchRepository


def _normalize(raw: dict) -> dict:
    return {
        **raw,
        "kickoff": raw.get("kickoff") or raw.get("utc_date"),
        "status": str(raw.get("status", "")).lower(),
    }


def load_backtest_matches() -> list[Match]:
    """
    Every FINISHED match in historical_matches.json, deduplicated by
    id (defensive - this file is written via merge-by-id, so it
    should not contain internal duplicates, but a target list must
    never silently double-count a match).
    """

    repository = MatchRepository()
    raw_matches = repository.get_all_historical_matches()

    by_id: dict[int, dict] = {}

    for raw in raw_matches:
        if str(raw.get("status", "")).lower() != "finished":
            continue

        if raw.get("home_score") is None or raw.get("away_score") is None:
            continue

        by_id[raw["id"]] = raw

    matches: list[Match] = []

    for raw in by_id.values():
        try:
            matches.append(Match(**_normalize(raw)))
        except Exception:
            continue

    return matches


def actual_result(match: Match) -> str:
    if match.home_score > match.away_score:
        return "HOME"
    if match.away_score > match.home_score:
        return "AWAY"
    return "DRAW"
