import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.match_service import MatchService

# Not a real football-data.org id (those are ~6 digits). Used to exercise
# 404 paths without depending on any specific match never existing.
UNKNOWN_MATCH_ID = 999999999


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def real_match_id():
    """
    An id that actually exists in app/data/matches.json right now.

    Deliberately not hardcoded: matches.json is live-synced data that
    gets refreshed, so a fixed id would eventually stop existing.
    """

    matches = MatchService().list_matches()

    assert matches, (
        "app/data/matches.json has no matches - "
        "tests need at least one to run against"
    )

    return matches[0].id


@pytest.fixture
def unknown_match_id():
    return UNKNOWN_MATCH_ID
