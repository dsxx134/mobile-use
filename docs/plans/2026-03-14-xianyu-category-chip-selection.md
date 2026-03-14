# Xianyu Category Chip Selection Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add deterministic support for selecting a visible category chip from the Xianyu metadata panel and wire one optional Bitable category field into the prepare runner.

**Architecture:** Extend the existing `metadata_panel` analyzer instead of opening a new class/tree flow. Extract visible category chips from the current panel, add a small flow helper that taps one chip and verifies the selected state, then let the prepare runner apply the category before the already-supported condition/source fields.

**Tech Stack:** Python, Pydantic, pytest, existing `AndroidDebugService`, Xianyu flow analyzer/service, Feishu Bitable source.

---

### Task 1: Add failing model/source/runner tests for optional category field

**Files:**
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_models.py`
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_feishu_source.py`
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_runner.py`
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/models.py`
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/settings.py`
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/feishu_source.py`
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/runner.py`

**Step 1: Write the failing tests**
- Assert `ListingDraft` accepts an optional `category`.
- Assert `FeishuBitableSource` maps the configured category field into `ListingDraft.category`.
- Assert `XianyuPrepareRunner` calls `flow.set_item_category()` before condition/source when the category exists.

**Step 2: Run tests to verify they fail**

Run:
```bash
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_models.py tests/mobile_use/scenarios/xianyu_publish/test_feishu_source.py tests/mobile_use/scenarios/xianyu_publish/test_runner.py -q
```

**Step 3: Write minimal implementation**
- Add `category: str | None = None` to `ListingDraft`.
- Add `category_field_name` to settings.
- Map the optional field in `FeishuBitableSource`.
- Call `set_item_category()` from `XianyuPrepareRunner`.

**Step 4: Run the tests to verify they pass**

Run the same command and confirm the new category assertions pass.

### Task 2: Add failing analyzer and flow tests for metadata-panel category chips

**Files:**
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_flow.py`
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/flow.py`

**Step 1: Write the failing tests**
- Add analyzer coverage for extracting visible category chip targets from `metadata_panel`.
- Add flow coverage for:
  - `advance_listing_form_to_metadata_panel()` plus category targets
  - `set_item_category()` selecting a chip and verifying the selected state
  - immediate return when the desired category is already selected

**Step 2: Run tests to verify they fail**

Run:
```bash
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_flow.py -q
```

**Step 3: Write minimal implementation**
- Extend analyzer target extraction to classify visible category chips on the metadata panel.
- Add `normalize_item_category()` only for empty-string rejection; matching remains exact against visible chips.
- Implement `set_item_category()` on top of the same selected-chip verification pattern used by condition/source.

**Step 4: Run the tests to verify they pass**

Run the same command and confirm the new category tests pass.

### Task 3: Verify the full scenario slice and update docs/memory

**Files:**
- Modify: `README.md`
- Modify: `project-memory/projects/mobile-use.md`
- Modify: `project-memory/architecture/mobile-use.md`
- Modify: `project-memory/patterns/INDEX.md`
- Create: `project-memory/patterns/xianyu-category-selection-uses-visible-chips.md`
- Modify: `project-memory/projects/INDEX.md`
- Modify: `project-memory/architecture/INDEX.md`

**Step 1: Run full verification**

Run:
```bash
uv run pytest tests/mobile_use/scenarios/xianyu_publish -v
uv run ruff check
uv run python -m compileall minitap/mobile_use/scenarios/xianyu_publish
```

**Step 2: Run one real-device probe**
- Verify the current tablet page is `metadata_panel`.
- Verify selecting a visible category chip ends on `metadata_panel` with an `已选中...` target.

**Step 3: Update docs and project memory**
- Document that category support is limited to currently visible metadata chips.
- Record the real-device behavior that category chip taps remain in place and confirm via `已选中...`.

**Step 4: Commit and push**

Suggested commits:
```bash
git commit -m "feat: add xianyu category chip selection"
git commit -m "docs: record xianyu category chip flow"
git push origin feat/android-debug-mcp
```
