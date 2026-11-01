# Inventory Management System

Small hardware-store inventory application. Stock, suppliers, and sales live in SQLite. You can search products, restock, record sales, and run a few reports from a terminal menu.

## What it does

- Five tables: suppliers, products, sales, sale_items, stock_movements
- Operations: Add / look up / search products (with filters) / Restock / record sales
- The 4 Reports provided: stock value by supplier, low stock, sales by product, never sold
- There's also Backup option via SQLite's backup API
- Runs locally or in Docker (`INVENTORY_DB` for the database path)

Money is stored as **integer cents** and shown with two decimal places.

## Requirements

- Python 3.12+
- SQLite 3.37+ (STRICT tables)
- Docker

```bash
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
```

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate 
pip install -r requirements.txt
```

## SQLite  Version
```bash
sqlite3 --version
3.54.0 2026-04-09
```

## Configuration

`INVENTORY_DB`: Path to the SQLite database file. If not set, the app uses `inventory.db` next to the code.
In Docker the image uses `INVENTORY_DB=/data/inventory.db`.

```bash
export INVENTORY_DB=./inventory.db
```

## Docker
```bash
docker build -t inventory:1.0.0 .
[+] Building 8.0s (10/10) FINISHED                                                                                                    docker:desktop-linux
 => [internal] load build definition from Dockerfile                                                                                              0.0s
 => => transferring dockerfile: 236B                                                                                                              0.0s
 => [internal] load metadata for docker.io/library/python:3.12.10-slim-bookworm                                                                   1.0s
 => [internal] load .dockerignore                                                                                                                 0.0s
 => => transferring context: 161B                                                                                                                 0.0s
 => [1/5] FROM docker.io/library/python:3.12.
 => [internal] load build context                                                                                                                 0.0s
 => => transferring context: 138.83kB                                                                                                             0.0s
 => [2/5] WORKDIR /app                                                                                                                            0.2s
 => [3/5] COPY requirements.txt .                                                                                                                 0.0s
 => [4/5] RUN pip install --no-cache-dir -r requirements.txt                                                                                      3.2s
 => [5/5] COPY . .                                                                                                                                0.0s

 => => naming to docker.io/library/inventory:1.0.0                                                                                                0.0s
 => => unpacking to docker.io/library/inventory:1.0.0                                                                                             0.8s

View build details: docker-desktop://dashboard/build/desktop-linux/desktop-linux/
```

## Database and Seed Data
```bash
python seed_db.py
suppliers: 4
products: 12
sales: 5
sale_items: 12
stock_movements: 0
```

## Tests
```bash
ruff check .
pytest -q
All checks passed!
.......................................                                                                                                         [100%]
39 passed in 0.03s
```

## Database Backup
```bash
python3 main.py

1. Search products
2. Look up a product
3. Add a product
4. Restock
5. Record a sale
6. Report: stock value by supplier
7. Report: low stock
8. Report: sales by product
9. Report: never sold
10. Back up database
0. Exit

Choose an option: 10
Backup file path: inventory-backup-2026-11-01.db
Backup written to inventory-backup-2026-11-01.db.

1. Search products
2. Look up a product
3. Add a product
4. Restock
5. Record a sale
6. Report: stock value by supplier
7. Report: low stock
8. Report: sales by product
9. Report: never sold
10. Back up database
0. Exit

Choose an option: 0
Bye!


Inventory-Management-System % sqlite3 inventory.db "SELECT 'suppliers', COUNT(*) FROM suppliers UNION ALL SELECT 'products', COUNT(*) FROM products UNION ALL SELECT 'sales', COUNT(*) FROM sales UNION ALL SELECT 'sale_items', COUNT(*) FROM sale_items UNION ALL SELECT 'stock_movements', COUNT(*) FROM stock_movements;"
╭─────────────────┬──────────╮
│   'suppliers'   │ COUNT(*) │
╞═════════════════╪══════════╡
│ suppliers       │        4 │
│ products        │       12 │
│ sales           │        5 │
│ sale_items      │       12 │
│ stock_movements │        0 │
╰─────────────────┴──────────╯
 Inventory-Management-System % sqlite3 inventory-backup-2026-11-01.db "PRAGMA integrity_check;"
╭─────────────────╮
│ integrity_check │
╞═════════════════╡
│ ok              │
╰─────────────────╯
 Inventory-Management-System % sqlite3 inventory-backup-2026-11-01.db "SELECT 'suppliers', COUNT(*) FROM suppliers UNION ALL SELECT 'products', COUNT(*) FROM products UNION ALL SELECT 'sales', COUNT(*) FROM sales UNION ALL SELECT 'sale_items', COUNT(*) FROM sale_items UNION ALL SELECT 'stock_movements', COUNT(*) FROM stock_movements;"
╭─────────────────┬──────────╮
│   'suppliers'   │ COUNT(*) │
╞═════════════════╪══════════╡
│ suppliers       │        4 │
│ products        │       12 │
│ sales           │        5 │
│ sale_items      │       12 │
│ stock_movements │        0 │
╰─────────────────┴──────────╯
```

### Restore

Stop the app, then replace the live database with the backup:

```bash
cp inventory-backup-2026-11-01.db inventory.db
```

## Persistence check
```bash
docker run --rm \
  -e INVENTORY_DB=/data/inventory.db \
  -v inventory-data:/data \
  inventory:1.0.0 \
  python seed_db.py
suppliers: 4
products: 12
sales: 5
sale_items: 12
stock_movements: 0

docker run -it --rm \
  -e INVENTORY_DB=/data/inventory.db \
  -v inventory-data:/data \
  inventory:1.0.0

