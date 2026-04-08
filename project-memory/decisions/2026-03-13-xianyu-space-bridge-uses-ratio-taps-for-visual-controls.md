# xianyu space bridge uses ratio taps for visual controls

Date: 2026-03-13

## Decision
- Implement the Xianyu `photo_analysis -> publish_chooser` bridge in `XianyuPublishFlowService` using normalized ratio taps for the two visual-only controls that the accessibility tree does not expose on the Huawei tablet:
  - the initial analysis-overlay dismiss control
  - the `发宝贝` button on the `space_items_empty` page

## Rationale
- Real-device probing showed that both controls are visible and stable on screen, but absent from the flattened accessibility elements.
- The `宝贝` tab itself is accessible, so only the truly visual-only steps need coordinate fallback.
- Normalized ratios are less brittle than raw absolute pixels and remain tied to the current screen size at runtime.

## Consequences
- The flow can deterministically recover from `photo_analysis` to the standard publish chooser.
- The bridge is still tablet-layout-specific and may need different ratios on a different device class or orientation.
- Future work can keep using accessibility targets where available and reserve ratio taps for confirmed visual-only controls.
