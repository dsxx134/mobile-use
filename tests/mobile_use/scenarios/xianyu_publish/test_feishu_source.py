import json

import httpx

from minitap.mobile_use.scenarios.xianyu_publish.feishu_source import FeishuBitableSource
from minitap.mobile_use.scenarios.xianyu_publish.models import FeishuAttachment
from minitap.mobile_use.scenarios.xianyu_publish.settings import XianyuPublishSettings


def _make_settings() -> XianyuPublishSettings:
    return XianyuPublishSettings(
        FEISHU_APP_ID="cli_xxx",
        FEISHU_APP_SECRET="secret",
        XIANYU_BITABLE_APP_TOKEN="app_token",
        XIANYU_BITABLE_TABLE_ID="tbl_token",
    )


def test_build_filter_for_pending_publishable_records():
    source = FeishuBitableSource(
        settings=_make_settings(),
        token_provider=lambda: "tenant-token",
    )

    filter_payload = source.build_pending_filter()

    assert filter_payload["conjunction"] == "and"
    assert filter_payload["conditions"] == [
        {
            "field_name": "是否允许发布",
            "operator": "is",
            "value": [True],
        },
        {
            "field_name": "发布状态",
            "operator": "is",
            "value": ["待发布"],
        },
        {
            "field_name": "商品图片",
            "operator": "isNotEmpty",
        },
    ]


def test_pick_first_publishable_record_maps_fields_to_listing_draft():
    source = FeishuBitableSource(
        settings=_make_settings(),
        token_provider=lambda: "tenant-token",
    )
    records = [
        {
            "record_id": "recA",
            "fields": {
                "商品标题": "二手显示器",
                "商品描述": "成色很好",
                "售价": 199,
                "分类": "家居摆件",
                "成色": "几乎全新",
                "商品来源": "闲置",
                "预设地址": "上海虹桥站",
                "商品图片": [
                    {"file_token": "ft-1", "name": "1.jpg", "size": 111},
                    {"file_token": "ft-2", "name": "2.jpg", "size": 222},
                ],
            },
        }
    ]

    listing = source.pick_first_publishable_record(records)

    assert listing is not None
    assert listing.record_id == "recA"
    assert listing.title == "二手显示器"
    assert listing.description == "成色很好"
    assert listing.price == 199.0
    assert listing.category == "家居摆件"
    assert listing.condition == "几乎全新"
    assert listing.item_source == "闲置"
    assert listing.location_search_query == "上海虹桥站"
    assert [attachment.file_token for attachment in listing.attachments] == ["ft-1", "ft-2"]


def test_get_attachment_download_urls_uses_file_tokens_in_order():
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        captured["authorization"] = request.headers["Authorization"]
        captured["payload"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(
            200,
            json={
                "code": 0,
                "data": {
                    "tmp_download_urls": [
                        {
                            "file_token": "ft-1",
                            "tmp_download_url": "https://files.example/1.jpg",
                        },
                        {
                            "file_token": "ft-2",
                            "tmp_download_url": "https://files.example/2.jpg",
                        },
                    ]
                },
            },
        )

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://open.feishu.cn/open-apis",
    )
    source = FeishuBitableSource(
        settings=_make_settings(),
        http_client=client,
        token_provider=lambda: "tenant-token",
    )

    result = source.get_attachment_download_urls(
        [
            FeishuAttachment(file_token="ft-1", name="1.jpg"),
            FeishuAttachment(file_token="ft-2", name="2.jpg"),
        ]
    )

    assert captured["path"] == "/open-apis/drive/v1/medias/batch_get_tmp_download_url"
    assert captured["authorization"] == "Bearer tenant-token"
    assert captured["payload"] == {"file_tokens": ["ft-1", "ft-2"]}
    assert list(result.keys()) == ["ft-1", "ft-2"]
    assert result["ft-1"] == "https://files.example/1.jpg"


def test_update_listing_status_writes_status_field():
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["method"] = request.method
        captured["path"] = request.url.path
        captured["authorization"] = request.headers["Authorization"]
        captured["payload"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(200, json={"code": 0, "data": {"record": {"record_id": "recA"}}})

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://open.feishu.cn/open-apis",
    )
    source = FeishuBitableSource(
        settings=_make_settings(),
        http_client=client,
        token_provider=lambda: "tenant-token",
    )

    source.update_listing_status("recA", "准备中")

    assert captured["method"] == "PUT"
    assert captured["path"] == "/open-apis/bitable/v1/apps/app_token/tables/tbl_token/records/recA"
    assert captured["authorization"] == "Bearer tenant-token"
    assert captured["payload"] == {"fields": {"发布状态": "准备中", "失败原因": None}}


def test_update_listing_status_can_write_failure_reason():
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["payload"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(200, json={"code": 0, "data": {"record": {"record_id": "recA"}}})

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://open.feishu.cn/open-apis",
    )
    source = FeishuBitableSource(
        settings=_make_settings(),
        http_client=client,
        token_provider=lambda: "tenant-token",
    )

    source.update_listing_status("recA", "准备失败", failure_reason="price panel missing")

    assert captured["payload"] == {
        "fields": {
            "发布状态": "准备失败",
            "失败原因": "price panel missing",
        }
    }
