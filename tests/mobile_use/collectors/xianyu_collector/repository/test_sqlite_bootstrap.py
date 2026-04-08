from minitap.mobile_use.collectors.xianyu_collector.repository.sqlite_db import CollectorDatabase


def test_initialize_creates_required_tables_and_columns(tmp_path):
    db = CollectorDatabase(tmp_path / "collector.db")

    db.initialize()

    assert set(db.list_tables()) >= {"app_goods", "app_user_config"}
    assert db.table_columns("app_user_config") == [
        "id",
        "keyCode",
        "gatherConfig",
        "gradeConfig",
        "xiaJiaConfig",
    ]
    assert db.table_columns("app_goods") == [
        "id",
        "dataDict",
        "sort",
        "createTime",
        "status",
        "result",
        "releaseTime",
        "faBuShiJian",
    ]
