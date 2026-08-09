def test_list_teams(client):
    response = client.get("/teams/")

    assert response.status_code == 200

    body = response.json()

    assert isinstance(body, list)
    assert len(body) > 0
    assert "name" in body[0]
