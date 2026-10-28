### Why each table exists

| Table | Why it exists|
|---|---|
| `suppliers` | The products in the store have suppliers. This table stores inforamtion about those suppliers |
| `products` | The product details in the store such as a SKU, a name, a category, a supplier, a unit price, a quantity in stock, and a reorder level |
| `sales` | it records when the sale happened |
| `sale_items` | It records details of a sale such as product, quantity, and the price at the time of the sale so that changes in price do not rewrite the history |
| `stock_movements` | Changes in stock, the reason and the time it happened at |


### Constraints

**suppliers**
- `id` INTEGER PRIMARY KEY
- `name` TEXT NOT NULL UNIQUE

**products**
- `id` INTEGER PRIMARY KEY
- `sku` TEXT NOT NULL UNIQUE
- `name` TEXT NOT NULL
- `category` TEXT NOT NULL
- `supplier_id` INTEGER NOT NULL REFERENCES `suppliers(id)`
- `unit_price_cents` INTEGER NOT NULL CHECK (`unit_price_cents >= 0`)
- `quantity_on_hand` INTEGER NOT NULL CHECK (`quantity_on_hand >= 0`)
- `reorder_level` INTEGER NOT NULL CHECK (`reorder_level >= 0`)

**sales**
- `id` INTEGER PRIMARY KEY
- `sold_at` TEXT NOT NULL

**sale_items**
- `id` INTEGER PRIMARY KEY
- `sale_id` INTEGER NOT NULL REFERENCES `sales(id)`
- `product_id` INTEGER NOT NULL REFERENCES `products(id)`
- `quantity` INTEGER NOT NULL CHECK (`quantity > 0`)
- `unit_price_cents` INTEGER NOT NULL CHECK (`unit_price_cents >= 0`)
- UNIQUE (`sale_id`, `product_id`)

**stock_movements**
- `id` INTEGER PRIMARY KEY
- `product_id` INTEGER NOT NULL REFERENCES `products(id)`
- `delta` INTEGER NOT NULL CHECK (`delta != 0`)
- `reason` TEXT NOT NULL CHECK (`reason IN ('restock', 'adjustment', 'sale')`)
- `occurred_at` TEXT NOT NULL

### Relationship between tables

- `products.supplier_id` → `suppliers.id` — one supplier, many products, each product has one supplier
- `sale_items.sale_id` → `sales.id` — one sale, many line items
- `sale_items.product_id` → `products.id` — one product, many sale lines, each line is one product
- `stock_movements.product_id` → `products.id` — one product, many stock changes, each movement is one product
- Suppliers are not linked to sales or movements — only through products
- Stock movements are not linked to sales — only through products

### Public Functions
| Name | Inputs | Returns |
|---|---|---|
| `connect(db_path=None)` | Optional path | `sqlite3.Connection` with foreign keys on and rows by column name |
| `init_db(conn)` | connection | `None` |
| `add_product(conn, sku, name, category, supplier_id, unit_price_cents, quantity_on_hand, reorder_level)` | product fields | new product `id` (`int`) |
| `get_product(conn, product_id)` | product id | mapping including `supplier_name` from a join, or `None` |
| `update_price(conn, product_id, unit_price_cents)` | product id, new price in cents | `True` if a row changed, `False` if missing |
| `delete_product(conn, product_id)` | product id | `None` or raises an error if the product has sales history |
| `search_products(conn, text, category=None, max_price_cents=None, in_stock_only=False, low_stock_only=False)` | search text and optional filters | list of product rows sorted by name |
| `report_stock_value_by_supplier(conn)` | connection | rows of supplier name and total stock value in cents, highest first |
| `report_low_stock(conn)` | connection | products at or below reorder level, with units short |
| `report_sales_by_product(conn)` | connection | products with units sold and revenue in cents, highest revenue first |
| `report_never_sold(conn)` | connection | products that appear in no sale |
| `restock(conn, product_id, amount, occurred_at=None)` | product id, positive amount, optional timestamp | `None` |
| `adjust_stock(conn, product_id, delta, occurred_at=None)` | product id, signed delta, optional timestamp | `None` |
| `record_sale(conn, items, sold_at=None)` | list of `(product_id, quantity)` pairs, optional timestamp | new `sale_id` |
| `backup_db(conn, dest_path)` | connection, destination path | `None` |

### Transaction steps
Multi-step changes use one `with conn:` block. On exception, SQLite rolls back everything in that block. Helpers inside a transaction never commit on their own.

#### Restock
1. If `amount` is zero or less, refuse. Nothing is written.
2. Inside one transaction, increase the product’s stock by `amount`.
3. If the product does not exist, raise an error (transaction undoes nothing extra — no prior writes).
4. Insert a `stock_movements` row with positive `delta` and reason `restock`.
5. If any step fails, the stock update and movement are both undone.

#### Adjust
1. Inside one transaction: read the product’s current stock.
2. If the product does not exist, raise an error. Nothing is written.
3. If stock plus `delta` would be negative, refuse. Nothing is written.
4. If `delta` is zero, refuse. Nothing is written.
5. Update stock and insert a movement with reason `adjustment`.
6. If any step fails after writes begin, stock and movement changes are both undone. A refused adjustment leaves stock and `stock_movements` unchanged.

#### Record a sale
1. Before any write, refuse an empty list, refuse if the same product appears twice. Nothing is written.
2. Inside one transaction, insert a `sales` row.
3. For each `(product_id, quantity)`:
   - Load the product. Unknown product → fail.
   - Invalid or non-positive quantity → fail.
   - Quantity greater than stock → fail.
   - Insert a `sale_items` row at the product’s current price.
   - Reduce the product’s stock.
   - Insert a `stock_movements` row with negative `delta` and reason `sale`.
4. If any line fails, the whole sale is undone, no sale row, no sale items, no movements, and no stock changes.

#### Release plan
Build in six pull requests. Each branch has its own PR, a passing CI run before merge, then the branch is deleted.
| # | Branch | What it delivers |
|---|---|---|
| 1 | `feature/database-and-seed` | `schema.sql`, `seed_db.py`, `connect` / `init_db`, CI |
| 2 | `feature/products-and-search` | Product add/get/update/delete, search, and tests |
| 3 | `feature/reports` | Four report functions and tests |
| 4 | `feature/stock-and-sales` | Restock, adjust, record sale, and failed-sale tests |
| 5 | `feature/menu-and-container` | Terminal menu, Docker, backup, docker-build CI job, README → tag **v1.0.0** / image `inventory:1.0.0` |
| 6 | `feature/low-stock-banner` | Low-stock banner on menu start, CHANGELOG → tag **v1.1.0** / image `inventory:1.1.0` |
