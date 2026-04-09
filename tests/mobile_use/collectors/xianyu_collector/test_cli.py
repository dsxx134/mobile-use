import os

from minitap.mobile_use.collectors.xianyu_collector.api.client import GoofishBurstError
from minitap.mobile_use.collectors.xianyu_collector.cli import main
from minitap.mobile_use.collectors.xianyu_collector.models import BitBrowserConfig, GatherConditionConfig
from minitap.mobile_use.collectors.xianyu_collector.repository.app_config_repo import AppConfigRepository
from minitap.mobile_use.collectors.xianyu_collector.repository.goods_repo import GoodsRepository
from minitap.mobile_use.collectors.xianyu_collector.repository.sqlite_db import CollectorDatabase
from minitap.mobile_use.collectors.xianyu_collector.transport.proxy_config import ProxyConfig


def test_cli_set_proxy_persists_gather_config(tmp_path, capsys):
    db_path = tmp_path / "collector.db"

    exit_code = main(
        [
            "--db-path",
            str(db_path),
            "config",
            "set-proxy",
            "--proxy-url",
            "http://proxy-source",
            "--enabled",
        ]
    )

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "proxy config saved" in output


def test_cli_set_cookie_persists_saved_cookie_string(tmp_path, capsys):
    db_path = tmp_path / "collector.db"

    exit_code = main(
        [
            "--db-path",
            str(db_path),
            "config",
            "set-cookie",
            "--cookie-string",
            "a=1; _m_h5_tk=token_123",
        ]
    )

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "cookie string saved" in output


def test_cli_set_bitbrowser_persists_runtime_config(tmp_path, capsys):
    db_path = tmp_path / "collector.db"

    exit_code = main(
        [
            "--db-path",
            str(db_path),
            "config",
            "set-bitbrowser",
            "--browser-id",
            "browser-123",
            "--api-host",
            "127.0.0.2",
            "--api-port",
            "60000",
        ]
    )

    db = CollectorDatabase(db_path)
    db.initialize()
    repo = AppConfigRepository(db)

    assert exit_code == 0
    assert repo.load_bitbrowser_config() == BitBrowserConfig(
        browser_id="browser-123",
        api_host="127.0.0.2",
        api_port=60000,
    )
    output = capsys.readouterr().out
    assert "bitbrowser config saved" in output


def test_cli_sync_cookie_from_bitbrowser_persists_saved_cookie_string(tmp_path, capsys, monkeypatch):
    db_path = tmp_path / "collector.db"
    db = CollectorDatabase(db_path)
    db.initialize()
    repo = AppConfigRepository(db)
    repo.save_bitbrowser_config(
        BitBrowserConfig(
            browser_id="browser-123",
            api_host="127.0.0.1",
            api_port=54345,
        )
    )

    class FakeBitBrowserBrowserSession:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def get_cookie_string(self, url: str) -> str:
            assert url == "https://www.goofish.com/"
            return "a=1; _m_h5_tk=token_123; unb=2207148365801"

    monkeypatch.setattr(
        "minitap.mobile_use.collectors.xianyu_collector.cli.BitBrowserBrowserSession",
        FakeBitBrowserBrowserSession,
    )

    exit_code = main(
        [
            "--db-path",
            str(db_path),
            "config",
            "sync-cookie-from-bitbrowser",
        ]
    )

    assert exit_code == 0
    assert repo.load_saved_cookie_string() == "a=1; _m_h5_tk=token_123; unb=2207148365801"
    output = capsys.readouterr().out
    assert "cookie string synced from bitbrowser" in output


