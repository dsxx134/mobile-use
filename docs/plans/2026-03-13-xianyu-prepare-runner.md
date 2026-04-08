# Xianyu Prepare Runner Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a deterministic runner that takes the first publishable Feishu Bitable record and prepares a Xianyu listing form on the Huawei tablet with media, merged title+description text, and price filled in.

**Architecture:** Reuse the existing `FeishuBitableSource`, `XianyuMediaSyncService`, and `XianyuPublishFlowService` instead of inventing a second business path. Add a small `runner.py` orchestration layer that fetches one record, resolves/downloads/pushes media, re-enters the portrait listing form, selects the first prepared image, bridges back from `photo_analysis` into the form, then fills description and price. While doing that, harden `advance_to_listing_form()` so the draft-resume dialog can linger briefly after tapping `继续` without breaking the flow. Because the current Xianyu form does not expose a separate title field on this device, fold `ListingDraft.title` into the description body as the first line.

**Tech Stack:** Python 3.12, pytest, existing Xianyu scenario services, mocked service dependencies for orchestration tests, Huawei Android tablet for final probe.

---

### Task 1: TDD harden draft-resume continuation waiting

**Files:**
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`

**Step 1: Write the failing test**

Add a test like:

```python
def test_advance_to_listing_form_waits_for_listing_form_after_tapping_draft_resume_continue():
    ...
```

Expectation:
- after tapping `继续`, the next one or two analyzed snapshots can still be `draft_resume_dialog`
- the flow should poll through that tail and finally return `listing_form`

**Step 2: Run test to verify it fails**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_flow.py -k "draft_resume_continue and waits" -v
```

Expected: FAIL because `advance_to_listing_form()` currently re-analyzes too early and can stop on `draft_resume_dialog`.

**Step 3: Write minimal implementation**

Update `flow.py` so:
- after tapping `draft_resume_continue`, the flow waits through loading/duplicate-dialog tail states
- it only returns once `listing_form` appears or the normal step loop continues with a meaningful next screen

**Step 4: Re-run the test to verify it passes**

Run the same pytest command and expect PASS.

**Step 5: Commit**

```powershell
git add minitap/mobile_use/scenarios/xianyu_publish/flow.py tests/mobile_use/scenarios/xianyu_publish/test_flow.py
git commit -m "fix: wait through xianyu draft resume tail"
```

### Task 2: TDD runner text formatting and result contract

**Files:**
- Create: `minitap/mobile_use/scenarios/xianyu_publish/runner.py`
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_runner.py`

**Step 1: Write the failing tests**

Add tests like:

```python
def test_build_listing_body_prefers_title_then_blank_line_then_description():
    ...


def test_build_listing_body_deduplicates_when_description_already_starts_with_title():
    ...
```

Expectations:
- default body is:
  - first line = title
  - blank line
  - description
- if the description already starts with the exact title, do not duplicate it

**Step 2: Run tests to verify RED**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_runner.py -k "build_listing_body" -v
```

Expected: FAIL because `runner.py` does not exist yet.

**Step 3: Write minimal implementation**

Create `runner.py` with:
- a pure helper `build_listing_body(listing: ListingDraft) -> str`
- a small result model such as `XianyuPrepareListingResult`

**Step 4: Re-run tests to verify GREEN**

Run the same pytest command and expect PASS.

**Step 5: Commit**

```powershell
git add minitap/mobile_use/scenarios/xianyu_publish/runner.py tests/mobile_use/scenarios/xianyu_publish/test_runner.py
git commit -m "feat: add xianyu prepare runner text contract"
```

### Task 3: TDD orchestration runner for one publishable listing

**Files:**
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/runner.py`
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_runner.py`

**Step 1: Write the failing tests**

Add tests like:

```python
def test_prepare_first_publishable_listing_runs_feishu_media_and_flow_chain_in_order(tmp_path):
    ...


def test_prepare_first_publishable_listing_raises_when_no_publishable_record_exists(tmp_path):
    ...
```

Expectation for the happy path:
- `pick_first_publishable_record()` is called
- `get_attachment_download_urls()` is called with the listing attachments
- `download_listing_media()` is called
- `push_listing_media()` is called
- flow calls happen in order:
  - `advance_to_listing_form`
  - `advance_listing_form_to_album_picker`
  - `select_cover_image`
  - `advance_photo_analysis_to_publish_chooser`
  - `advance_to_listing_form`
  - `fill_description`
  - `fill_price`
- final result includes:
  - `record_id`
  - `serial`
  - remote media paths
  - filled body text
  - final screen name

**Step 2: Run tests to verify RED**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_runner.py -v
```

Expected: FAIL because the orchestration service does not exist yet.

**Step 3: Write minimal implementation**

Implement a runner class such as `XianyuPrepareRunner` that:
- depends on injected source/media/flow services
- accepts `serial` and `staging_root`
- prepares only the currently deterministic fields:
  - media
  - merged title+description body
  - price
- does not claim category, location persistence, shipping, or final publish submission yet

**Step 4: Re-run tests to verify GREEN**

Run the same pytest command and expect PASS.

**Step 5: Commit**

```powershell
git add minitap/mobile_use/scenarios/xianyu_publish/runner.py tests/mobile_use/scenarios/xianyu_publish/test_runner.py
git commit -m "feat: add xianyu prepare listing runner"
```

### Task 4: Document, remember, verify, and push the milestone

**Files:**
- Modify: `README.md`
- Modify: `project-memory/projects/mobile-use.md`
- Modify: `project-memory/architecture/mobile-use.md`
- Modify: `project-memory/patterns/INDEX.md`
- Create: `project-memory/patterns/xianyu-title-is-folded-into-description-body.md`
- Create: `project-memory/patterns/xianyu-draft-resume-continue-needs-post-tap-polling.md`

**Step 1: Update docs and memory**

Document that:
- the current device/app form still has no separate title field, so `ListingDraft.title` is folded into the prepared description body
- the new runner only prepares deterministic fields and stops before unresolved final-publish steps
- after tapping draft `继续`, the flow must poll until the dialog tail clears

**Step 2: Run batch verification**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/scenarios/xianyu_publish -v
uv run ruff check
uv run python -m compileall minitap/mobile_use/scenarios/xianyu_publish
```

Plus one real-device probe that confirms:
- `advance_to_listing_form()` can start from an arbitrary in-app Xianyu page, survive the draft-resume dialog, and return to `listing_form`
- the runner can at least reach the second `advance_to_listing_form()` after selecting media on the Huawei tablet

**Step 3: Commit and push**

```powershell
git add README.md project-memory/projects/mobile-use.md project-memory/architecture/mobile-use.md project-memory/patterns/INDEX.md project-memory/patterns/xianyu-title-is-folded-into-description-body.md project-memory/patterns/xianyu-draft-resume-continue-needs-post-tap-polling.md
git commit -m "docs: record xianyu prepare runner behavior"
git push origin feat/android-debug-mcp
```
