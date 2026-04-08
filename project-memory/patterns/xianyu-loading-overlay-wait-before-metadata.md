# xianyu loading overlay wait before metadata

Date: 2026-03-19

## Pattern
- When the listing editor briefly shows an `unknown` screen with no visible texts
  (FishFlutterBoostTransparencyActivity), treat it as a loading overlay and wait
  before attempting to open the metadata panel.

## Why it matters
- This transient overlay can appear between listing-form steps and should not be
  treated as a hard failure.