def test_cli_profile_save_list_and_load_round_trip_current_runtime_config(tmp_path, capsys):
    db_path = tmp_path / "collector.db"

    main(
        [
            "--db-path",
            str(db_path),
            "config",
            "set-proxy",
            "--proxy-url",
            "http://proxy-source",
            "--enabled",
        ]
    )
    main(
        [
            "--db-path",
            str(db_path),
            "config",
            "set-bitbrowser",
            "--browser-id",
            "browser-123",
        ]
    )

    db = CollectorDatabase(db_path)
    db.initialize()
    repo = AppConfigRepository(db)
    repo.save_gather_conditions(GatherConditionConfig(liuLanLiang_text="100"))
    repo.save_selected_gather_type(2)
    repo.save_gather_type_input(2, "https://www.goofish.com/?userId=seller-a")
    repo.save_region_list_str("上海-上海-黄浦区")

    save_exit = main(
        [
            "--db-path",
            str(db_path),
            "config",
            "save-profile",
            "--name",
            "default",
        ]
    )
    list_exit = main(
        [
            "--db-path",
            str(db_path),
            "config",
            "list-profiles",
        ]
    )

    repo.save_gather_config(ProxyConfig())
    repo.save_bitbrowser_config(BitBrowserConfig())
    repo.save_gather_conditions(GatherConditionConfig())
    repo.save_selected_gather_type(0)
    repo.save_gather_type_input(2, "")
    repo.save_region_list_str("")

    load_exit = main(
        [
            "--db-path",
            str(db_path),
            "config",
            "load-profile",
            "--name",
            "default",
        ]
    )

    assert save_exit == 0
    assert list_exit == 0
    assert load_exit == 0
    output = capsys.readouterr().out
    assert "profile saved" in output
    assert "default" in output
    assert "profile loaded" in output
    assert repo.load_gather_config() == ProxyConfig(
        is_open_proxy=True,
        proxy_url="http://proxy-source",
    )
    assert repo.load_bitbrowser_config() == BitBrowserConfig(
        browser_id="browser-123",
        api_host="127.0.0.1",
        api_port=54345,
    )


def test_cli_db_list_item_ids_prints_saved_item_ids(tmp_path, capsys):
    db = CollectorDatabase(tmp_path / "collector.db")
    db.initialize()
    repo = GoodsRepository(db)
    repo.insert_good({"item_id": "1001", "title": "A"})
    repo.insert_good({"item_id": "1002", "title": "B"})

    exit_code = main(["--db-path", str(tmp_path / "collector.db"), "db", "list-item-ids"])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "1001" in output
    assert "1002" in output


class FakeService:
    def __init__(self):
        self.calls = []
        self.default_proxy_config = ProxyConfig(
            is_open_proxy=True,
            proxy_url="http://proxy-source",
        )
        self.api_client = type(
            "FakeApiClient",
            (),
            {
                "search_items": lambda _self, **kwargs: ["111", "222"],
                "cookie_provider": type(
                    "FakeCookieProvider",
                    (),
                    {"_active_provider": type("SavedCookieProvider", (), {})(), "get_cookie_dict": lambda _self: {"_m_h5_tk": "token", "unb": "123"}} ,
                )(),
            },
        )()

    def collect_manual(self, **kwargs):
        self.calls.append(("manual", kwargs))
        return type("Summary", (), {"saved": 1, "filtered": 0, "duplicates": 0, "errors": 0})()

    def collect_keyword(self, **kwargs):
        self.calls.append(("keyword", kwargs))
        return type("Summary", (), {"saved": 2, "filtered": 1, "duplicates": 0, "errors": 0})()

    def collect_shop(self, **kwargs):
        self.calls.append(("shop", kwargs))
        return type("Summary", (), {"saved": 3, "filtered": 0, "duplicates": 1, "errors": 0})()


def test_cli_collect_manual_invokes_service_factory(tmp_path, capsys):
    fake_service = FakeService()

    exit_code = main(
        [
            "--db-path",
            str(tmp_path / "collector.db"),
            "collect",
            "manual",
            "--item-url",
            "https://www.goofish.com/item?id=2001",
        ],
        service_factory=lambda _db_path: fake_service,
    )

    assert exit_code == 0
    assert fake_service.calls[0][0] == "manual"
    assert fake_service.calls[0][1]["urls"] == ["https://www.goofish.com/item?id=2001"]
    assert fake_service.calls[0][1]["proxy_config"] == fake_service.default_proxy_config
    assert "saved=1" in capsys.readouterr().out


