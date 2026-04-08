from __future__ import annotations

from typing import Any
from urllib.parse import parse_qs, urlparse

from minitap.mobile_use.collectors.xianyu_collector.api.endpoints import (
    APP_KEY,
    DETAIL_ENDPOINT,
    JSV,
    MULTI_SPEC_ENDPOINT,
    SEARCH_ENDPOINT,
    SHOP_LIST_ENDPOINT,
    TIMEOUT,
    USER_HEAD_ENDPOINT,
    EndpointSpec,
)
from minitap.mobile_use.collectors.xianyu_collector.session.cookie_provider import CookieProvider
from minitap.mobile_use.collectors.xianyu_collector.signing.mtop_signer import MtopSigner
from minitap.mobile_use.collectors.xianyu_collector.transport.proxy_config import ProxyConfig


DEFAULT_HEADERS = {
    "accept": "application/json",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://www.goofish.com",
    "priority": "u=1, i",
    "referer": "https://www.goofish.com/",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    ),
}

MULTI_SPEC_HEADERS = {
    **DEFAULT_HEADERS,
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "sec-ch-ua": '"Microsoft Edge";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 "
        "Safari/537.36 Edg/143.0.0.0"
    ),
}


class GoofishApiError(RuntimeError):
    """Base exception for upstream Goofish collector failures."""


class GoofishBurstError(GoofishApiError):
    """Raised when upstream returns an anti-burst / anti-bot response."""


class GoofishSystemError(GoofishApiError):
    """Raised when upstream asks the client to retry later."""


class GoofishLoginRedirectError(GoofishApiError):
    """Raised when upstream responds with a login redirect payload."""


