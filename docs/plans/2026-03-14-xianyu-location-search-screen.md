# Xianyu Location Search Screen Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add deterministic support for the Xianyu location search screen so the flow can enter the search UI, fill the focused address field with `set_text()`, and select a visible result row.

**Architecture:** Keep this slice narrowly scoped to the flow and Android UI client layers. Do not wire location writeback into `XianyuPrepareRunner` yet. Instead, add screen analysis for the search UI, add a targeted focused-EditText text-entry helper, and expose a deterministic flow helper that selects a visible search result while documenting that visible persistence is still unresolved.

**Tech Stack:** Python, pytest, `uiautomator2`, existing `XianyuFlowAnalyzer`, `XianyuPublishFlowService`, Android real-device probing.

---

### Task 1: Add failing analyzer tests for the Xianyu location search screen

**Files:**
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`

**Step 1: Write the failing tests**
- Add a fixture for the location search UI that includes:
  - a focused `android.widget.EditText` with `hint="搜索地址"`
  - a `取消` button
  - visible result rows such as `上海虹桥站\n新虹街道申贵路1500号`
- Assert the analyzer classifies this screen as a dedicated search state.
- Assert the analysis exposes:
  - a target for the focused search field
  - a target for `取消`
  - targets for the visible search results

**Step 2: Run test to verify it fails**

Run:
```bash
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_flow.py::test_detects_location_search_screen_targets -q
```

**Step 3: Write minimal implementation**
- Extend the analyzer with the smallest possible search-screen detection and result-target extraction.

**Step 4: Run test to verify it passes**

Run the same command and confirm it passes.

### Task 2: Add failing flow tests for focused address input and result selection

**Files:**
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`
- Modify: `minitap/mobile_use/clients/ui_automator_client.py`
- Modify: `minitap/mobile_use/mcp/android_debug_service.py`
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`

**Step 1: Write the failing tests**
- Add a focused unit test for a new UI client helper that sets text on the focused `EditText` without using FastInputIME.
- Add a flow test that:
  - starts from `location_panel`
  - taps `搜索地址`
  - fills a search query through the new helper
  - taps the first visible result row
  - returns to the next visible Xianyu screen

**Step 2: Run tests to verify they fail**

Run:
```bash
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_flow.py -q
```

**Step 3: Write minimal implementation**
- Add a narrow UI client helper such as `set_focused_text()`.
- Expose it through `AndroidDebugService` with a dedicated method.
- Add a flow helper such as `search_location_and_select_result()` that uses the dedicated helper.

**Step 4: Run tests to verify they pass**

Run the same command and confirm the new tests pass.

### Task 3: Verify on the real device and update docs/memory

**Files:**
- Modify: `README.md`
- Modify: `project-memory/projects/mobile-use.md`
- Modify: `project-memory/architecture/mobile-use.md`
- Modify: `project-memory/decisions/INDEX.md`
- Modify: `project-memory/patterns/INDEX.md`
- Create: `project-memory/patterns/xianyu-location-search-needs-focused-edittext-set-text.md`

**Step 1: Run full verification**

Run:
```bash
uv run pytest tests/mobile_use/scenarios/xianyu_publish -v
uv run ruff check
uv run python -m compileall minitap/mobile_use/scenarios/xianyu_publish minitap/mobile_use/mcp minitap/mobile_use/clients
```

**Step 2: Run one real-device probe**
- Verify that:
  - tapping `搜索地址` reaches the search UI
  - FastInputIME text entry still no-ops there
  - focused `EditText.set_text()` surfaces visible result rows
  - tapping a visible result returns to the next screen

**Step 3: Update docs and memory**
- Document the search-screen helper and its current boundary.
- Record the reusable pattern that this screen needs focused-EditText `set_text()` instead of the existing FastInputIME path.

**Step 4: Commit and push**

Suggested commits:
```bash
git commit -m "feat: add xianyu location search flow"
git commit -m "docs: record xianyu location search flow"
git push origin feat/android-debug-mcp
```
