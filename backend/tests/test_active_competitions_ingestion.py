import pytest

from app.repositories.match_repository import MatchRepository
from app.services.match_service import MatchService

# The 3 competitions actually in-season right now (mixed
# scheduled/finished/live state), as opposed to competitions that
# haven't started their 2026/27 campaign yet or fully-concluded past
# tournaments. Selected from real synced data, not assumed.
ACTIVE_COMPETITIONS = [
    "Campeonato Brasileiro Série A",
    "Eredivisie",
    "Primeira Liga",
]


def _first_match(status, competition):
    for match in MatchService().list_matches():
        if match.competition == competition and match.status == status:
            return match
    return None


@pytest.mark.parametrize("competition", ACTIVE_COMPETITIONS)
def test_competition_has_real_matches_in_the_existing_schema(competition):
    """
    Real matches for this competition parse cleanly into the existing
    Match model - no schema changes were needed to connect it.
    """

    matches = [m for m in MatchService().list_matches() if m.competition == competition]

    assert len(matches) > 0
    sample = matches[0]
    assert sample.home_team and sample.away_team
    assert sample.kickoff is not None


@pytest.mark.parametrize("competition", ACTIVE_COMPETITIONS)
def test_competition_has_real_finished_history(competition):
    """
    Confirms the competition is genuinely active (not just scheduled
    fixtures with no results yet) - real finished matches exist to
    serve as evidence.
    """

    finished = [
        m
        for m in MatchService().list_matches()
        if m.competition == competition and m.status == "finished"
    ]

    assert len(finished) > 0, f"{competition} has no finished matches on record"


@pytest.mark.parametrize("competition", ACTIVE_COMPETITIONS)
def test_prediction_endpoint_processes_a_real_upcoming_match(client, competition):
    """
    Acceptance criterion: the existing prediction endpoint can process
    real matches from each newly-connected competition, unmodified.
    """

    match = _first_match("scheduled", competition)
    assert match is not None, f"No scheduled match found for {competition}"

    response = client.get(f"/prediction/{match.id}")

    assert response.status_code == 200

    body = response.json()
    assert body["winner"] in ("HOME", "AWAY", "DRAW")
    assert 0 <= body["probability"] <= 100
    assert 0 <= body["confidence"] <= 100
    assert body["summary"]


@pytest.mark.parametrize("competition", ACTIVE_COMPETITIONS)
def test_finished_match_never_leaks_into_its_own_evidence(competition):
    """
    Extends the temporal-safety guarantee to real data from each
    newly-connected competition specifically, not just the
    previously-verified Eredivisie (Cambuur) case.

    Deliberately does not pass exclude_match_id - this checks the
    `before` strict-inequality boundary alone is enough to keep a
    finished match out of its own evidence, since a match's kickoff
    can never be strictly earlier than itself.
    """

    match = _first_match("finished", competition)
    assert match is not None

    repo = MatchRepository()
    qualifying = repo.get_finished_matches_by_team(
        match.home_team, before=match.kickoff,
    )

    assert all(m["id"] != match.id for m in qualifying), (
        f"{competition} match {match.id} leaked into its own evidence"
    )
