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


def test_prediction_endpoint_404_for_unknown_match(client, unknown_match_id):
    response = client.get(f"/prediction/{unknown_match_id}")

    assert response.status_code == 404