def test_cli_collect_keyword_invokes_service_with_pages_and_keywords(tmp_path, capsys):
    fake_service = FakeService()

    exit_code = main(
        [
            "--db-path",
            str(tmp_path / "collector.db"),
            "collect",
            "keyword",
            "--keyword",
            "耳机",
            "--keyword",
            "手机",
            "--pages",
            "2",
        ],
        service_factory=lambda _db_path: fake_service,
    )

    assert exit_code == 0
    assert fake_service.calls[0][0] == "keyword"
    assert fake_service.calls[0][1]["keywords"] == ["耳机", "手机"]
    assert fake_service.calls[0][1]["pages"] == 2
    assert fake_service.calls[0][1]["proxy_config"] == fake_service.default_proxy_config
    assert "saved=2" in capsys.readouterr().out


def test_cli_collect_shop_invokes_service_with_shop_urls(tmp_path, capsys):
    fake_service = FakeService()

    exit_code = main(
        [
            "--db-path",
            str(tmp_path / "collector.db"),
            "collect",
            "shop",
            "--shop-url",
            "https://www.goofish.com/?userId=seller-x",
        ],
        service_factory=lambda _db_path: fake_service,
    )

    assert exit_code == 0
    assert fake_service.calls[0][0] == "shop"
    assert fake_service.calls[0][1]["shop_urls"] == ["https://www.goofish.com/?userId=seller-x"]
    assert fake_service.calls[0][1]["proxy_config"] == fake_service.default_proxy_config
    assert "saved=3" in capsys.readouterr().out


def test_cli_collect_keyword_uses_saved_gather_conditions_as_defaults(tmp_path, capsys):
    db_path = tmp_path / "collector.db"
    db = CollectorDatabase(db_path)
    db.initialize()
    repo = AppConfigRepository(db)
    repo.save_gather_conditions(
        GatherConditionConfig(
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
            lineEdit_guan_jian_ci_cai_ji_xian_zhi="5",
            is_kai_qi_duo_gui_ge_cai_ji=True,
        )
    )
    fake_service = FakeService()

    exit_code = main(
        [
            "--db-path",
            str(db_path),
            "collect",
            "keyword",
            "--keyword",
            "耳机",
        ],
        service_factory=lambda _db_path: fake_service,
    )

    assert exit_code == 0
    kwargs = fake_service.calls[0][1]
    assert kwargs["multi_spec_enabled"] is True
    assert kwargs["per_keyword_success_limit"] == 5
    assert kwargs["filter_config"].browse_min == 100
    assert kwargs["filter_config"].excluded_words == ["定制", "虚拟"]
    assert "saved=2" in capsys.readouterr().out


def test_cli_collect_shop_uses_saved_shop_recent_publish_filter(tmp_path, capsys):
    db_path = tmp_path / "collector.db"
    db = CollectorDatabase(db_path)
    db.initialize()
    repo = AppConfigRepository(db)
    repo.save_gather_conditions(
        GatherConditionConfig(dian_pu_cai_ji_fa_bu_tian_shu_text="72小时内发布")
    )
    fake_service = FakeService()

    exit_code = main(
        [
            "--db-path",
            str(db_path),
            "collect",
            "shop",
            "--shop-url",
            "https://www.goofish.com/?userId=seller-x",
        ],
        service_factory=lambda _db_path: fake_service,
    )

    assert exit_code == 0
    kwargs = fake_service.calls[0][1]
    assert kwargs["recent_publish_filter"] == "72小时内发布"
    assert "saved=3" in capsys.readouterr().out


def test_cli_collect_keyword_falls_back_to_saved_gather_type_input(tmp_path, capsys):
    db_path = tmp_path / "collector.db"
    db = CollectorDatabase(db_path)
    db.initialize()
    repo = AppConfigRepository(db)
    repo.save_gather_type_input(0, "gemini\nclaude")
    fake_service = FakeService()

    exit_code = main(
        [
            "--db-path",
            str(db_path),
            "collect",
            "keyword",
        ],
        service_factory=lambda _db_path: fake_service,
    )

    assert exit_code == 0
    kwargs = fake_service.calls[0][1]
    assert kwargs["keywords"] == ["gemini", "claude"]
    assert "saved=2" in capsys.readouterr().out


