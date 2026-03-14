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
                    "value": [],
                },
            ],
        }

    def list_candidate_records(self) -> list[dict[str, Any]]:
        app_token = self._require_setting("XIANYU_BITABLE_APP_TOKEN")
        table_id = self._require_setting("XIANYU_BITABLE_TABLE_ID")
        payload = self._request_json(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/search",
            json={
                "page_size": 100,
                "filter": self.build_pending_filter(),
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
        ordered_urls: dict[str, str] = {}
        for attachment in attachments:
            direct_url = attachment.url or attachment.tmp_url
            if direct_url:
                ordered_urls[attachment.file_token] = direct_url
        return ordered_urls

    def download_attachment_file(self, url: str, destination: Any) -> None:
        with self._http_client.stream(
            "GET",
            url,
            headers={"Authorization": f"Bearer {self._token_provider()}"},
        ) as response:
            response.raise_for_status()
            destination.write_bytes(response.read())

    def update_listing_status(
        self,
        record_id: str,
        status: str,
        *,
        failure_reason: str | None = None,
    ) -> None:
        self._update_record_fields(
            record_id,
            {
                self.settings.status_field_name: status,
                self.settings.failure_reason_field_name: failure_reason,
            },
        )

    def update_publish_result(
        self,
        record_id: str,
        *,
        status: str,
        failure_reason: str | None = None,
        published_at: str | None = None,
        listing_id: str | None = None,
        listing_url: str | None = None,
    ) -> None:
        self._update_record_fields(
            record_id,
            {
                self.settings.status_field_name: status,
                self.settings.failure_reason_field_name: failure_reason,
                self.settings.published_at_field_name: published_at,
                self.settings.listing_id_field_name: listing_id,
                self.settings.listing_url_field_name: self._format_url_field(listing_url),
            },
        )

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
            title=self._get_required_text_field(fields, self.settings.title_field_name),
            description=self._get_required_text_field(fields, self.settings.description_field_name),
            price=float(fields[self.settings.price_field_name]),
            attachments=attachments,
            category=self._get_optional_text_field(fields, self.settings.category_field_name),
            condition=self._get_optional_text_field(fields, self.settings.condition_field_name),
            item_source=self._get_optional_text_field(
                fields, self.settings.item_source_field_name
            ),
            location_search_query=self._get_optional_text_field(
                fields, self.settings.location_search_query_field_name
            ),
            allow_auto_publish=bool(fields.get(self.settings.auto_publish_field_name)),
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

    def _update_record_fields(self, record_id: str, fields: dict[str, Any]) -> None:
        app_token = self._require_setting("XIANYU_BITABLE_APP_TOKEN")
        table_id = self._require_setting("XIANYU_BITABLE_TABLE_ID")
        self._request_json(
            "PUT",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}",
            json={"fields": fields},
        )

    def _require_setting(self, field_name: str) -> str:
        value = getattr(self.settings, field_name)
        if not value:
            raise ValueError(f"Missing required Xianyu publish setting: {field_name}")
        return value

    def _get_optional_text_field(self, fields: dict[str, Any], field_name: str) -> str | None:
        value = fields.get(field_name)
        if value is None:
            return None
        text = self._extract_text_value(value)
        return text or None

    def _get_required_text_field(self, fields: dict[str, Any], field_name: str) -> str:
        value = fields.get(field_name)
        text = self._extract_text_value(value)
        if not text:
            raise ValueError(f"Missing required text field: {field_name}")
        return text

    def _extract_text_value(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, list):
            parts: list[str] = []
            for item in value:
                if isinstance(item, dict):
                    text = item.get("text")
                    if isinstance(text, str) and text.strip():
                        parts.append(text.strip())
                elif isinstance(item, str) and item.strip():
                    parts.append(item.strip())
            if parts:
                return "".join(parts).strip()
        return str(value).strip()

    def _format_url_field(self, value: str | None) -> Any:
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return None
        return {
            "text": text,
            "link": text,
        }
