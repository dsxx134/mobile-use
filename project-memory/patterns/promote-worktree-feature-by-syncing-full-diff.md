# promote-worktree-feature-by-syncing-full-diff

Updated: 2026-04-08

## Pattern
- When a feature has been developed in a repo-local worktree branch, migrate it into the primary working tree by syncing the branch's full diff instead of copying a few top-level scripts.
- Include dependent code, tests, docs, and project-memory updates in the same promotion step.

## When To Use
- The "latest" implementation lives in a local worktree or branch instead of the current working tree.
- The feature surface spans package code, CLI entrypoints, tests, and operational documentation.
- A placeholder repository exists but does not actually contain the current implementation.

## Why
- Prevents partial migrations where entry scripts arrive without the scenario package, settings, tests, or documentation they depend on.
- Preserves the branch's architectural context and operational memory when promoting work into the main tree.
