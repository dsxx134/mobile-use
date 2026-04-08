from __future__ import annotations

from typing import Protocol


class BrowserSession(Protocol):
    def get_cookie_string(self, url: str) -> str: ...
