# xianyu failure evidence stays local with path writeback

Date: 2026-03-15

## Decision
- Keep Xianyu failure evidence on the local workstation instead of uploading screenshots or XML
  snapshots into Feishu directly.
- When a live prepare or publish step fails, capture local artifacts and write their absolute paths
  back to dedicated Bitable text fields.

## Why
- Local path writeback is the smallest reliable production hardening step.
- It avoids introducing a second file-upload pipeline just for failure triage.
- It keeps the operator-facing table useful immediately while preserving raw evidence on disk.

## Consequences
- Operators can jump from the Feishu row to the local evidence directory quickly.
- Evidence remains machine-local, so another workstation will not be able to open those paths.
- If future production use needs cross-machine access, the next step is a proper artifact upload
  target, not more text fields.
