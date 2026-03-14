# Xianyu Bitable Status Writeback Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** After a prepare-runner attempt, write the listing status back to Feishu Bitable so the table shows whether a row is `准备中`, `已就绪`, or `准备失败`, plus a failure reason when available.

**Architecture:** Keep this minimal. Reuse `FeishuBitableSource` as the read/write integration point, add a `失败原因` field name to settings, and let `XianyuPrepareRunner` update the record around its existing happy-path and exception-path flow. Preserve the current boundary that the runner still prepares the form rather than tapping final publish.

**Tech Stack:** Python, pytest, existing Xianyu flow/runner stack, Feishu Bitable HTTP API.

---

### Task 1: Add failing source tests for writeback

**Files:**
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_feishu_source.py`
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/feishu_source.py`
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/settings.py`

**Step 1: Write the failing tests**
- Add coverage showing the source can update a record status field.
- Add coverage showing a failure reason can be written alongside a failure status.

**Step 2: Run tests to verify they fail**

Run:
```bash
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_feishu_source.py -q
```

**Step 3: Write minimal implementation**
- Add the settings field name for `失败原因`.
- Add a writeback helper on `FeishuBitableSource`.

**Step 4: Run tests to verify they pass**

Run the same command and confirm it passes.

### Task 2: Add failing runner tests for status transitions

**Files:**
- Modify: `tests/mobile_use/scenarios/xianyu_publish/test_runner.py`
- Modify: `minitap/mobile_use/scenarios/xianyu_publish/runner.py`

**Step 1: Write the failing tests**
- Add coverage showing the runner marks a record `准备中` before device work starts.
- Add coverage showing the runner marks a record `已就绪` on success.
- Add coverage showing the runner marks a record `准备失败` with a failure reason if device work raises.

**Step 2: Run tests to verify they fail**

Run:
```bash
uv run pytest tests/mobile_use/scenarios/xianyu_publish/test_runner.py -q
```

**Step 3: Write minimal implementation**
- Wrap the prepare flow with source writeback calls.
- Re-raise failures after recording them.

**Step 4: Run tests to verify they pass**

Run the same command and confirm it passes.

### Task 3: Verify, document, and push

**Files:**
- Modify: `README.md`
- Modify: `project-memory/projects/mobile-use.md`
- Modify: `project-memory/architecture/mobile-use.md`
- Modify: `project-memory/patterns/`

**Step 1: Run full verification**

Run:
```bash
uv run pytest tests/mobile_use/scenarios/xianyu_publish -v
uv run ruff check
uv run python -m compileall minitap/mobile_use/scenarios/xianyu_publish
```

**Step 2: Update docs and memory**
- Document the new writeback statuses and the `失败原因` field.
- Record that the runner now closes the loop into Bitable without yet submitting the final publish button.

**Step 3: Commit and push**

Suggested commits:
```bash
git commit -m "feat: add xianyu bitable status writeback"
git commit -m "docs: record xianyu bitable status writeback"
git push origin feat/android-debug-mcp
```
