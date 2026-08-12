from datetime import datetime


def parse_kickoff(match: dict) -> datetime | None:
    """
    Safely parse a match's kickoff/utc_date into a timezone-aware
    datetime. Returns None if missing or unparseable - callers must
    treat that as "unknown" and exclude the match rather than guess.
    """

    raw = match.get("kickoff") or match.get("utc_date")

    if not raw:
        return None

    try:
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
