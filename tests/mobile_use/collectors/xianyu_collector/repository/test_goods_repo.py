from minitap.mobile_use.collectors.xianyu_collector.repository.goods_repo import GoodsRepository
from minitap.mobile_use.collectors.xianyu_collector.repository.sqlite_db import CollectorDatabase


def test_insert_goods_defaults_to_collected_status_and_lists_item_ids(tmp_path):
    db = CollectorDatabase(tmp_path / "collector.db")
    db.initialize()
    repo = GoodsRepository(db)

    repo.insert_good({"item_id": "1001", "title": "A"})
    repo.insert_good({"item_id": "1002", "title": "B"})

    rows = repo.list_goods_by_status(0)

    assert [row["item_id"] for row in rows] == ["1001", "1002"]
    assert repo.list_goods_item_ids() == ["1001", "1002"]


def test_batch_insert_goods_defaults_to_pending_publish_status(tmp_path):
    db = CollectorDatabase(tmp_path / "collector.db")
    db.initialize()
    repo = GoodsRepository(db)

    repo.batch_insert_goods(
        [
            {"item_id": "2001", "title": "A"},
            {"item_id": "2002", "title": "B"},
        ]
    )

    pending_rows = repo.list_goods_by_status(1)

    assert [row["item_id"] for row in pending_rows] == ["2001", "2002"]


def test_batch_update_goods_status_moves_rows_between_status_buckets(tmp_path):
    db = CollectorDatabase(tmp_path / "collector.db")
    db.initialize()
    repo = GoodsRepository(db)

    first_id = repo.insert_good({"item_id": "3001", "title": "A"})
    second_id = repo.insert_good({"item_id": "3002", "title": "B"})

    updated = repo.batch_update_goods_status([first_id, second_id], 3)

    assert updated == 2
    assert repo.list_goods_by_status(0) == []
    assert [row["item_id"] for row in repo.list_goods_by_status(3)] == ["3001", "3002"]
