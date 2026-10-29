import os
import sqlite3
from pathlib import Path

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


class InventoryError(Exception):
    """Base error class for inventory rule violations."""


class ProductHasSalesError(InventoryError):
    """Raised when deleting a product that appears in sale_items."""


def add_product(conn,sku,name,category,supplier_id,unit_price_cents,quantity_on_hand=0,reorder_level=0):
    """Insert a product and return its new id."""
    with conn:
        cur = conn.execute(
            """
            INSERT INTO products (sku, name, category, supplier_id,unit_price_cents, quantity_on_hand, reorder_level) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sku,name,category,supplier_id,unit_price_cents,quantity_on_hand,reorder_level,
            ),
        )
        return cur.lastrowid


def get_product(conn, product_id):
    """Return one product with supplier_name, or None."""
    return conn.execute(
        """
        SELECT p.*, s.name AS supplier_name FROM products p
        JOIN suppliers s ON s.id = p.supplier_id
        WHERE p.id = ?
        """,
        (product_id,),
    ).fetchone()


def update_price(conn, product_id, unit_price_cents):
    """Update unit price. True if a row changed, False if missing."""
    with conn:
        cur = conn.execute(
            """
            UPDATE products SET unit_price_cents = ?
            WHERE id = ?
            """,
            (unit_price_cents, product_id),
        )
        return cur.rowcount == 1


def delete_product(conn, product_id):
    """Delete a product. Raises if it has sales history."""
    with conn:
        sold = conn.execute(
            """
            SELECT 1 FROM sale_items WHERE product_id = ?
            LIMIT 1
            """,
            (product_id,),
        ).fetchone()
        if sold is not None:
            raise ProductHasSalesError(
                "Product cannot be deleted because it has sales history."
            )
        conn.execute("DELETE FROM products WHERE id = ?", (product_id,))

def search_products(conn,text,category=None,max_price_cents=None,in_stock_only=False,low_stock_only=False,):
    pattern = "%" + text + "%"
    sql = """
        SELECT p.*, s.name AS supplier_name FROM products p
        JOIN suppliers s ON s.id = p.supplier_id
        WHERE (LOWER(p.name) LIKE LOWER(?) OR LOWER(p.sku) LIKE LOWER(?) OR LOWER(s.name) LIKE LOWER(?))
    """
    params = [pattern, pattern, pattern]
    if category is not None:
        sql += " AND p.category = ?"
        params.append(category)
    if max_price_cents is not None:
        sql += " AND p.unit_price_cents <= ?"
        params.append(max_price_cents)
    if in_stock_only:
        sql += " AND p.quantity_on_hand > 0"
    if low_stock_only:
        sql += " AND p.quantity_on_hand <= p.reorder_level"
    sql += " ORDER BY p.name"
    return conn.execute(sql, params).fetchall()