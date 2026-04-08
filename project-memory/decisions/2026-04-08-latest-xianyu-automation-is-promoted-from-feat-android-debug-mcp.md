# latest xianyu automation is promoted from feat/android-debug-mcp

Date: 2026-04-08

## Decision
- Treat the local `feat/android-debug-mcp` worktree as the source of truth for the latest Xianyu automation implementation on this machine.
- Promote the feature into `D:\github\mobile-use` by syncing the full branch diff, not by copying only the visible entry scripts.

## Context
- The user asked to find the latest Xianyu automation script and migrate the related files into `D:\github\mobile-use`.
- The placeholder repo at `E:\github2.0\xianyu` is an empty git repository with no commits, so it is not the source of the current automation.
- The local worktree branch `feat/android-debug-mcp` contains the full Xianyu publish stack and is ahead of `origin/feat/android-debug-mcp`.
- The latest local Xianyu commit found during migration is `f4d0fee` from 2026-03-20 (`fix(xianyu): detect shipping time toggle variants`).

## Consequences
- `main` in `D:\github\mobile-use` now carries the latest local Xianyu automation code, tests, plans, and project memory together.
- Future agents should inspect repo-local worktrees and local-only branch heads before assuming the latest automation lives in a dedicated `xianyu` repository or on `origin`.
