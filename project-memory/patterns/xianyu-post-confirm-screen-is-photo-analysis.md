# xianyu-post-confirm-screen-is-photo-analysis

Updated: 2026-03-13

## Rule
- Do not assume Xianyu opens the final listing form immediately after media confirmation.
- Treat the first post-confirm destination as a separate `photo_analysis` screen.

## Why
- On the Huawei tablet used for development, the app shows price-analysis and image-analysis content after `确定`.
- The exact text can vary between states like `照片模糊未识别到宝贝` and `价格计算中`, so flow logic should key off the shared analysis signals instead of one exact phrase.

## Applied In
- `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
