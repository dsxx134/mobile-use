# xianyu review mode stops at manual publish

Date: 2026-03-14

## Decision
- Add a review mode after the existing prepare slice and write the row back as `待人工发布`
  instead of tapping the final `发布` button automatically.

## Context
- The Huawei-tablet automation can already prepare a row into a valid editor state, but post-submit
  success navigation is not yet live-verified.
- Shipping a direct auto-submit step before we can recognize a real success page would make a
  wrong click far more expensive than a conservative stop point.
- The business need right now is to know whether a row is truly ready for a human final check.

## Consequences
- Operators now get a safer checkpoint than `已就绪`: the row has been prepared and the visible
  `发布` target is still present on a supported editor screen.
- The code path toward future auto-submit is still being built, but the default live runner remains
  non-submitting.
