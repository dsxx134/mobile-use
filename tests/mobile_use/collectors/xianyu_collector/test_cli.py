from minitap.mobile_use.collectors.xianyu_collector.cli import main
from minitap.mobile_use.collectors.xianyu_collector.models import GatherConditionConfig
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
