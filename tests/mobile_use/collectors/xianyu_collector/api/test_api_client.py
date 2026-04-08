import pytest

from minitap.mobile_use.collectors.xianyu_collector.api.client import (
    GoofishApiClient,
    GoofishBurstError,
    GoofishLoginRedirectError,
    GoofishSystemError,
)
from minitap.mobile_use.collectors.xianyu_collector.session.saved_cookie_provider import SavedCookieProvider
from minitap.mobile_use.collectors.xianyu_collector.signing.mtop_signer import MtopSigner
from minitap.mobile_use.collectors.xianyu_collector.transport.proxy_config import ProxyConfig


class FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code

    def json(self) -> dict:
        return self._payload


class RecordingTransport:
    def __init__(self, response: FakeResponse):
        self.response = response
        self.calls = []

    def request(self, method: str, url: str, **kwargs):
        self.calls.append((method, url, kwargs))
        return self.response


def build_client(response_payload: dict) -> tuple[GoofishApiClient, RecordingTransport]:
    transport = RecordingTransport(FakeResponse(response_payload))
    cookie_provider = SavedCookieProvider(
        "_m_h5_tk=abc123_999999; _m_h5_tk_enc=enc999; cna=cna-token"
    )
    signer = MtopSigner(time_provider=lambda: 1710000000.123)
    client = GoofishApiClient(
        transport=transport,
        cookie_provider=cookie_provider,
        signer=signer,
    )
    return client, transport


def test_search_items_builds_signed_request_and_extracts_item_ids():
    client, transport = build_client(
        {
            "data": {
                "resultList": [
                    {"data": {"item": {"main": {"exContent": {"itemId": "111"}}}}},
                    {"data": {"item": {"main": {"exContent": {"itemId": "222"}}}}},
                ]
            }
        }
    )

    item_ids = client.search_items(
        page=2,
        keyword="耳机",
        proxy_config=ProxyConfig(is_open_proxy=True, proxy_url="http://proxy-source"),
    )

    assert item_ids == ["111", "222"]
    method, url, kwargs = transport.calls[0]
    assert method == "POST"
    assert url == "https://h5api.m.goofish.com/h5/mtop.taobao.idlemtopsearch.pc.search/1.0/"
    assert kwargs["proxy_config"] == ProxyConfig(
        is_open_proxy=True,
        proxy_url="http://proxy-source",
    )
    assert kwargs["cookies"]["_m_h5_tk"] == "abc123_999999"
    assert kwargs["params"]["api"] == "mtop.taobao.idlemtopsearch.pc.search"
    assert kwargs["params"]["v"] == "1.0"
    assert kwargs["params"]["sign"] == "72b0040a60bf6bf6a7a33c43597b4acc"
    assert kwargs["params"]["t"] == "1710000000123"
    assert kwargs["data"]["data"] == (
        '{"pageNumber":2,"keyword":"耳机","fromFilter":false,"rowsPerPage":30,'
        '"sortValue":"","sortField":"","customDistance":"","gps":"","propValueStr":{},'
        '"customGps":"","searchReqFromPage":"pcSearch","extraFilterValue":"{}",'
        '"userPositionJson":"{}"}'
    )


def test_get_item_detail_builds_item_request_and_returns_data_payload():
    client, transport = build_client({"data": {"itemDO": {"itemId": "555"}}})

    payload = client.get_item_detail("555")

    assert payload == {"itemDO": {"itemId": "555"}}
    _method, url, kwargs = transport.calls[0]
    assert url == "https://h5api.m.goofish.com/h5/mtop.taobao.idle.pc.detail/1.0/"
    assert kwargs["params"]["api"] == "mtop.taobao.idle.pc.detail"
    assert kwargs["params"]["v"] == "1.0"
    assert kwargs["data"]["data"] == '{"itemId":"555"}'


def test_get_shop_items_builds_shop_request_and_returns_card_list():
    client, transport = build_client({"data": {"cardList": [{"id": 1}, {"id": 2}]}})

    cards = client.get_shop_items(page=3, user_id="user-1")

    assert cards == [{"id": 1}, {"id": 2}]
    _method, url, kwargs = transport.calls[0]
    assert url == "https://h5api.m.goofish.com/h5/mtop.idle.web.xyh.item.list/1.0/"
    assert kwargs["params"]["api"] == "mtop.idle.web.xyh.item.list"
    assert kwargs["data"]["data"] == '{"needGroupInfo":true,"pageNumber":3,"userId":"user-1","pageSize":20}'


def test_get_item_specification_uses_saved_cookie_provider_and_render_endpoint():
    client, transport = build_client({"data": {"skuSelectorVO": {"sku": []}}})

    payload = client.get_item_specification("sku-1")

    assert payload == {"skuSelectorVO": {"sku": []}}
    _method, url, kwargs = transport.calls[0]
    assert url == "https://h5api.m.goofish.com/h5/mtop.taobao.idle.trade.order.render/7.0/"
    assert kwargs["params"]["api"] == "mtop.taobao.idle.trade.order.render"
    assert kwargs["params"]["v"] == "7.0"
    assert kwargs["params"]["valueType"] == "string"
    assert kwargs["data"]["data"] == '{"itemId":"sku-1"}'


def test_get_item_id_from_goofish_url_extracts_id_query_param():
    client, _transport = build_client({"data": {}})

    assert (
        client.get_item_id_from_url("https://www.goofish.com/item?id=9988&foo=bar")
        == "9988"
    )


def test_get_user_id_from_url_resolves_encoded_user_id_via_user_head_endpoint():
    client, transport = build_client({"data": {"baseInfo": {"kcUserId": "user-real"}}})

    user_id = client.get_user_id_from_url("https://www.goofish.com/?userId=abc%3D%3D")

    assert user_id == "user-real"
    _method, url, kwargs = transport.calls[0]
    assert url == "https://h5api.m.goofish.com/h5/mtop.idle.web.user.page.head/1.0/"
    assert kwargs["data"]["data"] == '{"self":false,"userId":"abc=="}'


def test_search_items_raises_burst_error_when_ret_contains_rgv587():
    client, _transport = build_client(
        {
            "ret": ["RGV587_ERROR::SM::哎哟喂,被挤爆啦,请稍后重试!"],
            "data": {
                "url": "https://passport.goofish.com/mini_login.htm?foo=bar",
            },
        }
    )

    with pytest.raises(GoofishBurstError, match="RGV587_ERROR::SM"):
        client.search_items(page=1, keyword="gemini")


def test_search_items_raises_login_redirect_error_when_payload_points_to_passport():
    client, _transport = build_client(
        {
            "ret": [],
            "data": {
                "url": "https://passport.goofish.com/mini_login.htm?foo=bar",
            },
        }
    )

    with pytest.raises(GoofishLoginRedirectError, match="passport.goofish.com"):
        client.search_items(page=1, keyword="gemini")


def test_get_item_detail_raises_system_error_when_ret_contains_retryable_system_error():
    client, _transport = build_client(
        {
            "ret": ["FAIL_SYS::系统错误请稍候再试"],
            "data": {},
        }
    )

    with pytest.raises(GoofishSystemError, match="系统错误请稍候再试"):
        client.get_item_detail("555")
