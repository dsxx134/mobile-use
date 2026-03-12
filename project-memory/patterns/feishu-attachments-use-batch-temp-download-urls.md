# feishu-attachments-use-batch-temp-download-urls

Updated: 2026-03-12

## Rule
- For Feishu Bitable attachment fields, normalize each attachment around its `file_token`.
- Resolve actual download URLs in batch through `/drive/v1/medias/batch_get_tmp_download_url` before downloading files.

## Why
- Bitable record payloads are stable enough to carry attachment metadata, but the actual download URL should be treated as temporary.
- Resolving all `file_token`s in one request preserves attachment order and reduces API round-trips.

## Applied In
- `minitap/mobile_use/scenarios/xianyu_publish/feishu_source.py`
