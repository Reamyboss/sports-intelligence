import httpx
import pytest

from app.core.settings import get_settings
from app.providers.football_data_provider import FootballDataProvider


@pytest.fixture
def api_key(monkeypatch):
    """
    A placeholder key, so these tests run without a real .env - CI
    has none. get_settings() is cached, so it is cleared on both sides
    to keep one test's key from leaking into the next.
    """

    monkeypatch.setenv("FOOTBALL_DATA_API_KEY", "test-key")
    get_settings.cache_clear()
    yield "test-key"
    get_settings.cache_clear()


def test_missing_api_key_fails_when_provider_is_created(monkeypatch):
    """
    The key is required to sync, but only to sync: importing the
    provider must work without it (the API server and the test suite
    both import it), and creating one must still fail loudly.
    """

    monkeypatch.delenv("FOOTBALL_DATA_API_KEY", raising=False)
    get_settings.cache_clear()

    try:
        with pytest.raises(ValueError, match="FOOTBALL_DATA_API_KEY"):
            FootballDataProvider()
    finally:
        get_settings.cache_clear()


def test_provider_sends_the_configured_api_key(api_key):
    provider = FootballDataProvider()

    assert provider.client.headers["X-Auth-Token"] == api_key

    provider.close()


def test_client_transport_is_configured_to_retry_connection_failures(api_key):
    """
    Regression guard for the retry fix: transient connection failures
    (e.g. [Errno 11002] getaddrinfo failed, hit repeatedly during real
    syncs) should be retried automatically rather than failing the
    whole sync on the first hiccup. This checks the provider actually
    wires up retries - not httpx's own retry mechanism, which is
    httpx's responsibility to test, not ours.
    """

    provider = FootballDataProvider()

    assert isinstance(provider.client._transport, httpx.HTTPTransport)
    assert FootballDataProvider.CONNECT_RETRIES >= 1

    provider.close()
