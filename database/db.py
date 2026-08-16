import os
import sqlite3
from datetime import date

from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "expense_tracker.db")


def get_db_path():
    """Return the SQLite file path.

    Reads the environment on every call so the test suite can point the
    whole app at a throwaway database without touching the real one.
    """
    return os.environ.get("SPENDLY_DB_PATH", DEFAULT_DB_PATH)


def get_db():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.commit()
    finally:
        conn.close()


def seed_db():
    conn = get_db()
    try:
        existing = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if existing > 0:
            return

        password_hash = generate_password_hash("demo123")
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", password_hash),
        )
        user_id = cursor.lastrowid

        today = date.today()
        sample_expenses = [
            (2, "Food", 45.50, "Grocery shopping"),
            (4, "Transport", 18.00, "Uber ride"),
            (7, "Bills", 120.00, "Electricity bill"),
            (10, "Health", 35.75, "Pharmacy"),
            (13, "Entertainment", 60.00, "Movie tickets"),
            (16, "Shopping", 89.99, "New shoes"),
            (20, "Other", 15.00, "Miscellaneous"),
            (24, "Food", 32.20, "Restaurant dinner"),
        ]
        for day, category, amount, description in sample_expenses:
            expense_date = today.replace(day=day).isoformat()
            conn.execute(
                """
                INSERT INTO expenses (user_id, amount, category, date, description)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, amount, category, expense_date, description),
            )
        conn.commit()
    finally:
        conn.close()


def get_user_by_email(email):
    """Return the user row matching this email, or None."""
    conn = get_db()
    try:
        return conn.execute(
            """
            SELECT id, name, email, password_hash, created_at
            FROM users
            WHERE email = ?
            """,
            (email,),
        ).fetchone()
    finally:
        conn.close()


def create_user(name, email, password_hash):
    """Insert a new user and return the new row id.

    Raises sqlite3.IntegrityError if the email is already taken.
    """
    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()
