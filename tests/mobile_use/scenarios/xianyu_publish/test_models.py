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
