# Xianyu Location Region Path Selection Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a deterministic flow helper that selects a hierarchical Xianyu location path, starting from the editor and ending back on the listing form after the final district selection.

**Architecture:** Build this as a pure flow-layer helper first, without Feishu mapping. Reuse the existing `location_panel` and `location_region_picker` states, then add a small path-selection loop that can handle the real-device quirk where a top-level region such as `上海` must be tapped twice: once to narrow, and once to expand the district list.

**Tech Stack:** Python, pytest, existing `XianyuPublishFlowService`, Android real-device probing.

---

### Task 1: Add failing tests for hierarchical region-path selection

**Files:**
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`

**Step 1: Write the failing tests**
- Add a flow test for `set_location_region_path("device-1", ["上海", "黄浦区"])` using a fake screen sequence:
  - `listing_form`
  - `location_panel`
  - full `location_region_picker`
  - narrowed picker with only `上海`
  - district picker with `黄浦区`
  - final `listing_form`
- Assert the taps are:
  - `location_entry`
  - `location_region_entry`
  - `上海`
  - `上海` again
  - `黄浦区`
- Add a negative test where the requested next segment is never found.

**Step 2: Run test to verify it fails**

Run:
```bash
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_flow.py -q
```

**Step 3: Write minimal implementation**
- Add a `set_location_region_path()` helper to `XianyuPublishFlowService`.
- Keep it scoped to hierarchical picker navigation only.

**Step 4: Run test to verify it passes**

Run the same command and confirm the new tests pass.

### Task 2: Add analyzer support only if required by tests

**Files:**
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`

**Step 1: Add any missing failing analyzer coverage**
- If the path-selection helper needs richer picker-state recognition, add the smallest failing test.

**Step 2: Run test to verify it fails**

Run:
```bash
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_flow.py -q
```

**Step 3: Write minimal implementation**
- Only broaden the analyzer if the helper truly needs extra targets or state distinctions.

**Step 4: Run test to verify it passes**

Run the same command and confirm the helper and analyzer stay green.

### Task 3: Verify on the real device and update docs/memory

**Files:**
- Modify: `README.md`
- Modify: `project-memory/projects/mobile-use.md`
- Modify: `project-memory/architecture/mobile-use.md`
- Modify: `project-memory/patterns/INDEX.md`
- Create: `project-memory/patterns/xianyu-location-region-picker-needs-two-taps-for-city-then-district.md`

**Step 1: Run full verification**

Run:
```bash
uv run pytest tests/mobile_use/scenarios/xianyu_publish -v
uv run ruff check
uv run python -m compileall minitap/mobile_use/scenarios/xianyu_publish
```

**Step 2: Run one real-device probe**
- Verify `["上海", "黄浦区"]` returns to `listing_form`.
- Record the real-device quirk:
  - first tap on `上海` narrows to only `上海`
  - second tap on `上海` expands districts
  - tapping `黄浦区` returns to the editor

**Step 3: Update docs and memory**
- Document the new flow helper and its current boundary.
- Record the two-tap city behavior as a reusable pattern.

**Step 4: Commit and push**

Suggested commits:
```bash
git commit -m "feat: add xianyu location region path flow"
git commit -m "docs: record xianyu location region path flow"
git push origin feat/android-debug-mcp
```
