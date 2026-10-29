
import pytest

from inventory_db import add_product, search_products


def test_search_filter_category(seeded_conn):
    rows = search_products(seeded_conn, "", category="Safety")
    assert rows
    assert all(row["category"] == "Safety" for row in rows)
    names = [row["name"] for row in rows]
    assert names == sorted(names)

def test_search_filters_combine(seeded_conn):
    rows = search_products(seeded_conn, "paint", category="Coatings",max_price_cents=2000,in_stock_only=True,low_stock_only=True,)
    assert len(rows) == 1
    assert rows[0]["sku"] == "ENL-1L"

def _insert_supplier(conn, name="Search Supplier"):
    cur = conn.execute("INSERT INTO suppliers (name) VALUES (?)", (name,))
    return cur.lastrowid

def test_search_filter_max_price(seeded_conn):
    rows = search_products(seeded_conn, "", max_price_cents=300)
    assert rows
    assert all(row["unit_price_cents"] <= 300 for row in rows)

def test_search_sql_injection_text_is_harmless(seeded_conn):
    rows = search_products(seeded_conn, "'; DROP TABLE products; --")
    assert rows == []
    tables = seeded_conn.execute(
        """
        SELECT name FROM sqlite_master
        WHERE type = 'table' AND name = ?
        """,
        ("products",),
    ).fetchone()
    assert tables is not None
    assert seeded_conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 12

def test_search_filter_low_stock_only(seeded_conn):
    rows = search_products(seeded_conn, "", low_stock_only=True)
    skus = {row["sku"] for row in rows}
    assert "WAS-M8" in skus
    assert "ENL-1L" in skus
    assert "EAR-N25" in skus
    assert all(
        row["quantity_on_hand"] <= row["reorder_level"] for row in rows
    )

@pytest.mark.parametrize(
    ("text", "expected_sku"),
    [
        ("ball peen", "HAM-16"),       
        ("hex-m8", "HEX-M8"),          
        ("cedar valley", "HEX-M8"), 
    ],
)
def test_search_matches_name_sku_supplier_case_insensitive(
    seeded_conn, text, expected_sku
):
    rows = search_products(seeded_conn, text)
    skus = [row["sku"] for row in rows]
    assert expected_sku in skus

def test_search_filter_in_stock_only(conn):
    supplier_id = _insert_supplier(conn)
    add_product(conn,sku="ZERO-1",name="Out Of Stock Item",category="Tools",supplier_id=supplier_id,unit_price_cents=100,quantity_on_hand=0,reorder_level=1,)
    add_product(conn,sku="STOCK-1",name="In Stock Item",category="Tools",supplier_id=supplier_id,unit_price_cents=100,quantity_on_hand=3,reorder_level=1,)
    rows = search_products(conn, "Stock Item", in_stock_only=True)
    skus = [row["sku"] for row in rows]
    assert "STOCK-1" in skus
    assert "ZERO-1" not in skus