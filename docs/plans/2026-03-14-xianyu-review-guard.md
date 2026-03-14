# Xianyu Review Guard and Publish Outcome Plan

## Goal

Add a safe review layer after the existing prepare runner so the automation can:

1. validate that the current Xianyu editor is in a reviewable pre-submit state,
2. write that reviewed state back into Feishu as a manual-publish checkpoint,
3. recognize a basic publish-success screen shape for the future auto-submit slice,
4. keep default behavior non-submitting.

## Scope

1. Keep `XianyuPrepareRunner.prepare_first_publishable_listing()` backward compatible.
2. Add an opt-in review mode that:
   - checks the final editor state is still supported (`listing_form` or `metadata_panel`)
   - checks the `submit_listing` target is visible
   - marks the record `待人工发布` when the review passes
   - marks the record `准备失败` with `失败原因` when the review fails
3. Add analyzer support for a minimal `publish_success` screen shape.
4. Add optional Feishu field names for future publish writeback:
   - `允许自动发布`
   - `闲鱼商品ID`
   - `闲鱼商品链接`
   - `发布时间`
5. Add a dedicated live review script instead of changing the existing prepare script semantics.

## Non-Goals

- Do not tap the final `发布` button automatically in this batch.
- Do not claim stable publish-success heuristics beyond the explicit success screen shape covered by tests.
- Do not wire final `闲鱼商品ID/链接/发布时间` writeback yet unless a real success page is actually reached.

## TDD Steps

1. Add failing analyzer tests for `publish_success`.
2. Add failing runner tests for review mode:
   - success path writes `待人工发布`
   - failure path raises when `submit_listing` is not visible
3. Implement the minimal analyzer and runner changes.
4. Add a live review entrypoint that opts into review mode without changing the existing prepare script.
5. Update README and project memory, then verify on the real device and Feishu table.

## Assumptions

- `待人工发布` is the safest next status because it makes the current boundary explicit.
- The existing prepare slice remains the source of truth for media/body/price completion; the new review layer only confirms that the editor is still in a supported pre-submit state.
- The live table can safely receive the future-facing fields now even if they are not populated in this batch.
