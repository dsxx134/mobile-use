from __future__ import annotations

import ast
from datetime import datetime
from typing import Any

from minitap.mobile_use.collectors.xianyu_collector.repository.sqlite_db import CollectorDatabase


class GoodsRepository:
    def __init__(self, database: CollectorDatabase):
        self.database = database

    def insert_good(self, data_dict: dict[str, Any], *, status: int = 0) -> int:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO app_goods (
                    dataDict,
                    sort,
                    createTime,
                    status,
                    result,
                    releaseTime,
                    faBuShiJian
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (str(data_dict), 0, now, status, "", "", ""),
            )
            connection.commit()
            return int(cursor.lastrowid)

    def batch_insert_goods(self, goods: list[dict[str, Any]]) -> list[int]:
        inserted_ids: list[int] = []
        for item in goods:
            inserted_ids.append(self.insert_good(item, status=1))
        return inserted_ids

    def list_goods_item_ids(self) -> list[str]:
        with self.database.connect() as connection:
            rows = connection.execute("SELECT dataDict FROM app_goods ORDER BY id").fetchall()

        item_ids: list[str] = []
        for row in rows:
            data_dict = ast.literal_eval(row["dataDict"])
            item_id = data_dict.get("item_id")
            if item_id:
                item_ids.append(str(item_id))
        return item_ids

    def list_goods_by_status(self, status: int) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT id, dataDict, status FROM app_goods WHERE status = ? ORDER BY id",
                (status,),
            ).fetchall()

        result: list[dict[str, Any]] = []
        for row in rows:
            data_dict = ast.literal_eval(row["dataDict"])
            result.append(
                {
                    "db_id": int(row["id"]),
                    "status": int(row["status"]),
                    **data_dict,
                }
            )
        return result

    def batch_update_goods_status(self, ids: list[int], status: int) -> int:
        if not ids:
            return 0

        placeholders = ",".join("?" for _ in ids)
        params = [status, *ids]
        with self.database.connect() as connection:
            cursor = connection.execute(
                f"UPDATE app_goods SET status = ? WHERE id IN ({placeholders})",
                params,
            )
            connection.commit()
            return int(cursor.rowcount)
