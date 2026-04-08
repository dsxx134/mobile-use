# Xianyu Listing Form Album Bridge Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Extend the portrait `发闲置` flow so the standard listing form can reliably open the media picker and expose the real clickable targets needed for image upload.

**Architecture:** Keep the portrait listing form as the default publish path, but enrich `XianyuFlowAnalyzer` with better target extraction for the real Huawei tablet semantics, especially `content-desc` values like `发布, 发布` and the large description tile. Then add one small bridge method on `XianyuPublishFlowService` that starts from `listing_form`, taps `添加图片`, handles the optional media permission dialog, and returns once the existing album picker is visible.

**Tech Stack:** Python 3.12, existing `AndroidDebugService`, `XianyuFlowAnalyzer`, `XianyuPublishFlowService`, pytest, adb/UI dump findings from the Huawei Android tablet.

---

### Task 1: TDD richer portrait listing-form target extraction

**Files:**
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`

**Step 1: Write the failing tests**

Add analyzer coverage for the real portrait publish form semantics:

```python
def test_detects_portrait_listing_form_targets_from_content_desc():
    ...
```

Expectations:
- `listing_form` is detected when the screen uses `content-desc`
- `submit_listing` is extracted from `发布, 发布`
- `description_entry` is extracted from `描述, 描述一下宝贝的品牌型号、货品来源…`
- existing `add_image` extraction still works

**Step 2: Run test to verify RED**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_flow.py -v
```

Expected: FAIL because the current analyzer only matches exact `发布`.

**Step 3: Implement minimal analyzer support**

Update `flow.py` so the portrait listing form exposes:
- `submit_listing`
- `add_image`
- `description_entry`

Use the least permissive matching that still fits the real device dump.

**Step 4: Run test to verify GREEN**

Run the same pytest command and expect PASS.

**Step 5: Commit**

```powershell
git add minitap/mobile_use/scenarios/xianyu_publish/flow.py tests/mobile_use/scenarios/xianyu_publish/test_flow.py
git commit -m "feat: enrich xianyu listing form targets"
```

### Task 2: TDD bridge from portrait listing form into the album picker

**Files:**
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`

**Step 1: Write the failing tests**

Add flow coverage like:

```python
def test_advance_listing_form_to_album_picker_taps_add_image():
    ...


def test_advance_listing_form_to_album_picker_handles_media_permission_dialog():
    ...
```

Expectations:
- when already on `listing_form`, the flow taps `add_image`
- if Android shows the media permission dialog, it taps `允许`
- the method returns the existing `album_picker` analysis

**Step 2: Run the tests to verify RED**

Run the same `pytest` command and expect FAIL.

**Step 3: Implement minimal bridge support**

Add a method on `XianyuPublishFlowService`:

```python
def advance_listing_form_to_album_picker(
    self,
    serial: str,
    max_steps: int = 4,
) -> XianyuScreenAnalysis:
    ...
```

Rules:
- accept an existing `album_picker` immediately
- require `listing_form` as the normal start state
- tap `add_image`
- handle `media_permission_dialog` if it appears
- stop once `album_picker` is visible

**Step 4: Run the tests to verify GREEN**

Run the same pytest command and expect PASS.

**Step 5: Commit**

```powershell
git add minitap/mobile_use/scenarios/xianyu_publish/flow.py tests/mobile_use/scenarios/xianyu_publish/test_flow.py
git commit -m "feat: bridge xianyu listing form to album picker"
```

### Task 3: Document, remember, and verify the new bridge

**Files:**
- Modify: `README.md`
- Modify: `project-memory/projects/mobile-use.md`
- Modify: `project-memory/architecture/mobile-use.md`
- Modify: `project-memory/patterns/INDEX.md`
- Create: `project-memory/patterns/xianyu-listing-form-opens-album-picker.md`

**Step 1: Update docs and memory**

Document that:
- the portrait listing form exposes `content-desc` driven targets
- `添加图片` opens the album picker directly from `发闲置`
- the image-upload automation should start from the portrait form instead of the old publish chooser

**Step 2: Run batch verification**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/scenarios/xianyu_publish -v
uv run ruff check
uv run python -m compileall minitap/mobile_use/scenarios/xianyu_publish
```

Plus one real-device probe that starts from the portrait form and confirms `album_picker`.

**Step 3: Commit**

```powershell
git add README.md project-memory/projects/mobile-use.md project-memory/architecture/mobile-use.md project-memory/patterns/INDEX.md project-memory/patterns/xianyu-listing-form-opens-album-picker.md
git commit -m "docs: record xianyu listing form album bridge"
```
