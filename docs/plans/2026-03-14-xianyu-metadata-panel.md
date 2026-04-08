# Xianyu Metadata Panel

## Goal

Add deterministic support for the expanded Xianyu metadata/spec section reached from the portrait `发闲置` form, and wire at least one reusable metadata field into the prepare runner.

## Scope

1. Detect the expanded metadata/spec page as its own screen instead of misclassifying it as `publish_chooser`.
2. Extract deterministic targets for:
   - metadata entry from the base listing form
   - condition options under `成色`
   - source options under `商品来源`
3. Add flow helpers to:
   - advance from `listing_form` to `metadata_panel`
   - set item condition
   - set item source
4. Extend listing data/settings/Feishu mapping with optional metadata fields.
5. Update the prepare runner to apply these metadata fields when present.

## TDD Steps

1. Add failing analyzer tests for `metadata_panel` detection and option targets.
2. Add failing flow tests for `advance_listing_form_to_metadata_panel`, `set_item_condition`, and `set_item_source`.
3. Add failing model/source/runner tests for optional metadata fields.
4. Implement the smallest code changes to satisfy the tests.
5. Run focused tests, full scenario tests, lint, and compile checks.
6. Update README and project memory, then commit and push.

## Notes

- Real device behavior on `E2P6R22708000602` shows `成色` chips remain on the same page and change from `可选...` to `已选中...`.
- The page still contains `关闭` and `发闲置`, so detection must run before the looser `publish_chooser` rule.
