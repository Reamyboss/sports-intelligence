from datetime import datetime

from app.evidence.form_evidence import get_recent_form


def get_team_form(
    team_name: str,
    before: datetime | None = None,
    exclude_match_id: int | None = None,
) -> list[str]:
    """
    Real recent form, delegating to the same temporal-safe evidence-
    layer implementation the prediction pipeline uses - not a second,
    independent computation that (without a before/exclude_match_id
    boundary) could show results from after the match it's describing.
    """

    return get_recent_form(
        team_name,
        before=before,
        exclude_match_id=exclude_match_id,
    )
