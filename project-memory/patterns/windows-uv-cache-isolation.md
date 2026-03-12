# windows-uv-cache-isolation

Updated: 2026-03-12

## Problem
- `uv sync`, `uv run`, or `uv build` can fail on Windows with cache cleanup errors such as `os error 32` or transient cache rename issues.

## Working Pattern

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv sync --dev
uv run pytest -m "not ios_simulator"
uv build
```

## Notes
- This worked in the main workspace and in the project-local worktree.
- Use it by default for Windows work on this repository.
