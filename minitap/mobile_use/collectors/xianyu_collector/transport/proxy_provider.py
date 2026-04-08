from __future__ import annotations

import re
from typing import Callable

import requests


PROXY_PATTERN = re.compile(r"^[A-Za-z0-9.\-]+:\d+$")


class ProxySourceError(ValueError):
    """Raised when the proxy source cannot provide a usable proxy."""


class HttpProxyProvider:
    def __init__(self, fetch_text: Callable[[str], str] | None = None):
        self._fetch_text = fetch_text or self._default_fetch_text

    def fetch_proxy_map(self, proxy_url: str) -> dict[str, str]:
        if not proxy_url:
            raise ProxySourceError("proxy source URL is empty")

        payload = self._fetch_text(proxy_url).strip()
        first_line = next((line.strip() for line in payload.splitlines() if line.strip()), "")
        if not PROXY_PATTERN.match(first_line):
            raise ProxySourceError("invalid proxy format")

        proxy_address = f"http://{first_line}"
        return {
            "http": proxy_address,
            "https": proxy_address,
        }

    @staticmethod
    def _default_fetch_text(proxy_url: str) -> str:
        response = requests.get(proxy_url, timeout=5)
        response.raise_for_status()
        return response.text
