def test_knowledge_endpoint_returns_match_profile(client, real_match_id):
    response = client.get(f"/knowledge/{real_match_id}")

    assert response.status_code == 200

    body = response.json()

    assert "home_team" in body
    assert "away_team" in body
    assert "home_form" in body
    assert "away_form" in body

    # home_advantage used to be a hardcoded True on every match,
    # presented as a verified fact - removed rather than left as an
    # unverifiable guess. Must not silently reappear.
    assert "home_advantage" not in body


def test_knowledge_404_for_unknown_id(client, unknown_match_id):
    response = client.get(f"/knowledge/{unknown_match_id}")

    assert response.status_code == 404
