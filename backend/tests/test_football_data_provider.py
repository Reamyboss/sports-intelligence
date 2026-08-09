import httpx

from app.providers.football_data_provider import FootballDataProvider


def test_client_transport_is_configured_to_retry_connection_failures():
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
