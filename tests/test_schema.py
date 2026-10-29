from inventory_db import init_db


def test_supplier_index_exists(conn):
    row = conn.execute(
        """
        SELECT name FROM sqlite_master
        WHERE type = 'index' AND name = ?
        """,
        ("idx_products_supplier_id",),
    ).fetchone()

    assert row is not None

def test_foreign_keys_are_on(conn):
    enabled = conn.execute("PRAGMA foreign_keys").fetchone()[0]

    assert enabled == 1

def test_seed_has_at_least_two_never_sold_products(seeded_conn):
    rows = seeded_conn.execute(
        """
        SELECT sku FROM products p
        WHERE NOT EXISTS (
            SELECT 1 FROM sale_items si WHERE si.product_id = p.id
        )
        ORDER BY sku
        """
    ).fetchall()
    skus = [row["sku"] for row in rows]

    assert len(skus) >= 2
    assert "BRU-038" in skus
    assert "EAR-N25" in skus

def test_schema_is_idempotent(seeded_conn):
    init_db(seeded_conn)

    assert seeded_conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 12
    assert seeded_conn.execute("SELECT COUNT(*) FROM sale_items").fetchone()[0] == 12
    assert seeded_conn.execute("SELECT COUNT(*) FROM stock_movements").fetchone()[0] == 0


def test_seed_has_at_least_three_categories(seeded_conn):
    count = seeded_conn.execute(
        "SELECT COUNT(DISTINCT category) FROM products"
    ).fetchone()[0]

    assert count >= 3

def test_schema_creates_five_tables(conn):
    rows = conn.execute(
        """
        SELECT name FROM sqlite_master
        WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    ).fetchall()
    names = [row["name"] for row in rows]

    assert names == [
        "products",
        "sale_items",
        "sales",
        "stock_movements",
        "suppliers",
    ]

def test_seed_has_at_least_two_low_stock_products(seeded_conn):
    rows = seeded_conn.execute(
        """
        SELECT sku FROM products
        WHERE quantity_on_hand <= reorder_level
        ORDER BY sku
        """
    ).fetchall()
    skus = [row["sku"] for row in rows]
    
    assert len(skus) >= 2
    assert "EAR-N25" in skus
    assert "ENL-1L" in skus
    assert "WAS-M8" in skus

def test_seed_row_counts(seeded_conn):
    assert seeded_conn.execute("SELECT COUNT(*) FROM suppliers").fetchone()[0] == 4
    assert seeded_conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 12
    assert seeded_conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0] == 5
    assert seeded_conn.execute("SELECT COUNT(*) FROM sale_items").fetchone()[0] == 12
    assert seeded_conn.execute("SELECT COUNT(*) FROM stock_movements").fetchone()[0] == 0