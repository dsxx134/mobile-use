from __future__ import annotations

import json
import time
from urllib.parse import urlparse

import requests


class BitBrowserBrowserSession:
    def __init__(
        self,
        *,
        browser_id: str,
        api_host: str = "127.0.0.1",
        api_port: int = 54345,
        requests_module=requests,
        websocket_factory=None,
        sleep=None,
        max_wait_cycles: int = 10,
        max_open_attempts: int = 5,
    ):
        self.browser_id = browser_id
        self.api_host = api_host
        self.api_port = api_port
        self.requests_module = requests_module
        self.websocket_factory = websocket_factory or self._default_websocket_factory
        self.sleep = sleep or time.sleep
        self.max_wait_cycles = max_wait_cycles
        self.max_open_attempts = max_open_attempts
        self._message_id = 0

    def get_cookie_string(self, url: str) -> str:
        http_address = self._open_browser()
        websocket_url = self._resolve_websocket_url(http_address, url)
        websocket = self.websocket_factory(websocket_url)

        try:
            for _ in range(self.max_wait_cycles):
                cookies = self._get_cookies(websocket, url)
                if any(cookie.get("name") == "_m_h5_tk" for cookie in cookies):
                    return "; ".join(
                        f"{cookie['name']}={cookie['value']}"
                        for cookie in cookies
                        if cookie.get("name") and cookie.get("value") is not None
                    )
                self.sleep(1)
        finally:
            try:
                websocket.close()
            except Exception:
                pass

        raise RuntimeError("bitbrowser session did not return _m_h5_tk in time")

    def _open_browser(self) -> str:
        for attempt in range(1, self.max_open_attempts + 1):
            response = self.requests_module.post(
                f"http://{self.api_host}:{self.api_port}/browser/open",
                json={"id": self.browser_id},
                timeout=10,
            )
            payload = response.json()
            if payload.get("success"):
                http_address = payload.get("data", {}).get("http")
                if not http_address:
                    raise RuntimeError("BitBrowser API response missing data.http")
                return http_address

            message = payload.get("message") or payload.get("msg") or str(payload)
            if "正在打开" in str(message) and attempt < self.max_open_attempts:
                self.sleep(1)
                continue
            raise RuntimeError(message)

        raise RuntimeError("unreachable")

    def _resolve_websocket_url(self, http_address: str, url: str) -> str:
        response = self.requests_module.get(f"http://{http_address}/json", timeout=10)
        targets = response.json()
        requested_host = urlparse(url).netloc
        fallback_target = None

        for target in targets:
            if target.get("type") != "page":
                continue
            fallback_target = fallback_target or target
            if requested_host and requested_host in target.get("url", ""):
                websocket_url = target.get("webSocketDebuggerUrl")
                if websocket_url:
                    return websocket_url

        if fallback_target and fallback_target.get("webSocketDebuggerUrl"):
            return fallback_target["webSocketDebuggerUrl"]
        raise RuntimeError("BitBrowser page target not found")

    def _get_cookies(self, websocket, url: str) -> list[dict]:
        result = self._cdp_call(websocket, "Network.getCookies", {"urls": [url]})
        return result.get("cookies", [])

    def _cdp_call(self, websocket, method: str, params: dict | None = None) -> dict:
        self._message_id += 1
        request_id = self._message_id
        websocket.send(json.dumps({"id": request_id, "method": method, "params": params or {}}))

        while True:
            raw_response = websocket.recv()
            if isinstance(raw_response, bytes):
                raw_response = raw_response.decode("utf-8")
            response = json.loads(raw_response)
            if response.get("id") != request_id:
                continue
            if "error" in response:
                raise RuntimeError(f"CDP error: {response['error']}")
            return response.get("result", {})

    @staticmethod
    def _default_websocket_factory(websocket_url: str):
        from websockets.sync.client import connect

        return connect(websocket_url, open_timeout=10, close_timeout=10, max_size=None)
