from minitap.mobile_use.collectors.xianyu_collector.session.drission_browser_session import DrissionBrowserSession


class FakeCookieJar:
    def __init__(self):
        self.dict_calls = 0

    def as_dict(self):
        self.dict_calls += 1
        if self.dict_calls == 1:
            return {}
        return {"_m_h5_tk": "token_123", "_m_h5_tk_enc": "enc_999"}

    def as_str(self):
        return "_m_h5_tk=token_123; _m_h5_tk_enc=enc_999"


class FakeBrowserController:
    def __init__(self):
        self.quit_calls = 0

    def quit(self):
        self.quit_calls += 1


class FakeTab:
    def __init__(self, jar):
        self.jar = jar
        self.browser = FakeBrowserController()
        self.visited = []

    def get(self, url: str):
        self.visited.append(url)

    def cookies(self):
        return self.jar


class FakeBrowser:
    def __init__(self, tab):
        self.latest_tab = tab


class FakeOptions:
    def __init__(self):
        self.browser_path = None
        self.local_port = None
        self.auto_port_called = False

    def set_browser_path(self, path: str):
        self.browser_path = path

    def set_local_port(self, port: str):
        self.local_port = port

    def auto_port(self):
        self.auto_port_called = True


def test_drission_browser_session_waits_for_m_h5_tk_and_returns_cookie_string():
    jar = FakeCookieJar()
    tab = FakeTab(jar)
    session = DrissionBrowserSession(
        local_port="9222",
        browser_path_resolver=lambda: "C:/Chrome/chrome.exe",
        options_factory=FakeOptions,
        chromium_factory=lambda opts: FakeBrowser(tab),
        sleep=lambda _seconds: None,
        max_wait_cycles=2,
    )

    cookie_string = session.get_cookie_string("https://www.goofish.com/")

    assert cookie_string == "_m_h5_tk=token_123; _m_h5_tk_enc=enc_999"
    assert tab.visited == ["https://www.goofish.com/"]
    assert tab.browser.quit_calls == 1


def test_drission_browser_session_can_use_auto_port_when_no_fixed_port_is_provided():
    jar = FakeCookieJar()
    tab = FakeTab(jar)
    captured = {}

    def chromium_factory(opts):
        captured["options"] = opts
        return FakeBrowser(tab)

    session = DrissionBrowserSession(
        local_port=None,
        browser_path_resolver=lambda: "C:/Chrome/chrome.exe",
        options_factory=FakeOptions,
        chromium_factory=chromium_factory,
        sleep=lambda _seconds: None,
        max_wait_cycles=2,
    )

    cookie_string = session.get_cookie_string("https://www.goofish.com/")

    assert cookie_string == "_m_h5_tk=token_123; _m_h5_tk_enc=enc_999"
    assert captured["options"].auto_port_called is True
    assert captured["options"].local_port is None
