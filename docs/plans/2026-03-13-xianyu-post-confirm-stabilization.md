# Xianyu Post-Confirm Stabilization Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make `select_cover_image()` wait deterministically until the post-confirm media flow leaves the album picker and reaches a stable downstream screen such as `photo_analysis`, instead of returning too early on real Android devices.

**Architecture:** Keep the existing analyzer heuristics and fix the problem at the flow-service layer. Add a dedicated post-confirm polling helper that treats two states as transitional after tapping `确定`: blank/loading overlays and the lingering album-picker tail state where the picker still shows `预览 (1)` and `确定`. Return only when the flow has advanced to a non-picker screen, or fail clearly if it never does.

**Tech Stack:** Python 3.12, existing `AndroidDebugService`, `XianyuFlowAnalyzer`, pytest, condition-based polling.

---

### Task 1: TDD the post-confirm transition bug

**Files:**
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`

**Step 1: Write the failing tests**

Extend `tests/mobile_use/scenarios/xianyu_publish/test_flow.py` with tests for:

```python
def test_select_cover_image_waits_until_album_picker_tail_transitions_to_photo_analysis():
    ...


def test_select_cover_image_raises_when_post_confirm_flow_never_leaves_album_picker():
    ...
```

Expectations:
- After tapping `确定`, if the first few snapshots still look like an album picker with `预览 (1)` and `确定`, the service keeps polling instead of returning that picker snapshot.
- If the post-confirm flow never leaves that state within the poll budget, the service raises a clear `RuntimeError` instead of silently returning the wrong screen.

**Step 2: Run the tests to verify RED**

Run:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_flow.py -v
```

Expected: FAIL because the current implementation returns too early after `album_confirm`.

**Step 3: Implement the minimal flow changes**

In `minitap/mobile_use/scenarios/xianyu_publish/flow.py`:

- Add a helper that identifies the lingering post-confirm album-picker state
- Add a helper that polls until the flow leaves transitional states after confirm
- Update `select_cover_image()` to use that post-confirm helper after tapping `album_confirm`

Rules:
- Transitional states after confirm are:
  - loading overlays already handled by `_wait_for_non_loading_screen()`
  - album-picker snapshots that still show `album_confirm`
- Stable downstream states include `photo_analysis` and any future non-picker form screen
- Timeout should raise an explicit error mentioning the last screen name

**Step 4: Re-run the tests to verify GREEN**

Run the same `pytest` command and expect PASS.

**Step 5: Commit**

```powershell
git add minitap/mobile_use/scenarios/xianyu_publish/flow.py tests/mobile_use/scenarios/xianyu_publish/test_flow.py
git commit -m "fix: wait for xianyu post-confirm screen transition"
```

### Task 2: Re-verify the scenario and refresh smoke/docs

**Files:**
- Modify: `README.md`
- Modify: `scripts/xianyu_publish_flow_smoke.py`

**Step 1: Refresh the smoke output if needed**

If the script currently hides the boundary, make it print:
- detected screen name
- target keys
- current album name

**Step 2: Update README**

Document that:
- real devices can linger on an `album_picker` tail state after tapping `确定`
- the flow now waits until that transient state resolves before returning
- the next functional boundary is still the `photo_analysis` screen

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
- flow tests pass
- scenario tests pass
- `ruff check` passes
- smoke script still runs on the connected device
- compileall succeeds

**Step 4: Commit**

```powershell
git add README.md scripts/xianyu_publish_flow_smoke.py
git commit -m "docs: add xianyu post-confirm stabilization notes"
```
