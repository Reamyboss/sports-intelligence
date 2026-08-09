from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


def test_unhandled_exception_returns_clean_json_500():
    """
    Regression guard for the class of bug that started this whole
    effort: prediction_engine.py once raised an uncaught pydantic
    ValidationError. Before the catch-all handler existed, that kind
    of bug would have surfaced as Starlette's default plain-text 500
    instead of the {"detail": ...} JSON shape the rest of the API
    uses. This forces a crash in a route and checks the response
    shape, without depending on any specific bug still existing.
    """

    client = TestClient(app, raise_server_exceptions=False)

    with patch(
        "app.api.predictions.build_match_profile",
        side_effect=RuntimeError("simulated crash"),
    ):
        matches = client.get("/matches/").json()
        match_id = matches[0]["id"]

        response = client.get(f"/prediction/{match_id}")

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error."}


def test_known_http_errors_are_unaffected_by_the_catch_all():
    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/matches/999999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Match not found"}
