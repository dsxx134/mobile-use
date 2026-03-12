# Personal GitHub Only

Date: 2026-03-12

## Decision
- Use only repositories under the user's GitHub account for this project.
- Keep `origin=https://github.com/dsxx134/mobile-use.git` as the sole active remote.
- Do not sync the original `minitap-ai/mobile-use` repository.
- If a writable remote is needed in the future, create a new repository under `dsxx134` or use an existing one there.

## Why
- The original repository is not administratively controlled by the user.
- A single writable remote avoids accidental pushes or syncs to the wrong place.
- Future agents need a simple, stable rule for milestone pushes and branch publication.

## Operational Impact
- Push all milestones and feature branches to the personal repository only.
- Leave the original repository out of the local remote configuration unless the user explicitly requests otherwise.
- Treat personal-repo creation or reuse as the default fallback whenever write access is missing.
