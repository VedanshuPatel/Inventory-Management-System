import os
import sqlite3
from pathlib import Path
from __future__ import annotations


DEFAULT_DB_PATH = Path(__file__).resolve().with_name("inventory.db")
SCHEMA_PATH = Path(__file__).resolve().with_name("schema.sql")

def connect(db_path: str | Path | None = None) -> sqlite3.Connection:
    """Open a connection with foreign keys on and Row factory."""
    if db_path is None:
        db_path = os.environ.get("INVENTORY_DB", str(DEFAULT_DB_PATH))
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Create tables from schema.sql if they do not already exist."""
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(schema)