from __future__ import annotations

from typing import Protocol


class CookieProvider(Protocol):
    def get_cookie_dict(self) -> dict[str, str]: ...

    def get_cookie_string(self) -> str: ...
