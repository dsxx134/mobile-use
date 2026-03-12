import json
import time
from collections.abc import Callable
from typing import Any

import httpx

from minitap.mobile_use.scenarios.xianyu_publish.models import FeishuAttachment, ListingDraft
from minitap.mobile_use.scenarios.xianyu_publish.settings import XianyuPublishSettings


class FeishuAuthClient:
    def __init__(
        self,
        app_id: str,
        app_secret: str,
        http_client: httpx.Client,
    ) -> None:
        self._app_id = app_id
        self._app_secret = app_secret
        self._http_client = http_client
        self._tenant_access_token: str | None = None
        self._token_expire_time = 0.0

    def get_tenant_access_token(self) -> str:
        now = time.time()
        if self._tenant_access_token and now < (self._token_expire_time - 300):
            return self._tenant_access_token

        response = self._http_client.post(
            "/auth/v3/tenant_access_token/internal",
            json={
                "app_id": self._app_id,
                "app_secret": self._app_secret,
            },
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("code") != 0:
            raise ValueError(f"Feishu auth failed: {payload.get('msg', 'unknown error')}")

        self._tenant_access_token = payload["tenant_access_token"]
        self._token_expire_time = now + payload.get("expire", 7200)
        return self._tenant_access_token


class FeishuBitableSource:
    def __init__(
        self,
        settings: XianyuPublishSettings,
        http_client: httpx.Client | None = None,
        token_provider: Callable[[], str] | None = None,
    ) -> None:
        self.settings = settings
        self._http_client = http_client or httpx.Client(
            base_url="https://open.feishu.cn/open-apis",
            timeout=30.0,
        )
        self._auth_client = FeishuAuthClient(
            app_id=settings.FEISHU_APP_ID or "",
            app_secret=(
                settings.FEISHU_APP_SECRET.get_secret_value()
                if settings.FEISHU_APP_SECRET is not None
                else ""
            ),
            http_client=self._http_client,
        )
        self._token_provider = token_provider or self._auth_client.get_tenant_access_token

    def build_pending_filter(self) -> dict[str, Any]:
        return {
            "conjunction": "and",
            "conditions": [
                {
                    "field_name": self.settings.allow_publish_field_name,
                    "operator": "is",
                    "value": [True],
                },
                {
                    "field_name": self.settings.status_field_name,
                    "operator": "is",
                    "value": ["待发布"],
                },
                {
                    "field_name": self.settings.attachment_field_name,
                    "operator": "isNotEmpty",
                },
            ],
        }

    def list_candidate_records(self) -> list[dict[str, Any]]:
        app_token = self._require_setting("XIANYU_BITABLE_APP_TOKEN")
        table_id = self._require_setting("XIANYU_BITABLE_TABLE_ID")
        payload = self._request_json(
            "GET",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records",
            params={
                "page_size": 100,
                "filter": json.dumps(self.build_pending_filter(), ensure_ascii=False),
            },
        )
        return payload.get("items", [])

    def pick_first_publishable_record(
        self,
        records: list[dict[str, Any]] | None = None,
    ) -> ListingDraft | None:
        candidate_records = records if records is not None else self.list_candidate_records()
        if not candidate_records:
            return None

        for record in candidate_records:
            draft = self._record_to_listing_draft(record)
            if draft is not None:
                return draft
        return None

    def get_attachment_download_urls(
        self,
        attachments: list[FeishuAttachment],
    ) -> dict[str, str]:
        payload = self._request_json(
            "POST",
            "/drive/v1/medias/batch_get_tmp_download_url",
            json={"file_tokens": [attachment.file_token for attachment in attachments]},
        )
        ordered_urls: dict[str, str] = {}
        tmp_download_urls = payload.get("tmp_download_urls", [])
        for attachment in attachments:
            matched = next(
                (
                    item.get("tmp_download_url")
                    for item in tmp_download_urls
                    if item.get("file_token") == attachment.file_token
                ),
                None,
            )
            if matched:
                ordered_urls[attachment.file_token] = matched
        return ordered_urls

    def _request_json(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        response = self._http_client.request(
            method,
            path,
            json=json,
            params=params,
            headers={"Authorization": f"Bearer {self._token_provider()}"},
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("code") != 0:
            raise ValueError(f"Feishu request failed: {payload.get('msg', 'unknown error')}")
        return payload.get("data", payload)

    def _record_to_listing_draft(self, record: dict[str, Any]) -> ListingDraft | None:
        fields = record.get("fields", {})
        attachments_raw = fields.get(self.settings.attachment_field_name) or []
        attachments = [self._parse_attachment(item) for item in attachments_raw]
        if not attachments:
            return None

        return ListingDraft(
            record_id=record["record_id"],
            title=str(fields[self.settings.title_field_name]).strip(),
            description=str(fields[self.settings.description_field_name]).strip(),
            price=float(fields[self.settings.price_field_name]),
            attachments=attachments,
        )

    def _parse_attachment(self, attachment: dict[str, Any]) -> FeishuAttachment:
        return FeishuAttachment(
            file_token=attachment["file_token"],
            name=attachment.get("name") or attachment.get("file_name") or attachment["file_token"],
            size=attachment.get("size"),
            tmp_url=attachment.get("tmp_url"),
            url=attachment.get("url"),
            file_type=attachment.get("type"),
        )

    def _require_setting(self, field_name: str) -> str:
        value = getattr(self.settings, field_name)
        if not value:
            raise ValueError(f"Missing required Xianyu publish setting: {field_name}")
        return value
