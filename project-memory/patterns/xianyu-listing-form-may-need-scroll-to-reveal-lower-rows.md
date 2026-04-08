# xianyu listing form may need scroll to reveal lower rows

Date: 2026-03-18

## Pattern
- When a required row such as `发货时间/发货时效` is missing on the listing form, scroll the
  portrait editor area before failing the flow.
- Use the same portrait swipe ratios as the metadata panel so the flow stays within the editor.

## Why it matters
- The listing form is a scrollable editor; lower rows can be hidden even though the screen is still
  classified as `listing_form`.
- Shipping-time is category-dependent, so the flow should reveal it if present and only skip after
  scrolling fails to surface the row.
