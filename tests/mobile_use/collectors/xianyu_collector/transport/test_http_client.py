import requests

from minitap.mobile_use.collectors.xianyu_collector.transport.http_client import CollectorHttpClient
from minitap.mobile_use.collectors.xianyu_collector.transport.proxy_config import ProxyConfig
from minitap.mobile_use.collectors.xianyu_collector.transport.proxy_state import ProxyState


class RecordingSession:
    def __init__(self, behavior):
        self.behavior = behavior
        self.calls = []

    def request(self, method: str, url: str, **kwargs):
        self.calls.append((method, url, kwargs))
        return self.behavior(len(self.calls), method, url, kwargs)


class DummyResponse:
    def __init__(self, status_code: int = 200):
        self.status_code = status_code


class RotatingProvider:
    def __init__(self):
        self.calls = 0

    def fetch_proxy_map(self, proxy_url: str) -> dict[str, str]:
        self.calls += 1
        return {
            "http": f"http://10.0.0.{self.calls}:8080",
            "https": f"http://10.0.0.{self.calls}:8080",
        }


def test_request_includes_proxies_when_proxy_mode_is_enabled():
    provider = RotatingProvider()
    state = ProxyState(provider)
    session = RecordingSession(lambda *_: DummyResponse())
    client = CollectorHttpClient(session=session, proxy_state=state, max_attempts=2)

    client.request(
        "POST",
        "https://example.com/items",
        proxy_config=ProxyConfig(is_open_proxy=True, proxy_url="http://proxy-source"),
        timeout=5,
        data={"hello": "world"},
    )

    assert provider.calls == 1
    assert session.calls[0][2]["proxies"] == {
        "http": "http://10.0.0.1:8080",
        "https": "http://10.0.0.1:8080",
    }


def test_request_clears_proxy_and_retries_after_timeout():
    provider = RotatingProvider()
    state = ProxyState(provider)

    def behavior(call_number, *_args):
        if call_number == 1:
            raise requests.exceptions.Timeout("boom")
        return DummyResponse()

    session = RecordingSession(behavior)
    client = CollectorHttpClient(session=session, proxy_state=state, max_attempts=2)

    response = client.request(
        "GET",
        "https://example.com/items",
        proxy_config=ProxyConfig(is_open_proxy=True, proxy_url="http://proxy-source"),
        timeout=5,
    )

    assert response.status_code == 200
    assert provider.calls == 2
    assert session.calls[0][2]["proxies"]["http"] == "http://10.0.0.1:8080"
    assert session.calls[1][2]["proxies"]["http"] == "http://10.0.0.2:8080"
