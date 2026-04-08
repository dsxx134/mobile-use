# Xianyu Controlled Auto Publish Plan

## Goal

Add a controlled auto-publish path that only submits when the Bitable row explicitly enables
`允许自动发布`, then writes back publish status and timestamp while staying honest about any fields
that are not yet live-verifiable.

## Scope

1. Extend the Feishu mapping layer so a listing can carry `允许自动发布`.
2. Add a deterministic flow helper to:
   - tap the visible `发布` target,
   - wait for either a supported success screen or a fallback editor state,
   - return the resulting analysis.
3. Extend the runner with an opt-in auto-publish mode that:
   - requires review mode to pass first,
   - requires `ListingDraft.allow_auto_publish` to be true,
   - writes `发布中` before tapping publish,
   - writes `已发布` plus `发布时间` when the success screen is recognized,
   - writes `发布失败` plus `失败原因` if submission or post-submit recognition fails.
4. Add a live script entrypoint that uses the new auto-publish mode.

## Non-Goals

- Do not require `闲鱼商品ID` or `闲鱼商品链接` to be populated in this batch unless the real app
  exposes a stable value during verification.
- Do not change the default review script or prepare script into auto-submit mode.
- Do not broaden success heuristics beyond the tested screen shape unless the real device proves a
  different shape.

## TDD Steps

1. Add failing source/model tests for `allow_auto_publish`.
2. Add failing flow tests for `submit_listing_and_wait_for_result()`.
3. Add failing runner tests for:
   - auto-publish success path
   - auto-publish blocked when the row does not allow it
   - auto-publish failure path writing `发布失败`
4. Implement the minimal code to satisfy those tests.
5. Add the live auto-publish script.
6. Run focused tests, full scenario verification, then a real-device auto-publish probe on the
   Feishu test row.

## Assumptions

- `发布成功` plus visible `看看宝贝` / `继续发布` actions is a sufficient initial success shape.
- `发布时间` can be written as a local ISO-like timestamp string from the automation host.
- `闲鱼商品ID` and `闲鱼商品链接` remain optional and may stay empty after this batch.
