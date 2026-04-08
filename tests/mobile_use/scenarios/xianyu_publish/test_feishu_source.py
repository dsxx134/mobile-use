import json

import httpx

from minitap.mobile_use.scenarios.xianyu_publish.feishu_source import FeishuBitableSource
from minitap.mobile_use.scenarios.xianyu_publish.models import FeishuAttachment
from minitap.mobile_use.scenarios.xianyu_publish.settings import XianyuPublishSettings


def _make_settings(
    *,
    include_retry_fields: bool = False,
    include_publish_fields: bool = False,
) -> XianyuPublishSettings:
    return XianyuPublishSettings(
        FEISHU_APP_ID="cli_xxx",
        FEISHU_APP_SECRET="secret",
        XIANYU_BITABLE_APP_TOKEN="app_token",
        XIANYU_BITABLE_TABLE_ID="tbl_token",
        retry_count_field_name="失败重试次数" if include_retry_fields else None,
        retry_limit_field_name="失败重试上限" if include_retry_fields else None,
        allow_publish_field_name="是否允许发布" if include_publish_fields else None,
        auto_publish_field_name="允许自动发布" if include_publish_fields else None,
    )


def test_build_filter_for_pending_publishable_records():
    source = FeishuBitableSource(
        settings=_make_settings(include_retry_fields=True),
        token_provider=lambda: "tenant-token",
    )

    filter_payload = source.build_pending_filter()

    assert filter_payload["conjunction"] == "and"
    assert filter_payload["conditions"] == [
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


def test_build_filter_includes_allow_publish_when_configured():
    source = FeishuBitableSource(
        settings=_make_settings(include_publish_fields=True),
        token_provider=lambda: "tenant-token",
    )

    filter_payload = source.build_pending_filter()

    assert filter_payload["conditions"][0] == {
        "field_name": "是否允许发布",
        "operator": "is",
        "value": [True],
    }


def test_pick_first_publishable_record_maps_fields_to_listing_draft():
    source = FeishuBitableSource(
        settings=_make_settings(include_retry_fields=True, include_publish_fields=True),
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
                "闲鱼币抵扣": "30%",
                "发货方式": "包邮",
                "发货时间": "24小时发货",
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
    assert listing.coin_discount == "30%"
    assert listing.shipping_method == "包邮"
    assert listing.shipping_time == "24小时发货"
    assert listing.allow_auto_publish is True
    assert listing.retry_count == 0
    assert listing.retry_limit == 3
    assert [attachment.file_token for attachment in listing.attachments] == ["ft-1", "ft-2"]


def test_pick_first_publishable_record_skips_retry_exhausted_rows():
    source = FeishuBitableSource(
        settings=_make_settings(include_retry_fields=True),
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


def test_pick_first_publishable_record_defaults_auto_publish_when_field_missing():
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
                "商品图片": [{"file_token": "ft-1", "name": "1.jpg", "size": 111}],
            },
        }
    ]

    listing = source.pick_first_publishable_record(records)

    assert listing is not None
    assert listing.allow_auto_publish is True


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
        settings=_make_settings(include_retry_fields=True),
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
        settings=_make_settings(include_retry_fields=True),
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
        settings=_make_settings(include_retry_fields=True),
        http_client=client,
        token_provider=lambda: "tenant-token",
    )

    source.update_listing_status("recA", "准备中")

    assert captured["method"] == "PUT"
    assert captured["path"] == "/open-apis/bitable/v1/apps/app_token/tables/tbl_token/records/recA"
    assert captured["authorization"] == "Bearer tenant-token"
    assert captured["payload"] == {"fields": {"发布状态": "准备中", "日志路径": None}}


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
        settings=_make_settings(include_retry_fields=True),
        http_client=client,
        token_provider=lambda: "tenant-token",
    )

    source.update_listing_status("recA", "准备失败", failure_reason="price panel missing")

    assert captured["payload"] == {
        "fields": {
            "发布状态": "准备失败",
            "日志路径": "price panel missing",
        }
    }


