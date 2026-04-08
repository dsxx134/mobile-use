from minitap.mobile_use.collectors.xianyu_collector.repository.app_config_repo import AppConfigRepository
from minitap.mobile_use.collectors.xianyu_collector.repository.sqlite_db import CollectorDatabase


def test_saved_cookie_string_round_trips_through_grade_config(tmp_path):
    db = CollectorDatabase(tmp_path / "collector.db")
    db.initialize()
    repo = AppConfigRepository(db)

    repo.save_saved_cookie_string("a=1; _m_h5_tk=token_123")

    assert repo.load_saved_cookie_string() == "a=1; _m_h5_tk=token_123"
