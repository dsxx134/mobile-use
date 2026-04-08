from __future__ import annotations

from typing import Iterable, Protocol


class CookieLikeProvider(Protocol):
    def get_cookie_dict(self) -> dict[str, str]: ...

    def get_cookie_string(self) -> str: ...


def _has_signing_token(cookies: dict[str, str]) -> bool:
    return bool(cookies.get("_m_h5_tk") or cookies.get("tfstk"))


class FallbackCookieProvider:
    def __init__(self, providers: Iterable[CookieLikeProvider]):
        self.providers = list(providers)
        self._active_provider: CookieLikeProvider | None = None

    def get_cookie_dict(self) -> dict[str, str]:
        if self._active_provider is not None:
            return dict(self._active_provider.get_cookie_dict())

        for provider in self.providers:
            try:
                cookies = dict(provider.get_cookie_dict())
            except Exception:
                continue
            if not _has_signing_token(cookies):
                continue
            self._active_provider = provider
            return cookies

        raise ValueError("no valid cookie provider produced a signing token")

    def get_cookie_string(self) -> str:
        if self._active_provider is None:
            self.get_cookie_dict()
        assert self._active_provider is not None
        return self._active_provider.get_cookie_string()
