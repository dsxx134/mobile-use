# feishu-app-credentials-stay-in-local-env

Updated: 2026-03-14

## Pattern
- Keep `FEISHU_APP_ID` and `FEISHU_APP_SECRET` only in the worktree-local `.env`.
- Do not copy app credentials into tracked docs, plans, memory files, or committed config.

## Why
- The Xianyu publish scenario needs live Feishu credentials to read and update Bitable rows.
- Repo-local memory is committed and pushed, so it must never contain secrets.

## Reuse
- Apply the same rule to any later Feishu, Lark, or third-party app secret used by automation
  runners in this repository.