def test_update_listing_status_uses_log_path_when_provided():
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["payload"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(200, json={"code": 0, "data": {"record": {"record_id": "recA"}}})

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://open.feishu.cn/open-apis",
    )
    source = FeishuBitableSource(
        settings=_make_settings(include_retry_fields=True),
        http_client=client,
        token_provider=lambda: "tenant-token",
    )

    source.update_listing_status(
        "recA",
        "准备失败",
        failure_reason="price panel missing",
        log_path="D:\\logs\\recA\\prepare.log",
    )

    assert captured["payload"] == {
        "fields": {
            "发布状态": "准备失败",
            "日志路径": "D:\\logs\\recA\\prepare.log",
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
        settings=_make_settings(include_retry_fields=True),
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
            "日志路径": "price panel missing",
            "失败重试次数": 2,
        }
    }


def test_update_listing_status_can_write_location_search_query():
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["payload"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(200, json={"code": 0, "data": {"record": {"record_id": "recA"}}})

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://open.feishu.cn/open-apis",
    )
    source = FeishuBitableSource(
        settings=_make_settings(include_retry_fields=True),
        http_client=client,
        token_provider=lambda: "tenant-token",
    )

    source.update_listing_status(
        "recA",
        "已就绪",
        failure_reason=None,
        location_search_query="上海虹桥站 新虹街道申贵路1500号",
    )

    assert captured["payload"] == {
        "fields": {
            "发布状态": "已就绪",
            "日志路径": None,
            "预设地址": "上海虹桥站 新虹街道申贵路1500号",
        }
    }


def test_update_listing_status_ignores_failure_artifact_fields():
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["payload"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(200, json={"code": 0, "data": {"record": {"record_id": "recA"}}})

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://open.feishu.cn/open-apis",
    )
    source = FeishuBitableSource(
        settings=_make_settings(include_retry_fields=True),
        http_client=client,
        token_provider=lambda: "tenant-token",
    )

    source.update_listing_status(
        "recA",
        "准备失败",
        failure_reason="price panel missing",
        failure_captured_at="2026-03-15T12:00:00+08:00",
        failure_screenshot_path="D:\\debug\\recA\\screen.png",
        failure_hierarchy_path="D:\\debug\\recA\\hierarchy.xml",
        failure_activity_dump_path="D:\\debug\\recA\\activities.txt",
        failure_current_app="com.taobao.idlefish/com.taobao.idlefish.maincontainer.activity.MainActivity",
    )

    assert captured["payload"] == {
        "fields": {
            "发布状态": "准备失败",
            "日志路径": "price panel missing",
        }
    }


def test_update_listing_status_can_write_batch_run_fields():
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["payload"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(200, json={"code": 0, "data": {"record": {"record_id": "recA"}}})

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://open.feishu.cn/open-apis",
    )
    source = FeishuBitableSource(
        settings=_make_settings(include_retry_fields=True),
        http_client=client,
        token_provider=lambda: "tenant-token",
    )

    source.update_listing_status(
        "recA",
        "准备中",
        batch_run_id="batch-001",
        batch_ran_at="2026-03-15T09:00:00+08:00",
    )

    assert captured["payload"] == {
        "fields": {
            "发布状态": "准备中",
            "日志路径": None,
            "最近批次运行ID": "batch-001",
            "最近批次运行时间": "2026-03-15T09:00:00+08:00",
            "最近批次运行结果": "准备中",
        }
    }


