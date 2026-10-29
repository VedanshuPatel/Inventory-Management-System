

import sqlite3

import pytest

from inventory_db import (
    ProductHasSalesError,
    add_product,
    delete_product,
    get_product,
    update_price,
)


def test_add_product_returns_id(conn):
    supplier_id = _insert_supplier(conn)
    product_id = add_product(
        conn,
        sku="TST-001",
        name="Test Product",
        category="Tools",
        supplier_id=supplier_id,
        unit_price_cents=1000,
        quantity_on_hand=5,
        reorder_level=2,
    )

    assert isinstance(product_id, int)
    row = get_product(conn, product_id)
    assert row["sku"] == "TST-001"
    assert row["supplier_name"] == "Test Supplier"


def test_update_price_changes_value(seeded_conn):
    assert update_price(seeded_conn, 1, 999) is True
    row = get_product(seeded_conn, 1)
    assert row["unit_price_cents"] == 999

def test_cannot_delete_sold_product(seeded_conn):

    with pytest.raises(ProductHasSalesError):
        delete_product(seeded_conn, 1)
    assert get_product(seeded_conn, 1) is not None


def test_add_product_unknown_supplier_refused(conn):
    with pytest.raises(sqlite3.IntegrityError):
        add_product(
            conn,
            sku="BAD-SUP",
            name="Orphan",
            category="Tools",
            supplier_id=99999,
            unit_price_cents=100,
            quantity_on_hand=1,
            reorder_level=0,
        )


@pytest.mark.parametrize(
    ("unit_price_cents", "quantity_on_hand"),
    [
        (-1, 5),
        (100, -1),
    ],
)


def _insert_supplier(conn, name="Test Supplier"):
    cur = conn.execute("INSERT INTO suppliers (name) VALUES (?)", (name,))
    return cur.lastrowid


def test_add_product_duplicate_sku_refused(conn):
    supplier_id = _insert_supplier(conn)
    add_product(
        conn,
        sku="DUP-001",
        name="First",
        category="Tools",
        supplier_id=supplier_id,
        unit_price_cents=100,
        quantity_on_hand=1,
        reorder_level=0,
    )
    with pytest.raises(sqlite3.IntegrityError):
        add_product(
            conn,
            sku="DUP-001",
            name="Second",
            category="Tools",
            supplier_id=supplier_id,
            unit_price_cents=200,
            quantity_on_hand=1,
            reorder_level=0,
        )

def test_add_product_negative_values_refused(
    conn, unit_price_cents, quantity_on_hand
):
    supplier_id = _insert_supplier(conn)
    with pytest.raises(sqlite3.IntegrityError):
        add_product(
            conn,
            sku="NEG-001",
            name="Negative",
            category="Tools",
            supplier_id=supplier_id,
            unit_price_cents=unit_price_cents,
            quantity_on_hand=quantity_on_hand,
            reorder_level=0,
        )



def test_update_price_missing_returns_false(conn):
    assert update_price(conn, 99999, 500) is False



def test_can_delete_never_sold_product(seeded_conn):

    delete_product(seeded_conn, 4)
    assert get_product(seeded_conn, 4) is None