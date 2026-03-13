# Xianyu Draft Resume And Location Entry Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Restore deterministic entry into the portrait `发闲置` form when Xianyu shows a draft-resume dialog, and add deterministic recognition/navigation for the location chooser and city-region picker.

**Architecture:** Extend `XianyuFlowAnalyzer` with two new screen types: a `draft_resume_dialog` that appears after tapping `发闲置` with an unfinished draft, and location-related screens for the root `location_panel` plus the hierarchical `location_region_picker`. Then update `advance_to_listing_form()` to continue the existing draft, and add a helper that enters the region picker from the listing form. Do not claim final location writeback yet; real-device probing did not show a stable visible confirmation on the listing form.

**Tech Stack:** Python 3.12, existing `AndroidDebugService`, `XianyuFlowAnalyzer`, `XianyuPublishFlowService`, pytest, real-device UI snapshots from the Huawei Android tablet.

---

### Task 1: TDD draft-resume dialog recognition and recovery

**Files:**
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`

**Step 1: Write the failing tests**

Add tests like:

```python
def test_detects_draft_resume_dialog_targets():
    ...


def test_advance_to_listing_form_continues_existing_draft():
    ...
```

Expectations:
- the analyzer recognizes the screen with:
  - `你有未编辑完成的宝贝，是否继续？`
  - `放弃`
  - `继续`
- `advance_to_listing_form()` can go:
  - `home -> publish_chooser -> draft_resume_dialog -> listing_form`

**Step 2: Run the tests to verify RED**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_flow.py -k "draft_resume or continues_existing_draft" -v
```

Expected: FAIL because draft-resume support does not exist yet.

**Step 3: Implement minimal analyzer and flow support**

Update `flow.py` so:
- `draft_resume_dialog` is detected before generic `unknown`
- targets include `draft_resume_continue` and optionally `draft_resume_discard`
- `advance_to_listing_form()` taps `draft_resume_continue`

**Step 4: Re-run the tests to verify GREEN**

Run the same pytest command and expect PASS.

**Step 5: Commit**

```powershell
git add minitap/mobile_use/scenarios/xianyu_publish/flow.py tests/mobile_use/scenarios/xianyu_publish/test_flow.py
git commit -m "feat: resume xianyu draft before listing form"
```

### Task 2: TDD location-entry and region-picker recognition

**Files:**
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`

**Step 1: Write the failing tests**

Add tests like:

```python
def test_detects_listing_form_location_entry_target():
    ...


def test_detects_location_panel_targets():
    ...


def test_detects_location_region_picker_targets():
    ...
```

Expectations:
- `listing_form` exposes a `location_entry` target from `选择位置`
- `location_panel` is recognized when the root chooser shows:
  - `宝贝所在地`
  - `搜索地址`
  - `常用地址`
  - `城市区域`
  - `请选择宝贝所在地`
- `location_region_picker` is recognized when the hierarchical region page shows:
  - `所在地`
  - `返回`
  - `获取当前位置`
  - a visible region option such as `上海` or `浦东新区`

**Step 2: Run the tests to verify RED**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_flow.py -k "location_entry or location_panel or location_region_picker" -v
```

Expected: FAIL because location support does not exist yet.

**Step 3: Implement minimal analyzer support**

Update `flow.py` so:
- `location_entry` is exposed on `listing_form`
- `location_panel` and `location_region_picker` are recognized
- the region picker exports general-purpose targets for:
  - `location_region_back`
  - `location_region_get_current`
  - visible region options by normalized key such as `location_region_shanghai`
  - or a generic `location_region_options` mapping if cleaner

**Step 4: Re-run the tests to verify GREEN**

Run the same pytest command and expect PASS.

**Step 5: Commit**

```powershell
git add minitap/mobile_use/scenarios/xianyu_publish/flow.py tests/mobile_use/scenarios/xianyu_publish/test_flow.py
git commit -m "feat: detect xianyu location chooser screens"
```

### Task 3: TDD deterministic entry into the location region picker

**Files:**
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`

**Step 1: Write the failing test**

Add a test like:

```python
def test_advance_listing_form_to_location_region_picker_taps_choose_region():
    ...
```

Expectations:
- from `listing_form`, the flow taps `location_entry`
- waits for `location_panel`
- taps the clickable `请选择宝贝所在地` row
- reaches `location_region_picker`

**Step 2: Run the test to verify RED**

Run the same pytest command and expect FAIL.

**Step 3: Implement minimal flow support**

Add:
- `advance_listing_form_to_location_panel(...)`
- `advance_listing_form_to_location_region_picker(...)`

Rules:
- use the clickable region row, not the tiny `去选择` label as the main path
- keep scope to entering the picker only
- do not claim final location writeback yet

**Step 4: Re-run the test to verify GREEN**

Run the same pytest command and expect PASS.

**Step 5: Commit**

```powershell
git add minitap/mobile_use/scenarios/xianyu_publish/flow.py tests/mobile_use/scenarios/xianyu_publish/test_flow.py
git commit -m "feat: enter xianyu location region picker"
```

### Task 4: Document, remember, and verify the new entry paths

**Files:**
- Modify: `README.md`
- Modify: `project-memory/projects/mobile-use.md`
- Modify: `project-memory/architecture/mobile-use.md`
- Modify: `project-memory/patterns/INDEX.md`
- Create: `project-memory/patterns/xianyu-draft-resume-dialog-blocks-form-entry.md`
- Create: `project-memory/patterns/xianyu-location-region-picker-uses-clickable-region-row.md`

**Step 1: Update docs and memory**

Document that:
- `advance_to_listing_form()` must sometimes handle a draft-resume dialog
- the location root chooser and the hierarchical region picker are now recognized
- `请选择宝贝所在地` is the stable path into region selection
- final location writeback is still unresolved and should not be treated as deterministic yet

**Step 2: Run batch verification**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/scenarios/xianyu_publish -v
uv run ruff check
uv run python -m compileall minitap/mobile_use/scenarios/xianyu_publish
```

Plus real-device probes that confirm:
- `advance_to_listing_form()` now handles `继续`
- `advance_listing_form_to_location_region_picker()` reaches the region picker from the form

**Step 3: Commit**

```powershell
git add README.md project-memory/projects/mobile-use.md project-memory/architecture/mobile-use.md project-memory/patterns/INDEX.md project-memory/patterns/xianyu-draft-resume-dialog-blocks-form-entry.md project-memory/patterns/xianyu-location-region-picker-uses-clickable-region-row.md
git commit -m "docs: record xianyu draft resume and location entry flow"
```