1. Search products
2. Look up a product
3. Add a product
4. Restock
5. Record a sale
6. Report: stock value by supplier
7. Report: low stock
8. Report: sales by product
9. Report: never sold
10. Back up database
0. Exit

Choose an option: 2
Product id: 1
HEX-M8 — Hex Bolt M8x40 (box) (Cedar Valley Metals)
  category: Fasteners
  price: $4.50
  qty: 50 (reorder at 15)

1. Search products
2. Look up a product
3. Add a product
4. Restock
5. Record a sale
6. Report: stock value by supplier
7. Report: low stock
8. Report: sales by product
9. Report: never sold
10. Back up database
0. Exit

Choose an option: 0
Bye!
```

## Reports Output
```bash
python3 seed_db.py

suppliers: 4
products: 12
sales: 5
sale_items: 12
stock_movements: 0


Inventory-Management-System % python3 main.py


1. Search products
2. Look up a product
3. Add a product
4. Restock
5. Record a sale
6. Report: stock value by supplier
7. Report: low stock
8. Report: sales by product
9. Report: never sold
10. Back up database
0. Exit

Choose an option: 6
Ironbark Tools: $414.63
Harbor Coatings: $349.67
Ridgeway Supply: $332.59
Cedar Valley Metals: $300.73

1. Search products
2. Look up a product
3. Add a product
4. Restock
5. Record a sale
6. Report: stock value by supplier
7. Report: low stock
8. Report: sales by product
9. Report: never sold
10. Back up database
0. Exit

Choose an option: 7
ENL-1L Clear Enamel 1L: 4/6 (short 2)
WAS-M8 Flat Washer M8 (box): 5/12 (short 7)
EAR-N25 Foam Ear Plugs N25: 2/10 (short 8)

1. Search products
2. Look up a product
3. Add a product
4. Restock
5. Record a sale
6. Report: stock value by supplier
7. Report: low stock
8. Report: sales by product
9. Report: never sold
10. Back up database
0. Exit

Choose an option: 8
Metal Primer 1L: 3 sold, $47.97
Ball Peen Hammer 16oz: 2 sold, $29.98
Phillips Screwdriver #2: 3 sold, $23.97
Clear Enamel 1L: 1 sold, $18.99
Hex Bolt M8x40 (box): 3 sold, $13.50
Combination Pliers 8in: 1 sold, $12.99
Clear Safety Goggles: 2 sold, $10.98
Work Gloves Large: 1 sold, $9.99
Hex Nut M8 (box): 2 sold, $5.98

1. Search products
2. Look up a product
3. Add a product
4. Restock
5. Record a sale
6. Report: stock value by supplier
7. Report: low stock
8. Report: sales by product
9. Report: never sold
10. Back up database
0. Exit

Choose an option: 9
WAS-M8 — Flat Washer M8 (box)
EAR-N25 — Foam Ear Plugs N25
BRU-038 — Utility Brush 38mm

1. Search products
2. Look up a product
3. Add a product
4. Restock
5. Record a sale
6. Report: stock value by supplier
7. Report: low stock
8. Report: sales by product
9. Report: never sold
10. Back up database
0. Exit

Choose an option: 0
Bye!
```

## Failed Sale
```bash
python3 seed_db.py

suppliers: 4
products: 12
sales: 5
sale_items: 12
stock_movements: 0

Inventory-Management-System % python3 main.py   


1. Search products
2. Look up a product
3. Add a product
4. Restock
5. Record a sale
6. Report: stock value by supplier
7. Report: low stock
8. Report: sales by product
9. Report: never sold
10. Back up database
0. Exit

Choose an option: 2
Product id: 1
HEX-M8 — Hex Bolt M8x40 (box) (Cedar Valley Metals)
  category: Fasteners
  price: $4.50
  qty: 50 (reorder at 15)

1. Search products
2. Look up a product
3. Add a product
4. Restock
5. Record a sale
6. Report: stock value by supplier
7. Report: low stock
8. Report: sales by product
9. Report: never sold
10. Back up database
0. Exit

Choose an option: 2
Product id: 8
SCR-PH2 — Phillips Screwdriver #2 (Ironbark Tools)
  category: Hand Tools
  price: $7.99
  qty: 18 (reorder at 6)

1. Search products
2. Look up a product
3. Add a product
4. Restock
5. Record a sale
6. Report: stock value by supplier
7. Report: low stock
8. Report: sales by product
9. Report: never sold
10. Back up database
0. Exit

Choose an option: 5
Enter product id and quantity. Leave product id blank when done.
Product id: 1
Quantity: 2
Product id: 8
Quantity: 898
Product id: 
not enough stock for sale

1. Search products
2. Look up a product
3. Add a product
4. Restock
5. Record a sale
6. Report: stock value by supplier
7. Report: low stock
8. Report: sales by product
9. Report: never sold
10. Back up database
0. Exit

Choose an option: 2
Product id: 1
HEX-M8 — Hex Bolt M8x40 (box) (Cedar Valley Metals)
  category: Fasteners
  price: $4.50
  qty: 50 (reorder at 15)

1. Search products
2. Look up a product
3. Add a product
4. Restock
5. Record a sale
6. Report: stock value by supplier
7. Report: low stock
8. Report: sales by product
9. Report: never sold
10. Back up database
0. Exit

Choose an option: 2
Product id: 8
SCR-PH2 — Phillips Screwdriver #2 (Ironbark Tools)
  category: Hand Tools
  price: $7.99
  qty: 18 (reorder at 6)

1. Search products
2. Look up a product
3. Add a product
4. Restock
5. Record a sale
6. Report: stock value by supplier
7. Report: low stock
8. Report: sales by product
9. Report: never sold
10. Back up database
0. Exit

Choose an option: 0
Bye!
```