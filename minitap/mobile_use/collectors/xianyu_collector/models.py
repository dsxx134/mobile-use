from __future__ import annotations

from dataclasses import asdict, dataclass

from minitap.mobile_use.collectors.xianyu_collector.domain.filter_config import FilterConfig


def _to_int(value: str, *, default: int | None = None) -> int | None:
    text = str(value).strip()
    if not text:
        return default
    return int(text)


def _to_float(value: str, *, default: float | None = None) -> float | None:
    text = str(value).strip()
    if not text:
        return default
    return float(text)


@dataclass(frozen=True, slots=True)
class BitBrowserConfig:
    browser_id: str = ""
    api_host: str = "127.0.0.1"
    api_port: int = 54345

    @property
    def enabled(self) -> bool:
        return bool(self.browser_id.strip())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, object] | None) -> "BitBrowserConfig":
        if not payload:
            return cls()
        return cls(
            browser_id=str(payload.get("browser_id", "")),
            api_host=str(payload.get("api_host", "127.0.0.1") or "127.0.0.1"),
            api_port=int(payload.get("api_port", 54345) or 54345),
        )


@dataclass(frozen=True, slots=True)
class CollectorProfileConfig:
    proxy_config: object
    bitbrowser_config: BitBrowserConfig
    gather_conditions: "GatherConditionConfig"
    selected_gather_type: int | None
    gather_type_inputs: dict[int, str]
    region_list_str: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "proxy_config": {
                "is_open_proxy": bool(getattr(self.proxy_config, "is_open_proxy", False)),
                "proxy_url": str(getattr(self.proxy_config, "proxy_url", "")),
            },
            "bitbrowser_config": self.bitbrowser_config.to_dict(),
            "gather_conditions": self.gather_conditions.to_dict(),
            "selected_gather_type": self.selected_gather_type,
            "gather_type_inputs": {str(key): value for key, value in self.gather_type_inputs.items()},
            "region_list_str": self.region_list_str,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object] | None) -> "CollectorProfileConfig":
        from minitap.mobile_use.collectors.xianyu_collector.transport.proxy_config import ProxyConfig

        payload = payload or {}
        proxy_payload = payload.get("proxy_config")
        if not isinstance(proxy_payload, dict):
            proxy_payload = {}
        gather_inputs_payload = payload.get("gather_type_inputs")
        if not isinstance(gather_inputs_payload, dict):
            gather_inputs_payload = {}
        return cls(
            proxy_config=ProxyConfig(
                is_open_proxy=bool(proxy_payload.get("is_open_proxy", False)),
                proxy_url=str(proxy_payload.get("proxy_url", "")),
            ),
            bitbrowser_config=BitBrowserConfig.from_dict(payload.get("bitbrowser_config") if isinstance(payload.get("bitbrowser_config"), dict) else None),
            gather_conditions=GatherConditionConfig.from_dict(
                payload.get("gather_conditions") if isinstance(payload.get("gather_conditions"), dict) else None
            ),
            selected_gather_type=(
                int(payload["selected_gather_type"])
                if payload.get("selected_gather_type") is not None
                else None
            ),
            gather_type_inputs={int(key): str(value) for key, value in gather_inputs_payload.items()},
            region_list_str=str(payload.get("region_list_str", "")),
        )


@dataclass(frozen=True, slots=True)
class GatherConditionConfig:
    liuLanLiang_text: str = ""
    xiangYaoRenShu_text: str = ""
    comboBox_faBuTianShu_text: str = ""
    faBuTianShu_text: str = ""
    binRiChuDan_text: str = ""
    ziXunLv_text: str = ""
    jia_ge_start: str = ""
    jia_ge_end: str = ""
    xiao_dao_jia_start: str = ""
    xiao_dao_jia_end: str = ""
    lineEdit_guan_jian_ci_cai_ji_xian_zhi: str = ""
    dian_pu_cai_ji_fa_bu_tian_shu_text: str = ""
    buCaiJiCiZu: str = ""
    is_kai_qi_duo_gui_ge_cai_ji: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, object] | None) -> "GatherConditionConfig":
        if not payload:
            return cls()
        return cls(
            liuLanLiang_text=str(payload.get("liuLanLiang_text", "")),
            xiangYaoRenShu_text=str(payload.get("xiangYaoRenShu_text", "")),
            comboBox_faBuTianShu_text=str(payload.get("comboBox_faBuTianShu_text", "")),
            faBuTianShu_text=str(payload.get("faBuTianShu_text", "")),
            binRiChuDan_text=str(payload.get("binRiChuDan_text", "")),
            ziXunLv_text=str(payload.get("ziXunLv_text", "")),
            jia_ge_start=str(payload.get("jia_ge_start", "")),
            jia_ge_end=str(payload.get("jia_ge_end", "")),
            xiao_dao_jia_start=str(payload.get("xiao_dao_jia_start", "")),
            xiao_dao_jia_end=str(payload.get("xiao_dao_jia_end", "")),
            lineEdit_guan_jian_ci_cai_ji_xian_zhi=str(
                payload.get("lineEdit_guan_jian_ci_cai_ji_xian_zhi", "")
            ),
            dian_pu_cai_ji_fa_bu_tian_shu_text=str(
                payload.get("dian_pu_cai_ji_fa_bu_tian_shu_text", "")
            ),
            buCaiJiCiZu=str(payload.get("buCaiJiCiZu", "")),
            is_kai_qi_duo_gui_ge_cai_ji=bool(
                payload.get("is_kai_qi_duo_gui_ge_cai_ji", False)
            ),
        )

    def to_filter_config(self) -> FilterConfig:
        excluded_words = [line.strip() for line in self.buCaiJiCiZu.splitlines() if line.strip()]
        return FilterConfig(
            excluded_words=excluded_words,
            browse_min=_to_int(self.liuLanLiang_text, default=0) or 0,
            want_min=_to_int(self.xiangYaoRenShu_text, default=0) or 0,
            publish_days_operator=self.comboBox_faBuTianShu_text.strip(),
            publish_days_value=_to_int(self.faBuTianShu_text),
            daily_item_min=_to_float(self.binRiChuDan_text, default=-1.0) or -1.0,
            consultation_rate_min_percent=_to_int(self.ziXunLv_text, default=-1) or -1,
            price_min=_to_float(self.jia_ge_start),
            price_max=_to_float(self.jia_ge_end),
            knife_price_min=_to_float(self.xiao_dao_jia_start),
            knife_price_max=_to_float(self.xiao_dao_jia_end),
        )

    @property
    def keyword_collect_limit(self) -> int | None:
        value = _to_int(self.lineEdit_guan_jian_ci_cai_ji_xian_zhi)
        if value is None or value <= 0:
            return None
        return value

    @property
    def shop_recent_publish_filter(self) -> str | None:
        value = self.dian_pu_cai_ji_fa_bu_tian_shu_text.strip()
        return value or None
