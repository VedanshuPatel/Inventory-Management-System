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
[+] Building 8.0s (10/10) FINISHED                                                                                                    

 => => naming to docker.io/library/inventory:1.0.0
 => => unpacking to docker.io/library/inventory:1.0.0

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
SCR-PH2 — Phillips Screwdriver
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
SCR-PH2 — Phillips Screwdriver
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

## Release 2 and Rollback
```bash
docker build -t inventory:1.1.0 .

[+] Building 0.6s (10/10) FINISHED  

 => => naming to docker.io/library/inventory:1.1.0
 => => unpacking to docker.io/library/inventory:1.1.0   

docker run --rm \
  -e INVENTORY_DB=/data/inventory.db \
  -v inventory-data:/data \
  inventory:1.1.0 \
  python seed_db.py

suppliers: 4
products: 12
sales: 5
sale_items: 12
stock_movements: 0

Inventory-Management-System % docker run -it --rm \
  -e INVENTORY_DB=/data/inventory.db \
  -v inventory-data:/data \
  inventory:1.1.0
Low stock: 3 product(s) need your attention
            ENL-1L — Clear Enamel 1L
            WAS-M8 — Flat Washer M8 (box)
            EAR-N25 — Foam Ear Plugs N25

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

Inventory-Management-System % docker run -it --rm \
  -e INVENTORY_DB=/data/inventory.db \
  -v inventory-data:/data \
  inventory:1.1.0
Low stock: 3 product(s) need your attention
  ENL-1L — Clear Enamel 1L
  WAS-M8 — Flat Washer M8 (box)
  EAR-N25 — Foam Ear Plugs N25

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

Choose an option: 4
Product id: 1
Amount to add: 24
Restocked.

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
  qty: 74 (reorder at 15)

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

Inventory-Management-System % 
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
  qty: 74 (reorder at 15)

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

## Version Table
| Version | Git tag | Docker tag | 
|---|---|---|
| 1.0.0 | `v1.0.0` | `inventory:1.0.0` |
| 1.1.0 | `v1.1.0` | `inventory:1.1.0` |


## How to run
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 seed_db.py
python3 main.py
```
## How to run the tests
```bash
ruff check .
pytest -q
```

## How to deploy with Docker

Build the image:

```bash
docker build -t inventory:1.0.0 .
docker build -t inventory:1.1.0 .

docker run --rm \
  -e INVENTORY_DB=/data/inventory.db \
  -v inventory-data:/data \
  inventory:1.0.0 \
  python seed_db.py

docker run -it --rm \
  -e INVENTORY_DB=/data/inventory.db \
  -v inventory-data:/data \
  inventory:1.0.0
```

## How to back up and restore
Run the menu and choose option 10.
```bash
python3 main.py
# Choose an option: 10
# Backup file path: inventory-backup-2026-11-01.db

cp inventory-backup-2026-11-01.db inventory.db
```
## How to rollback
Rollback means running the older **image** on the **same volume**. The database stays, only the application code changes (the changes in 1.1.0 goes away).

```bash
docker build -t inventory:1.1.0 .
docker run -it --rm \
  -e INVENTORY_DB=/data/inventory.db \
  -v inventory-data:/data \
  inventory:1.1.0


docker run -it --rm \
  -e INVENTORY_DB=/data/inventory.db \
  -v inventory-data:/data \
  inventory:1.0.0
```

## Self-review

If I rebuilt this from scratch, I would expose adjust-stock on the menu. The function already exists and is tested, but the terminal only offers restock. That means a damage write off or a recount has no path in the UI even though the database rules for adjustments are already there. Putting adjust next to restock would make the menu match what the library can do.

I would also spend more time on the sale flow before writing code. Getting “all lines save or nothing does” right took more trial and error than I expected, and a clearer step list up front would have helped.

One thing I'd want a reviewer to double-check is the search filters in `search_products`. Combining category, max price, in stock, and low stock with the LIKE text felt easy to get subtly wrong. The tests cover the cases I thought of, but I'd still like someone else to skim that SQL before I explain it live.