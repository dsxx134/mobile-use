# xianyu-media-selection-should-switch-to-a-dedicated-album

Updated: 2026-03-13

## Rule
- Before tapping `选择` in the Xianyu media picker, switch the source away from `所有文件` and into a dedicated folder such as `XianyuPublish`.

## Why
- `所有文件` can surface unrelated screenshots and videos, which makes selection nondeterministic.
- A dedicated folder keeps media ordering aligned with the files pushed by `XianyuMediaSyncService`.

## Applied In
- `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
