from minitap.mobile_use.collectors.xianyu_collector.models import (
    BitBrowserConfig,
    CollectorProfileConfig,
    CollectorRunDefaults,
    GatherConditionConfig,
)
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


def test_bitbrowser_config_round_trips_through_grade_config(tmp_path):
    db = CollectorDatabase(tmp_path / "collector.db")
    db.initialize()
    repo = AppConfigRepository(db)

    repo.save_bitbrowser_config(
        BitBrowserConfig(
            browser_id="93d2f197e35a42e4813d990522a19189",
            api_host="127.0.0.1",
            api_port=54345,
        )
    )

    assert repo.load_bitbrowser_config() == BitBrowserConfig(
        browser_id="93d2f197e35a42e4813d990522a19189",
        api_host="127.0.0.1",
        api_port=54345,
    )


def test_run_defaults_round_trip_through_grade_config(tmp_path):
    db = CollectorDatabase(tmp_path / "collector.db")
    db.initialize()
    repo = AppConfigRepository(db)

    repo.save_run_defaults(
        CollectorRunDefaults(
            ensure_searchable_default=True,
            keyword_pages_default=3,
            shop_pages_default=5,
        )
    )

    assert repo.load_run_defaults() == CollectorRunDefaults(
        ensure_searchable_default=True,
        keyword_pages_default=3,
        shop_pages_default=5,
    )


def test_collector_profile_round_trips_stable_runtime_configuration(tmp_path):
    db = CollectorDatabase(tmp_path / "collector.db")
    db.initialize()
    repo = AppConfigRepository(db)

    repo.save_gather_config(ProxyConfig(is_open_proxy=True, proxy_url="http://proxy-source"))
    repo.save_bitbrowser_config(
        BitBrowserConfig(browser_id="browser-123", api_host="127.0.0.1", api_port=54345)
    )
    repo.save_gather_conditions(GatherConditionConfig(liuLanLiang_text="100"))
    repo.save_selected_gather_type(2)
    repo.save_gather_type_input(0, "gemini")
    repo.save_gather_type_input(1, "https://www.goofish.com/item?id=1")
    repo.save_gather_type_input(2, "https://www.goofish.com/?userId=seller-a")
    repo.save_region_list_str("上海-上海-黄浦区")
    repo.save_run_defaults(
        CollectorRunDefaults(
            ensure_searchable_default=True,
            keyword_pages_default=3,
            shop_pages_default=5,
        )
    )

    repo.save_profile("default")

    assert repo.list_profile_names() == ["default"]
    assert repo.load_profile("default") == CollectorProfileConfig(
        proxy_config=ProxyConfig(is_open_proxy=True, proxy_url="http://proxy-source"),
        bitbrowser_config=BitBrowserConfig(
            browser_id="browser-123",
            api_host="127.0.0.1",
            api_port=54345,
        ),
        gather_conditions=GatherConditionConfig(liuLanLiang_text="100"),
        selected_gather_type=2,
        gather_type_inputs={
            0: "gemini",
            1: "https://www.goofish.com/item?id=1",
            2: "https://www.goofish.com/?userId=seller-a",
        },
        region_list_str="上海-上海-黄浦区",
        run_defaults=CollectorRunDefaults(
            ensure_searchable_default=True,
            keyword_pages_default=3,
            shop_pages_default=5,
        ),
    )


def test_apply_profile_restores_saved_runtime_configuration(tmp_path):
    db = CollectorDatabase(tmp_path / "collector.db")
    db.initialize()
    repo = AppConfigRepository(db)

    repo.save_gather_config(ProxyConfig(is_open_proxy=True, proxy_url="http://proxy-source"))
    repo.save_bitbrowser_config(
        BitBrowserConfig(browser_id="browser-123", api_host="127.0.0.1", api_port=54345)
    )
    repo.save_gather_conditions(GatherConditionConfig(liuLanLiang_text="100"))
    repo.save_selected_gather_type(1)
    repo.save_gather_type_input(0, "gemini")
    repo.save_region_list_str("上海-上海-黄浦区")
    repo.save_run_defaults(
        CollectorRunDefaults(
            ensure_searchable_default=True,
            keyword_pages_default=3,
            shop_pages_default=5,
        )
    )
    repo.save_profile("default")

    repo.save_gather_config(ProxyConfig())
    repo.save_bitbrowser_config(BitBrowserConfig())
    repo.save_gather_conditions(GatherConditionConfig())
    repo.save_selected_gather_type(0)
    repo.save_gather_type_input(0, "other")
    repo.save_region_list_str("")
    repo.save_run_defaults(CollectorRunDefaults())

    repo.apply_profile("default")

    assert repo.load_gather_config() == ProxyConfig(is_open_proxy=True, proxy_url="http://proxy-source")
    assert repo.load_bitbrowser_config() == BitBrowserConfig(
        browser_id="browser-123",
        api_host="127.0.0.1",
        api_port=54345,
    )
    assert repo.load_gather_conditions() == GatherConditionConfig(liuLanLiang_text="100")
    assert repo.load_selected_gather_type() == 1
    assert repo.load_gather_type_input(0) == "gemini"
    assert repo.load_region_list_str() == "上海-上海-黄浦区"
    assert repo.load_run_defaults() == CollectorRunDefaults(
        ensure_searchable_default=True,
        keyword_pages_default=3,
        shop_pages_default=5,
    )


