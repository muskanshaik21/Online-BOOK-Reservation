"""Initialize BookNest's department catalogue from the shared application seed data."""

import sqlite3

from app import DB_PATH, init_db


if __name__ == "__main__":
    init_db()
    with sqlite3.connect(DB_PATH) as connection:
        total = connection.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    print(f"BookNest catalogue ready with {total} books.")
