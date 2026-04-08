# xianyu default path is portrait form

Date: 2026-03-13

## Decision
- Use portrait mode plus `卖闲置 -> 发闲置` as the default entry path for Xianyu publishing on the Huawei tablet.

## Rationale
- Real-device verification showed that this path lands directly on the standard listing form.
- The older landscape route often enters the split-pane `闲鱼空间` analysis flow, which is more complex and less deterministic.
- The portrait form exposes the real publish fields needed for the next automation layer.

## Consequences
- `advance_to_listing_form()` should be the preferred flow helper for publish automation.
- Orientation control is now part of the Xianyu scenario contract on this tablet.
- The landscape space-analysis path remains available for investigation and as a fallback, but is no longer the main route.
