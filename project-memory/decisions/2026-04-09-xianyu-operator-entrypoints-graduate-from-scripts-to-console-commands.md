# xianyu operator entrypoints graduate from scripts to console commands

Date: 2026-04-09

## Decision
- Promote the main Xianyu operator flows from repo-local `scripts/*.py` wrappers into installable
  `project.scripts` entrypoints.

## Scope
- `mobile-use-xianyu-prepare`
- `mobile-use-xianyu-review`
- `mobile-use-xianyu-publish`
- `mobile-use-xianyu-publish-auto`
- `mobile-use-xianyu-publish-schedule`
- keep the old `scripts/xianyu_*.py` files as thin compatibility wrappers

## Why
- Operators should not need repo-relative script paths once a workflow becomes stable enough for
  repeated use.
- Installable commands make downstream wrapper repos, schedulers, and human operators all call the
  same supported surface.
- Keeping legacy script files as wrappers avoids breaking existing local habits while letting the
  real behavior live inside the package.

## Consequence
- README examples should prefer the installable commands.
- Future business/product packaging can wrap the package entrypoints directly instead of importing
  ad-hoc script files.
