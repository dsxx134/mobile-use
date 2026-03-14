# xianyu live prepare entrypoint is scripted

Date: 2026-03-14

## Decision
- The verified Feishu-backed prepare flow should be exposed as a dedicated script entrypoint:
  `scripts/xianyu_prepare_runner_live.py`
- The script should own the live orchestration glue that is not part of the pure business runner:
  - resolve Android serial from `XIANYU_ANDROID_SERIAL` or `--serial`
  - build `FeishuBitableSource`, `XianyuMediaSyncService`, `XianyuPublishFlowService`, and
    `XianyuPrepareRunner` with the authenticated Feishu download hook
  - preheat Xianyu back to the portrait `发闲置` form before running the deterministic prepare slice

## Context
- The business runner is intentionally generic and testable, but the real Huawei-tablet path also
  needs live-device concerns such as serial selection and an initial form preheat.
- The previously verified live run depended on ad-hoc inline Python that was too easy to forget or
  mis-assemble.
- The development machine can have both the Huawei tablet and an Android emulator attached, so the
  live entrypoint must handle ambiguous ADB device selection safely.

## Consequences
- Operators now have a one-command way to run the verified Feishu-backed prepare slice.
- The authenticated Feishu attachment download path is encoded once instead of being rebuilt ad hoc.
- The live orchestration can absorb Huawei-tablet startup flakiness without complicating the core
  `XianyuPrepareRunner`.
