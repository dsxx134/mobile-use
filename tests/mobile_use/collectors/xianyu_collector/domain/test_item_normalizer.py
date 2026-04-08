from minitap.mobile_use.collectors.xianyu_collector.domain.item_normalizer import ItemNormalizer


def test_normalize_detail_maps_raw_item_and_seller_fields_to_canonical_shape():
    normalizer = ItemNormalizer()

    normalized = normalizer.normalize_detail(
        item_id="555",
        detail_payload={
            "itemDO": {
                "title": "蓝牙耳机",
                "desc": "成色很好",
                "soldPrice": "99.5",
                "browseCnt": "150",
                "wantCnt": "12",
                "GMT_CREATE_DATE_KEY": "2026-03-10",
                "maxPrice": "199",
                "imageInfos": [
                    {"url": "https://img1.example/a.jpg"},
                    {"url": "https://img2.example/b.jpg"},
                ],
                "itemLabelExtList": [{"text": "耳机"}],
                "promotionPriceDO": {
                    "promotionName": "小刀可刀",
                    "promotionPriceMin": "88",
                },
            },
            "sellerDO": {
                "sellerId": "seller-1",
                "nick": "卖家A",
                "signature": "秒回",
                "userRegDay": 40,
                "hasSoldNumInteger": 20,
            },
        },
        specification_payload={"skuSelectorVO": {"sku": []}},
    )

    assert normalized == {
        "item_id": "555",
        "item_url": "https://www.goofish.com/item?id=555",
        "item_images": "https://img1.example/a.jpg_790x10000Q90.jpg_.webp,https://img2.example/b.jpg_790x10000Q90.jpg_.webp,",
        "title": "蓝牙耳机",
        "desc": "成色很好",
        "soldPrice": "99.5",
        "browseCnt": "150",
        "wantCnt": "12",
        "goodName": "耳机",
        "create_date": "2026-03-10",
        "sellerId": "seller-1",
        "nick": "卖家A",
        "signature": "秒回",
        "avgReply30dLong": 0.5,
        "knife_price": "88",
        "maxPrice": "199",
        "hasSoldNumInteger": 20,
        "userRegDay": 40,
        "specification": {"skuSelectorVO": {"sku": []}},
        "data_sources": "采集导入",
    }


def test_normalize_detail_accepts_already_canonical_payload():
    normalizer = ItemNormalizer()

    normalized = normalizer.normalize_detail(
        item_id="777",
        detail_payload={
            "item_id": "777",
            "title": "现成字典",
            "browseCnt": "10",
            "wantCnt": "2",
        },
    )

    assert normalized["item_id"] == "777"
    assert normalized["title"] == "现成字典"
    assert normalized["data_sources"] == "采集导入"
