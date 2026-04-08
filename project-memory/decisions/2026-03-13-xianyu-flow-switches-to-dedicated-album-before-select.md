# Xianyu Flow Switches To Dedicated Album Before Select

Date: 2026-03-13

## Decision
- Extend the deterministic Xianyu flow so media selection switches from the default `所有文件` source into a dedicated folder such as `XianyuPublish` before tapping `选择`.
- Treat the screen after `确定` as `photo_analysis`, not as the final listing form.

## Why
- The default source can expose unrelated screenshots and produce unstable behavior.
- Real-device inspection showed the current app version routes through a photo-analysis stage whose copy changes across runs, so downstream form filling must start after that state is handled explicitly.

## Operational Impact
- Future publish-flow work should assume a dedicated album source already exists on device.
- The next batch should focus on what actions are available from `photo_analysis` to reach the real edit form.
