from minitap.mobile_use.collectors.xianyu_collector.domain.filter_config import FilterConfig
from minitap.mobile_use.collectors.xianyu_collector.models import GatherConditionConfig


def test_gather_condition_config_maps_reverse_engineered_fields_to_filter_config():
    config = GatherConditionConfig(
        liuLanLiang_text="100",
        xiangYaoRenShu_text="20",
        comboBox_faBuTianShu_text="小于",
        faBuTianShu_text="7",
        binRiChuDan_text="3",
        ziXunLv_text="10",
        jia_ge_start="50",
        jia_ge_end="200",
        xiao_dao_jia_start="20",
        xiao_dao_jia_end="80",
        buCaiJiCiZu="定制\n虚拟",
    )

    assert config.to_filter_config() == FilterConfig(
        excluded_words=["定制", "虚拟"],
        browse_min=100,
        want_min=20,
        publish_days_operator="小于",
        publish_days_value=7,
        daily_item_min=3.0,
        consultation_rate_min_percent=10,
        price_min=50.0,
        price_max=200.0,
        knife_price_min=20.0,
        knife_price_max=80.0,
    )


def test_gather_condition_config_exposes_keyword_limit_and_shop_recency_filter():
    config = GatherConditionConfig(
        lineEdit_guan_jian_ci_cai_ji_xian_zhi="300",
        dian_pu_cai_ji_fa_bu_tian_shu_text="72小时内发布",
    )

    assert config.keyword_collect_limit == 300
    assert config.shop_recent_publish_filter == "72小时内发布"


def test_gather_condition_config_treats_blank_special_fields_as_disabled():
    config = GatherConditionConfig(
        lineEdit_guan_jian_ci_cai_ji_xian_zhi="",
        dian_pu_cai_ji_fa_bu_tian_shu_text="  ",
    )

    assert config.keyword_collect_limit is None
    assert config.shop_recent_publish_filter is None
