# xianyu publish form prefers portrait

Updated: 2026-03-13

## Pattern
- On the Huawei tablet, entering Xianyu publishing in portrait mode and tapping `发闲置` lands directly on the standard listing form.
- The same app in landscape tends to route through split-pane space-analysis UI that is harder to automate deterministically.
- Prefer forcing portrait before publish-form navigation.

## Why it matters
- Portrait mode gives a direct, form-based publish entrypoint with visible fields like `添加图片`, `价格设置`, and `发货方式`.
- This avoids unnecessary detours through `闲鱼空间` and reduces reliance on visual-only recovery steps.

## Applies to
- `minitap/mobile_use/scenarios/xianyu_publish/flow.py`
- real-device automation on the Huawei tablet serial `E2P6R22708000602`
