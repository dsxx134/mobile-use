from datetime import date

from minitap.mobile_use.collectors.xianyu_collector.domain.filter_config import FilterConfig
from minitap.mobile_use.collectors.xianyu_collector.domain.filter_engine import FilterEngine


def build_engine() -> FilterEngine:
    return FilterEngine(today_provider=lambda: date(2026, 3, 14))


def build_item(**overrides):
    item = {
        "title": "蓝牙耳机",
        "browseCnt": "120",
        "wantCnt": "18",
        "create_date": "2026-03-10",
        "soldPrice": "99",
        "knife_price": "88",
        "goodName": "耳机",
    }
    item.update(overrides)
    return item


def test_filter_engine_accepts_item_when_all_thresholds_are_met():
    engine = build_engine()
    config = FilterConfig(
        browse_min=100,
        want_min=10,
        publish_days_operator="小于",
        publish_days_value=7,
        daily_item_min=3,
        consultation_rate_min_percent=10,
        price_min=50,
        price_max=120,
        knife_price_min=70,
        knife_price_max=90,
    )

    assert engine.should_keep(build_item(), config=config, gather_type=0) is True


def test_filter_engine_rejects_title_containing_excluded_word():
    engine = build_engine()
    config = FilterConfig(excluded_words=["定制"])

    assert engine.should_keep(
        build_item(title="蓝牙耳机 定制款"),
        config=config,
        gather_type=0,
    ) is False


def test_filter_engine_rejects_when_publish_day_or_price_constraints_fail():
    engine = build_engine()
    config = FilterConfig(
        publish_days_operator="大于",
        publish_days_value=10,
        price_min=100,
        knife_price_min=90,
    )

    assert engine.should_keep(build_item(soldPrice="80", knife_price="50"), config=config, gather_type=0) is False


def test_filter_engine_bypasses_thresholds_in_manual_mode():
    engine = build_engine()
    config = FilterConfig(
        excluded_words=["蓝牙"],
        browse_min=999,
        want_min=999,
        publish_days_operator="大于",
        publish_days_value=999,
        daily_item_min=999,
        consultation_rate_min_percent=99,
        price_min=999,
        knife_price_min=999,
    )

    assert engine.should_keep(build_item(browseCnt="1", wantCnt="0", soldPrice="1"), config=config, gather_type=1) is True
