from __future__ import annotations

from typing import Any

import requests

from minitap.mobile_use.collectors.xianyu_collector.transport.proxy_config import ProxyConfig
from minitap.mobile_use.collectors.xianyu_collector.transport.proxy_state import ProxyState


class CollectorHttpClient:
    def __init__(
        self,
        session: Any | None = None,
        proxy_state: ProxyState | None = None,
        max_attempts: int = 10,
    ):
        self.session = session or requests.Session()
        self.proxy_state = proxy_state
        self.max_attempts = max_attempts

    def request(
        self,
        method: str,
        url: str,
        *,
        proxy_config: ProxyConfig | None = None,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> Any:
        active_proxy_config = proxy_config or ProxyConfig()

        for attempt in range(1, self.max_attempts + 1):
            request_kwargs = dict(kwargs)
            if timeout is not None:
                request_kwargs["timeout"] = timeout
            if active_proxy_config.enabled:
                if self.proxy_state is None:
                    raise ValueError("proxy_state is required when proxy mode is enabled")
                request_kwargs["proxies"] = self.proxy_state.get_proxy(
                    active_proxy_config.proxy_url
                )

            try:
                return self.session.request(method, url, **request_kwargs)
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                if active_proxy_config.enabled and self.proxy_state is not None:
                    self.proxy_state.clear()
                if attempt == self.max_attempts:
                    raise

        raise RuntimeError("unreachable")
