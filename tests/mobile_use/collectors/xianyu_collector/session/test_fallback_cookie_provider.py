from minitap.mobile_use.collectors.xianyu_collector.session.fallback_cookie_provider import FallbackCookieProvider
from minitap.mobile_use.collectors.xianyu_collector.session.saved_cookie_provider import SavedCookieProvider


class ExplodingProvider:
    def get_cookie_dict(self):
        raise RuntimeError("boom")

    def get_cookie_string(self):
        raise RuntimeError("boom")


class StaticProvider:
    def __init__(self, payload: dict[str, str], cookie_string: str = ""):
        self.payload = payload
        self.cookie_string = cookie_string
        self.calls = 0

    def get_cookie_dict(self):
        self.calls += 1
        return dict(self.payload)

    def get_cookie_string(self):
        return self.cookie_string


def test_fallback_cookie_provider_skips_invalid_provider_and_uses_first_valid_signing_cookie():
    valid_provider = StaticProvider(
        {"_m_h5_tk": "abc123_777", "_m_h5_tk_enc": "enc999"},
        "_m_h5_tk=abc123_777; _m_h5_tk_enc=enc999",
    )
    provider = FallbackCookieProvider(
        [
            SavedCookieProvider(""),
            ExplodingProvider(),
            valid_provider,
        ]
    )

    cookies = provider.get_cookie_dict()

    assert cookies["_m_h5_tk"] == "abc123_777"
    assert valid_provider.calls == 1
    assert provider.get_cookie_string() == "_m_h5_tk=abc123_777; _m_h5_tk_enc=enc999"


def test_fallback_cookie_provider_prefers_first_provider_when_it_is_already_valid():
    first = StaticProvider({"_m_h5_tk": "token1_abc"}, "_m_h5_tk=token1_abc")
    second = StaticProvider({"_m_h5_tk": "token2_abc"}, "_m_h5_tk=token2_abc")
    provider = FallbackCookieProvider([first, second])

    cookies = provider.get_cookie_dict()

    assert cookies["_m_h5_tk"] == "token1_abc"
    assert first.calls == 1
    assert second.calls == 0