def test_cli_collect_manual_falls_back_to_saved_gather_type_input(tmp_path, capsys):
    db_path = tmp_path / "collector.db"
    db = CollectorDatabase(db_path)
    db.initialize()
    repo = AppConfigRepository(db)
    repo.save_gather_type_input(1, "https://www.goofish.com/item?id=2001\nhttps://www.goofish.com/item?id=2002")
    fake_service = FakeService()

    exit_code = main(
        [
            "--db-path",
            str(db_path),
            "collect",
            "manual",
        ],
        service_factory=lambda _db_path: fake_service,
    )

    assert exit_code == 0
    kwargs = fake_service.calls[0][1]
    assert kwargs["urls"] == [
        "https://www.goofish.com/item?id=2001",
        "https://www.goofish.com/item?id=2002",
    ]
    assert "saved=1" in capsys.readouterr().out


def test_cli_collect_shop_falls_back_to_saved_gather_type_input(tmp_path, capsys):
    db_path = tmp_path / "collector.db"
    db = CollectorDatabase(db_path)
    db.initialize()
    repo = AppConfigRepository(db)
    repo.save_gather_type_input(2, "https://www.goofish.com/?userId=seller-a\nhttps://www.goofish.com/?userId=seller-b")
    fake_service = FakeService()

    exit_code = main(
        [
            "--db-path",
            str(db_path),
            "collect",
            "shop",
        ],
        service_factory=lambda _db_path: fake_service,
    )

    assert exit_code == 0
    kwargs = fake_service.calls[0][1]
    assert kwargs["shop_urls"] == [
        "https://www.goofish.com/?userId=seller-a",
        "https://www.goofish.com/?userId=seller-b",
    ]
    assert "saved=3" in capsys.readouterr().out


def test_cli_collect_keyword_returns_nonzero_when_service_raises_collector_error(tmp_path, capsys):
    class FailingService(FakeService):
        def collect_keyword(self, **kwargs):
            raise GoofishBurstError("RGV587_ERROR::SM::哎哟喂,被挤爆啦,请稍后重试!")

    exit_code = main(
        [
            "--db-path",
            str(tmp_path / "collector.db"),
            "collect",
            "keyword",
            "--keyword",
            "gemini",
        ],
        service_factory=lambda _db_path: FailingService(),
    )

    assert exit_code == 2
    assert "collector error" in capsys.readouterr().out


def test_cli_collect_keyword_passes_bitbrowser_cli_args_through_environment(tmp_path, capsys):
    captured = {}

    def service_factory(_db_path):
        captured["bitbrowser_id"] = os.environ.get("XIANYU_COLLECTOR_BITBROWSER_ID")
        captured["bitbrowser_host"] = os.environ.get("XIANYU_COLLECTOR_BITBROWSER_API_HOST")
        captured["bitbrowser_port"] = os.environ.get("XIANYU_COLLECTOR_BITBROWSER_API_PORT")
        return FakeService()

    exit_code = main(
        [
            "--db-path",
            str(tmp_path / "collector.db"),
            "--bitbrowser-id",
            "browser-123",
            "--bitbrowser-api-host",
            "127.0.0.2",
            "--bitbrowser-api-port",
            "60000",
            "collect",
            "keyword",
            "--keyword",
            "gemini",
        ],
        service_factory=service_factory,
    )

    assert exit_code == 0
    assert captured == {
        "bitbrowser_id": "browser-123",
        "bitbrowser_host": "127.0.0.2",
        "bitbrowser_port": "60000",
    }
    assert "saved=2" in capsys.readouterr().out
    assert os.environ.get("XIANYU_COLLECTOR_BITBROWSER_ID") is None


def test_cli_doctor_session_reports_searchable_cookie_source(tmp_path, capsys):
    exit_code = main(
        [
            "--db-path",
            str(tmp_path / "collector.db"),
            "doctor",
            "session",
            "--keyword",
            "gemini",
        ],
        service_factory=lambda _db_path: FakeService(),
    )

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "session=searchable" in output
    assert "cookie_source=SavedCookieProvider" in output
    assert "item_count=2" in output


