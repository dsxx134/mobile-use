# Xianyu Publish Foundation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the first business-layer foundation for Xianyu publishing by reading one publishable listing from Feishu Bitable and syncing its images onto an Android device.

**Architecture:** Add a repo-local `xianyu_publish` scenario package that stays separate from the generic MCP/debug stack. The Feishu layer should normalize one Bitable record into a clean `ListingDraft` model with attachment metadata, then a media-sync layer should download those attachments to a local staging directory and push them to Android through the same `adbutils` semantics already used elsewhere in the repo.

**Tech Stack:** Python 3.12, Pydantic v2, pydantic-settings, httpx, adbutils, pytest, tempfile/pathlib.

---

### Task 1: Add scenario package, models, and settings

**Files:**
- Create: `minitap/mobile_use/scenarios/__init__.py`
- Create: `minitap/mobile_use/scenarios/xianyu_publish/__init__.py`
- Create: `minitap/mobile_use/scenarios/xianyu_publish/models.py`
- Create: `minitap/mobile_use/scenarios/xianyu_publish/settings.py`
- Test: `tests/mobile_use/scenarios/xianyu_publish/test_models.py`

**Step 1: Write the failing model tests**

Create `tests/mobile_use/scenarios/xianyu_publish/test_models.py`:

```python
from minitap.mobile_use.scenarios.xianyu_publish.models import (
    FeishuAttachment,
    ListingDraft,
)


def test_listing_draft_requires_at_least_one_attachment():
    ListingDraft(
        record_id="rec1",
        title="二手显示器",
        description="成色很好",
        price=199.0,
        attachments=[],
    )
```

Add a second test that validates:
- `FeishuAttachment` keeps `file_token`, `name`, and `size`
- `ListingDraft.local_image_paths` defaults to an empty list

**Step 2: Run the tests to verify RED**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_models.py -v
```

Expected: FAIL because the scenario package does not exist yet.

**Step 3: Implement minimal models and settings**

Create `models.py` with:
- `FeishuAttachment`
- `ListingDraft`
- `ListingStatusFilter`

Use a validator so `attachments` must be non-empty.

Create `settings.py` with a scenario-local `XianyuPublishSettings(BaseSettings)` that reads:
- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`
- `XIANYU_BITABLE_APP_TOKEN`
- `XIANYU_BITABLE_TABLE_ID`
- `XIANYU_ANDROID_MEDIA_DIR`

Keep the field mapping configurable with defaults for:
- `title_field_name`
- `description_field_name`
- `price_field_name`
- `attachment_field_name`
- `status_field_name`
- `allow_publish_field_name`

**Step 4: Re-run the tests to verify GREEN**

Run the same command and expect PASS.

**Step 5: Commit**

```powershell
git add minitap/mobile_use/scenarios tests/mobile_use/scenarios/xianyu_publish/test_models.py
git commit -m "feat: add xianyu publish models and settings"
```

### Task 2: TDD the Feishu source layer

**Files:**
- Create: `minitap/mobile_use/scenarios/xianyu_publish/feishu_source.py`
- Create: `tests/mobile_use/scenarios/xianyu_publish/test_feishu_source.py`
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/models.py`

**Step 1: Write the failing source tests**

Create `tests/mobile_use/scenarios/xianyu_publish/test_feishu_source.py` with tests for:

```python
def test_build_filter_for_pending_publishable_records():
    ...


def test_pick_first_publishable_record_maps_fields_to_listing_draft():
    ...


def test_get_attachment_download_urls_uses_file_tokens_in_order():
    ...
```

Design the tests so the source layer uses an injected HTTP client and token provider instead of real network calls.

Expectations:
- the record filter checks `是否允许发布=true`, `发布状态=待发布`, and non-empty attachment field
- one record maps into `ListingDraft`
- attachment order is preserved
- download URL lookup uses `/drive/v1/medias/batch_get_tmp_download_url`

**Step 2: Run the tests to verify RED**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_feishu_source.py -v
```

Expected: FAIL because the source layer does not exist yet.

**Step 3: Implement the minimal Feishu source**

Create `feishu_source.py` with:
- `FeishuAuthClient` for tenant token retrieval with simple in-memory caching
- `FeishuBitableSource` with dependency-injected `httpx.Client | httpx.MockTransport` support
- `build_pending_filter()`
- `list_candidate_records()`
- `pick_first_publishable_record()`
- `get_attachment_download_urls()`

