# xianyu operator entrypoints should live in package modules

Updated: 2026-04-09

## Pattern
- Put stable Xianyu operator CLIs under `minitap/mobile_use/scenarios/xianyu_publish/*.py`.
- Keep repo-root `scripts/xianyu_*.py` files as one-line wrappers that delegate to the package
  `main()` functions.

## Why
- The package modules are importable by `project.scripts`, tests, and future wrapper repos.
- Thin script wrappers preserve backwards compatibility without duplicating parsing logic.
- This keeps documentation, entrypoints, and automation on one code path.

## Notes
- Favor `run_*_cli(...)` helpers for testable argument forwarding.
- Prefer non-zero exit codes for machine-observable batch/schedule failures.