def test_cli_doctor_session_reports_signing_only_when_search_is_blocked(tmp_path, capsys):
    class FailingSearchApiClient:
        def __init__(self):
            self.cookie_provider = type(
                "FakeCookieProvider",
                (),
                {"_active_provider": type("BitBrowserBrowserSession", (), {})(), "get_cookie_dict": lambda _self: {"_m_h5_tk": "token"}} ,
            )()

        def search_items(self, **kwargs):
            raise GoofishBurstError("RGV587_ERROR::SM::哎哟喂,被挤爆啦,请稍后重试!")

    class FailingService(FakeService):
        def __init__(self):
            super().__init__()
            self.api_client = FailingSearchApiClient()

    exit_code = main(
        [
            "--db-path",
            str(tmp_path / "collector.db"),
            "doctor",
            "session",
            "--keyword",
            "gemini",
        ],
        service_factory=lambda _db_path: FailingService(),
    )

    assert exit_code == 2
    output = capsys.readouterr().out
    assert "session=signing-only" in output
    assert "cookie_source=BitBrowserBrowserSession" in output
    assert "RGV587_ERROR::SM" in output


def test_cli_doctor_session_unwraps_browser_cookie_provider_to_session_name(tmp_path, capsys):
    class WrappedBrowserApiClient:
        def __init__(self):
            session = type("BitBrowserBrowserSession", (), {})()
            active_provider = type(
                "BrowserCookieProvider",
                (),
                {
                    "session": session,
                    "get_cookie_dict": lambda _self: {"_m_h5_tk": "token", "unb": "123"},
                },
            )()
            self.cookie_provider = type(
                "FallbackCookieProvider",
                (),
                {"_active_provider": active_provider, "get_cookie_dict": lambda _self: {"_m_h5_tk": "token", "unb": "123"}},
            )()

        def search_items(self, **kwargs):
            return ["111"]

    class WrappedBrowserService(FakeService):
        def __init__(self):
            super().__init__()
            self.api_client = WrappedBrowserApiClient()

    exit_code = main(
        [
            "--db-path",
            str(tmp_path / "collector.db"),
            "doctor",
            "session",
            "--keyword",
            "gemini",
        ],
        service_factory=lambda _db_path: WrappedBrowserService(),
    )

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "cookie_source=BitBrowserBrowserSession" in output


def test_cli_doctor_compare_reports_probe_rows(tmp_path, capsys, monkeypatch):
    class DummySigner:
        pass

    class CompareService(FakeService):
        def __init__(self):
            super().__init__()
            self.api_client.transport = object()
            self.api_client.signer = DummySigner()
            self.default_bitbrowser_config = BitBrowserConfig(
                browser_id="browser-123",
                api_host="127.0.0.1",
                api_port=54345,
            )

    class FakeSavedCookieProvider:
        def __init__(self, _cookie_string):
            self.label = "saved"

        def get_cookie_dict(self):
            raise ValueError("empty saved cookie")

    class FakeBitBrowserBrowserSession:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class FakeBrowserCookieProvider:
        def __init__(self, session, url):
            self.label = "bitbrowser"
            self.session = session
            self.url = url

        def get_cookie_dict(self):
            return {"_m_h5_tk": "token", "unb": "123"}

    class FakeAnonymousBootstrapCookieProvider:
        def __init__(self, **kwargs):
            self.label = "bootstrap"

        def get_cookie_dict(self):
            return {"_m_h5_tk": "token"}

    class FakeGoofishApiClient:
        def __init__(self, *, transport, cookie_provider, signer):
            self.cookie_provider = cookie_provider

        def search_items(self, **kwargs):
            if self.cookie_provider.label == "bitbrowser":
                return ["111", "222"]
            raise GoofishBurstError("RGV587_ERROR::SM::哎哟喂,被挤爆啦,请稍后重试!")

    monkeypatch.setattr(
        "minitap.mobile_use.collectors.xianyu_collector.cli.SavedCookieProvider",
        FakeSavedCookieProvider,
    )
    monkeypatch.setattr(
        "minitap.mobile_use.collectors.xianyu_collector.cli.BitBrowserBrowserSession",
        FakeBitBrowserBrowserSession,
    )
    monkeypatch.setattr(
        "minitap.mobile_use.collectors.xianyu_collector.cli.BrowserCookieProvider",
        FakeBrowserCookieProvider,
    )
    monkeypatch.setattr(
        "minitap.mobile_use.collectors.xianyu_collector.cli.AnonymousBootstrapCookieProvider",
        FakeAnonymousBootstrapCookieProvider,
    )
    monkeypatch.setattr(
        "minitap.mobile_use.collectors.xianyu_collector.cli.GoofishApiClient",
        FakeGoofishApiClient,
    )

    exit_code = main(
        [
            "--db-path",
            str(tmp_path / "collector.db"),
            "doctor",
            "compare",
            "--keyword",
            "gemini",
        ],
        service_factory=lambda _db_path: CompareService(),
    )

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "source=saved status=unavailable" in output
    assert "source=bitbrowser status=searchable" in output
    assert "item_count=2" in output
    assert "source=bootstrap status=signing-only" in output


