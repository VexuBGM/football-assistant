# tests/conftest.py
import os
import sqlite3
import pytest

from src import db


@pytest.fixture(autouse=True)
def _fresh_db(tmp_path, monkeypatch):
    """Each test gets a fresh in-memory-like SQLite DB (file in tmp_path)."""
    db_file = str(tmp_path / "test.db")

    # Reset the module-level connection
    db._DB_CONN = None
    monkeypatch.setattr(db, "get_db_path", lambda: db_file)

    schema_path = os.path.join(os.path.dirname(__file__), "..", "sql", "schema.sql")
    db.init_db(schema_path)

    yield

    if db._DB_CONN is not None:
        db._DB_CONN.close()
        db._DB_CONN = None
