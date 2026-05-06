"""Create the local SQLite schema by executing create_tables_sqlite.sql.

Idempotent: if local.db already exists with tables, it does nothing.
"""
import os
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "local.db")
SQL_PATH = os.path.join(ROOT, "create_tables_sqlite.sql")


def main() -> None:
    if not os.path.exists(SQL_PATH):
        sys.exit(f"Missing schema file: {SQL_PATH}")

    fresh = not os.path.exists(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        with open(SQL_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
    finally:
        conn.close()

    print(f"{'Created' if fresh else 'Verified'} schema at {DB_PATH}")


if __name__ == "__main__":
    main()
