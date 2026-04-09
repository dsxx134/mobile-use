from __future__ import annotations

import json
from typing import Any

from minitap.mobile_use.collectors.xianyu_collector.models import (
    BitBrowserConfig,
    CollectorProfileConfig,
    CollectorRunDefaults,
    GatherConditionConfig,
)
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

    def load_run_defaults(self) -> CollectorRunDefaults:
        payload = self._load_grade_config_value("collector_run_defaults")
        if not isinstance(payload, dict):
            return CollectorRunDefaults()
        return CollectorRunDefaults.from_dict(payload)

    def save_run_defaults(self, defaults: CollectorRunDefaults) -> None:
        self._save_grade_config_value("collector_run_defaults", defaults.to_dict())

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

    def list_profile_names(self) -> list[str]:
        profiles = self._load_profiles_payload()
        return sorted(profiles.keys())

    def save_profile(self, name: str, *, overwrite: bool = False) -> None:
        profiles = self._load_profiles_payload()
        if not overwrite and name in profiles:
            raise FileExistsError(f"profile already exists: {name}")
        profiles[name] = CollectorProfileConfig(
            proxy_config=self.load_gather_config(),
            bitbrowser_config=self.load_bitbrowser_config(),
            gather_conditions=self.load_gather_conditions(),
            selected_gather_type=self.load_selected_gather_type(),
            gather_type_inputs={
                0: self.load_gather_type_input(0),
                1: self.load_gather_type_input(1),
                2: self.load_gather_type_input(2),
            },
            region_list_str=self.load_region_list_str(),
            run_defaults=self.load_run_defaults(),
        ).to_dict()
        self._save_grade_config_value("collector_profiles", profiles)

    def delete_profile(self, name: str) -> None:
        profiles = self._load_profiles_payload()
        if name not in profiles:
            raise KeyError(name)
        profiles.pop(name, None)
        self._save_grade_config_value("collector_profiles", profiles)

    def export_profile_payload(self, name: str) -> dict[str, Any]:
        profile = self.load_profile(name)
        if profile is None:
            raise KeyError(name)
        return {
            "format_version": 1,
            "name": name,
            "profile": profile.to_dict(),
        }

    def import_profile_payload(
        self,
        payload: dict[str, Any],
        *,
        overwrite: bool = False,
        name_override: str | None = None,
    ) -> str:
        raw_name = name_override or payload.get("name")
        name = str(raw_name or "").strip()
        if not name:
            raise ValueError("profile payload missing name")
        profile_payload = payload.get("profile")
        if not isinstance(profile_payload, dict):
            raise ValueError("profile payload missing profile object")
        profiles = self._load_profiles_payload()
        if not overwrite and name in profiles:
            raise FileExistsError(f"profile already exists: {name}")
        profile = CollectorProfileConfig.from_dict(profile_payload)
        profiles[name] = profile.to_dict()
        self._save_grade_config_value("collector_profiles", profiles)
        return name

    def load_profile(self, name: str) -> CollectorProfileConfig | None:
        profiles = self._load_profiles_payload()
        payload = profiles.get(name)
        if not isinstance(payload, dict):
            return None
        return CollectorProfileConfig.from_dict(payload)

    def apply_profile(self, name: str) -> None:
        profile = self.load_profile(name)
        if profile is None:
            raise KeyError(name)
        self.save_gather_config(profile.proxy_config)
        self.save_bitbrowser_config(profile.bitbrowser_config)
        self.save_gather_conditions(profile.gather_conditions)
        if profile.selected_gather_type is not None:
            self.save_selected_gather_type(profile.selected_gather_type)
        for gather_type, value in profile.gather_type_inputs.items():
            self.save_gather_type_input(gather_type, value)
        self.save_region_list_str(profile.region_list_str)
        if profile.run_defaults is not None:
            self.save_run_defaults(profile.run_defaults)

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

    def _load_profiles_payload(self) -> dict[str, Any]:
        payload = self._load_grade_config_value("collector_profiles")
        if not isinstance(payload, dict):
            return {}
        return dict(payload)

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
