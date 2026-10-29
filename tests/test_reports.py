from inventory_db import (
    report_low_stock,
    report_never_sold,
    report_sales_by_product,
    report_stock_value_by_supplier,
)


def test_report_never_sold(seeded_conn):
    rows = report_never_sold(seeded_conn)
    skus = [r["sku"] for r in rows]
    
    assert skus == ["WAS-M8", "EAR-N25", "BRU-038"]

def test_report_low_stock(seeded_conn):
    rows = report_low_stock(seeded_conn)

    assert len(rows) == 3
    by_sku = {r["sku"]: r for r in rows}
    assert by_sku["WAS-M8"]["units_short"] == 7
    assert by_sku["EAR-N25"]["units_short"] == 8
    assert by_sku["ENL-1L"]["units_short"] == 2
    


def test_report_sales_by_product(seeded_conn):
    rows = report_sales_by_product(seeded_conn)

    assert rows[0]["sku"] == "PRI-1L"
    assert rows[0]["units_sold"] == 3
    assert rows[0]["revenue_cents"] == 4797
    assert rows[-1]["sku"] == "NUT-M8"
    assert rows[-1]["revenue_cents"] == 598
    assert rows[1]["revenue_cents"] == 2998
    assert len(rows) == 9
    assert rows[1]["sku"] == "HAM-16"


def test_report_stock_value_by_supplier(seeded_conn):
    rows = report_stock_value_by_supplier(seeded_conn)

    assert len(rows) == 4
    assert rows[2]["name"] == "Ridgeway Supply"
    assert rows[0]["total_cents"] == 41463
    assert rows[1]["name"] == "Harbor Coatings"
    assert rows[1]["total_cents"] == 34967
    assert rows[2]["total_cents"] == 33259
    assert rows[3]["name"] == "Cedar Valley Metals"
    assert rows[3]["total_cents"] == 30073