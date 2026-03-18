# xianyu location search writeback uses selected result text

Updated: 2026-03-17

## Pattern
- When selecting a location via the search UI, capture the tapped result text.
- Normalize multi-line results into a single-line string (join lines with spaces).
- Treat the normalized value as the selected location even if the editor still shows `选择位置`.
- Write the normalized value back to the listing `预设地址` field during prepare completion.

## Why
- The location panel exposes stable, selectable search results.
- The listing form does not reliably expose a location confirmation row in accessibility text.
- The selected search result is the most reliable proxy for what the user chose.
