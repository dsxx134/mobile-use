# xianyu-ai-helper-rows-are-forbidden-tap-targets

Updated: 2026-03-15

## Pattern
- Treat Xianyu assistant rows such as `AI帮你写`, `AI帮你润色`, `AI生成仅供参考`, and `小艺帮写` as forbidden tap targets.
- If a computed `TapTarget` resolves to one of those helper rows, fail fast instead of tapping it.

## Why
- On the Huawei tablet, tapping the assistant row opens a side flow that stalls the deterministic
  publish runner instead of advancing the form.
- Those controls are advisory helpers, not required publish inputs.
- Failing fast is safer than silently letting the automation drift into an unsupported AI subflow.

## Implementation Notes
- `XianyuPublishFlowService._tap_target()` and `_long_press_target()` now reject assistant-text
  targets before issuing the Android tap.
- The regression test `test_tap_target_rejects_ai_assistant_entry` proves the tap never reaches the
  fake Android service.