def test_update_listing_status_retries_when_batch_fields_missing():
    captured: dict[str, object] = {"put_payloads": []}
    put_calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal put_calls
        if request.method == "PUT":
            payload = json.loads(request.content.decode("utf-8"))
            captured["put_payloads"].append(payload)
            put_calls += 1
            if put_calls == 1:
                return httpx.Response(200, json={"code": 1254040, "msg": "FieldNameNotFound"})
            return httpx.Response(
                200,
                json={"code": 0, "data": {"record": {"record_id": "recA"}}},
            )
        if request.method == "GET" and request.url.path.endswith("/fields"):
            return httpx.Response(
                200,
                json={
                    "code": 0,
                    "data": {
                        "items": [
                            {"field_name": "发布状态", "is_primary": False},
                            {"field_name": "日志路径", "is_primary": False},
                        ],
                        "has_more": False,
                    },
                },
            )
        return httpx.Response(500, json={"code": 500, "msg": "unexpected"})

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://open.feishu.cn/open-apis",
    )
    source = FeishuBitableSource(
        settings=_make_settings(include_retry_fields=True),
        http_client=client,
        token_provider=lambda: "tenant-token",
    )

    source.update_listing_status(
        "recA",
        "准备中",
        batch_run_id="batch-001",
        batch_ran_at="2026-03-15T09:00:00+08:00",
    )

    assert len(captured["put_payloads"]) == 2
    assert captured["put_payloads"][-1] == {
        "fields": {
            "发布状态": "准备中",
            "日志路径": None,
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
        settings=_make_settings(include_retry_fields=True),
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
            "日志路径": None,
            "发布时间": "2026-03-14T20:15:00+08:00",
            "闲鱼商品ID": "xy123",
            "闲鱼商品链接": {
                "text": "https://2.taobao.com/item.htm?id=xy123",
                "link": "https://2.taobao.com/item.htm?id=xy123",
            },
        }
    }


def test_update_publish_result_uses_log_path_when_provided():
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["payload"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(200, json={"code": 0, "data": {"record": {"record_id": "recA"}}})

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://open.feishu.cn/open-apis",
    )
    source = FeishuBitableSource(
        settings=_make_settings(include_retry_fields=True),
        http_client=client,
        token_provider=lambda: "tenant-token",
    )

    source.update_publish_result(
        "recA",
        status="发布失败",
        failure_reason="location missing",
        published_at=None,
        listing_id=None,
        listing_url=None,
        log_path="D:\\logs\\recA\\publish.log",
    )

    assert captured["payload"] == {
        "fields": {
            "发布状态": "发布失败",
            "日志路径": "D:\\logs\\recA\\publish.log",
            "发布时间": None,
            "闲鱼商品ID": None,
            "闲鱼商品链接": None,
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
        settings=_make_settings(include_retry_fields=True),
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
            "日志路径": "location missing",
            "发布时间": None,
            "闲鱼商品ID": None,
            "闲鱼商品链接": None,
            "失败重试次数": 3,
        }
    }


def test_update_publish_result_can_write_batch_run_fields():
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["payload"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(200, json={"code": 0, "data": {"record": {"record_id": "recA"}}})

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://open.feishu.cn/open-apis",
    )
    source = FeishuBitableSource(
        settings=_make_settings(include_retry_fields=True),
        http_client=client,
        token_provider=lambda: "tenant-token",
    )

    source.update_publish_result(
        "recA",
        status="已发布",
        published_at="2026-03-15T09:05:00+08:00",
        listing_id="xy123",
        batch_run_id="batch-001",
        batch_ran_at="2026-03-15T09:00:00+08:00",
    )

    assert captured["payload"] == {
        "fields": {
            "发布状态": "已发布",
            "日志路径": None,
            "发布时间": "2026-03-15T09:05:00+08:00",
            "闲鱼商品ID": "xy123",
            "闲鱼商品链接": None,
            "最近批次运行ID": "batch-001",
            "最近批次运行时间": "2026-03-15T09:00:00+08:00",
            "最近批次运行结果": "已发布",
        }
    }


def test_update_publish_result_ignores_failure_artifact_fields():
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["payload"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(200, json={"code": 0, "data": {"record": {"record_id": "recA"}}})

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://open.feishu.cn/open-apis",
    )
    source = FeishuBitableSource(
        settings=_make_settings(include_retry_fields=True),
        http_client=client,
        token_provider=lambda: "tenant-token",
    )

    source.update_publish_result(
        "recA",
        status="发布失败",
        failure_reason="Publish did not reach success screen: metadata_panel",
        published_at=None,
        listing_id=None,
        listing_url=None,
        retry_count=2,
        failure_captured_at="2026-03-15T12:30:00+08:00",
        failure_screenshot_path="D:\\debug\\recA\\publish\\screen.png",
        failure_hierarchy_path="D:\\debug\\recA\\publish\\hierarchy.xml",
        failure_activity_dump_path="D:\\debug\\recA\\publish\\activities.txt",
        failure_current_app="com.taobao.idlefish/com.taobao.idlefish.publish.PublishActivity",
    )

    assert captured["payload"] == {
        "fields": {
            "发布状态": "发布失败",
            "日志路径": "Publish did not reach success screen: metadata_panel",
            "发布时间": None,
            "闲鱼商品ID": None,
            "闲鱼商品链接": None,
            "失败重试次数": 2,
        }
    }


