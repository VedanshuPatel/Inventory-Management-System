PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS suppliers (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
) STRICT;

CREATE TABLE IF NOT EXISTS products (
    id                INTEGER PRIMARY KEY,
    sku               TEXT NOT NULL UNIQUE,
    name              TEXT NOT NULL,
    category          TEXT NOT NULL,
    supplier_id       INTEGER NOT NULL REFERENCES suppliers(id),
    unit_price_cents  INTEGER NOT NULL CHECK (unit_price_cents >= 0),
    quantity_on_hand  INTEGER NOT NULL CHECK (quantity_on_hand >= 0),
    reorder_level     INTEGER NOT NULL CHECK (reorder_level >= 0)
) STRICT;

CREATE TABLE IF NOT EXISTS sales (
    id      INTEGER PRIMARY KEY,
    sold_at TEXT NOT NULL
) STRICT;


CREATE TABLE IF NOT EXISTS stock_movements (
    id          INTEGER PRIMARY KEY,
    product_id  INTEGER NOT NULL REFERENCES products(id),
    delta       INTEGER NOT NULL CHECK (delta != 0),
    reason      TEXT NOT NULL CHECK (reason IN ('restock', 'adjustment', 'sale')),
    occurred_at TEXT NOT NULL
) STRICT;

CREATE TABLE IF NOT EXISTS sale_items (
    id               INTEGER PRIMARY KEY,
    sale_id          INTEGER NOT NULL REFERENCES sales(id),
    product_id       INTEGER NOT NULL REFERENCES products(id),
    quantity         INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_cents INTEGER NOT NULL CHECK (unit_price_cents >= 0),
    UNIQUE (sale_id, product_id)
) STRICT;


CREATE INDEX IF NOT EXISTS idx_products_supplier_id
    ON products(supplier_id);