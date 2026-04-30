# tests/conftest.py
import os
import re
import uuid
import pytest

from src import db


@pytest.fixture(autouse=True)
def _fresh_db(monkeypatch, request):
    """Each test gets a fresh SQLite DB in the writable repository workspace."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db_dir = os.path.join(repo_root, ".test_dbs")
    os.makedirs(db_dir, exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", request.node.nodeid)
    db_file = os.path.join(db_dir, f"{safe_name}-{uuid.uuid4().hex}.db")

    # Reset the module-level connection
    db._DB_CONN = None
    monkeypatch.setattr(db, "get_db_path", lambda: db_file)

    schema_path = os.path.join(os.path.dirname(__file__), "..", "sql", "schema.sql")
    db.init_db(schema_path)

    yield

    if db._DB_CONN is not None:
        db._DB_CONN.close()
        db._DB_CONN = None

    if os.path.exists(db_file):
        os.remove(db_file)
