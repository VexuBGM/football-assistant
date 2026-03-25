import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Optional, Sequence

_DB_CONN: Optional[sqlite3.Connection] = None


def get_db_path() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "football_clubs.db"))


def get_connection() -> sqlite3.Connection:
    global _DB_CONN
    if _DB_CONN is None:
        try:
            _DB_CONN = sqlite3.connect(get_db_path())
            _DB_CONN.row_factory = sqlite3.Row
            _DB_CONN.execute("PRAGMA foreign_keys = ON;")
        except sqlite3.Error as exc:
            raise RuntimeError(f"DB connection failed: {exc}") from exc
    return _DB_CONN


@contextmanager
def transaction() -> Iterator[sqlite3.Cursor]:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN")
        yield cursor
        conn.commit()
    except sqlite3.Error as exc:
        conn.rollback()
        raise RuntimeError(f"DB transaction error: {exc}") from exc
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()


def execute(sql: str, params: Sequence[Any] = ()) -> int:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount
    except sqlite3.Error as exc:
        raise RuntimeError(f"DB execute error: {exc} | SQL={sql} | params={params}") from exc


def fetch_all(sql: str, params: Sequence[Any] = ()) -> list[sqlite3.Row]:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()
    except sqlite3.Error as exc:
        raise RuntimeError(f"DB fetch_all error: {exc} | SQL={sql} | params={params}") from exc


def fetch_one(sql: str, params: Sequence[Any] = ()) -> Optional[sqlite3.Row]:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchone()
    except sqlite3.Error as exc:
        raise RuntimeError(f"DB fetch_one error: {exc} | SQL={sql} | params={params}") from exc


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND lower(name) = lower(?)",
        (table_name,),
    ).fetchone()
    return row is not None


def _column_names(conn: sqlite3.Connection, table_name: str) -> set[str]:
    if not _table_exists(conn, table_name):
        return set()
    rows = conn.execute(f'PRAGMA table_info("{table_name}")').fetchall()
    return {row["name"] for row in rows}


def _rename_legacy_table(conn: sqlite3.Connection, table_name: str, id_column: str, legacy_name: str) -> None:
    columns = _column_names(conn, table_name)
    if columns and id_column in columns and "id" not in columns and not _table_exists(conn, legacy_name):
        conn.execute(f'ALTER TABLE "{table_name}" RENAME TO "{legacy_name}"')


def _copy_legacy_data(conn: sqlite3.Connection) -> None:
    if _table_exists(conn, "clubs_legacy"):
        conn.execute(
            """
            INSERT OR IGNORE INTO clubs (id, name, city, founded_year)
            SELECT club_id, name, city, founded_year
            FROM clubs_legacy
            """
        )

    if _table_exists(conn, "players_legacy"):
        conn.execute(
            """
            INSERT OR IGNORE INTO players (
              id, full_name, birth_date, nationality, position, number, status, club_id
            )
            SELECT
              player_id,
              full_name,
              birth_date,
              nationality,
              position,
              number,
              status,
              club_id
            FROM players_legacy
            """
        )

    if _table_exists(conn, "matches_legacy"):
        conn.execute(
            """
            INSERT OR IGNORE INTO matches (
              id, home_club_id, away_club_id, match_date, home_score, away_score
            )
            SELECT
              match_id,
              home_club_id,
              away_club_id,
              match_date,
              home_score,
              away_score
            FROM matches_legacy
            """
        )

    for legacy_name in ("players_legacy", "matches_legacy", "clubs_legacy"):
        if _table_exists(conn, legacy_name):
            conn.execute(f'DROP TABLE "{legacy_name}"')


def _load_schema(conn: sqlite3.Connection, schema_path: str) -> None:
    with open(schema_path, "r", encoding="utf-8") as schema_file:
        conn.executescript(schema_file.read())


def init_db(schema_path: Optional[str] = None) -> None:
    if schema_path is None:
        schema_path = str(Path(__file__).resolve().parents[2] / "sql" / "schema.sql")

    conn = get_connection()
    try:
        conn.execute("PRAGMA foreign_keys = OFF;")
        _rename_legacy_table(conn, "clubs", "club_id", "clubs_legacy")
        _rename_legacy_table(conn, "players", "player_id", "players_legacy")
        _rename_legacy_table(conn, "matches", "match_id", "matches_legacy")
        _load_schema(conn, schema_path)
        _copy_legacy_data(conn)
        conn.commit()
    except (OSError, sqlite3.Error) as exc:
        conn.rollback()
        raise RuntimeError(f"DB init failed: {exc}") from exc
    finally:
        conn.execute("PRAGMA foreign_keys = ON;")
