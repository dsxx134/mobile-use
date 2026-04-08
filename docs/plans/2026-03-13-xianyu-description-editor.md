# Xianyu Description Editor Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a deterministic description-editing path for the portrait `发闲置` form so automation can open the editor, input text, and return to the listing form.

**Architecture:** Extend `XianyuFlowAnalyzer` with a `description_editor` state that recognizes the real Huawei tablet editor by its `完成` control and the same large description tile used by the portrait form. Then add a small flow bridge that opens the editor from `listing_form`, uses `AndroidDebugService.input_text()` to enter content, taps `完成`, and waits until the normal listing form returns.

**Tech Stack:** Python 3.12, existing `AndroidDebugService`, `XianyuFlowAnalyzer`, `XianyuPublishFlowService`, pytest, real-device UI dumps from the Huawei Android tablet.

---

### Task 1: TDD description-editor screen recognition

**Files:**
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`

**Step 1: Write the failing tests**

Add tests like:

```python
def test_detects_description_editor_from_portrait_form():
    ...
```

Expectations:
- the analyzer returns `description_editor`
- the state is recognized when the screen contains:
  - `发闲置`
  - `完成`
  - the same description tile used by the portrait form
- the returned targets include:
  - `description_done`
  - `description_entry`

**Step 2: Run test to verify it fails**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_flow.py -v
```

Expected: FAIL because the analyzer does not yet distinguish `description_editor`.

**Step 3: Implement minimal analyzer support**

Update `flow.py` so `description_editor` is detected before the generic `listing_form`.

**Step 4: Re-run the test to verify it passes**

Run the same pytest command and expect PASS.

**Step 5: Commit**

```powershell
git add minitap/mobile_use/scenarios/xianyu_publish/flow.py tests/mobile_use/scenarios/xianyu_publish/test_flow.py
git commit -m "feat: detect xianyu description editor"
```

### Task 2: TDD description fill from the portrait form

**Files:**
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`

**Step 1: Write the failing tests**

Add tests like:

```python
def test_open_description_editor_taps_description_entry():
    ...


def test_fill_description_inputs_text_and_taps_done():
    ...
```

Expectations:
- from `listing_form`, the flow taps `description_entry` and reaches `description_editor`
- `fill_description()` calls `android_service.input_text()`
- the flow taps `完成`
- the method returns once `listing_form` is visible again

**Step 2: Run the tests to verify they fail**

Run the same pytest command and expect FAIL.

**Step 3: Implement the minimal flow support**

Add:
- `advance_listing_form_to_description_editor(...)`
- `fill_description(...)`

Rules:
- accept an existing `description_editor` immediately
- use existing non-loading wait logic where helpful
- do not add title or price behavior yet

**Step 4: Re-run the tests to verify they pass**

Run the same pytest command and expect PASS.

**Step 5: Commit**

```powershell
git add minitap/mobile_use/scenarios/xianyu_publish/flow.py tests/mobile_use/scenarios/xianyu_publish/test_flow.py
git commit -m "feat: fill xianyu description from listing form"
```

### Task 3: Document, remember, and verify the description path

**Files:**
- Modify: `README.md`
- Modify: `project-memory/projects/mobile-use.md`
- Modify: `project-memory/architecture/mobile-use.md`
- Modify: `project-memory/patterns/INDEX.md`
- Create: `project-memory/patterns/xianyu-description-editing-uses-complete-button.md`

**Step 1: Update docs and memory**

Document that:
- the portrait form description flow uses a dedicated editor state
- the editor is exited through `完成`
- the next publish-layer code should reuse this helper rather than typing directly into the base form

**Step 2: Run batch verification**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/scenarios/xianyu_publish -v
uv run ruff check
uv run python -m compileall minitap/mobile_use/scenarios/xianyu_publish
```

Plus one real-device probe that:
- opens `卖闲置 -> 发闲置`
- enters the description editor
- types a short string
- returns to the portrait form

**Step 3: Commit**

```powershell
git add README.md project-memory/projects/mobile-use.md project-memory/architecture/mobile-use.md project-memory/patterns/INDEX.md project-memory/patterns/xianyu-description-editing-uses-complete-button.md
git commit -m "docs: record xianyu description editing flow"
```
