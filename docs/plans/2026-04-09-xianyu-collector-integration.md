# Xianyu Collector Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Integrate the reconstructed Xianyu collector capability into `mobile-use` as a self-contained collector package with tests and a runnable CLI entrypoint.

**Architecture:** Keep the collector isolated from the existing publish-flow stack by vendoring it under `minitap.mobile_use.collectors.xianyu_collector`. Preserve its current layered design (`session -> signer/api -> service -> repository`) and only add the minimum repo-level integration points: dependencies, script entrypoint, tests, and project memory.

**Tech Stack:** Python 3.12, pytest, sqlite3, requests, optional DrissionPage.

---

### Task 1: Establish integration baseline

**Files:**
- Create: `tests/mobile_use/collectors/xianyu_collector/...`
- Verify: `pyproject.toml`

**Steps:**
1. Copy the collector test suite into `mobile-use` under `tests/mobile_use/collectors/xianyu_collector/`.
2. Rewrite imports from `xianyu_collector...` to `minitap.mobile_use.collectors.xianyu_collector...`.
3. Run only the copied tests.
4. Confirm they fail because the package is not yet present.

### Task 2: Vendor the collector source

**Files:**
- Create: `minitap/mobile_use/collectors/__init__.py`
- Create: `minitap/mobile_use/collectors/xianyu_collector/...`

**Steps:**
1. Copy source files from the reconstructed collector project into the new package path.
2. Rewrite imports to the new package path.
3. Exclude `__pycache__` and non-source artifacts.
4. Keep the runtime and CLI behavior unchanged unless needed for repo compatibility.

### Task 3: Wire repo-level integration

**Files:**
- Modify: `pyproject.toml`

**Steps:**
1. Add any missing dependency required by the collector (`requests`).
2. Add a dedicated script entrypoint for the collector CLI.
3. Keep DrissionPage optional by leaving its import lazy in runtime-only code.

### Task 4: Verify and fix

**Files:**
- Test: `tests/mobile_use/collectors/xianyu_collector/...`

**Steps:**
1. Run the collector-only test suite.
2. Fix any package-path or dependency issues.
3. Re-run until green.

### Task 5: Record project memory

**Files:**
- Modify: `project-memory/projects/mobile-use.md`
- Modify: `project-memory/architecture/mobile-use.md`
- Modify: `project-memory/decisions/INDEX.md`
- Modify: `project-memory/patterns/INDEX.md`

**Steps:**
1. Record that the collector capability was integrated as a separate package.
2. Note the source of truth and package boundary.
3. Record the reusable migration pattern if useful.
