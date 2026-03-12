from pathlib import Path
from unittest.mock import Mock, call

from minitap.mobile_use.scenarios.xianyu_publish.media_sync import XianyuMediaSyncService
from minitap.mobile_use.scenarios.xianyu_publish.models import FeishuAttachment, ListingDraft
from minitap.mobile_use.scenarios.xianyu_publish.settings import XianyuPublishSettings


def _make_settings() -> XianyuPublishSettings:
    return XianyuPublishSettings(
        XIANYU_ANDROID_MEDIA_DIR="/sdcard/DCIM/XianyuPublish",
    )


def _make_listing() -> ListingDraft:
    return ListingDraft(
        record_id="recA",
        title="二手显示器",
        description="成色很好",
        price=199.0,
        attachments=[
            FeishuAttachment(file_token="ft-1", name="1.jpg"),
            FeishuAttachment(file_token="ft-2", name="2.jpg"),
        ],
    )


def test_download_attachments_writes_files_into_listing_staging_dir(tmp_path):
    downloaded_urls: list[tuple[str, str]] = []

    def fake_download(url: str, destination: Path) -> None:
        downloaded_urls.append((url, destination.name))
        destination.write_bytes(url.encode("utf-8"))

    service = XianyuMediaSyncService(
        settings=_make_settings(),
        adb_client=Mock(),
        download_file=fake_download,
    )
    listing = _make_listing()

    result = service.download_listing_media(
        listing,
        download_urls={
            "ft-1": "https://files.example/1.jpg",
            "ft-2": "https://files.example/2.jpg",
        },
        staging_root=tmp_path,
    )

    assert [path.parent.name for path in result.local_image_paths] == ["recA", "recA"]
    assert [path.name for path in result.local_image_paths] == ["01_1.jpg", "02_2.jpg"]
    assert result.local_image_paths[0].read_bytes() == b"https://files.example/1.jpg"
    assert downloaded_urls == [
        ("https://files.example/1.jpg", "01_1.jpg"),
        ("https://files.example/2.jpg", "02_2.jpg"),
    ]


def test_push_listing_media_uses_device_sync_push_for_each_file(tmp_path):
    adb_client = Mock()
    device = Mock()
    adb_client.device.return_value = device
    service = XianyuMediaSyncService(
        settings=_make_settings(),
        adb_client=adb_client,
        download_file=Mock(),
    )
    first = tmp_path / "recA" / "01_1.jpg"
    second = tmp_path / "recA" / "02_2.jpg"
    first.parent.mkdir(parents=True, exist_ok=True)
    first.write_bytes(b"1")
    second.write_bytes(b"2")
    listing = _make_listing().model_copy(update={"local_image_paths": [first, second]})

    result = service.push_listing_media(listing, serial="device-1", scan_media=False)

    device.sync.push.assert_has_calls(
        [
            call(str(first.resolve()), "/sdcard/DCIM/XianyuPublish/recA/01_1.jpg"),
            call(str(second.resolve()), "/sdcard/DCIM/XianyuPublish/recA/02_2.jpg"),
        ]
    )
    assert result.remote_paths == [
        "/sdcard/DCIM/XianyuPublish/recA/01_1.jpg",
        "/sdcard/DCIM/XianyuPublish/recA/02_2.jpg",
    ]


def test_media_sync_broadcasts_media_scan_when_enabled(tmp_path):
    adb_client = Mock()
    device = Mock()
    adb_client.device.return_value = device
    service = XianyuMediaSyncService(
        settings=_make_settings(),
        adb_client=adb_client,
        download_file=Mock(),
    )
    image_path = tmp_path / "recA" / "01_1.jpg"
    image_path.parent.mkdir(parents=True, exist_ok=True)
    image_path.write_bytes(b"1")
    listing = _make_listing().model_copy(update={"local_image_paths": [image_path]})

    service.push_listing_media(listing, serial="device-1", scan_media=True)

    device.shell.assert_called_once_with(
        'am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE '
        '-d "file:///sdcard/DCIM/XianyuPublish/recA/01_1.jpg"'
    )
