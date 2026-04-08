from __future__ import annotations

from pathlib import Path
import sqlite3


APP_USER_CONFIG_SCHEMA = """
CREATE TABLE IF NOT EXISTS app_user_config (
    id INTEGER NOT NULL,
    keyCode TEXT,
    gatherConfig TEXT,
    gradeConfig TEXT,
    xiaJiaConfig TEXT,
    PRIMARY KEY (id)
)
"""


APP_GOODS_SCHEMA = """
CREATE TABLE IF NOT EXISTS app_goods (
    id INTEGER NOT NULL,
    dataDict TEXT,
    sort INTEGER,
    createTime TEXT,
    status INTEGER,
    result TEXT,
    releaseTime TEXT,
    faBuShiJian TEXT,
    PRIMARY KEY (id)
)
"""


class CollectorDatabase:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)

    def connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.execute(APP_USER_CONFIG_SCHEMA)
            connection.execute(APP_GOODS_SCHEMA)
            connection.commit()

    def list_tables(self) -> list[str]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
                """
            ).fetchall()
        return [row["name"] for row in rows]

    def table_columns(self, table_name: str) -> list[str]:
        with self.connect() as connection:
            rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
        return [row["name"] for row in rows]
