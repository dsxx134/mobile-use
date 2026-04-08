from __future__ import annotations

from typing import Protocol


class ProxyProvider(Protocol):
    def fetch_proxy_map(self, proxy_url: str) -> dict[str, str]: ...


class ProxyState:
    def __init__(self, provider: ProxyProvider):
        self.provider = provider
        self._current_proxy: dict[str, str] | None = None

    def get_proxy(self, proxy_url: str) -> dict[str, str]:
        if self._current_proxy is None:
            self._current_proxy = self.provider.fetch_proxy_map(proxy_url)
        return self._current_proxy

    def clear(self) -> None:
        self._current_proxy = None
