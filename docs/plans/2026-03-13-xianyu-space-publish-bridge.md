# Xianyu Space Publish Bridge Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Encode the real-device bridge from the Xianyu `photo_analysis` state into the standard publish chooser by dismissing the analysis overlay, opening the `宝贝` tab empty-state page, and tapping `发宝贝`.

**Architecture:** Keep the analyzer responsible for recognizing newly discovered Xianyu states, and keep the tablet-specific transition logic in `XianyuPublishFlowService`. Use one new analyzer state for the `宝贝` empty-state page, one new high-level flow helper for `photo_analysis -> publish_chooser`, and normalized screen-ratio taps for the two visual-only controls that are not exposed through the accessibility tree on the Huawei tablet.

**Tech Stack:** Python 3.12, existing `AndroidDebugService`, `XianyuFlowAnalyzer`, pytest, ratio-based coordinate taps.

---

### Task 1: TDD the new Xianyu space empty-state recognition

**Files:**
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`

**Step 1: Write the failing analyzer test**

Add a test like:

```python
def test_detects_space_items_empty_screen_after_switching_to_baobei_tab():
    ...
```

Expectations:
- the analyzer returns `space_items_empty`
- the screen is recognized when texts include `这里空空如也～`
- the root text can contain `发宝贝`

**Step 2: Run the test to verify RED**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_flow.py -v
```

Expected: FAIL because the analyzer does not yet know `space_items_empty`.

**Step 3: Implement minimal analyzer support**

Update `flow.py` to detect `space_items_empty` before falling back to `unknown`.

**Step 4: Re-run the test to verify GREEN**

Run the same `pytest` command and expect PASS.

**Step 5: Commit**

```powershell
git add minitap/mobile_use/scenarios/xianyu_publish/flow.py tests/mobile_use/scenarios/xianyu_publish/test_flow.py
git commit -m "feat: detect xianyu space empty state"
```

### Task 2: TDD the `photo_analysis -> publish_chooser` bridge

**Files:**
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/settings.py`
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`

**Step 1: Write the failing flow tests**

Add tests like:

```python
def test_advance_photo_analysis_to_publish_chooser_dismisses_overlay_and_taps_space_publish():
    ...


def test_advance_photo_analysis_to_publish_chooser_returns_existing_publish_chooser():
    ...
```

Expectations:
- from `photo_analysis`, the service taps the visual overlay dismiss point
- then taps the `宝贝` tab target from the analyzer
- then taps the visual `发宝贝` button location
- the method returns `publish_chooser`
- if already on `publish_chooser`, it returns immediately without taps

**Step 2: Run the tests to verify RED**

Run the same `pytest` command and expect FAIL.

**Step 3: Implement minimal flow support**

In `settings.py`, add normalized ratios for:
- dismissing the analysis overlay
- tapping the `发宝贝` button on the empty-state page

In `flow.py`, add:
- a helper to tap by screen ratio
- `advance_photo_analysis_to_publish_chooser(serial: str) -> XianyuScreenAnalysis`

Rules:
- accept `publish_chooser` as an immediate success state
- raise a clear error if the post-dismiss screen never reaches `space_items_empty`
- use the existing `宝贝` target instead of hardcoding the tab coordinate

**Step 4: Re-run the tests to verify GREEN**

Run the same `pytest` command and expect PASS.

**Step 5: Commit**

```powershell
git add minitap/mobile_use/scenarios/xianyu_publish/settings.py minitap/mobile_use/scenarios/xianyu_publish/flow.py tests/mobile_use/scenarios/xianyu_publish/test_flow.py
git commit -m "feat: bridge xianyu photo analysis to publish chooser"
```

### Task 3: Document, remember, and verify the bridge

**Files:**
- Modify: `README.md`
- Modify: `project-memory/projects/mobile-use.md`
- Modify: `project-memory/architecture/mobile-use.md`
- Modify: `project-memory/patterns/INDEX.md`
- Create: `project-memory/patterns/xianyu-space-empty-state-leads-to-publish-chooser.md`
- Modify: `project-memory/decisions/INDEX.md`
- Create: `project-memory/decisions/2026-03-13-xianyu-space-bridge-uses-ratio-taps-for-visual-controls.md`

**Step 1: Update docs and memory**

Document that:
- the Huawei tablet shows a visual-only analysis overlay after image selection
- dismissing that overlay and entering the `宝贝` empty-state page is now encoded
- the `发宝贝` button is currently visual-only and handled with normalized ratio taps

**Step 2: Run batch verification**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_flow.py -v
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

flow.open_home(serial)
flow.advance_to_album_picker(serial, max_steps=15)
flow.switch_album_source(serial, preferred_album_name="ChairProbe")
flow.select_cover_image(serial)
result = flow.advance_photo_analysis_to_publish_chooser(serial)
print(result.screen_name)
PY
```

Expected:
- all tests pass
- lint passes
- compileall succeeds
- the real-device probe prints `publish_chooser`

**Step 3: Commit**

```powershell
git add README.md project-memory/projects/mobile-use.md project-memory/architecture/mobile-use.md project-memory/patterns/INDEX.md project-memory/patterns/xianyu-space-empty-state-leads-to-publish-chooser.md project-memory/decisions/INDEX.md project-memory/decisions/2026-03-13-xianyu-space-bridge-uses-ratio-taps-for-visual-controls.md
git commit -m "docs: record xianyu space publish bridge"
```
