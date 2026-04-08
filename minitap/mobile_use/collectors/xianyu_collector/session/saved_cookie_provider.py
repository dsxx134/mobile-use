from __future__ import annotations

from http.cookies import SimpleCookie


class SavedCookieProvider:
    def __init__(self, cookie_string: str):
        self.cookie_string = cookie_string

    def get_cookie_string(self) -> str:
        return self.cookie_string

    def get_cookie_dict(self) -> dict[str, str]:
        cookie = SimpleCookie()
        cookie.load(self.cookie_string)
        return {key: morsel.value for key, morsel in cookie.items()}
