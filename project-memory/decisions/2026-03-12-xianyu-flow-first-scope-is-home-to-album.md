# Xianyu Flow First Scope Is Home To Album

Date: 2026-03-12

## Decision
- Build the first deterministic Xianyu in-app flow only up to:
  - recovering the Xianyu home tab
  - entering the publish chooser
  - handling the Android media permission dialog
  - reaching the album picker
  - selecting and confirming one image
- Defer title, description, price, category, and final publish submission to the next batch.

## Why
- These screens were verified directly on the connected Huawei tablet and can be tested with stable heuristics today.
- The downstream edit form still needs more real-device inspection before hard-coding safe selectors.
- A partial but deterministic flow is more useful than a larger speculative flow for direct publishing automation.

## Operational Impact
- The current smoke tooling can tell us whether the device is on a recognized pre-form screen.
- The next implementation batch should focus on recognizing the actual edit form and filling deterministic fields from `ListingDraft`.
