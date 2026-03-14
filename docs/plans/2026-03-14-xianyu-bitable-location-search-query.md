# Xianyu Bitable Location Search Query Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Let Xianyu listings optionally carry a preset address search query from Feishu Bitable and apply it through the existing location search helper during prepare-runner execution.

**Architecture:** Keep this slice narrow. Add one optional field to `ListingDraft`, map it from Bitable, and have `XianyuPrepareRunner` call the existing `search_location_and_select_result()` helper when the field is present. Preserve the documented boundary that visible location writeback is still unresolved.

**Tech Stack:** Python, pytest, existing Xianyu flow/runner stack, Feishu Bitable mapping.

---

### Task 1: Add failing data-layer tests

**Files:**
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_models.py`
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_feishu_source.py`
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/models.py`
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/feishu_source.py`
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/settings.py`

**Step 1: Write the failing tests**
- Add coverage showing `ListingDraft` accepts an optional preset address search query.
- Add coverage showing `FeishuBitableSource` maps a Bitable field like `预设地址` into that draft field.

**Step 2: Run tests to verify they fail**

Run:
```bash
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_models.py tests/mobile_use/scenarios/xianyu_publish/test_feishu_source.py -q
```

**Step 3: Write minimal implementation**
- Add the optional field to `ListingDraft`.
- Add a matching settings field name.
- Map the Bitable field into the draft.

**Step 4: Run tests to verify they pass**

Run the same command and confirm they pass.

### Task 2: Add failing runner test for optional location search application

**Files:**
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_runner.py`
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/runner.py`

**Step 1: Write the failing test**
- Add a runner test showing that when the draft contains a preset address search query:
  - the runner still performs the existing prepare steps
  - then calls `flow.search_location_and_select_result(serial, query)`

**Step 2: Run test to verify it fails**

Run:
```bash
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_runner.py::test_prepare_first_publishable_listing_applies_optional_location_search_query -q
```

**Step 3: Write minimal implementation**
- Call the existing flow helper from `XianyuPrepareRunner` when the optional field is present.

**Step 4: Run test to verify it passes**

Run the same command and confirm it passes.

### Task 3: Verify, document, and push

**Files:**
- Modify: `README.md`
- Modify: `project-memory/projects/mobile-use.md`
- Modify: `project-memory/architecture/mobile-use.md`
- Modify: `project-memory/decisions/INDEX.md`
- Create: `project-memory/decisions/2026-03-14-xianyu-runner-can-apply-best-effort-location-search-query.md`

**Step 1: Run full verification**

Run:
```bash
uv run pytest tests/mobile_use/scenarios/xianyu_publish tests/mobile_use/mcp -v
uv run ruff check
uv run python -m compileall minitap/mobile_use/scenarios/xianyu_publish minitap/mobile_use/mcp minitap/mobile_use/clients
```

**Step 2: Do one real-device probe**
- Confirm a manually stepped prepare flow can call the location search helper and return to the editor.
- Reconfirm that the visible location row still does not show a stable writeback.

**Step 3: Update docs and memory**
- Document the new Bitable field and runner behavior.
- Record that runner support is best-effort and does not yet imply visible persistence.

**Step 4: Commit and push**

Suggested commits:
```bash
git commit -m "feat: add xianyu bitable location search query"
git commit -m "docs: record xianyu bitable location search query"
git push origin feat/android-debug-mcp
```
