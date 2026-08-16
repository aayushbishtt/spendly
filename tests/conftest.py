"""Test configuration for Spendly.

IMPORTANT: the environment variable below must be set *before* ``app`` is
imported. ``app.py`` calls ``init_db()`` and ``seed_db()`` at import time, so
importing it with the default path would create and seed the developer's real
``expense_tracker.db``. pytest imports conftest.py before any test module, so
setting it at module level here is early enough.

Do not let an autoformatter hoist the imports above the os.environ line.
"""

import os
import shutil
import sys
import tempfile

import pytest

# 1. Put the project root on sys.path so ``import app`` works. pytest's default
#    import mode only puts tests/ on the path, not the project root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 2. Redirect the database BEFORE importing the application.
_IMPORT_TIME_DIR = tempfile.mkdtemp(prefix="spendly-tests-")
os.environ["SPENDLY_DB_PATH"] = os.path.join(_IMPORT_TIME_DIR, "import-time.db")

# 3. Only now is it safe to import the app.
from app import app as flask_app          # noqa: E402
from database.db import get_db, init_db   # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _clean_import_time_db():
    """Remove the throwaway database that app.py creates when it is imported."""
    yield
    shutil.rmtree(_IMPORT_TIME_DIR, ignore_errors=True)


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    """Give every test its own empty database.

    ``get_db()`` reads SPENDLY_DB_PATH on every call, so re-pointing the
    variable here is enough — no module reloading required. ``seed_db()`` is
    deliberately NOT called: tests start with zero users and create exactly
    the rows they need.
    """
    db_file = tmp_path / "spendly-test.db"
    monkeypatch.setenv("SPENDLY_DB_PATH", str(db_file))
    init_db()
    yield db_file


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    return flask_app.test_client()


def fetch_user(email):
    """Read a user row straight from the test database."""
    conn = get_db()
    try:
        return conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
    finally:
        conn.close()


def count_users():
    conn = get_db()
    try:
        return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    finally:
        conn.close()
