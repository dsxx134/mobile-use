# xianyu-home-recovery-uses-explicit-main-activity

Updated: 2026-03-12

## Rule
- Recover the Xianyu app to its home tab with:
  - `am start -n com.taobao.idlefish/com.taobao.idlefish.maincontainer.activity.MainActivity`
- Do not rely only on generic `app_start(package)` when deterministic publish automation needs a known home state.

## Why
- On the Huawei tablet used for development, generic package launch could bring a `CategoryPageActivity` task to the front instead of the home tab.
- Deterministic flows need a stable starting screen before tapping `卖闲置`.

## Applied In
- `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
