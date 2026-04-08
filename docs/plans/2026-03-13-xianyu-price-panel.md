# Xianyu Price Panel Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a deterministic sale-price flow for the portrait `发闲置` form so automation can open the price panel, tap the numeric keypad, confirm, and return to the listing form.

**Architecture:** Extend `XianyuFlowAnalyzer` with two small additions: expose a `price_entry` target on the portrait `listing_form`, and recognize the Xianyu bottom-sheet `price_panel` with keypad and confirm/delete controls. Then add `advance_listing_form_to_price_panel()` plus `fill_price()` on `XianyuPublishFlowService`, using keypad taps rather than IME text input.

**Tech Stack:** Python 3.12, existing `AndroidDebugService`, `XianyuFlowAnalyzer`, `XianyuPublishFlowService`, pytest, real-device UI snapshots from the Huawei Android tablet.

---

### Task 1: TDD price-panel screen recognition and listing-form entry target

**Files:**
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`

**Step 1: Write the failing tests**

Add tests like:

```python
def test_detects_listing_form_price_entry_target():
    ...


def test_detects_price_panel_with_confirm_delete_and_keypad_targets():
    ...
```

Expectations:
- `listing_form` exposes a `price_entry` target from the real `价格设置` row
- `price_panel` is recognized when the screen contains:
  - `价格设置`
  - `原价设置`
  - `库存设置`
  - `确定`
- returned targets include:
  - `price_confirm`
  - `price_delete`
  - `price_key_0` ... `price_key_9`
  - `price_key_decimal`

**Step 2: Run the tests to verify RED**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_flow.py -v
```

Expected: FAIL because price panel support does not exist yet.

**Step 3: Implement minimal analyzer support**

Update `flow.py` so:
- `price_entry` is exposed on `listing_form`
- `price_panel` is recognized before generic `unknown`

**Step 4: Re-run the tests to verify GREEN**

Run the same pytest command and expect PASS.

**Step 5: Commit**

```powershell
git add minitap/mobile_use/scenarios/xianyu_publish/flow.py tests/mobile_use/scenarios/xianyu_publish/test_flow.py
git commit -m "feat: detect xianyu price panel"
```

### Task 2: TDD sale-price fill from the portrait form

**Files:**
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`

**Step 1: Write the failing tests**

Add tests like:

```python
def test_advance_listing_form_to_price_panel_taps_price_entry():
    ...


def test_fill_price_clears_existing_digits_taps_keypad_and_confirms():
    ...
```

Expectations:
- from `listing_form`, the flow taps `price_entry` and reaches `price_panel`
- `fill_price()` clears existing value with delete taps
- the flow taps keypad targets for a normalized price string such as `399.9`
- it taps `确定`
- it returns once `listing_form` is visible again

**Step 2: Run the tests to verify RED**

Run the same pytest command and expect FAIL.

**Step 3: Implement minimal flow support**

Add:
- `advance_listing_form_to_price_panel(...)`
- `fill_price(...)`

Rules:
- use keypad taps, not `input_text()`
- keep scope to sale price only
- allow test-friendly control over clear count / key delay if needed

**Step 4: Re-run the tests to verify GREEN**

Run the same pytest command and expect PASS.

**Step 5: Commit**

```powershell
git add minitap/mobile_use/scenarios/xianyu_publish/flow.py tests/mobile_use/scenarios/xianyu_publish/test_flow.py
git commit -m "feat: fill xianyu sale price from listing form"
```

### Task 3: Document, remember, and verify the price flow

**Files:**
- Modify: `README.md`
- Modify: `project-memory/projects/mobile-use.md`
- Modify: `project-memory/architecture/mobile-use.md`
- Modify: `project-memory/patterns/INDEX.md`
- Create: `project-memory/patterns/xianyu-price-panel-uses-keypad-taps.md`

**Step 1: Update docs and memory**

Document that:
- Xianyu sale price uses a dedicated bottom sheet with keypad taps
- the portrait form should open it through the `价格设置` row
- sale price filling is deterministic and does not rely on IME text input

**Step 2: Run batch verification**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/scenarios/xianyu_publish -v
uv run ruff check
uv run python -m compileall minitap/mobile_use/scenarios/xianyu_publish
```

Plus one real-device probe that:
- opens the price panel from `listing_form`
- enters a test price
- confirms and returns to `listing_form`

**Step 3: Commit**

```powershell
git add README.md project-memory/projects/mobile-use.md project-memory/architecture/mobile-use.md project-memory/patterns/INDEX.md project-memory/patterns/xianyu-price-panel-uses-keypad-taps.md
git commit -m "docs: record xianyu price panel flow"
```
