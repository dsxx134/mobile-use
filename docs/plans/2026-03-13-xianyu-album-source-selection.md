# Xianyu Album Source Selection Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make Xianyu image selection deterministic by switching the album picker to the configured media folder before selection, and recognize the post-confirm photo-analysis screen as a first-class state instead of treating it like an unknown form page.

**Architecture:** Extend the existing `XianyuFlowAnalyzer` with two additional concepts: the album-source menu that appears after tapping the current source label, and the photo-analysis/result screen that appears after confirming a photo. Then extend `XianyuPublishFlowService` with a dedicated source-switching step that runs before media selection. Keep the flow testable with fake Android service snapshots.

**Tech Stack:** Python 3.12, Pydantic v2, existing `AndroidDebugService`, pytest, regex/string heuristics.

---

### Task 1: TDD analyzer support for album sources and photo-analysis state

**Files:**
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/settings.py`
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`

**Step 1: Write the failing analyzer tests**

Extend `tests/mobile_use/scenarios/xianyu_publish/test_flow.py` with tests for:

```python
def test_detects_album_source_menu_and_preferred_source_target():
    ...


def test_detects_album_picker_when_preferred_source_is_selected():
    ...


def test_detects_photo_analysis_screen_after_confirm():
    ...
```

Expectations:
- `XianyuPublish·1` in the source menu is exposed as a tappable target
- the analyzer recognizes `XianyuPublish` as an album-picker source label, not just `所有文件`
- the post-confirm screen is recognized as `photo_analysis` when it includes signals like:
  - `宝贝价格是根据市场行情计算得出`
  - `添加`
  - `删除`

**Step 2: Run the tests to verify RED**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_flow.py -v
```

Expected: FAIL because the analyzer does not yet understand these states.

**Step 3: Implement the minimal analyzer changes**

Update settings with:
- `preferred_album_name`
- `album_source_label_text`

Update the analyzer to recognize:
- `album_source_menu`
- `photo_analysis`

Add targets for:
- `album_source`
- `preferred_album_source`

**Step 4: Re-run the tests to verify GREEN**

Run the same command and expect PASS.

**Step 5: Commit**

```powershell
git add minitap/mobile_use/scenarios/xianyu_publish/settings.py minitap/mobile_use/scenarios/xianyu_publish/flow.py tests/mobile_use/scenarios/xianyu_publish/test_flow.py
git commit -m "feat: detect xianyu album sources and photo analysis"
```

### Task 2: TDD deterministic source switching before selection

**Files:**
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`

**Step 1: Write the failing flow tests**

Extend `tests/mobile_use/scenarios/xianyu_publish/test_flow.py` with tests for:

```python
def test_switch_album_source_opens_source_menu_and_chooses_preferred_album():
    ...


def test_select_cover_image_can_switch_to_preferred_album_before_selecting():
    ...
```

Expectations:
- `switch_album_source()` taps the current source label then taps the configured preferred folder
- `select_cover_image(preferred_album_name=...)` can call `switch_album_source()` before tapping `选择`
- after confirmation, the service returns the `photo_analysis` screen analysis

**Step 2: Run the tests to verify RED**

Run the same `pytest` command and expect FAIL.

**Step 3: Implement minimal flow changes**

Add:
- `switch_album_source(serial: str, preferred_album_name: str | None = None) -> XianyuScreenAnalysis`

Update:
- `select_cover_image()` to accept an optional `preferred_album_name`

Rules:
- if already on the preferred source, do not reopen the source menu
- if the source menu target is missing, raise a clear error
- stop after the post-confirm `photo_analysis` screen and return it

**Step 4: Re-run the tests to verify GREEN**

Run the same command and expect PASS.

**Step 5: Commit**

```powershell
git add minitap/mobile_use/scenarios/xianyu_publish/flow.py tests/mobile_use/scenarios/xianyu_publish/test_flow.py
git commit -m "feat: switch xianyu album source before media select"
```

### Task 3: Document and verify the new behavior

**Files:**
- Modify: `README.md`
- Modify: `scripts/xianyu_publish_flow_smoke.py`

**Step 1: Update smoke output**

Make the smoke script print:
- current screen name
- current app package/activity
- current target keys
- configured preferred album name

**Step 2: Update README**

Document:
- why deterministic media selection should use a dedicated album folder
- that the current post-confirm destination is a `photo_analysis` screen, not yet the final form

**Step 3: Run batch verification**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_flow.py -v
uv run pytest tests/mobile_use/scenarios/xianyu_publish -v
uv run ruff check
uv run python scripts/xianyu_publish_flow_smoke.py
uv run python -m compileall minitap/mobile_use/scenarios/xianyu_publish
```

Expected:
- all flow tests pass
- all scenario tests pass
- `ruff check` passes
- smoke script prints the preferred album name
- compileall succeeds

**Step 4: Commit**

```powershell
git add README.md scripts/xianyu_publish_flow_smoke.py
git commit -m "docs: add xianyu album source notes"
```
