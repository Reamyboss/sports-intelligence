def test_prediction_endpoint_returns_valid_prediction(client, real_match_id):
    """
    This is the endpoint that was crashing with a pydantic
    ValidationError before prediction_engine.py's PredictionResult()
    call was fixed to use winner= instead of prediction=. If that
    regresses, this is the test that should catch it.
    """

    response = client.get(f"/prediction/{real_match_id}")

    assert response.status_code == 200

    body = response.json()

    assert body["winner"] in ("HOME", "AWAY", "DRAW")
    assert 0 <= body["probability"] <= 100
    assert 0 <= body["confidence"] <= 100
    assert body["market"] == "MATCH_WINNER"
    assert isinstance(body["explanation"], list)
    assert "reasoning" in body
    assert isinstance(body["summary"], str) and body["summary"]


def test_prediction_endpoint_404_for_unknown_match(client, unknown_match_id):
    response = client.get(f"/prediction/{unknown_match_id}")

    assert response.status_code == 404


def test_prediction_returns_real_supporting_evidence_for_an_established_matchup(client):
    """
    Regression guard: supporting_evidence was hardcoded to [] in
    api/predictions.py regardless of how much real evidence existed.
    Arsenal FC has a full, real match history on record, so a
    prediction involving them should surface at least one real,
    structured Evidence item - not an empty list.
    """

    from app.services.match_service import MatchService

    match = next(
        m
        for m in MatchService().list_matches()
        if m.home_team == "Arsenal FC" or m.away_team == "Arsenal FC"
    )

    response = client.get(f"/prediction/{match.id}")

    assert response.status_code == 200

    supporting_evidence = response.json()["reasoning"]["supporting_evidence"]

    assert len(supporting_evidence) > 0

    for item in supporting_evidence:
        assert set(item.keys()) == {"title", "supports", "strength", "reason"}
        assert item["supports"] in ("HOME", "AWAY")
        assert item["reason"]
