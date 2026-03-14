# feishu-attachment-downloads-use-record-urls-with-bearer-auth

Updated: 2026-03-14

## Pattern
- For the live Xianyu Bitable table, use the `url` already present on each attachment item as the
  download URL.
- Download the file with a tenant bearer token in the `Authorization` header.
- Do not depend on the older `/drive/v1/medias/batch_get_tmp_download_url` endpoint for this flow.

## Why
- The live environment returned `404` for the old batch temp-download endpoint.
- The attachment `url` from the Bitable record payload worked immediately when called with bearer
  auth and preserved attachment order without another lookup step.

## Applied In
- `minitap/mobile_use/scenarios/xianyu_publish/feishu_source.py`
- Live Feishu-backed `XianyuMediaSyncService` construction via
  `download_file=source.download_attachment_file`
