# primary working copy moved to e-drive xianyu path

Date: 2026-04-09

## Decision
- Treat `E:\github2.0\xianyu` as the primary working copy for this project from now on.
- Stop treating `D:\github\mobile-use` as the active place for new commits; keep it only as a legacy clone/worktree source if needed.

## Why
- The D-drive repository was already in a clean, pushed, reproducible state (`main` at `0d3012d`), so it formed a safe migration checkpoint.
- The old `E:\github2.0\xianyu` recovery workspace was not an independent git repository and was nested under the unrelated parent repo `E:\github2.0`, which made future git operations unsafe.
- Re-establishing the project as an independent repository directly at `E:\github2.0\xianyu` removes that git-boundary ambiguity.

## Consequence
- All future git maintenance should happen inside `E:\github2.0\xianyu`.
- The previous recovery workspace was preserved separately at `E:\github2.0\xianyu-recovery-backup-20260409-152943` for later selective import if needed.