class GoofishApiClient:
    def __init__(
        self,
        transport: Any,
        cookie_provider: CookieProvider,
        signer: MtopSigner,
        url_expander: Any | None = None,
    ):
        self.transport = transport
        self.cookie_provider = cookie_provider
        self.signer = signer
        self.url_expander = url_expander

    def search_items(
        self,
        *,
        page: int,
        keyword: str,
        proxy_config: ProxyConfig | None = None,
    ) -> list[str]:
        body = (
            '{"pageNumber":'
            f"{page}"
            ',"keyword":"'
            f"{keyword}"
            '","fromFilter":false,"rowsPerPage":30,"sortValue":"","sortField":"","customDistance":"","gps":"","propValueStr":{},"customGps":"","searchReqFromPage":"pcSearch","extraFilterValue":"{}","userPositionJson":"{}"}'
        )
        response = self._post(
            endpoint=SEARCH_ENDPOINT,
            body=body,
            proxy_config=proxy_config,
        )
        payload = response.json().get("data", {})
        result_list = payload.get("resultList", [])
        item_ids: list[str] = []
        for item in result_list:
            item_id = (
                item.get("data", {})
                .get("item", {})
                .get("main", {})
                .get("exContent", {})
                .get("itemId")
            )
            if item_id:
                item_ids.append(item_id)
        return item_ids

    def get_item_detail(
        self,
        item_id: str,
        *,
        proxy_config: ProxyConfig | None = None,
    ) -> dict[str, Any]:
        response = self._post(
            endpoint=DETAIL_ENDPOINT,
            body=f'{{"itemId":"{item_id}"}}',
            proxy_config=proxy_config,
        )
        return response.json().get("data", {})

    def get_shop_items(
        self,
        *,
        page: int,
        user_id: str,
        proxy_config: ProxyConfig | None = None,
    ) -> list[dict[str, Any]]:
        response = self._post(
            endpoint=SHOP_LIST_ENDPOINT,
            body=(
                '{"needGroupInfo":true,"pageNumber":'
                f"{page}"
                ',"userId":"'
                f"{user_id}"
                '","pageSize":20}'
            ),
            proxy_config=proxy_config,
        )
        return response.json().get("data", {}).get("cardList", []) or []

    def get_item_specification(
        self,
        item_id: str,
        *,
        proxy_config: ProxyConfig | None = None,
    ) -> dict[str, Any]:
        response = self._post(
            endpoint=MULTI_SPEC_ENDPOINT,
            body=f'{{"itemId":"{item_id}"}}',
            proxy_config=proxy_config,
        )
        return response.json().get("data", {})

    def get_item_id_from_url(self, url: str) -> str:
        normalized_url = self._normalize_url(url)
        query = parse_qs(urlparse(normalized_url).query)
        ids = query.get("id") or []
        return ids[0] if ids else ""

    def get_user_id_from_url(
        self,
        url: str,
        *,
        proxy_config: ProxyConfig | None = None,
    ) -> str:
        normalized_url = self._normalize_url(url)
        query = parse_qs(urlparse(normalized_url).query)
        user_ids = query.get("userid") or query.get("userId") or []
        user_id = user_ids[0] if user_ids else ""
        if "==" not in user_id:
            return user_id

        response = self._post(
            endpoint=USER_HEAD_ENDPOINT,
            body=f'{{"self":false,"userId":"{user_id}"}}',
            proxy_config=proxy_config,
        )
        return (
            response.json()
            .get("data", {})
            .get("baseInfo", {})
            .get("kcUserId", user_id)
        )

    def _post(
        self,
        *,
        endpoint: EndpointSpec,
        body: str,
        proxy_config: ProxyConfig | None,
    ):
        cookies = self.cookie_provider.get_cookie_dict()
        payload = {"data": body}
        sign, timestamp = self.signer.sign(cookies, payload)
        params = self._build_params(endpoint, sign=sign, timestamp=timestamp)
        headers = MULTI_SPEC_HEADERS if endpoint == MULTI_SPEC_ENDPOINT else DEFAULT_HEADERS
        response = self.transport.request(
            "POST",
            endpoint.url,
            headers=headers,
            cookies=cookies,
            params=params,
            data=payload,
            timeout=10,
            proxy_config=proxy_config or ProxyConfig(),
        )
        self._raise_for_upstream_error(response)
        return response

    @staticmethod
    def _build_params(endpoint: EndpointSpec, *, sign: str, timestamp: int) -> dict[str, str]:
        params = {
            "jsv": JSV,
            "appKey": APP_KEY,
            "t": str(timestamp),
            "sign": sign,
            "v": endpoint.version,
            "type": "originaljson",
            "accountSite": "xianyu",
            "dataType": "json",
            "timeout": TIMEOUT,
            "api": endpoint.api,
            "sessionOption": "AutoLoginOnly",
        }
        if endpoint.spm_cnt:
            params["spm_cnt"] = endpoint.spm_cnt
        if endpoint.spm_pre:
            params["spm_pre"] = endpoint.spm_pre
        if endpoint.value_type:
            params["valueType"] = endpoint.value_type
        return params

    def _normalize_url(self, url: str) -> str:
        if "m.tb.cn" in url and self.url_expander is not None:
            expanded = self.url_expander(url)
            if expanded:
                return expanded
        return url

    @staticmethod
    def _raise_for_upstream_error(response: Any) -> None:
        payload = response.json()
        ret = payload.get("ret") or []
        ret_text = " | ".join(ret) if isinstance(ret, list) else str(ret)
        data = payload.get("data")
        login_url = ""
        if isinstance(data, dict):
            candidate = data.get("url") or data.get("h5url") or ""
            login_url = str(candidate)

        if "RGV587" in ret_text or "被挤爆" in ret_text:
            extra = f" | redirect={login_url}" if login_url else ""
            raise GoofishBurstError(f"{ret_text}{extra}")
        if "系统错误请稍候再试" in ret_text:
            raise GoofishSystemError(ret_text)
        if login_url and "passport.goofish.com" in login_url:
            raise GoofishLoginRedirectError(login_url)
