# Xianyu Publish Flow Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the first deterministic Xianyu publish flow layer that can recognize key publish screens, recover to the Xianyu home tab, and advance through the publish entry and album picker using the repo-local Android debug service.

**Architecture:** Keep the business logic inside `minitap/mobile_use/scenarios/xianyu_publish/` and consume the existing `AndroidDebugService` rather than introducing a second Android control path. Split the work into two layers: a pure screen analyzer that classifies snapshots and extracts tappable targets from UI text/bounds, then a small deterministic flow service that uses those targets to recover the app and advance toward the publish form.

**Tech Stack:** Python 3.12, Pydantic v2, adbutils, existing `AndroidDebugService`, pytest, pathlib, regex/string parsing.

---

### Task 1: Add Xianyu flow models and screen analyzer

**Files:**
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/models.py`
- Create: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- Create: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`

**Step 1: Write the failing analyzer tests**

Create `tests/mobile_use/scenarios/xianyu_publish/test_flow.py` with tests for:

```python
def test_detects_xianyu_home_screen_and_publish_entry_target():
    ...


def test_detects_publish_chooser_from_multiline_accessibility_text():
    ...


def test_detects_media_permission_dialog_and_album_picker():
    ...
```

Expectations:
- bounds strings like `"[537,1420][742,1600]"` are parsed into center coordinates
- screen detection uses current package + visible text heuristics
- analyzer extracts targets for:
  - `publish_entry`
  - `publish_idle_item`
  - `permission_allow`
  - `album_select`
  - `album_confirm`

Use snapshot dictionaries shaped like `AndroidDebugService.get_screen_data()`.

**Step 2: Run the tests to verify RED**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_flow.py -v
```

Expected: FAIL because the flow module and new models do not exist yet.

**Step 3: Implement the minimal analyzer**

Update `models.py` with small scenario-specific types such as:
- `TapTarget`
- `XianyuScreenAnalysis`

Create `flow.py` with:
- `parse_android_bounds(bounds: str | dict | None) -> TapTarget | None`
- `XianyuFlowAnalyzer`
  - `detect_screen(screen_data: dict) -> XianyuScreenAnalysis`
  - helpers for collecting visible text, finding elements by exact text / substring, and extracting tap centers

Keep the analyzer pure and synchronous.

**Step 4: Re-run the tests to verify GREEN**

Run the same command and expect PASS.

**Step 5: Commit**

```powershell
git add minitap/mobile_use/scenarios/xianyu_publish/models.py minitap/mobile_use/scenarios/xianyu_publish/flow.py tests/mobile_use/scenarios/xianyu_publish/test_flow.py
git commit -m "feat: add xianyu flow screen analyzer"
```

### Task 2: Add deterministic navigation to the album picker

**Files:**
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/settings.py`
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`

**Step 1: Write the failing flow-service tests**

Extend `tests/mobile_use/scenarios/xianyu_publish/test_flow.py` with tests for:

```python
def test_open_home_uses_explicit_main_activity_shell():
    ...


def test_advance_to_album_picker_taps_home_entry_then_publish_choice():
    ...


def test_advance_to_album_picker_handles_media_permission_dialog():
    ...
```

Use a fake Android service object with scripted responses for:
- `get_current_app()`
- `get_screen_data()`
- `tap()`
- `get_device().shell()`

Expectations:
- `open_home()` uses `am start -n com.taobao.idlefish/com.taobao.idlefish.maincontainer.activity.MainActivity`
- flow loops deterministically with a small max-step budget
- if the permission dialog appears, the flow taps `允许` before continuing
- when the album picker is reached, the service returns the latest `XianyuScreenAnalysis`

**Step 2: Run the tests to verify RED**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_flow.py -v
```

Expected: FAIL because the service methods do not exist yet.

**Step 3: Implement the minimal flow service**

Update `settings.py` with scenario-local defaults for:
- `xianyu_package_name`
- `xianyu_main_activity`
- `publish_entry_text`
- `publish_option_text`
- `permission_allow_text`
- `album_select_text`
- `album_confirm_text`

Update `flow.py` with `XianyuPublishFlowService` that provides:
- `open_home(serial: str) -> None`
- `advance_to_album_picker(serial: str, max_steps: int = 6) -> XianyuScreenAnalysis`

Recovery rules:
- if the current app is not Xianyu home or a recognized publish screen, use `open_home()`
- on home: tap the publish entry
- on publish chooser: tap the publish option
- on permission dialog: tap allow
- on album picker: stop and return the analysis
- if a recognized target is missing, raise a clear `RuntimeError`

**Step 4: Re-run the tests to verify GREEN**

Run the same command and expect PASS.

**Step 5: Commit**

```powershell
git add minitap/mobile_use/scenarios/xianyu_publish/settings.py minitap/mobile_use/scenarios/xianyu_publish/flow.py tests/mobile_use/scenarios/xianyu_publish/test_flow.py
git commit -m "feat: add xianyu album navigation flow"
```

### Task 3: Add media selection and a smoke entrypoint

**Files:**
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- Create: `scripts/xianyu_publish_flow_smoke.py`
- Modify: `README.md`
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`

**Step 1: Write the failing selection tests**

Extend `tests/mobile_use/scenarios/xianyu_publish/test_flow.py` with tests for:

```python
def test_select_cover_image_taps_first_select_then_confirm():
    ...


def test_select_cover_image_returns_latest_analysis_after_confirm():
    ...
```

Expectations:
- on an album picker screen, the flow taps the first available `选择`
- it refreshes the screen and taps `确定` when present
- it returns the latest analysis after confirmation for the next stage

**Step 2: Run the tests to verify RED**

Run the same `pytest` command and expect FAIL.

**Step 3: Implement minimal selection + smoke script**

Update `flow.py` with:
- `select_cover_image(serial: str) -> XianyuScreenAnalysis`
- a shared `_tap_target()` helper for `TapTarget`

Create `scripts/xianyu_publish_flow_smoke.py` that:
- instantiates settings and `AndroidDebugService`
- prints current package/activity
- prints the detected Xianyu screen name and target keys for a chosen serial

Update `README.md` to document:
- explicit-main-activity recovery
- current recognized screens: home, publish chooser, media permission dialog, album picker
- that the form-fill step is still the next layer

**Step 4: Run batch verification**

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
- new flow tests pass
- all scenario tests pass
- `ruff check` passes
- smoke script prints current screen classification
- compileall succeeds

**Step 5: Commit**

```powershell
git add minitap/mobile_use/scenarios/xianyu_publish/flow.py scripts/xianyu_publish_flow_smoke.py README.md tests/mobile_use/scenarios/xianyu_publish/test_flow.py
git commit -m "docs: add xianyu flow smoke tooling"
```
