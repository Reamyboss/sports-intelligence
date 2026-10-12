import pytest


def test_health_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "running"
    assert "platform" in body
    assert "version" in body


def test_cors_headers_present_for_allowed_origin(client):
    response = client.get(
        "/matches/",
        headers={"Origin": "http://localhost:5173"},
    )

    assert response.status_code == 200
    assert (
        response.headers.get("access-control-allow-origin")
        == "http://localhost:5173"
    )


def test_cors_headers_present_for_production_frontend_origin(client):
    """
    Regression guard: CORS_ORIGINS didn't include the deployed
    frontend's real origin, so the browser blocked every request from
    production even though the backend itself returned 200.
    """

    response = client.get(
        "/matches/",
        headers={"Origin": "https://sports-intelligence-svpl.onrender.com"},
    )

    assert response.status_code == 200
    assert (
        response.headers.get("access-control-allow-origin")
        == "https://sports-intelligence-svpl.onrender.com"
    )



@pytest.mark.parametrize(
    "origin",
    [
        "https://sports-intelligence.vercel.app",
        "https://sports-intelligence-git-main-agrilink-ai.vercel.app",
        "https://sports-intelligence-a1b2c3d4e-agrilink-ai.vercel.app",
    ],
)
def test_cors_allows_vercel_frontend_origins(client, origin):
    response = client.get("/", headers={"Origin": origin})

    assert response.headers.get("access-control-allow-origin") == origin


@pytest.mark.parametrize(
    "origin",
    [
        "https://evil.vercel.app",
        "https://sports-intelligence-x-other-team.vercel.app",
        "https://sports-intelligence-x-agrilink-ai.vercel.app.evil.com",
    ],
)
def test_cors_rejects_other_vercel_origins(client, origin):
    response = client.get("/", headers={"Origin": origin})

    assert "access-control-allow-origin" not in response.headers
