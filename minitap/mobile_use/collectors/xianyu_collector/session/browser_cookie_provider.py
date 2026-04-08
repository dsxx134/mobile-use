from __future__ import annotations

from http.cookies import SimpleCookie

from minitap.mobile_use.collectors.xianyu_collector.session.browser_session import BrowserSession


class BrowserCookieProvider:
    def __init__(self, session: BrowserSession, url: str):
        self.session = session
        self.url = url
        self._cached_cookie_string: str | None = None

    def get_cookie_string(self) -> str:
        if self._cached_cookie_string is None:
            self._cached_cookie_string = self.session.get_cookie_string(self.url)
        return self._cached_cookie_string

    def get_cookie_dict(self) -> dict[str, str]:
        cookie = SimpleCookie()
        cookie.load(self.get_cookie_string())
        return {key: morsel.value for key, morsel in cookie.items()}
