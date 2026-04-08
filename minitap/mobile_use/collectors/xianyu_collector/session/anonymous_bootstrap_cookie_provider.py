from __future__ import annotations

from typing import Any, Callable

from minitap.mobile_use.collectors.xianyu_collector.api.endpoints import APP_KEY, JSV, TIMEOUT
from minitap.mobile_use.collectors.xianyu_collector.signing.mtop_signer import MtopSigner
from minitap.mobile_use.collectors.xianyu_collector.transport.proxy_config import ProxyConfig


BOOTSTRAP_URL = (
    "https://h5api.m.goofish.com/h5/mtop.taobao.idlehome.home.webpc.feed/1.0/"
)
BOOTSTRAP_API = "mtop.taobao.idlehome.home.webpc.feed"
BOOTSTRAP_VERSION = "1.0"
BOOTSTRAP_BODY = '{"itemId":"","pageSize":30,"pageNumber":1,"machId":""}'


class AnonymousBootstrapError(ValueError):
    """Raised when anonymous bootstrap cannot obtain a signing session."""


class AnonymousBootstrapCookieProvider:
    def __init__(
        self,
        *,
        transport: Any,
        signer: MtopSigner,
        proxy_config: ProxyConfig | None = None,
        token_generator: Callable[[int], str] | None = None,
        cna_generator: Callable[[], str] | None = None,
    ):
        self.transport = transport
        self.signer = signer
        self.proxy_config = proxy_config or ProxyConfig()
        self.token_generator = token_generator or (lambda _length: "seedtoken")
        self.cna_generator = cna_generator or (lambda: "")
        self._cached_cookie_dict: dict[str, str] | None = None

    def get_cookie_dict(self) -> dict[str, str]:
        if self._cached_cookie_dict is None:
            self._cached_cookie_dict = self._bootstrap_cookie_dict()
        return dict(self._cached_cookie_dict)

    def get_cookie_string(self) -> str:
        cookies = self.get_cookie_dict()
        return "; ".join(f"{key}={value}" for key, value in cookies.items())

    def _bootstrap_cookie_dict(self) -> dict[str, str]:
        seed_token = self.token_generator(128)
        payload = {"data": BOOTSTRAP_BODY}
        cookies = {"tfstk": seed_token}
        sign, timestamp = self.signer.sign(cookies, payload)
        response = self.transport.request(
            "POST",
            BOOTSTRAP_URL,
            cookies=cookies,
            params={
                "jsv": JSV,
                "appKey": APP_KEY,
                "t": str(timestamp),
                "sign": sign,
                "v": BOOTSTRAP_VERSION,
                "type": "originaljson",
                "accountSite": "xianyu",
                "dataType": "json",
                "timeout": TIMEOUT,
                "api": BOOTSTRAP_API,
                "sessionOption": "AutoLoginOnly",
            },
            data=payload,
            timeout=10,
            proxy_config=self.proxy_config,
        )
        response_cookies = dict(response.cookies.get_dict())
        if not response_cookies.get("_m_h5_tk"):
            raise AnonymousBootstrapError("bootstrap session did not return _m_h5_tk")

        response_cookies.setdefault("cna", self.cna_generator())
        response_cookies.setdefault("xlly_s", "1")
        return response_cookies