def test_write_batch_run_summary_creates_record_in_summary_table():
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET" and request.url.path.endswith("/tables"):
            captured["list_tables_params"] = dict(request.url.params)
            return httpx.Response(
                200,
                json={
                    "code": 0,
                    "data": {
                        "items": [
                            {"table_id": "tbl_main", "name": "闲鱼自动发布联调"},
                            {"table_id": "tbl_summary", "name": "批次运行汇总"},
                        ],
                        "has_more": False,
                    },
                },
            )
        if request.method == "GET" and request.url.path.endswith("/fields"):
            captured["list_fields_params"] = dict(request.url.params)
            return httpx.Response(
                200,
                json={
                    "code": 0,
                    "data": {
                        "items": [
                            {"field_name": "多行文本", "is_primary": True},
                            {"field_name": "批次运行ID", "is_primary": False},
                        ],
                        "has_more": False,
                    },
                },
            )

        captured["create_method"] = request.method
        captured["create_path"] = request.url.path
        captured["create_payload"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(
            200,
            json={"code": 0, "data": {"record": {"record_id": "recSummary"}}},
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

    source.write_batch_run_summary(
        batch_run_id="batch-001",
        batch_ran_at="2026-03-15T09:00:00+08:00",
        requested_count=3,
        processed_count=2,
        success_count=1,
        failure_count=1,
        stopped_reason="no_publishable_listing",
        items=[
            {"record_id": "recA", "success": False, "error": "Publish blocked"},
            {"record_id": "recB", "success": True, "listing_id": "xyB"},
        ],
    )

    assert captured["list_tables_params"] == {"page_size": "100"}
    assert captured["list_fields_params"] == {"page_size": "100"}
    assert captured["create_method"] == "POST"
    assert (
        captured["create_path"]
        == "/open-apis/bitable/v1/apps/app_token/tables/tbl_summary/records"
    )
    assert captured["create_payload"] == {
        "fields": {
            "多行文本": "batch-001",
            "批次运行ID": "batch-001",
            "批次运行时间": "2026-03-15T09:00:00+08:00",
            "请求条数": 3,
            "处理条数": 2,
            "成功条数": 1,
            "失败条数": 1,
            "停止原因": "no_publishable_listing",
            "批次明细": (
                "1. recA | 失败 | 原因: Publish blocked\n"
                "2. recB | 成功 | 商品ID: xyB"
            ),
        }
    }


def test_write_batch_run_summary_uses_empty_state_text_when_no_items():
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET" and request.url.path.endswith("/tables"):
            return httpx.Response(
                200,
                json={
                    "code": 0,
                    "data": {
                        "items": [{"table_id": "tbl_summary", "name": "批次运行汇总"}],
                        "has_more": False,
                    },
                },
            )
        if request.method == "GET" and request.url.path.endswith("/fields"):
            return httpx.Response(
                200,
                json={
                    "code": 0,
                    "data": {
                        "items": [{"field_name": "多行文本", "is_primary": True}],
                        "has_more": False,
                    },
                },
            )

        captured["create_payload"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(
            200,
            json={"code": 0, "data": {"record": {"record_id": "recSummary"}}},
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

    source.write_batch_run_summary(
        batch_run_id="batch-empty",
        batch_ran_at="2026-03-15T10:00:00+08:00",
        requested_count=1,
        processed_count=0,
        success_count=0,
        failure_count=0,
        stopped_reason="no_publishable_listing",
        items=[],
    )

    assert captured["create_payload"] == {
        "fields": {
            "多行文本": "batch-empty",
            "批次运行ID": "batch-empty",
            "批次运行时间": "2026-03-15T10:00:00+08:00",
            "请求条数": 1,
            "处理条数": 0,
            "成功条数": 0,
            "失败条数": 0,
            "停止原因": "no_publishable_listing",
            "批次明细": "本批次没有处理任何记录。",
        }
    }