Use small focused helpers:
- `_get_access_token()`
- `_request_json()`
- `_parse_attachment()`
- `_record_to_listing_draft()`

Do not implement write-back yet. Read-only source only.

**Step 4: Re-run the tests to verify GREEN**

Run the same command and expect PASS.

**Step 5: Commit**

```powershell
git add minitap/mobile_use/scenarios/xianyu_publish/feishu_source.py tests/mobile_use/scenarios/xianyu_publish/test_feishu_source.py
git commit -m "feat: add feishu source for xianyu listings"
```

### Task 3: TDD the media sync layer

**Files:**
- Create: `minitap/mobile_use/scenarios/xianyu_publish/media_sync.py`
- Create: `tests/mobile_use/scenarios/xianyu_publish/test_media_sync.py`
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/models.py`

**Step 1: Write the failing media-sync tests**

Create `tests/mobile_use/scenarios/xianyu_publish/test_media_sync.py` with tests for:

```python
def test_download_attachments_writes_files_into_listing_staging_dir(tmp_path):
    ...


def test_push_listing_media_uses_device_sync_push_for_each_file(tmp_path):
    ...


def test_media_sync_broadcasts_media_scan_when_enabled(tmp_path):
    ...
```

Use fake downloader and fake adb device objects.

Expectations:
- downloaded files land under a stable per-record directory
- `ListingDraft.local_image_paths` is updated in attachment order
- remote target path uses `XIANYU_ANDROID_MEDIA_DIR`
- media scanner broadcast runs once per pushed file when enabled

**Step 2: Run the tests to verify RED**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_media_sync.py -v
```

Expected: FAIL because the media sync layer does not exist yet.

**Step 3: Implement minimal media sync**

Create `media_sync.py` with:
- `DownloadedMedia`
- `ListingMediaSyncResult`
- `XianyuMediaSyncService`

Methods:
- `download_listing_media(listing: ListingDraft, download_urls: dict[str, str], staging_root: Path) -> ListingDraft`
- `push_listing_media(listing: ListingDraft, serial: str, remote_dir: str | None = None, scan_media: bool = True) -> ListingMediaSyncResult`

Inject:
- an `AdbClient`
- a `download_file` callable for tests

Keep implementation synchronous and deterministic.

**Step 4: Re-run the tests to verify GREEN**

Run the same command and expect PASS.

**Step 5: Commit**

```powershell
git add minitap/mobile_use/scenarios/xianyu_publish/media_sync.py tests/mobile_use/scenarios/xianyu_publish/test_media_sync.py
git commit -m "feat: add xianyu media sync service"
```

### Task 4: Add a smoke script and document the foundation

**Files:**
- Create: `scripts/xianyu_publish_foundation_smoke.py`
- Modify: `README.md`

**Step 1: Add the smoke script**

Create `scripts/xianyu_publish_foundation_smoke.py`:

```python
from minitap.mobile_use.scenarios.xianyu_publish.settings import XianyuPublishSettings


def main() -> None:
    settings = XianyuPublishSettings()
    print(
        {
            "app_token": settings.XIANYU_BITABLE_APP_TOKEN,
            "table_id": settings.XIANYU_BITABLE_TABLE_ID,
            "android_media_dir": settings.XIANYU_ANDROID_MEDIA_DIR,
        }
    )


if __name__ == "__main__":
    main()
```

**Step 2: Add README notes**

Document:
- required Feishu env vars
- expected Bitable field mapping defaults
- what `feishu_source` and `media_sync` cover today
- that direct Xianyu publish flow is the next layer, not part of this smoke step

**Step 3: Run batch verification**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/scenarios/xianyu_publish -v
uv run ruff check
uv run python scripts/xianyu_publish_foundation_smoke.py
uv run python -m compileall minitap/mobile_use/scenarios/xianyu_publish
```

Expected:
- all new scenario tests pass
- `ruff check` passes
- smoke script prints configured tokens/paths
- compileall succeeds

**Step 4: Commit**

```powershell
git add scripts/xianyu_publish_foundation_smoke.py README.md
git commit -m "docs: add xianyu publish foundation usage notes"
```