def test_save_profile_rejects_overwrite_by_default(tmp_path):
    db = CollectorDatabase(tmp_path / "collector.db")
    db.initialize()
    repo = AppConfigRepository(db)

    repo.save_profile("default")

    try:
        repo.save_profile("default")
    except FileExistsError as exc:
        assert "default" in str(exc)
    else:
        raise AssertionError("expected FileExistsError when overwriting profile without opt-in")


def test_delete_profile_removes_saved_profile(tmp_path):
    db = CollectorDatabase(tmp_path / "collector.db")
    db.initialize()
    repo = AppConfigRepository(db)

    repo.save_profile("default")
    repo.delete_profile("default")

    assert repo.list_profile_names() == []
    assert repo.load_profile("default") is None


def test_export_profile_payload_contains_name_and_profile_dict(tmp_path):
    db = CollectorDatabase(tmp_path / "collector.db")
    db.initialize()
    repo = AppConfigRepository(db)

    repo.save_profile("default")

    exported = repo.export_profile_payload("default")

    assert exported["format_version"] == 1
    assert exported["name"] == "default"
    assert isinstance(exported["profile"], dict)


def test_import_profile_payload_restores_named_profile(tmp_path):
    db = CollectorDatabase(tmp_path / "collector.db")
    db.initialize()
    repo = AppConfigRepository(db)

    payload = {
        "format_version": 1,
        "name": "work",
        "profile": CollectorProfileConfig(
            proxy_config=ProxyConfig(is_open_proxy=True, proxy_url="http://proxy-source"),
            bitbrowser_config=BitBrowserConfig(browser_id="browser-123", api_host="127.0.0.1", api_port=54345),
            gather_conditions=GatherConditionConfig(liuLanLiang_text="100"),
            selected_gather_type=2,
            gather_type_inputs={0: "gemini"},
            region_list_str="上海-上海-黄浦区",
            run_defaults=CollectorRunDefaults(
                ensure_searchable_default=True,
                keyword_pages_default=3,
                shop_pages_default=5,
            ),
        ).to_dict(),
    }

    imported_name = repo.import_profile_payload(payload)

    assert imported_name == "work"
    profile = repo.load_profile("work")
    assert profile is not None
    assert profile.run_defaults == CollectorRunDefaults(
        ensure_searchable_default=True,
        keyword_pages_default=3,
        shop_pages_default=5,
    )


def test_current_config_snapshot_includes_stable_runtime_config_and_profile_names(tmp_path):
    db = CollectorDatabase(tmp_path / "collector.db")
    db.initialize()
    repo = AppConfigRepository(db)

    repo.save_gather_config(ProxyConfig(is_open_proxy=True, proxy_url="http://proxy-source"))
    repo.save_bitbrowser_config(
        BitBrowserConfig(browser_id="browser-123", api_host="127.0.0.1", api_port=54345)
    )
    repo.save_gather_conditions(GatherConditionConfig(liuLanLiang_text="100"))
    repo.save_run_defaults(
        CollectorRunDefaults(
            ensure_searchable_default=True,
            keyword_pages_default=3,
            shop_pages_default=5,
        )
    )
    repo.save_selected_gather_type(2)
    repo.save_gather_type_input(0, "gemini")
    repo.save_region_list_str("上海-上海-黄浦区")
    repo.save_profile("default")

    snapshot = repo.current_config_snapshot()

    assert snapshot["proxy_config"] == {
        "is_open_proxy": True,
        "proxy_url": "http://proxy-source",
    }
    assert snapshot["bitbrowser_config"] == {
        "browser_id": "browser-123",
        "api_host": "127.0.0.1",
        "api_port": 54345,
    }
    assert snapshot["run_defaults"] == {
        "ensure_searchable_default": True,
        "keyword_pages_default": 3,
        "shop_pages_default": 5,
    }
    assert snapshot["selected_gather_type"] == 2
    assert snapshot["gather_type_inputs"]["0"] == "gemini"
    assert snapshot["profiles"] == ["default"]
