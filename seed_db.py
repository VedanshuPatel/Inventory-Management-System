from contextlib import closing
from inventory_db import connect, init_db

SUPPLIERS = [
    (1, "Ridgeway Supply"),
    (2, "Cedar Valley Metals"),
    (3, "Harbor Coatings"),
    (4, "Ironbark Tools"),
]

PRODUCTS = [
    ("HEX-M8", "Hex Bolt M8x40 (box)", "Fasteners", 2, 450, 50, 15),
    ("NUT-M8", "Hex Nut M8 (box)", "Fasteners", 2, 299, 22, 10),
    ("WAS-M8", "Flat Washer M8 (box)", "Fasteners", 2, 199, 5, 12),
    ("BRU-038", "Utility Brush 38mm", "Coatings", 3, 649, 20, 8),
    ("ENL-1L", "Clear Enamel 1L", "Coatings", 3, 1899, 4, 6),  
    ("PRI-1L", "Metal Primer 1L", "Coatings", 3, 1599, 9, 5),
    ("HAM-16", "Ball Peen Hammer 16oz", "Hand Tools", 4, 1499, 12, 4),
    ("SCR-PH2", "Phillips Screwdriver #2", "Hand Tools", 4, 799, 18, 6),
    ("PLY-8IN", "Combination Pliers 8in", "Hand Tools", 4, 1299, 7, 3),
    ("GLO-L", "Work Gloves Large", "Safety", 1, 999, 25, 10),
    ("GOG-CLR", "Clear Safety Goggles", "Safety", 1, 549, 14, 8),
    ("EAR-N25", "Foam Ear Plugs N25", "Safety", 1, 299, 2, 10),  
]

SALES = [
    (1, "2026-01-12T09:30:00"),
    (2, "2026-02-18T13:05:00"),
    (3, "2026-03-07T11:40:00"),
    (4, "2026-04-19T15:20:00"),
    (5, "2026-05-03T10:10:00"),
]

SALE_ITEMS = [
    (1, 7, 1, 1499),
    (1, 8, 2, 799),
    (2, 5, 1, 1899),
    (2, 6, 1, 1599),
    (2, 10, 1, 999),
    (3, 9, 1, 1299),
    (3, 1, 3, 450),
    (4, 11, 2, 549),
    (4, 2, 2, 299),
    (4, 8, 1, 799),
    (5, 7, 1, 1499),
    (5, 6, 2, 1599),
]


def load_seed(conn):
    """Insert sample rows using placeholders and executemany."""
    conn.executemany(
        "INSERT INTO suppliers (id, name) VALUES (?, ?)",
        SUPPLIERS,
    )
    conn.executemany(
        """
        INSERT INTO products (
            sku, name, category, supplier_id,
            unit_price_cents, quantity_on_hand, reorder_level
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        PRODUCTS,
    )
    conn.executemany(
        "INSERT INTO sales (id, sold_at) VALUES (?, ?)",
        SALES,
    )
    conn.executemany(
        """
        INSERT INTO sale_items (
            sale_id, product_id, quantity, unit_price_cents
        ) VALUES (?, ?, ?, ?)
        """,
        SALE_ITEMS,
    )


def print_row_counts(conn):
    for table in ("suppliers", "products", "sales", "sale_items", "stock_movements"):
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table}: {count}")


def main():
    with closing(connect()) as conn:
        init_db(conn)
        with conn:
            load_seed(conn)
        print_row_counts(conn)


if __name__ == "__main__":
    main()