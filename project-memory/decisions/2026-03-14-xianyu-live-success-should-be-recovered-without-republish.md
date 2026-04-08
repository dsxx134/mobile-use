# xianyu live success should be recovered without republish

Date: 2026-03-14

## Decision
- When a live auto-publish run has already reached a recognizable `publish_success` page, repair
  the Feishu row from that success evidence instead of rerunning auto-publish on the same record.
- Treat the Huawei-tablet reward screen (`发布成功` + `再发一件`) as sufficient publish-success proof
  for that recovery path.

## Why
- The live row `recvdOzzR38eVi` had already been published in Xianyu, but the older analyzer only
  recognized the classic `看看宝贝 / 继续发布` success skin and miswrote the row as `发布失败`.
- Rerunning auto-publish on the same row would risk creating a duplicate Xianyu listing just to
  repair a writeback bug.

## Consequences
- Once the analyzer recognizes the live success screen, Bitable state can be corrected to `已发布`
  without another submit tap.
- Future post-submit debugging should prefer screen re-analysis over blind re-submission whenever a
  success page is still on screen.
