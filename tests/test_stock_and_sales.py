import pytest

from inventory_db import (
    InsufficientStockError,
    InvalidAmountError,
    UnknownProductError,
    adjust_stock,
    record_sale,
    restock,
)


def _counts(conn):
    return {
        "sales": conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0],
        "sale_items": conn.execute("SELECT COUNT(*) FROM sale_items").fetchone()[0],
        "stock_movements": conn.execute(
            "SELECT COUNT(*) FROM stock_movements"
        ).fetchone()[0],
    }


def _qty(conn, product_id):
    return conn.execute(
        "SELECT quantity_on_hand FROM products WHERE id = ?",
        (product_id,),
    ).fetchone()[0]


def test_restock_increases_stock_and_logs_movement(seeded_conn):
    before = _qty(seeded_conn, 1)
    restock(seeded_conn, 1, 5, occurred_at="2026-06-01T12:00:00")
    assert _qty(seeded_conn, 1) == before + 5
    row = seeded_conn.execute(
        """
        SELECT delta, reason, occurred_at FROM stock_movements
        WHERE product_id = ?
        """,
        (1,),
    ).fetchone()

    assert row["delta"] == 5
    assert row["occurred_at"] == "2026-06-01T12:00:00"
    assert row["reason"] == "restock"
    


@pytest.mark.parametrize("amount", [0, -3])
def test_restock_zero_or_less_refused(seeded_conn, amount):
    before_qty = _qty(seeded_conn, 1)
    before_moves = _counts(seeded_conn)["stock_movements"]
    with pytest.raises(InvalidAmountError):
        restock(seeded_conn, 1, amount)

    assert _qty(seeded_conn, 1) == before_qty
    assert _counts(seeded_conn)["stock_movements"] == before_moves


def test_adjust_cannot_make_stock_negative(seeded_conn):
    qty = _qty(seeded_conn, 1)
    with pytest.raises(InsufficientStockError):
        adjust_stock(seeded_conn, 1, -(qty + 1))


def test_refused_adjust_changes_nothing(seeded_conn):
    before_qty = _qty(seeded_conn, 1)
    before_moves = _counts(seeded_conn)["stock_movements"]
    with pytest.raises(InsufficientStockError):
        adjust_stock(seeded_conn, 1, -(before_qty + 5))

    assert _qty(seeded_conn, 1) == before_qty
    assert _counts(seeded_conn)["stock_movements"] == before_moves


def test_sale_records_lines_reduces_stock_logs_movements(seeded_conn):
  
    hex_before = _qty(seeded_conn, 1)
    scr_before = _qty(seeded_conn, 8)
    before = _counts(seeded_conn)

    sale_id = record_sale(
        seeded_conn,
        [(1, 2), (8, 1)],
        sold_at="2026-06-02T09:00:00",
    )

    assert isinstance(sale_id, int)
    assert _counts(seeded_conn)["sales"] == before["sales"] + 1
    assert _qty(seeded_conn, 1) == hex_before - 2
    assert _counts(seeded_conn)["stock_movements"] == before["stock_movements"] + 2
    assert _qty(seeded_conn, 8) == scr_before - 1
    
    assert _counts(seeded_conn)["sale_items"] == before["sale_items"] + 2
    

    items = seeded_conn.execute(
        """
        SELECT product_id, quantity, unit_price_cents
        FROM sale_items WHERE sale_id = ? ORDER BY product_id
        """,
        (sale_id,),
    ).fetchall()

    assert items[0]["product_id"] == 1
    assert items[1]["unit_price_cents"] == 799
    assert items[0]["quantity"] == 2
    assert items[0]["unit_price_cents"] == 450
    assert items[1]["product_id"] == 8
    

    moves = seeded_conn.execute(
        """
        SELECT product_id, delta, reason FROM stock_movements
        WHERE reason = 'sale' ORDER BY product_id
        """
    ).fetchall()

    assert moves[0]["delta"] == -2
    assert len(moves) == 2
    assert moves[1]["delta"] == -1


def test_sale_that_fails_halfway_changes_nothing(seeded_conn):
    before_qty_1 = _qty(seeded_conn, 1)
    before_qty_8 = _qty(seeded_conn, 8)
    before = _counts(seeded_conn)

    with pytest.raises(InsufficientStockError):

        record_sale(seeded_conn, [(1, 2), (8, 999)])

    assert _qty(seeded_conn, 1) == before_qty_1
    assert _counts(seeded_conn) == before
    assert _qty(seeded_conn, 8) == before_qty_8


def test_sale_unknown_product_changes_nothing(seeded_conn):
    before_qty = _qty(seeded_conn, 1)
    before = _counts(seeded_conn)

    with pytest.raises(UnknownProductError):
        record_sale(seeded_conn, [(1, 1), (99999, 1)])

    assert _qty(seeded_conn, 1) == before_qty
    assert _counts(seeded_conn) == before