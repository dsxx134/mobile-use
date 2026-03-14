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
            "value": [],
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
                "允许自动发布": True,
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
    assert listing.allow_auto_publish is True
    assert listing.retry_count == 0
    assert listing.retry_limit == 3
    assert [attachment.file_token for attachment in listing.attachments] == ["ft-1", "ft-2"]


def test_pick_first_publishable_record_skips_retry_exhausted_rows():
    source = FeishuBitableSource(
        settings=_make_settings(),
        token_provider=lambda: "tenant-token",
    )
    records = [
        {
            "record_id": "recA",
            "fields": {
                "商品标题": "旧记录",
                "商品描述": "会被跳过",
                "售价": 99,
                "失败重试次数": 3,
                "失败重试上限": 3,
                "商品图片": [{"file_token": "ft-exhausted", "name": "a.jpg"}],
            },
        },
        {
            "record_id": "recB",
            "fields": {
                "商品标题": "新记录",
                "商品描述": "应该被选中",
                "售价": 188,
                "失败重试次数": 1,
                "失败重试上限": 3,
                "商品图片": [{"file_token": "ft-ready", "name": "b.jpg"}],
            },
        },
    ]

    listing = source.pick_first_publishable_record(records)

    assert listing is not None
    assert listing.record_id == "recB"
    assert listing.retry_count == 1
    assert listing.retry_limit == 3


def test_pick_first_publishable_record_extracts_text_from_feishu_text_arrays():
    source = FeishuBitableSource(
        settings=_make_settings(),
        token_provider=lambda: "tenant-token",
    )
    records = [
        {
            "record_id": "recA",
            "fields": {
                "商品标题": [{"text": "34寸显示器", "type": "text"}],
                "商品描述": [{"text": "成色很好，北京自提。", "type": "text"}],
                "售价": 799,
                "分类": [{"text": "生活百科", "type": "text"}],
                "成色": [{"text": "几乎全新", "type": "text"}],
                "商品来源": [{"text": "闲置", "type": "text"}],
                "预设地址": [{"text": "上海虹桥站", "type": "text"}],
                "商品图片": [
                    {
                        "file_token": "ft-1",
                        "name": "image.png",
                        "size": 1328,
                        "url": "https://open.feishu.cn/open-apis/drive/v1/medias/ft-1/download",
                    }
                ],
            },
        }
    ]

    listing = source.pick_first_publishable_record(records)

    assert listing is not None
    assert listing.title == "34寸显示器"
    assert listing.description == "成色很好，北京自提。"
    assert listing.category == "生活百科"
    assert listing.condition == "几乎全新"
    assert listing.item_source == "闲置"
    assert listing.location_search_query == "上海虹桥站"


def test_get_attachment_download_urls_prefers_attachment_urls_in_order():
    source = FeishuBitableSource(
        settings=_make_settings(),
        token_provider=lambda: "tenant-token",
    )

    result = source.get_attachment_download_urls(
        [
            FeishuAttachment(
                file_token="ft-1",
                name="1.jpg",
                url="https://open.feishu.cn/open-apis/drive/v1/medias/ft-1/download",
            ),
            FeishuAttachment(
                file_token="ft-2",
                name="2.jpg",
                url="https://open.feishu.cn/open-apis/drive/v1/medias/ft-2/download",
            ),
        ]
    )

    assert list(result.keys()) == ["ft-1", "ft-2"]
    assert result["ft-1"] == "https://open.feishu.cn/open-apis/drive/v1/medias/ft-1/download"
    assert result["ft-2"] == "https://open.feishu.cn/open-apis/drive/v1/medias/ft-2/download"


def test_download_attachment_file_uses_bearer_token(tmp_path):
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["method"] = request.method
        captured["path"] = request.url.path
        captured["authorization"] = request.headers["Authorization"]
        return httpx.Response(200, content=b"image-bytes", headers={"content-type": "image/png"})

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://open.feishu.cn/open-apis",
    )
    source = FeishuBitableSource(
        settings=_make_settings(),
        http_client=client,
        token_provider=lambda: "tenant-token",
    )
    destination = tmp_path / "image.png"

    source.download_attachment_file(
        "https://open.feishu.cn/open-apis/drive/v1/medias/ft-1/download",
        destination,
    )

    assert captured["method"] == "GET"
    assert captured["path"] == "/open-apis/drive/v1/medias/ft-1/download"
    assert captured["authorization"] == "Bearer tenant-token"
    assert destination.read_bytes() == b"image-bytes"


def test_list_candidate_records_uses_search_endpoint_with_filter_body():
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["method"] = request.method
        captured["path"] = request.url.path
        captured["authorization"] = request.headers["Authorization"]
        captured["payload"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(
            200,
            json={
                "code": 0,
                "data": {
                    "items": [{"record_id": "recA", "fields": {}}],
                    "has_more": False,
                    "total": 1,
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

    records = source.list_candidate_records()

    assert records == [{"record_id": "recA", "fields": {}}]
    assert captured["method"] == "POST"
    assert (
        captured["path"]
        == "/open-apis/bitable/v1/apps/app_token/tables/tbl_token/records/search"
    )
    assert captured["authorization"] == "Bearer tenant-token"
    assert captured["payload"] == {
        "page_size": 100,
        "filter": source.build_pending_filter(),
    }


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


def test_update_listing_status_can_write_retry_count():
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

    source.update_listing_status(
        "recA",
        "准备失败",
        failure_reason="price panel missing",
        retry_count=2,
    )

    assert captured["payload"] == {
        "fields": {
            "发布状态": "准备失败",
            "失败原因": "price panel missing",
            "失败重试次数": 2,
        }
    }


def test_update_publish_result_can_write_published_at_and_optional_fields():
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

    source.update_publish_result(
        "recA",
        status="已发布",
        published_at="2026-03-14T20:15:00+08:00",
        listing_id="xy123",
        listing_url="https://2.taobao.com/item.htm?id=xy123",
    )

    assert captured["payload"] == {
        "fields": {
            "发布状态": "已发布",
            "失败原因": None,
            "发布时间": "2026-03-14T20:15:00+08:00",
            "闲鱼商品ID": "xy123",
            "闲鱼商品链接": {
                "text": "https://2.taobao.com/item.htm?id=xy123",
                "link": "https://2.taobao.com/item.htm?id=xy123",
            },
        }
    }


def test_update_publish_result_can_write_retry_count():
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

    source.update_publish_result(
        "recA",
        status="发布失败",
        failure_reason="location missing",
        retry_count=3,
    )

    assert captured["payload"] == {
        "fields": {
            "发布状态": "发布失败",
            "失败原因": "location missing",
            "发布时间": None,
            "闲鱼商品ID": None,
            "闲鱼商品链接": None,
            "失败重试次数": 3,
        }
    }
