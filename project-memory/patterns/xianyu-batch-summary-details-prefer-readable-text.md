# xianyu batch summary details prefer readable text

Updated: 2026-03-15

## Pattern
- For the Feishu `批次运行汇总` table, write `批次明细` as human-readable multi-line text instead of raw JSON.
- Use one processed row per line.
- Keep the line compact and operator-focused:
  - `序号. record_id | 成功/失败 | 额外关键信息`
- Include only fields that help humans triage the run quickly:
  - `商品ID`
  - `链接`
  - `最终页`
  - `发布结果页`
  - `详情页`
  - `原因`

## Why
- Feishu table operators read this column directly; raw JSON is harder to scan during queue review.
- The machine-readable batch result already exists in the worker's stdout/JSON return, so the table
  can optimize for eyeballing instead of replay.
- Multi-line text makes it easy to spot failures without opening the JSON payload.

## Example
- `1. recA | 失败 | 原因: Publish blocked`
- `2. recB | 成功 | 商品ID: xyB | 链接: https://m.tb.cn/...`
- Empty batch: `本批次没有处理任何记录。`
