import pytest

from minitap.mobile_use.collectors.xianyu_collector.session.anonymous_bootstrap_cookie_provider import (
    AnonymousBootstrapCookieProvider,
    AnonymousBootstrapError,
)
from minitap.mobile_use.collectors.xianyu_collector.signing.mtop_signer import MtopSigner
from minitap.mobile_use.collectors.xianyu_collector.transport.proxy_config import ProxyConfig


class FakeCookies:
    def __init__(self, payload: dict[str, str]):
        self.payload = payload

    def get_dict(self) -> dict[str, str]:
        return dict(self.payload)


class FakeResponse:
    def __init__(self, cookies: dict[str, str]):
        self.cookies = FakeCookies(cookies)


class RecordingTransport:
    def __init__(self, response: FakeResponse):
        self.response = response
        self.calls = []

    def request(self, method: str, url: str, **kwargs):
        self.calls.append((method, url, kwargs))
        return self.response


def test_anonymous_bootstrap_provider_requests_home_feed_and_caches_bootstrapped_cookies():
    transport = RecordingTransport(
        FakeResponse(
            {
                "_m_h5_tk": "abc123_777",
                "_m_h5_tk_enc": "enc999",
            }
        )
    )
    provider = AnonymousBootstrapCookieProvider(
        transport=transport,
        signer=MtopSigner(time_provider=lambda: 1710000000.123),
        proxy_config=ProxyConfig(is_open_proxy=True, proxy_url="http://proxy-source"),
        token_generator=lambda _length: "seedtoken",
        cna_generator=lambda: "cna-fixed/f",
    )

    first = provider.get_cookie_dict()
    second = provider.get_cookie_dict()

    assert first == second
    assert first["_m_h5_tk"] == "abc123_777"
    assert first["cna"] == "cna-fixed/f"
    assert first["xlly_s"] == "1"
    assert len(transport.calls) == 1

    method, url, kwargs = transport.calls[0]
    assert method == "POST"
    assert url == "https://h5api.m.goofish.com/h5/mtop.taobao.idlehome.home.webpc.feed/1.0/"
    assert kwargs["proxy_config"] == ProxyConfig(
        is_open_proxy=True,
        proxy_url="http://proxy-source",
    )
    assert kwargs["cookies"] == {"tfstk": "seedtoken"}
    assert kwargs["params"]["api"] == "mtop.taobao.idlehome.home.webpc.feed"
    assert kwargs["params"]["sign"] == "d584509607e061cd231fa68779c46806"
    assert kwargs["params"]["t"] == "1710000000123"
    assert kwargs["data"]["data"] == '{"itemId":"","pageSize":30,"pageNumber":1,"machId":""}'


def test_anonymous_bootstrap_provider_raises_when_bootstrap_response_has_no_m_h5_tk():
    transport = RecordingTransport(FakeResponse({"tfstk": "seedtoken"}))
    provider = AnonymousBootstrapCookieProvider(
        transport=transport,
        signer=MtopSigner(time_provider=lambda: 1710000000.123),
        proxy_config=ProxyConfig(),
        token_generator=lambda _length: "seedtoken",
        cna_generator=lambda: "cna-fixed/f",
    )

    with pytest.raises(AnonymousBootstrapError, match="bootstrap session did not return _m_h5_tk"):
        provider.get_cookie_dict()
