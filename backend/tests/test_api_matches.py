def test_list_matches_returns_real_data(client):
    response = client.get("/matches/")

    assert response.status_code == 200

    body = response.json()

    assert isinstance(body, list)
    assert len(body) > 0
    assert "home_team" in body[0]
    assert "away_team" in body[0]


def test_get_match_by_id(client, real_match_id):
    response = client.get(f"/matches/{real_match_id}")

    assert response.status_code == 200
    assert response.json()["id"] == real_match_id


def test_get_match_404_for_unknown_id(client, unknown_match_id):
    response = client.get(f"/matches/{unknown_match_id}")

    assert response.status_code == 404
