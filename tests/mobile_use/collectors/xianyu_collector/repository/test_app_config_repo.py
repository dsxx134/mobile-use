from minitap.mobile_use.collectors.xianyu_collector.models import GatherConditionConfig
from minitap.mobile_use.collectors.xianyu_collector.repository.app_config_repo import AppConfigRepository
from minitap.mobile_use.collectors.xianyu_collector.repository.sqlite_db import CollectorDatabase
from minitap.mobile_use.collectors.xianyu_collector.transport.proxy_config import ProxyConfig


def test_gather_config_round_trips_proxy_settings(tmp_path):
    db = CollectorDatabase(tmp_path / "collector.db")
    db.initialize()
    repo = AppConfigRepository(db)

    repo.save_gather_config(
        ProxyConfig(
            is_open_proxy=True,
            proxy_url="http://127.0.0.1:8080/proxy-pool",
        )
    )

    loaded = repo.load_gather_config()

    assert loaded == ProxyConfig(
        is_open_proxy=True,
        proxy_url="http://127.0.0.1:8080/proxy-pool",
    )


def test_save_gather_config_uses_a_single_config_row(tmp_path):
    db = CollectorDatabase(tmp_path / "collector.db")
    db.initialize()
    repo = AppConfigRepository(db)

    repo.save_gather_config(ProxyConfig(is_open_proxy=False, proxy_url=""))
    repo.save_gather_config(ProxyConfig(is_open_proxy=True, proxy_url="http://proxy-source"))

    assert repo.config_row_count() == 1
    assert repo.load_gather_config().proxy_url == "http://proxy-source"


def test_saved_cookie_string_round_trips_through_grade_config(tmp_path):
    db = CollectorDatabase(tmp_path / "collector.db")
    db.initialize()
    repo = AppConfigRepository(db)

    repo.save_saved_cookie_string("a=1; _m_h5_tk=token_123")

    assert repo.load_saved_cookie_string() == "a=1; _m_h5_tk=token_123"


def test_region_list_string_round_trips_through_grade_config(tmp_path):
    db = CollectorDatabase(tmp_path / "collector.db")
    db.initialize()
    repo = AppConfigRepository(db)

    value = "上海-上海-黄浦区\n上海-上海-徐汇区"
    repo.save_region_list_str(value)

    assert repo.load_region_list_str() == value


def test_gather_conditions_round_trip_exact_reverse_engineered_keys(tmp_path):
    db = CollectorDatabase(tmp_path / "collector.db")
    db.initialize()
    repo = AppConfigRepository(db)

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
        lineEdit_guan_jian_ci_cai_ji_xian_zhi="300",
        dian_pu_cai_ji_fa_bu_tian_shu_text="72小时内发布",
        buCaiJiCiZu="定制\n虚拟",
        is_kai_qi_duo_gui_ge_cai_ji=True,
    )

    repo.save_gather_conditions(config)

    assert repo.load_gather_conditions() == config


def test_gather_type_inputs_and_selected_index_round_trip(tmp_path):
    db = CollectorDatabase(tmp_path / "collector.db")
    db.initialize()
    repo = AppConfigRepository(db)

    repo.save_selected_gather_type(2)
    repo.save_gather_type_input(0, "耳机####关键词A\n键盘####关键词B")
    repo.save_gather_type_input(1, "https://www.goofish.com/item?id=123")
    repo.save_gather_type_input(2, "https://www.goofish.com/?userId=abc")

    assert repo.load_selected_gather_type() == 2
    assert repo.load_gather_type_input(0) == "耳机####关键词A\n键盘####关键词B"
    assert repo.load_gather_type_input(1) == "https://www.goofish.com/item?id=123"
    assert repo.load_gather_type_input(2) == "https://www.goofish.com/?userId=abc"


def test_updating_one_grade_config_key_preserves_existing_values(tmp_path):
    db = CollectorDatabase(tmp_path / "collector.db")
    db.initialize()
    repo = AppConfigRepository(db)

    repo.save_saved_cookie_string("cookie=1")
    repo.save_region_list_str("北京-北京-东城")

    assert repo.load_saved_cookie_string() == "cookie=1"
    assert repo.load_region_list_str() == "北京-北京-东城"
