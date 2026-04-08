from minitap.mobile_use.collectors.xianyu_collector.transport.proxy_state import ProxyState


class CountingProvider:
    def __init__(self):
        self.calls = 0

    def fetch_proxy_map(self, proxy_url: str) -> dict[str, str]:
        self.calls += 1
        return {
            "http": f"http://1.2.3.{self.calls}:8080",
            "https": f"http://1.2.3.{self.calls}:8080",
        }


def test_proxy_state_caches_proxy_until_cleared():
    provider = CountingProvider()
    state = ProxyState(provider)

    first = state.get_proxy("http://proxy-source")
    second = state.get_proxy("http://proxy-source")

    assert first == second
    assert provider.calls == 1


def test_proxy_state_fetches_again_after_clear():
    provider = CountingProvider()
    state = ProxyState(provider)

    first = state.get_proxy("http://proxy-source")
    state.clear()
    second = state.get_proxy("http://proxy-source")

    assert first != second
    assert provider.calls == 2
