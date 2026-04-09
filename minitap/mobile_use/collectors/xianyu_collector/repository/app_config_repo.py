from __future__ import annotations

import json
from typing import Any

from minitap.mobile_use.collectors.xianyu_collector.models import BitBrowserConfig, GatherConditionConfig
from minitap.mobile_use.collectors.xianyu_collector.repository.sqlite_db import CollectorDatabase
from minitap.mobile_use.collectors.xianyu_collector.transport.proxy_config import ProxyConfig


class AppConfigRepository:
    def __init__(self, database: CollectorDatabase):
        self.database = database

    def load_gather_config(self) -> ProxyConfig:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT gatherConfig FROM app_user_config WHERE id = 1"
            ).fetchone()

        if not row or not row["gatherConfig"]:
            return ProxyConfig()

        payload = json.loads(row["gatherConfig"])
        return ProxyConfig(
            is_open_proxy=bool(payload.get("is_open_proxy", False)),
            proxy_url=str(payload.get("proxy_url", "")),
        )

    def save_gather_config(self, config: ProxyConfig) -> None:
        gather_config = json.dumps(
            {
                "is_open_proxy": config.is_open_proxy,
                "proxy_url": config.proxy_url,
            }
        )

        with self.database.connect() as connection:
            existing = connection.execute(
                "SELECT id FROM app_user_config WHERE id = 1"
            ).fetchone()
            if existing:
                connection.execute(
                    "UPDATE app_user_config SET gatherConfig = ? WHERE id = 1",
                    (gather_config,),
                )
            else:
                connection.execute(
                    """
                    INSERT INTO app_user_config (
                        id,
                        keyCode,
                        gatherConfig,
                        gradeConfig,
                        xiaJiaConfig
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (1, None, gather_config, None, None),
                )
            connection.commit()

    def config_row_count(self) -> int:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS count FROM app_user_config"
            ).fetchone()
        return int(row["count"])

    def load_saved_cookie_string(self) -> str:
        return str(self._load_grade_config_value("cookices_str") or "")

    def save_saved_cookie_string(self, cookie_string: str) -> None:
        self._save_grade_config_value("cookices_str", cookie_string)

    def load_region_list_str(self) -> str:
        return str(self._load_grade_config_value("region_list_str") or "")

    def save_region_list_str(self, region_list_str: str) -> None:
        self._save_grade_config_value("region_list_str", region_list_str)

    def load_bitbrowser_config(self) -> BitBrowserConfig:
        payload = self._load_grade_config_value("bitbrowser_runtime")
        if not isinstance(payload, dict):
            return BitBrowserConfig()
        return BitBrowserConfig.from_dict(payload)

    def save_bitbrowser_config(self, config: BitBrowserConfig) -> None:
        self._save_grade_config_value("bitbrowser_runtime", config.to_dict())

    def load_gather_conditions(self) -> GatherConditionConfig:
        payload = self._load_grade_config_value("gather_tiao_jian")
        if not isinstance(payload, dict):
            return GatherConditionConfig()
        return GatherConditionConfig.from_dict(payload)

    def save_gather_conditions(self, config: GatherConditionConfig) -> None:
        self._save_grade_config_value("gather_tiao_jian", config.to_dict())

    def load_selected_gather_type(self) -> int | None:
        value = self._load_grade_config_value("gather_type")
        if value is None:
            return None
        return int(value)

    def save_selected_gather_type(self, gather_type: int) -> None:
        self._save_grade_config_value("gather_type", int(gather_type))

    def load_gather_type_input(self, gather_type: int) -> str:
        return str(self._load_grade_config_value(f"gather_type_{gather_type}") or "")

    def save_gather_type_input(self, gather_type: int, value: str) -> None:
        self._save_grade_config_value(f"gather_type_{gather_type}", value)

    def load_grade_config(self) -> dict[str, Any]:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT gradeConfig FROM app_user_config WHERE id = 1"
            ).fetchone()
        if not row or not row["gradeConfig"]:
            return {}
        return json.loads(row["gradeConfig"])

    def _load_grade_config_value(self, key: str) -> Any:
        return self.load_grade_config().get(key)

    def _save_grade_config_value(self, key: str, value: Any) -> None:
        grade_config = self.load_grade_config()
        grade_config[key] = value
        self._upsert_grade_config(grade_config)

    def _upsert_grade_config(self, grade_config: dict[str, Any]) -> None:
        serialized = json.dumps(grade_config, ensure_ascii=False)
        with self.database.connect() as connection:
            existing = connection.execute(
                "SELECT id FROM app_user_config WHERE id = 1"
            ).fetchone()
            if existing:
                connection.execute(
                    "UPDATE app_user_config SET gradeConfig = ? WHERE id = 1",
                    (serialized,),
                )
            else:
                connection.execute(
                    """
                    INSERT INTO app_user_config (
                        id,
                        keyCode,
                        gatherConfig,
                        gradeConfig,
                        xiaJiaConfig
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (1, None, None, serialized, None),
                )
            connection.commit()