def test_cli_doctor_compare_marks_bitbrowser_disabled_when_not_configured(tmp_path, capsys, monkeypatch):
    class DummySigner:
        pass

    class CompareService(FakeService):
        def __init__(self):
            super().__init__()
            self.api_client.transport = object()
            self.api_client.signer = DummySigner()
            self.default_bitbrowser_config = BitBrowserConfig()

    class FakeSavedCookieProvider:
        def __init__(self, _cookie_string):
            self.label = "saved"

        def get_cookie_dict(self):
            raise ValueError("empty saved cookie")

    class FakeAnonymousBootstrapCookieProvider:
        def __init__(self, **kwargs):
            self.label = "bootstrap"

        def get_cookie_dict(self):
            return {"_m_h5_tk": "token"}

    class FakeGoofishApiClient:
        def __init__(self, *, transport, cookie_provider, signer):
            self.cookie_provider = cookie_provider

        def search_items(self, **kwargs):
            raise GoofishBurstError("RGV587_ERROR::SM::哎哟喂,被挤爆啦,请稍后重试!")

    monkeypatch.setattr(
        "minitap.mobile_use.collectors.xianyu_collector.cli.SavedCookieProvider",
        FakeSavedCookieProvider,
    )
    monkeypatch.setattr(
        "minitap.mobile_use.collectors.xianyu_collector.cli.AnonymousBootstrapCookieProvider",
        FakeAnonymousBootstrapCookieProvider,
    )
    monkeypatch.setattr(
        "minitap.mobile_use.collectors.xianyu_collector.cli.GoofishApiClient",
        FakeGoofishApiClient,
    )

    exit_code = main(
        [
            "--db-path",
            str(tmp_path / "collector.db"),
            "doctor",
            "compare",
            "--keyword",
            "gemini",
        ],
        service_factory=lambda _db_path: CompareService(),
    )

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "source=bitbrowser status=disabled" in output


def test_cli_doctor_freshness_reports_missing_signing_token(tmp_path, capsys):
    db_path = tmp_path / "collector.db"

    exit_code = main(
        [
            "--db-path",
            str(db_path),
            "doctor",
            "freshness",
        ]
    )

    assert exit_code == 2
    output = capsys.readouterr().out
    assert "source=saved" in output
    assert "status=missing-signing-token" in output


def test_cli_doctor_freshness_reports_fresh_saved_cookie(tmp_path, capsys, monkeypatch):
    db_path = tmp_path / "collector.db"
    db = CollectorDatabase(db_path)
    db.initialize()
    repo = AppConfigRepository(db)
    repo.save_saved_cookie_string("a=1; _m_h5_tk=token_1710003600000; unb=2207148365801")

    monkeypatch.setattr(
        "minitap.mobile_use.collectors.xianyu_collector.cli._now_ms",
        lambda: 1710000000000,
    )

    exit_code = main(
        [
            "--db-path",
            str(db_path),
            "doctor",
            "freshness",
        ]
    )

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "source=saved" in output
    assert "status=fresh" in output
    assert "remaining_seconds=3600" in output


