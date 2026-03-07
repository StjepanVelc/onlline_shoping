from contextlib import asynccontextmanager
from pathlib import Path
import sqlite3

from fastapi import FastAPI

DB_PATH = Path("data/shop.db")
SQL_INIT_FILE = Path("data/database.sql")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """Initialize SQLite schema from data/database.sql or fallback SQL."""
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        if SQL_INIT_FILE.exists() and SQL_INIT_FILE.read_text(encoding="utf-8").strip():
            cur.executescript(SQL_INIT_FILE.read_text(encoding="utf-8"))
        else:
            cur.executescript(
                """
                PRAGMA foreign_keys=ON;

                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    country TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL CHECK (price >= 0),
                    stock INTEGER NOT NULL CHECK (stock >= 0)
                );

                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    address TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    order_date TEXT NOT NULL DEFAULT (datetime('now')),
                    total_amount REAL,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE RESTRICT
                );

                CREATE TABLE IF NOT EXISTS order_items (
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL CHECK (quantity > 0),
                    price REAL NOT NULL CHECK (price >= 0),
                    PRIMARY KEY(order_id, product_id),
                    FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE,
                    FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE RESTRICT
                );
                """
            )

        # Lightweight migration for older databases created before admin auth.
        admins_columns = {
            row[1]
            for row in cur.execute("PRAGMA table_info(admins)").fetchall()
        }
        if "password_hash" not in admins_columns:
            cur.execute(
                "ALTER TABLE admins ADD COLUMN password_hash TEXT NOT NULL DEFAULT ''"
            )
        conn.commit()
    finally:
        conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield