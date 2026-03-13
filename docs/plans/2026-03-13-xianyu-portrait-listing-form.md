# Xianyu Portrait Listing Form Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make the Xianyu flow prefer portrait mode and recognize the standard listing form reached by tapping `发闲置`, so automation can target the real publish form instead of the landscape space-analysis path.

**Architecture:** Extend `XianyuFlowAnalyzer` with a new `listing_form` state that matches the portrait publish form and does not get confused with the old `publish_chooser`. Then extend `XianyuPublishFlowService` with a small orientation helper plus a new `advance_to_listing_form()` method that forces portrait, opens Xianyu home, taps `卖闲置`, taps `发闲置`, and returns once the real form is visible.

**Tech Stack:** Python 3.12, existing `AndroidDebugService`, `XianyuFlowAnalyzer`, `XianyuPublishFlowService`, pytest, adb shell orientation settings.

---

### Task 1: TDD analyzer support for the portrait listing form

**Files:**
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`

**Step 1: Write the failing analyzer test**

Add a test like:

```python
def test_detects_portrait_listing_form_instead_of_publish_chooser():
    ...
```

Expectations:
- the analyzer returns `listing_form`
- the screen is recognized when texts include:
  - `发闲置`
  - `添加图片`
  - `价格设置`
  - `发货方式`
- it should not be misclassified as `publish_chooser`

**Step 2: Run the test to verify RED**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_flow.py -v
```

Expected: FAIL because the current analyzer still labels the portrait form as `publish_chooser`.

**Step 3: Implement minimal analyzer support**

Update `flow.py` so `listing_form` is detected before `publish_chooser`.

Add useful targets if present:
- `submit_listing`
- `add_image`

**Step 4: Re-run the test to verify GREEN**

Run the same command and expect PASS.

**Step 5: Commit**

```powershell
git add minitap/mobile_use/scenarios/xianyu_publish/flow.py tests/mobile_use/scenarios/xianyu_publish/test_flow.py
git commit -m "feat: detect xianyu portrait listing form"
```

### Task 2: TDD portrait-first navigation into the listing form

**Files:**
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`

**Step 1: Write the failing flow tests**

Add tests like:

```python
def test_advance_to_listing_form_forces_portrait_then_taps_publish_entry_and_publish_idle_item():
    ...


def test_advance_to_listing_form_returns_existing_listing_form_without_extra_taps():
    ...
```

Expectations:
- the flow calls the device shell to disable auto-rotate and set user rotation to portrait
- from `home`, it taps `卖闲置`, then `发闲置`, then returns `listing_form`
- from an existing `listing_form`, it returns immediately without extra taps

**Step 2: Run the tests to verify RED**

Run the same `pytest` command and expect FAIL.

**Step 3: Implement minimal flow support**

In `flow.py`, add:
- `ensure_portrait(serial: str) -> None`
- `advance_to_listing_form(serial: str, max_steps: int = 6) -> XianyuScreenAnalysis`

Rules:
- `ensure_portrait()` uses:
  - `settings put system accelerometer_rotation 0`
  - `settings put system user_rotation 0`
- accept `listing_form` as an immediate success state
- accept `publish_chooser` as an intermediate state and tap `publish_idle_item`
- preserve the existing home recovery behavior

**Step 4: Re-run the tests to verify GREEN**

Run the same `pytest` command and expect PASS.

**Step 5: Commit**

```powershell
git add minitap/mobile_use/scenarios/xianyu_publish/flow.py tests/mobile_use/scenarios/xianyu_publish/test_flow.py
git commit -m "feat: enter xianyu listing form in portrait mode"
```

### Task 3: Document, remember, and verify the portrait-first path

**Files:**
- Modify: `README.md`
- Modify: `project-memory/projects/mobile-use.md`
- Modify: `project-memory/architecture/mobile-use.md`
- Modify: `project-memory/patterns/INDEX.md`
- Create: `project-memory/patterns/xianyu-publish-form-prefers-portrait.md`
- Modify: `project-memory/decisions/INDEX.md`
- Create: `project-memory/decisions/2026-03-13-xianyu-default-path-is-portrait-form.md`

**Step 1: Update docs and memory**

Document that:
- the Huawei tablet should default to portrait for Xianyu publishing
- tapping `发闲置` in portrait reaches the real publish form
- the old landscape space-analysis path remains useful for exploration, but the preferred publish path is now the portrait form

**Step 2: Run batch verification**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/scenarios/xianyu_publish -v
uv run ruff check
uv run python -m compileall minitap/mobile_use/scenarios/xianyu_publish
```

Plus one real-device probe:

```powershell
uv run python - <<'PY'
from minitap.mobile_use.mcp.android_debug_service import AndroidDebugService
from minitap.mobile_use.scenarios.xianyu_publish.flow import XianyuPublishFlowService
from minitap.mobile_use.scenarios.xianyu_publish.settings import XianyuPublishSettings

serial = "E2P6R22708000602"
service = AndroidDebugService()
flow = XianyuPublishFlowService(
    settings=XianyuPublishSettings(preferred_album_name="ChairProbe"),
    android_service=service,
)

result = flow.advance_to_listing_form(serial, max_steps=8)
print(result.screen_name)
PY
```

Expected:
- tests pass
- lint passes
- compileall succeeds
- the real-device probe prints `listing_form`

**Step 3: Commit**

```powershell
git add README.md project-memory/projects/mobile-use.md project-memory/architecture/mobile-use.md project-memory/patterns/INDEX.md project-memory/patterns/xianyu-publish-form-prefers-portrait.md project-memory/decisions/INDEX.md project-memory/decisions/2026-03-13-xianyu-default-path-is-portrait-form.md
git commit -m "docs: record xianyu portrait listing form path"
```
