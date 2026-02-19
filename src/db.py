# src/db.py
import os
import sqlite3
from typing import Any, Iterable, Optional, Sequence, Tuple

_DB_CONN: Optional[sqlite3.Connection] = None


def get_db_path() -> str:
    # Базата ще е в корена на проекта: project/football_clubs.db
    # (може да промениш името ако искаш)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "football_clubs.db"))


def get_connection() -> sqlite3.Connection:
    """
    Централизирана връзка към SQLite.
    """
    global _DB_CONN
    if _DB_CONN is None:
        try:
            db_path = get_db_path()
            _DB_CONN = sqlite3.connect(db_path)
            _DB_CONN.row_factory = sqlite3.Row
            _DB_CONN.execute("PRAGMA foreign_keys = ON;")
        except sqlite3.Error as e:
            raise RuntimeError(f"DB connection failed: {e}") from e
    return _DB_CONN


def execute(sql: str, params: Sequence[Any] = ()) -> int:
    """
    Изпълнява INSERT/UPDATE/DELETE.
    Връща броя засегнати редове.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        return cur.rowcount
    except sqlite3.Error as e:
        raise RuntimeError(f"DB execute error: {e} | SQL={sql} | params={params}") from e


def fetch_all(sql: str, params: Sequence[Any] = ()) -> list[sqlite3.Row]:
    """
    Връща всички редове от SELECT.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()
    except sqlite3.Error as e:
        raise RuntimeError(f"DB fetch_all error: {e} | SQL={sql} | params={params}") from e


def fetch_one(sql: str, params: Sequence[Any] = ()) -> Optional[sqlite3.Row]:
    """
    Връща един ред от SELECT или None.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, params)
        return cur.fetchone()
    except sqlite3.Error as e:
        raise RuntimeError(f"DB fetch_one error: {e} | SQL={sql} | params={params}") from e


def init_db(schema_path: Optional[str] = None) -> None:
    """
    Зарежда schema.sql (ако таблиците не съществуват).
    """
    if schema_path is None:
        schema_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sql", "schema.sql"))

    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        conn = get_connection()
        conn.executescript(schema_sql)
        conn.commit()
    except (OSError, sqlite3.Error) as e:
        raise RuntimeError(f"DB init failed: {e}") from e
