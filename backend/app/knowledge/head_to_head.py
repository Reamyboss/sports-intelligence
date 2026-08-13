from datetime import datetime

from app.evidence.h2h_evidence import get_head_to_head as get_h2h_evidence


def get_head_to_head(
    home: str,
    away: str,
    before: datetime | None = None,
    exclude_match_id: int | None = None,
) -> dict:
    """
    Real historical head-to-head, delegating to the same temporal-safe
    evidence-layer implementation the prediction pipeline uses -
    not a second, independent computation, and not the fabricated
    4-2-3 every matchup used to receive regardless of which two teams
    were actually playing.
    """

    return get_h2h_evidence(
        home,
        away,
        before=before,
        exclude_match_id=exclude_match_id,
    )
