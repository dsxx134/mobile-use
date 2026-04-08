from __future__ import annotations

import hashlib
import time
from typing import Callable


class MissingTokenError(ValueError):
    """Raised when the cookie jar cannot provide a signing token."""


class MtopSigner:
    def __init__(self, time_provider: Callable[[], float] | None = None):
        self._time_provider = time_provider or time.time

    def sign(self, cookies: dict[str, str], payload: dict[str, str]) -> tuple[str, int]:
        token = self._extract_token(cookies)
        timestamp_ms = int(self._time_provider() * 1000)
        sign_str = f"{token}&{timestamp_ms}&34839810&{payload['data']}"
        sign = hashlib.md5(sign_str.encode("utf-8")).hexdigest()
        return sign, timestamp_ms

    @staticmethod
    def _extract_token(cookies: dict[str, str]) -> str:
        if cookies.get("_m_h5_tk"):
            return cookies["_m_h5_tk"].partition("_")[0]
        if cookies.get("tfstk"):
            return cookies["tfstk"]
        raise MissingTokenError("missing signing token")
