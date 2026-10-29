import os
import sqlite3
from datetime import UTC, datetime
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

class InvalidAmountError(InventoryError):
    """Raised when an amount is zero or otherwise invalid"""


class UnknownProductError(InventoryError):
    """Raised when a product id does not exist"""


class InsufficientStockError(InventoryError):
    """Raised when stock would go below zero"""


class DuplicateProductInSaleError(InventoryError):
    """Raised when the same product appears twice in one sale"""


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
    """Find products by name, SKU, or supplier with optional filters sorted by name."""
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



def report_low_stock(conn):
    """Products at or below reorder level with how many units short"""
    return conn.execute(
        """
        SELECT sku, name, quantity_on_hand, reorder_level, (reorder_level - quantity_on_hand) AS units_short
        FROM products WHERE quantity_on_hand <= reorder_level
        ORDER BY name
        """
    ).fetchall()

def report_never_sold(conn):
    """Products that do not appear in any sale"""
    return conn.execute(
        """
        SELECT sku, name FROM products p
        WHERE NOT EXISTS (SELECT 1 FROM sale_items si WHERE si.product_id = p.id)
        ORDER BY name
        """
    ).fetchall()

def report_stock_value_by_supplier(conn):
    """Supplier name and total stock value in cents with highest first"""
    return conn.execute(
        """
        SELECT s.name, SUM(p.unit_price_cents * p.quantity_on_hand) AS total_cents
        FROM products p JOIN suppliers s ON s.id = p.supplier_id
        GROUP BY s.id, s.name
        ORDER BY total_cents DESC
        """
    ).fetchall()

def report_sales_by_product(conn):
    """Units sold and revenue in cents per product with highest revenue first"""
    return conn.execute(
        """
        SELECT p.name, p.sku, SUM(si.quantity) AS units_sold, SUM(si.quantity * si.unit_price_cents) AS revenue_cents
        FROM sale_items si JOIN products p ON p.id = si.product_id
        GROUP BY p.id, p.name, p.sku
        ORDER BY revenue_cents DESC, p.name
        """
    ).fetchall()


def _default_timestamp():
    """Return the current time in UTC with microseconds removed"""
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def adjust_stock(conn, product_id, delta, occurred_at=None):
    """Change stock by a signed amount and log an adjustment movement"""
    if delta == 0:
        raise InvalidAmountError("adjustment delta cannot be zero")
    if occurred_at is None:
        occurred_at = _default_timestamp()

    with conn:
        row = conn.execute("SELECT quantity_on_hand FROM products WHERE id = ?",(product_id,),).fetchone()
        if row is None:
            raise UnknownProductError("product not found")
        if row["quantity_on_hand"] + delta < 0:
            raise InsufficientStockError("adjustment would make stock negative")

        conn.execute("""UPDATE products SET quantity_on_hand = quantity_on_hand + ? WHERE id = ?""",
            (delta, product_id),)
        conn.execute(
            """
            INSERT INTO stock_movements (product_id, delta, reason, occurred_at)
            VALUES (?, ?, 'adjustment', ?)
            """,
            (product_id, delta, occurred_at),)


def record_sale(conn, items, sold_at=None):
    """Record a sale with line items with all-or-nothing inside one transaction"""
    if not items:
        raise InvalidAmountError("sale must include at least one item")

    product_ids = [product_id for product_id, _qty in items]
    if len(product_ids) != len(set(product_ids)):
        raise DuplicateProductInSaleError("same product listed twice in one sale")

    if sold_at is None:
        sold_at = _default_timestamp()
    with conn:
        cur = conn.execute("INSERT INTO sales (sold_at) VALUES (?)",(sold_at,),)
        sale_id = cur.lastrowid
        for product_id, qty in items:
            if qty <= 0:
                raise InvalidAmountError("sale quantity must be positive")

            product = conn.execute(
                """
                SELECT unit_price_cents, quantity_on_hand FROM products WHERE id = ?
                """,
                (product_id,),
            ).fetchone()
            if product is None:
                raise UnknownProductError("product not found")
            if qty > product["quantity_on_hand"]:
                raise InsufficientStockError("not enough stock for sale")

            conn.execute("""INSERT INTO sale_items (sale_id, product_id, quantity, unit_price_cents) VALUES (?, ?, ?, ?)""",
                (sale_id, product_id, qty, product["unit_price_cents"]),)
            conn.execute("""UPDATE products SET quantity_on_hand = quantity_on_hand - ? WHERE id = ?""",
                (qty, product_id),)
            conn.execute("""INSERT INTO stock_movements (product_id, delta, reason, occurred_at) VALUES (?, ?, 'sale', ?)""",
                (product_id, -qty, sold_at),)

        return sale_id

def restock(conn, product_id, amount, occurred_at=None):
    """Increase stock by a positive amount and log a restock movement"""
    if amount <= 0:
        raise InvalidAmountError("restock amount must be positive")
    if occurred_at is None:
        occurred_at = _default_timestamp()

    with conn:
        cur = conn.execute("""UPDATE products SET quantity_on_hand = quantity_on_hand + ? WHERE id = ?""",
            (amount, product_id),)
        if cur.rowcount == 0:
            raise UnknownProductError("product not found")
        conn.execute(
            """
            INSERT INTO stock_movements (product_id, delta, reason, occurred_at)
            VALUES (?, ?, 'restock', ?)
            """,
            (product_id, amount, occurred_at),)
