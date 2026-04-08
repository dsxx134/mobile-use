from minitap.mobile_use.collectors.xianyu_collector.domain.filter_config import FilterConfig
from minitap.mobile_use.collectors.xianyu_collector.domain.filter_engine import FilterEngine
from minitap.mobile_use.collectors.xianyu_collector.domain.item_normalizer import ItemNormalizer
from minitap.mobile_use.collectors.xianyu_collector.repository.goods_repo import GoodsRepository
from minitap.mobile_use.collectors.xianyu_collector.repository.sqlite_db import CollectorDatabase
from minitap.mobile_use.collectors.xianyu_collector.services.collector_service import CollectorService


class FakeApiClient:
    def __init__(self):
        self.keyword_calls = []
        self.manual_urls = []
        self.shop_urls = []
        self.detail_calls = []
        self.spec_calls = []

    def search_items(self, *, page, keyword, proxy_config=None):
        self.keyword_calls.append((page, keyword, proxy_config))
        if keyword == "限量耳机" and page == 1:
            return ["1001", "1002"]
        if keyword == "限量耳机" and page == 2:
            return ["1003", "1004"]
        return ["1001", "1002"]

    def get_item_detail(self, item_id, *, proxy_config=None):
        self.detail_calls.append((item_id, proxy_config))
        return {
            "itemDO": {
                "title": f"商品{item_id}",
                "desc": "desc",
                "soldPrice": "99",
                "browseCnt": "150",
                "wantCnt": "20",
                "GMT_CREATE_DATE_KEY": "2026-03-10",
                "maxPrice": "199" if item_id == "1002" else "",
                "imageInfos": [{"url": "https://img.example/a.jpg"}],
                "itemLabelExtList": [{"text": "耳机"}],
            },
            "sellerDO": {
                "sellerId": "seller-1",
                "nick": "卖家A",
                "signature": "快发货",
                "userRegDay": 40,
                "hasSoldNumInteger": 20,
            },
        }

    def get_item_specification(self, item_id, *, proxy_config=None):
        self.spec_calls.append((item_id, proxy_config))
        return {"skuSelectorVO": {"sku": [{"item_id": item_id}]}}

    def get_item_id_from_url(self, url):
        self.manual_urls.append(url)
        return "2001"

    def get_user_id_from_url(self, url, *, proxy_config=None):
        self.shop_urls.append((url, proxy_config))
        return "seller-x"

    def get_shop_items(self, *, page, user_id, proxy_config=None):
        return [
            {"itemId": "3001"},
            {"data": {"item": {"main": {"exContent": {"itemId": "3002"}}}}},
        ]


def build_service(tmp_path):
    db = CollectorDatabase(tmp_path / "collector.db")
    db.initialize()
    repo = GoodsRepository(db)
    api = FakeApiClient()
    service = CollectorService(
        api_client=api,
        goods_repo=repo,
        item_normalizer=ItemNormalizer(),
        filter_engine=FilterEngine(),
    )
    return service, api, repo


def test_collect_keyword_skips_duplicates_filters_items_and_fetches_spec_when_needed(tmp_path):
    service, api, repo = build_service(tmp_path)
    repo.insert_good({"item_id": "1001", "title": "旧商品"})

    summary = service.collect_keyword(
        keywords=["耳机"],
        pages=1,
        filter_config=FilterConfig(browse_min=100, want_min=10),
        multi_spec_enabled=True,
    )

    assert summary.discovered == 2
    assert summary.duplicates == 1
    assert summary.saved == 1
    assert summary.filtered == 0
    assert repo.list_goods_item_ids() == ["1001", "1002"]
    assert api.spec_calls == [("1002", None)]


def test_collect_manual_uses_url_parser_and_bypasses_filters_in_manual_mode(tmp_path):
    service, api, repo = build_service(tmp_path)

    summary = service.collect_manual(
        urls=["https://www.goofish.com/item?id=2001"],
        filter_config=FilterConfig(browse_min=999, excluded_words=["商品"]),
    )

    assert summary.saved == 1
    assert summary.filtered == 0
    assert api.manual_urls == ["https://www.goofish.com/item?id=2001"]
    assert repo.list_goods_item_ids() == ["2001"]


def test_collect_shop_resolves_user_id_and_collects_item_ids_from_cards(tmp_path):
    service, api, repo = build_service(tmp_path)

    summary = service.collect_shop(
        shop_urls=["https://www.goofish.com/?userId=seller-x"],
        pages=1,
        filter_config=FilterConfig(),
    )

    assert summary.saved == 2
    assert summary.discovered == 2
    assert api.shop_urls == [("https://www.goofish.com/?userId=seller-x", None)]
    assert repo.list_goods_item_ids() == ["3001", "3002"]


def test_collect_keyword_respects_per_keyword_success_limit(tmp_path):
    service, api, repo = build_service(tmp_path)

    summary = service.collect_keyword(
        keywords=["限量耳机"],
        pages=2,
        filter_config=FilterConfig(),
        per_keyword_success_limit=1,
    )

    assert summary.saved == 1
    assert summary.discovered == 1
    assert api.keyword_calls == [(1, "限量耳机", None)]
    assert repo.list_goods_item_ids() == ["1001"]


def test_collect_shop_filters_cards_by_recent_publish_preset(tmp_path):
    service, api, repo = build_service(tmp_path)
    api.get_shop_items = lambda **_kwargs: [
        {
            "cardData": {
                "detailParams": {"itemId": "3001"},
                "itemLabelDataVO": {"serviceUtParams": ["24小时内发布"]},
            }
        },
        {
            "cardData": {
                "detailParams": {"itemId": "3002"},
                "itemLabelDataVO": {"serviceUtParams": ["15天前发布"]},
            }
        },
        {
            "cardData": {
                "detailParams": {"itemId": "3003"},
                "itemLabelDataVO": {"serviceUtParams": ["72小时内发布"]},
            }
        },
    ]

    summary = service.collect_shop(
        shop_urls=["https://www.goofish.com/?userId=seller-x"],
        pages=1,
        filter_config=FilterConfig(),
        recent_publish_filter="72小时内发布",
    )

    assert summary.discovered == 2
    assert summary.saved == 2
    assert repo.list_goods_item_ids() == ["3001", "3003"]
