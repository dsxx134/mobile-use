# Xianyu Scrolled Metadata Recovery Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Keep scrolled Xianyu metadata states classified as `metadata_panel` and allow downstream field flows like location, price, and shipping to continue from that state when their targets are visible.

**Architecture:** Broaden the `metadata_panel` detector so it no longer depends on the upper-form controls being visible. When price/shipping/location rows are visible inside the same scrolled editor state, extract their targets into the `metadata_panel` analysis. Then let the existing panel-entry helpers accept `metadata_panel` as a valid starting state for those rows.

**Tech Stack:** Python, pytest, existing `XianyuFlowAnalyzer`, `XianyuPublishFlowService`, Android real-device probing.

---

### Task 1: Add failing analyzer tests for scrolled metadata states

**Files:**
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`

**Step 1: Write the failing tests**
- Add a scrolled metadata fixture where:
  - `发闲置` header is still visible
  - metadata chips are visible
  - `价格设置` / `发货方式` / `选择位置` are visible
  - top controls like `添加图片` are missing
- Assert this state is still classified as `metadata_panel`, not `publish_chooser`.
- Assert the scrolled metadata analysis exposes `price_entry`, `shipping_entry`, and `location_entry`.

**Step 2: Run test to verify it fails**

Run:
```bash
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_flow.py -q
```

**Step 3: Write minimal implementation**
- Relax `metadata_panel` detection to key off metadata rows/chips rather than upper-form controls.
- Reuse existing entry extraction for `price_entry`, `shipping_entry`, and `location_entry` when those rows are visible.

**Step 4: Run test to verify it passes**

Run the same command and confirm the new scrolled-state tests pass.

### Task 2: Add failing flow tests for opening lower panels from metadata_panel

**Files:**
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`

**Step 1: Write the failing tests**
- Add flow coverage showing:
  - `advance_listing_form_to_location_panel()` can start from `metadata_panel`
  - `advance_listing_form_to_price_panel()` can start from `metadata_panel`
  - `advance_listing_form_to_shipping_panel()` can start from `metadata_panel`

**Step 2: Run tests to verify they fail**

Run:
```bash
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_flow.py -q
```

**Step 3: Write minimal implementation**
- Accept `metadata_panel` as a valid source state in those three helpers when the needed target is present.

**Step 4: Run tests to verify they pass**

Run the same command and confirm the helpers now pass from either state.

### Task 3: Verify, document, and push

**Files:**
- Modify: `README.md`
- Modify: `project-memory/projects/mobile-use.md`
- Modify: `project-memory/architecture/mobile-use.md`
- Modify: `project-memory/patterns/INDEX.md`
- Create: `project-memory/patterns/xianyu-scrolled-metadata-still-belongs-to-editor.md`

**Step 1: Run full verification**

Run:
```bash
uv run pytest tests/mobile_use/scenarios/xianyu_publish -v
uv run ruff check
uv run python -m compileall minitap/mobile_use/scenarios/xianyu_publish
```

**Step 2: Do one real-device probe**
- Confirm that a scrolled editor state with metadata chips plus price/location rows is recognized as `metadata_panel`.
- Confirm at least one lower-row bridge such as `选择位置` still opens its downstream panel from that state.

**Step 3: Update docs and memory**
- Record that scrolled metadata pages remain part of the editor flow and should not fall back to `publish_chooser`.
- Record the current boundary that the location region picker still becomes hierarchical after selecting a top-level region.

**Step 4: Commit and push**

Suggested commits:
```bash
git commit -m "feat: recover scrolled xianyu metadata panel state"
git commit -m "docs: record scrolled xianyu metadata recovery"
git push origin feat/android-debug-mcp
```
