from collections.abc import Callable
from pathlib import Path

import httpx
from adbutils import AdbClient
from pydantic import BaseModel, ConfigDict

from minitap.mobile_use.scenarios.xianyu_publish.models import ListingDraft
from minitap.mobile_use.scenarios.xianyu_publish.settings import XianyuPublishSettings


class DownloadedMedia(BaseModel):
    model_config = ConfigDict(extra="forbid")

    local_path: Path
    remote_path: str | None = None


class ListingMediaSyncResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    serial: str
    remote_dir: str
    remote_paths: list[str]
    pushed_count: int


class XianyuMediaSyncService:
    def __init__(
        self,
        settings: XianyuPublishSettings,
        adb_client: AdbClient,
        download_file: Callable[[str, Path], None] | None = None,
    ) -> None:
        self.settings = settings
        self._adb_client = adb_client
        self._download_file = download_file or self._default_download_file

    def download_listing_media(
        self,
        listing: ListingDraft,
        download_urls: dict[str, str],
        staging_root: Path,
    ) -> ListingDraft:
        staging_dir = staging_root / listing.record_id
        staging_dir.mkdir(parents=True, exist_ok=True)

        local_paths: list[Path] = []
        for index, attachment in enumerate(listing.attachments, start=1):
            download_url = download_urls.get(attachment.file_token)
            if not download_url:
                raise ValueError(
                    f"Missing download URL for attachment token: {attachment.file_token}"
                )

            destination = staging_dir / self._build_staged_name(
                index=index,
                original_name=attachment.name,
            )
            self._download_file(download_url, destination)
            local_paths.append(destination.resolve())

        return listing.model_copy(update={"local_image_paths": local_paths})

    def push_listing_media(
        self,
        listing: ListingDraft,
        serial: str,
        remote_dir: str | None = None,
        scan_media: bool = True,
        clean_remote_dir: bool = True,
    ) -> ListingMediaSyncResult:
        if not listing.local_image_paths:
            raise ValueError("ListingDraft has no local_image_paths to push")

        device = self._adb_client.device(serial=serial)
        remote_base_dir = (remote_dir or self.settings.XIANYU_ANDROID_MEDIA_DIR).rstrip("/")
        remote_root = f"{remote_base_dir}/{listing.record_id}"
        remote_paths: list[str] = []

        if clean_remote_dir:
            device.shell(f'rm -rf "{remote_base_dir}"')
            device.shell(f'mkdir -p "{remote_root}"')

        for local_path in listing.local_image_paths:
            remote_path = f"{remote_root}/{local_path.name}"
            device.sync.push(str(local_path.resolve()), remote_path)
            if scan_media:
                device.shell(
                    'am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE '
                    f'-d "file://{remote_path}"'
                )
            remote_paths.append(remote_path)

        return ListingMediaSyncResult(
            serial=serial,
            remote_dir=remote_root,
            remote_paths=remote_paths,
            pushed_count=len(remote_paths),
        )

    def _build_staged_name(self, index: int, original_name: str) -> str:
        safe_name = Path(original_name).name
        return f"{index:02d}_{safe_name}"

    def _default_download_file(self, url: str, destination: Path) -> None:
        with httpx.stream("GET", url, follow_redirects=True, timeout=60.0) as response:
            response.raise_for_status()
            destination.write_bytes(response.read())
