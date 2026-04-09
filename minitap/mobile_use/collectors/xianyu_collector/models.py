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
