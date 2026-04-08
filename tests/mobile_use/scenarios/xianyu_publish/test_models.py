import pytest

from minitap.mobile_use.scenarios.xianyu_publish.models import FeishuAttachment, ListingDraft


def test_listing_draft_requires_at_least_one_attachment():
    with pytest.raises(ValueError, match="at least one attachment"):
        ListingDraft(
            record_id="rec1",
            title="二手显示器",
            description="成色很好",
            price=199.0,
            attachments=[],
        )


def test_listing_draft_defaults_local_image_paths_and_keeps_attachment_metadata():
    attachment = FeishuAttachment(
        file_token="file-token-1",
        name="item-1.jpg",
        size=12345,
    )

    draft = ListingDraft(
        record_id="rec1",
        title="二手显示器",
        description="成色很好",
        price=199.0,
        attachments=[attachment],
    )

    assert draft.attachments[0].file_token == "file-token-1"
    assert draft.attachments[0].name == "item-1.jpg"
    assert draft.attachments[0].size == 12345
    assert draft.local_image_paths == []
    assert draft.category is None
    assert draft.condition is None
    assert draft.item_source is None


def test_listing_draft_accepts_optional_metadata_fields():
    draft = ListingDraft(
        record_id="rec1",
        title="二手显示器",
        description="成色很好",
        price=199.0,
        attachments=[FeishuAttachment(file_token="file-token-1", name="item-1.jpg")],
        category="家居摆件",
        condition="几乎全新",
        item_source="闲置",
        location_search_query="上海虹桥站",
        coin_discount="30%",
        shipping_method="包邮",
        shipping_time="24小时发货",
    )

    assert draft.category == "家居摆件"
    assert draft.condition == "几乎全新"
    assert draft.item_source == "闲置"
    assert draft.location_search_query == "上海虹桥站"
    assert draft.coin_discount == "30%"
    assert draft.shipping_method == "包邮"
    assert draft.shipping_time == "24小时发货"
