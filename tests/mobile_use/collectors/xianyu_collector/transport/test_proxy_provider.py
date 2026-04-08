import pytest

from minitap.mobile_use.collectors.xianyu_collector.transport.proxy_provider import HttpProxyProvider, ProxySourceError


def test_fetch_proxy_map_uses_first_proxy_line_and_builds_requests_map():
    provider = HttpProxyProvider(fetch_text=lambda _: "1.2.3.4:8080\r\n5.6.7.8:9090")

    proxy_map = provider.fetch_proxy_map("http://proxy-source")

    assert proxy_map == {
        "http": "http://1.2.3.4:8080",
        "https": "http://1.2.3.4:8080",
    }


def test_fetch_proxy_map_rejects_empty_proxy_source_url():
    provider = HttpProxyProvider(fetch_text=lambda _: "")

    with pytest.raises(ProxySourceError, match="proxy source URL is empty"):
        provider.fetch_proxy_map("")


def test_fetch_proxy_map_rejects_invalid_first_proxy_line():
    provider = HttpProxyProvider(fetch_text=lambda _: "not-a-proxy")

    with pytest.raises(ProxySourceError, match="invalid proxy format"):
        provider.fetch_proxy_map("http://proxy-source")
