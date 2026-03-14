# xianyu metadata panel is distinct from publish chooser

Date: 2026-03-14

## Decision
- Treat the expanded portrait-form metadata/spec page as a dedicated `metadata_panel` screen in
  `XianyuFlowAnalyzer` instead of letting it fall through to the looser `publish_chooser` rule.

## Why
- On the Huawei tablet, tapping the large metadata row from the portrait `发闲置` form keeps the
  user inside the same publishing flow and exposes chip-style fields such as `成色` and `商品来源`.
- That page still shows `关闭` and `发闲置`, so the previous `publish_chooser` heuristic was too
  broad and misclassified it.
- Real-device probing showed metadata interactions stay on this page and confirm themselves through
  visible text changes from `可选...` to `已选中...`.

## Consequences
- Screen detection for this state must run before the publish-chooser rule.
- Deterministic metadata helpers can now target chip selections without leaving the form flow.
- The prepare runner can consume optional Feishu fields such as `成色` and `商品来源`.