def test_cli_doctor_freshness_can_auto_refresh_from_bitbrowser(tmp_path, capsys, monkeypatch):
    db_path = tmp_path / "collector.db"
    db = CollectorDatabase(db_path)
    db.initialize()
    repo = AppConfigRepository(db)
    repo.save_bitbrowser_config(
        BitBrowserConfig(
            browser_id="browser-123",
            api_host="127.0.0.1",
            api_port=54345,
        )
    )

    class FakeBitBrowserBrowserSession:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def get_cookie_string(self, url: str) -> str:
            return "a=1; _m_h5_tk=token_1710003600000; unb=2207148365801"

    monkeypatch.setattr(
        "minitap.mobile_use.collectors.xianyu_collector.cli.BitBrowserBrowserSession",
        FakeBitBrowserBrowserSession,
    )
    monkeypatch.setattr(
        "minitap.mobile_use.collectors.xianyu_collector.cli._now_ms",
        lambda: 1710000000000,
    )

    exit_code = main(
        [
            "--db-path",
            str(db_path),
            "doctor",
            "freshness",
            "--refresh-from-bitbrowser-if-needed",
        ]
    )

    assert exit_code == 0
    assert repo.load_saved_cookie_string() == "a=1; _m_h5_tk=token_1710003600000; unb=2207148365801"
    output = capsys.readouterr().out
    assert "status=fresh" in output
    assert "refresh=performed" in output


def test_cli_doctor_freshness_skips_refresh_when_cookie_is_already_fresh(tmp_path, capsys, monkeypatch):
    db_path = tmp_path / "collector.db"
    db = CollectorDatabase(db_path)
    db.initialize()
    repo = AppConfigRepository(db)
    repo.save_saved_cookie_string("a=1; _m_h5_tk=token_1710003600000; unb=2207148365801")
    repo.save_bitbrowser_config(
        BitBrowserConfig(
            browser_id="browser-123",
            api_host="127.0.0.1",
            api_port=54345,
        )
    )

    class FakeBitBrowserBrowserSession:
        def __init__(self, **kwargs):
            raise AssertionError("should not refresh when cookie is already fresh")

    monkeypatch.setattr(
        "minitap.mobile_use.collectors.xianyu_collector.cli.BitBrowserBrowserSession",
        FakeBitBrowserBrowserSession,
    )
    monkeypatch.setattr(
        "minitap.mobile_use.collectors.xianyu_collector.cli._now_ms",
        lambda: 1710000000000,
    )

    exit_code = main(
        [
            "--db-path",
            str(db_path),
            "doctor",
            "freshness",
            "--refresh-from-bitbrowser-if-needed",
        ]
    )

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "status=fresh" in output
    assert "refresh=not-needed" in output


def test_cli_doctor_ensure_searchable_skips_refresh_when_saved_is_already_searchable(
    tmp_path, capsys, monkeypatch
):
    db_path = tmp_path / "collector.db"
    db = CollectorDatabase(db_path)
    db.initialize()
    repo = AppConfigRepository(db)
    repo.save_saved_cookie_string("a=1; _m_h5_tk=token_1710003600000; unb=2207148365801")
    repo.save_bitbrowser_config(
        BitBrowserConfig(
            browser_id="browser-123",
            api_host="127.0.0.1",
            api_port=54345,
        )
    )

    class GuardBitBrowserBrowserSession:
        def __init__(self, **kwargs):
            raise AssertionError("should not refresh when saved is already searchable")

    class FakeGoofishApiClient:
        def __init__(self, *, transport, cookie_provider, signer):
            self.cookie_provider = cookie_provider

        def search_items(self, **kwargs):
            return ["111", "222"]

    monkeypatch.setattr(
        "minitap.mobile_use.collectors.xianyu_collector.cli.BitBrowserBrowserSession",
        GuardBitBrowserBrowserSession,
    )
    monkeypatch.setattr(
        "minitap.mobile_use.collectors.xianyu_collector.cli.GoofishApiClient",
        FakeGoofishApiClient,
    )
    monkeypatch.setattr(
        "minitap.mobile_use.collectors.xianyu_collector.cli._now_ms",
        lambda: 1710000000000,
    )

    exit_code = main(
        [
            "--db-path",
            str(db_path),
            "doctor",
            "ensure-searchable",
            "--keyword",
            "gemini",
        ]
    )

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "source=saved" in output
    assert "status=searchable" in output
    assert "item_count=2" in output
    assert "repair=not-needed" in output


