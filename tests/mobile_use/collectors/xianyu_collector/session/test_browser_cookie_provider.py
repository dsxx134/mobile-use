from minitap.mobile_use.collectors.xianyu_collector.session.browser_cookie_provider import BrowserCookieProvider


class FakeBrowserSession:
    def __init__(self):
        self.calls = []

    def get_cookie_string(self, url: str) -> str:
        self.calls.append(url)
        return "a=1; _m_h5_tk=token_123; _m_h5_tk_enc=enc_999"


def test_browser_cookie_provider_reads_cookie_string_from_browser_session():
    session = FakeBrowserSession()
    provider = BrowserCookieProvider(session, "https://www.goofish.com/")

    cookie_dict = provider.get_cookie_dict()

    assert session.calls == ["https://www.goofish.com/"]
    assert cookie_dict["_m_h5_tk"] == "token_123"
    assert provider.get_cookie_string() == "a=1; _m_h5_tk=token_123; _m_h5_tk_enc=enc_999"
