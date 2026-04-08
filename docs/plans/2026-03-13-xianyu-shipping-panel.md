# Xianyu Shipping Panel Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a deterministic shipping-method flow for the portrait `发闲置` form so automation can open the shipping panel, choose a supported mail option, confirm, and return to the listing form.

**Architecture:** Extend `XianyuFlowAnalyzer` so the portrait `listing_form` exposes a `shipping_entry` target and the Xianyu bottom-sheet shipping selector is recognized as `shipping_panel`. Then add `advance_listing_form_to_shipping_panel()` plus `set_shipping_method()` on `XianyuPublishFlowService`, with support for the verified mail-option modes first: `包邮`, `不包邮-按距离付费`, `不包邮-固定邮费`, and `无需邮寄`. Derive tap coordinates from the left-side radio icons rather than the multiline text block.

**Tech Stack:** Python 3.12, existing `AndroidDebugService`, `XianyuFlowAnalyzer`, `XianyuPublishFlowService`, pytest, real-device UI snapshots from the Huawei Android tablet.

---

### Task 1: TDD shipping-entry and shipping-panel recognition

**Files:**
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`

**Step 1: Write the failing tests**

Add tests like:

```python
def test_detects_listing_form_shipping_entry_target():
    ...


def test_detects_shipping_panel_with_mail_and_pickup_targets():
    ...
```

Expectations:
- `listing_form` exposes a `shipping_entry` target from the real `发货方式\n包邮` row
- `shipping_panel` is recognized when the screen contains:
  - `发货方式`
  - `确定`
  - the multiline mail-options block
  - the left-side mail-option radio icons
- returned targets include:
  - `shipping_confirm`
  - `shipping_option_mail_free`
  - `shipping_option_mail_distance`
  - `shipping_option_mail_fixed`
  - `shipping_option_no_mail`

**Step 2: Run the tests to verify RED**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_flow.py -k "shipping" -v
```

Expected: FAIL because shipping-panel support does not exist yet.

**Step 3: Implement minimal analyzer support**

Update `flow.py` so:
- `shipping_entry` is exposed on `listing_form`
- `shipping_panel` is recognized before generic `unknown`
- `shipping_option_mail_free` is derived from the multiline mail-options block
- `shipping_option_pickup` is read from the dedicated `买家自提` element

**Step 4: Re-run the tests to verify GREEN**

Run the same pytest command and expect PASS.

**Step 5: Commit**

```powershell
git add minitap/mobile_use/scenarios/xianyu_publish/flow.py tests/mobile_use/scenarios/xianyu_publish/test_flow.py
git commit -m "feat: detect xianyu shipping panel"
```

### Task 2: TDD shipping selection from the portrait form

**Files:**
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`

**Step 1: Write the failing tests**

Add tests like:

```python
def test_advance_listing_form_to_shipping_panel_taps_shipping_entry():
    ...


def test_set_shipping_method_selects_no_mail_and_confirms():
    ...


def test_set_shipping_method_selects_free_mail_from_multiline_panel():
    ...
```

Expectations:
- from `listing_form`, the flow taps `shipping_entry` and reaches `shipping_panel`
- `set_shipping_method("无需邮寄")` taps the verified no-mail radio icon, taps `确定`, and returns to `listing_form`
- `set_shipping_method("包邮")` can choose the verified mail-free radio icon when the current form is on another shipping mode
- if the current listing-form row already matches the requested method, the flow returns immediately without extra taps

**Step 2: Run the tests to verify RED**

Run the same pytest command and expect FAIL.

**Step 3: Implement minimal flow support**

Add:
- `normalize_shipping_method(...)`
- `advance_listing_form_to_shipping_panel(...)`
- `set_shipping_method(...)`

Rules:
- support the real-device values `包邮`, `不包邮-按距离付费`, `不包邮-固定邮费`, and `无需邮寄`
- derive the current mode from the listing-form `shipping_entry` text when possible
- keep the scope to choosing and confirming the shipping method only

**Step 4: Re-run the tests to verify GREEN**

Run the same pytest command and expect PASS.

**Step 5: Commit**

```powershell
git add minitap/mobile_use/scenarios/xianyu_publish/flow.py tests/mobile_use/scenarios/xianyu_publish/test_flow.py
git commit -m "feat: set xianyu shipping method from listing form"
```

### Task 3: Document, remember, and verify the shipping flow

**Files:**
- Modify: `README.md`
- Modify: `project-memory/projects/mobile-use.md`
- Modify: `project-memory/architecture/mobile-use.md`
- Modify: `project-memory/patterns/INDEX.md`
- Create: `project-memory/patterns/xianyu-shipping-panel-uses-bottom-sheet-options.md`

**Step 1: Update docs and memory**

Document that:
- the portrait form opens a bottom-sheet shipping selector from `发货方式`
- the supported mail modes are selected by the left-side radio icons rather than the multiline text block
- the confirm step can briefly linger on `shipping_panel` or a status-only `unknown` overlay before returning to the form
- the flow now supports deterministic shipping selection and confirmation

**Step 2: Run batch verification**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/scenarios/xianyu_publish -v
uv run ruff check
uv run python -m compileall minitap/mobile_use/scenarios/xianyu_publish
```

Plus one real-device probe that:
- opens the shipping panel from `listing_form`
- switches to `无需邮寄`
- switches back to `包邮`
- confirms the form is back on `包邮`

**Step 3: Commit**

```powershell
git add README.md project-memory/projects/mobile-use.md project-memory/architecture/mobile-use.md project-memory/patterns/INDEX.md project-memory/patterns/xianyu-shipping-panel-uses-bottom-sheet-options.md
git commit -m "docs: record xianyu shipping panel flow"
```
