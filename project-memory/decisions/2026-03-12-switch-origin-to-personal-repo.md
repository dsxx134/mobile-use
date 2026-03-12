# Switch Origin To Personal Repo

Date: 2026-03-12

## Decision
- Create `dsxx134/mobile-use` as the writable GitHub repository for this project.
- Rename the original remote to `upstream`.
- Use the personal repository as default `origin` for future pushes and milestone backups.

## Why
- The original repository `minitap-ai/mobile-use` only grants `READ` permission to `dsxx134`.
- Ongoing automation work needs reliable push access at important milestones.
- Keeping the original repository as `upstream` preserves a clean sync path without blocking daily work.

## Operational Impact
- Future branches should be pushed to `origin` by default.
- Pull or compare with the original project through `upstream`.
- Agents working in this repository should assume `origin=https://github.com/dsxx134/mobile-use.git`.
