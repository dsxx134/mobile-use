from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProxyConfig:
    is_open_proxy: bool = False
    proxy_url: str = ""

    @property
    def enabled(self) -> bool:
        return self.is_open_proxy and bool(self.proxy_url)