def test_cli_doctor_ensure_searchable_refreshes_from_bitbrowser_when_saved_fails(
    tmp_path, capsys, monkeypatch
):
    db_path = tmp_path / "collector.db"
    db = CollectorDatabase(db_path)
    db.initialize()
    repo = AppConfigRepository(db)
    repo.save_bitbrowser_config(
        BitBrowserConfig(
            browser_id="browser-123",
            api_host="127.0.0.1",
            api_port=54345,
        )
    )

    class FakeBitBrowserBrowserSession:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def get_cookie_string(self, url: str) -> str:
            return "a=1; _m_h5_tk=token_1710003600000; unb=2207148365801"

    class FakeGoofishApiClient:
        def __init__(self, *, transport, cookie_provider, signer):
            self.cookie_provider = cookie_provider

        def search_items(self, **kwargs):
            cookies = self.cookie_provider.get_cookie_dict()
            if cookies.get("_m_h5_tk"):
                return ["111", "222", "333"]
            raise GoofishBurstError("RGV587_ERROR::SM::哎哟喂,被挤爆啦,请稍后重试!")

    monkeypatch.setattr(
        "minitap.mobile_use.collectors.xianyu_collector.cli.BitBrowserBrowserSession",
        FakeBitBrowserBrowserSession,
    )
    monkeypatch.setattr(
        "minitap.mobile_use.collectors.xianyu_collector.cli.GoofishApiClient",
        FakeGoofishApiClient,
    )
    monkeypatch.setattr(
        "minitap.mobile_use.collectors.xianyu_collector.cli._now_ms",
        lambda: 1710000000000,
    )

    exit_code = main(
        [
            "--db-path",
            str(db_path),
            "doctor",
            "ensure-searchable",
            "--keyword",
            "gemini",
        ]
    )

    assert exit_code == 0
    assert repo.load_saved_cookie_string() == "a=1; _m_h5_tk=token_1710003600000; unb=2207148365801"
    output = capsys.readouterr().out
    assert "source=saved" in output
    assert "status=searchable" in output
    assert "item_count=3" in output
    assert "repair=performed" in output


def test_cli_collect_keyword_can_preflight_ensure_searchable(tmp_path, capsys, monkeypatch):
    fake_service = FakeService()
    captured = {}

    def fake_ensure_saved_searchable(*, service, config_repo, keyword):
        captured["keyword"] = keyword
        return {
            "source": "saved",
            "status": "searchable",
            "cookie_source": "SavedCookieProvider",
            "item_count": 30,
            "repair": "not-needed",
            "freshness": "fresh",
        }

    monkeypatch.setattr(
        "minitap.mobile_use.collectors.xianyu_collector.cli._ensure_saved_searchable",
        fake_ensure_saved_searchable,
    )

    exit_code = main(
        [
            "--db-path",
            str(tmp_path / "collector.db"),
            "collect",
            "keyword",
            "--ensure-searchable",
            "--keyword",
            "gemini",
            "--pages",
            "1",
        ],
        service_factory=lambda _db_path: fake_service,
    )

    assert exit_code == 0
    assert captured["keyword"] == "gemini"
    assert fake_service.calls[0][0] == "keyword"
    output = capsys.readouterr().out
    assert "preflight source=saved status=searchable" in output
    assert "saved=2" in output


def test_cli_collect_stops_when_preflight_cannot_make_saved_searchable(tmp_path, capsys, monkeypatch):
    fake_service = FakeService()

    monkeypatch.setattr(
        "minitap.mobile_use.collectors.xianyu_collector.cli._ensure_saved_searchable",
        lambda **kwargs: {
            "source": "saved",
            "status": "signing-only",
            "cookie_source": "SavedCookieProvider",
            "repair": "failed",
            "reason": "RGV587",
        },
    )

    exit_code = main(
        [
            "--db-path",
            str(tmp_path / "collector.db"),
            "collect",
            "keyword",
            "--ensure-searchable",
            "--keyword",
            "gemini",
        ],
        service_factory=lambda _db_path: fake_service,
    )

    assert exit_code == 2
    assert fake_service.calls == []
    output = capsys.readouterr().out
    assert "preflight source=saved status=signing-only" in output
