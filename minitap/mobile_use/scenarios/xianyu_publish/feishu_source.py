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
        self._table_id_cache: dict[str, str] = {}
        self._primary_field_name_cache: dict[str, str] = {}

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
            if self._is_retry_exhausted(record):
                continue
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
        retry_count: int | None = None,
        batch_run_id: str | None = None,
        batch_ran_at: str | None = None,
        batch_result: str | None = None,
    ) -> None:
        fields = {
            self.settings.status_field_name: status,
            self.settings.failure_reason_field_name: failure_reason,
        }
        if retry_count is not None:
            fields[self.settings.retry_count_field_name] = retry_count
        self._apply_batch_run_fields(
            fields,
            status=status,
            batch_run_id=batch_run_id,
            batch_ran_at=batch_ran_at,
            batch_result=batch_result,
        )

        self._update_record_fields(record_id, fields)

    def update_publish_result(
        self,
        record_id: str,
        *,
        status: str,
        failure_reason: str | None = None,
        published_at: str | None = None,
        listing_id: str | None = None,
        listing_url: str | None = None,
        retry_count: int | None = None,
        batch_run_id: str | None = None,
        batch_ran_at: str | None = None,
        batch_result: str | None = None,
    ) -> None:
        fields = {
            self.settings.status_field_name: status,
            self.settings.failure_reason_field_name: failure_reason,
            self.settings.published_at_field_name: published_at,
            self.settings.listing_id_field_name: listing_id,
            self.settings.listing_url_field_name: self._format_url_field(listing_url),
        }
        if retry_count is not None:
            fields[self.settings.retry_count_field_name] = retry_count
        self._apply_batch_run_fields(
            fields,
            status=status,
            batch_run_id=batch_run_id,
            batch_ran_at=batch_ran_at,
            batch_result=batch_result,
        )

        self._update_record_fields(record_id, fields)

    def write_batch_run_summary(
        self,
        *,
        batch_run_id: str,
        batch_ran_at: str,
        requested_count: int,
        processed_count: int,
        success_count: int,
        failure_count: int,
        stopped_reason: str,
        items: list[dict[str, Any]],
    ) -> None:
        table_id = self._resolve_table_id_by_name(self.settings.batch_summary_table_name)
        if table_id is None:
            raise ValueError(
                f"Missing Xianyu batch summary table: {self.settings.batch_summary_table_name}"
            )
        primary_field_name = self._resolve_primary_field_name(table_id)

        app_token = self._require_setting("XIANYU_BITABLE_APP_TOKEN")
        self._request_json(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records",
            json={
                "fields": {
                    primary_field_name: batch_run_id,
                    self.settings.batch_summary_run_id_field_name: batch_run_id,
                    self.settings.batch_summary_ran_at_field_name: batch_ran_at,
                    self.settings.batch_summary_requested_count_field_name: requested_count,
                    self.settings.batch_summary_processed_count_field_name: processed_count,
                    self.settings.batch_summary_success_count_field_name: success_count,
                    self.settings.batch_summary_failure_count_field_name: failure_count,
                    self.settings.batch_summary_stop_reason_field_name: stopped_reason,
                    self.settings.batch_summary_items_field_name: json.dumps(
                        items,
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ),
                }
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

        retry_count = self._resolve_retry_count(fields)
        retry_limit = self._resolve_retry_limit(fields)

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
            retry_count=retry_count,
            retry_limit=retry_limit,
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

    def _resolve_table_id_by_name(self, table_name: str) -> str | None:
        cached = self._table_id_cache.get(table_name)
        if cached is not None:
            return cached

        app_token = self._require_setting("XIANYU_BITABLE_APP_TOKEN")
        payload = self._request_json(
            "GET",
            f"/bitable/v1/apps/{app_token}/tables",
            params={"page_size": 100},
        )
        for item in payload.get("items", []):
            if item.get("name") == table_name:
                table_id = item.get("table_id")
                if isinstance(table_id, str) and table_id:
                    self._table_id_cache[table_name] = table_id
                    return table_id
        return None

    def _resolve_primary_field_name(self, table_id: str) -> str:
        cached = self._primary_field_name_cache.get(table_id)
        if cached is not None:
            return cached

        app_token = self._require_setting("XIANYU_BITABLE_APP_TOKEN")
        payload = self._request_json(
            "GET",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields",
            params={"page_size": 100},
        )
        for item in payload.get("items", []):
            if item.get("is_primary"):
                field_name = item.get("field_name")
                if isinstance(field_name, str) and field_name:
                    self._primary_field_name_cache[table_id] = field_name
                    return field_name

        return self.settings.batch_summary_primary_field_name

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

    def _resolve_retry_count(self, fields: dict[str, Any]) -> int:
        value = fields.get(self.settings.retry_count_field_name)
        if value is None:
            return 0
        resolved = self._extract_int_value(value)
        return max(resolved, 0)

    def _resolve_retry_limit(self, fields: dict[str, Any]) -> int:
        value = fields.get(self.settings.retry_limit_field_name)
        if value is None:
            return max(self.settings.default_retry_limit, 0)
        resolved = self._extract_int_value(value)
        return max(resolved, 0)

    def _is_retry_exhausted(self, record: dict[str, Any]) -> bool:
        fields = record.get("fields", {})
        retry_count = self._resolve_retry_count(fields)
        retry_limit = self._resolve_retry_limit(fields)
        return retry_count >= retry_limit

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

    def _extract_int_value(self, value: Any) -> int:
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)

        text = self._extract_text_value(value)
        if not text:
            return 0
        try:
            return int(text)
        except ValueError:
            return int(float(text))

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

    def _apply_batch_run_fields(
        self,
        fields: dict[str, Any],
        *,
        status: str,
        batch_run_id: str | None,
        batch_ran_at: str | None,
        batch_result: str | None,
    ) -> None:
        if batch_run_id is None and batch_ran_at is None and batch_result is None:
            return

        if batch_run_id is not None:
            fields[self.settings.batch_run_id_field_name] = batch_run_id
        if batch_ran_at is not None:
            fields[self.settings.batch_ran_at_field_name] = batch_ran_at

        resolved_batch_result = batch_result or status
        fields[self.settings.batch_result_field_name] = resolved_batch_result
