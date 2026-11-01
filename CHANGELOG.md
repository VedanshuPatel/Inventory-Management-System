# Changelog

## 1.1.0
- Prints a low stock count banner with product names when the menu starts

## 1.0.0
- SQLite inventory application with 5 tables (suppliers, products, sales, sale items, stock movements)
- Terminal menu: search, look up, add products, restock, record sales, four reports, and Database backup
- Money stored as integer cents 
- Sales and stock changes run in one transaction each
- Docker image (`inventory:1.0.0`) with `INVENTORY_DB` for a mounted volume
- pytest coverage for schema, products, search, reports, stock, sales, and backup
- pytest, ruff and docker-build CI jobs