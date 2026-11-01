import sqlite3
from contextlib import closing
from pathlib import Path

from inventory_db import (
    InventoryError,
    add_product,
    backup_db,
    connect,
    format_cents,
    get_product,
    init_db,
    record_sale,
    report_low_stock,
    report_never_sold,
    report_sales_by_product,
    report_stock_value_by_supplier,
    restock,
    search_products,
)


def _optional_cents(prompt):
    """Ask for dollars and blank means skip"""
    raw = input(prompt).strip()
    if raw == "":
        return None
    try:
        return round(float(raw) * 100)
    except ValueError:
        raise ValueError("Please enter a number: ") from None

def _print_product_row(row):
    """Print one product on a single line"""
    print(
        f"{row['sku']} | {row['name']} | {row['category']} | "
        f"{row['supplier_name']} | ${format_cents(row['unit_price_cents'])} | "
        f"qty {row['quantity_on_hand']}"
    )

def _handle_choice(conn, choice):
    """Run the action for one menu choice and Returns False to exit"""
    if choice == "0":
        print("Bye!")
        return False
        
    action = MENU_ACTIONS.get(choice)
    if action is None:
        print("Unknown option, please try again.")
        return True
    action(conn)
    return True

def _ask_yes(prompt):
    """Return True if the user answers y"""
    return input(prompt).strip().lower() == "y"

def _read_int(prompt):
    """Read an integer from the user or raise a friendly ValueError"""
    raw = input(prompt).strip()
    try:
        return int(raw)
    except ValueError:
        raise ValueError("Please enter a number: ") from None


def _read_dollars_as_cents(prompt):
    """Read a dollar amount and convert it to integer cents"""
    raw = input(prompt).strip()
    try:
        return round(float(raw) * 100)
    except ValueError:
        raise ValueError("Please enter a number: ") from None


def _friendly_integrity_error(exc):
    """sqlite3.IntegrityError menu message"""
    msg = str(exc).lower()
    if "unique" in msg:
        return "That SKU is already in use."
    if "foreign key" in msg:
        return "That supplier does not exist."
    if "check" in msg:
        return "Price and quantity cannot be negative."
    return "Could not save that change."


def _print_menu():
    """Show the main menu options"""
    print(
        """
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
"""
    )


def _search(conn):
    """Search products with print matches and optional filters"""
    text = input("Search text: ").strip()
    category = input("Category (blank to skip): ").strip() or None
    max_price = _optional_cents("Max price in dollars (blank to skip): ")
    in_stock = _ask_yes("In stock only? (y/n): ")
    low_stock = _ask_yes("Low stock only? (y/n): ")

    rows = search_products(conn,text,category=category,max_price_cents=max_price,in_stock_only=in_stock,
        low_stock_only=low_stock,)
    if not rows:
        print("No products found.")
        return
    for row in rows:
        _print_product_row(row)


def _lookup(conn):
    """Look up one product by id and print its details"""
    product_id = _read_int("Product id: ")
    row = get_product(conn, product_id)
    if row is None:
        print("Product not found.")
        return
    print(f"{row['sku']} — {row['name']} ({row['supplier_name']})")
    print(f"  category: {row['category']}")
    print(f"  price: ${format_cents(row['unit_price_cents'])}")
    print(f"  qty: {row['quantity_on_hand']} (reorder at {row['reorder_level']})")


def _add(conn):
    """Prompt for product fields and insert a new product"""
    sku = input("SKU: ").strip()
    name = input("Name: ").strip()
    category = input("Category: ").strip()
    supplier_id = _read_int("Supplier id: ")
    price_cents = _read_dollars_as_cents("Unit price (dollars): ")
    qty = _read_int("Quantity on hand: ")
    reorder = _read_int("Reorder level: ")
    new_id = add_product(
        conn, sku, name, category, supplier_id, price_cents, qty, reorder
    )
    print(f"Added product id {new_id}.")


def _restock(conn):
    """Prompt for a product id and amount, then restock"""
    product_id = _read_int("Product id: ")
    amount = _read_int("Amount to add: ")
    restock(conn, product_id, amount)
    print("Restocked.")


def _sale(conn):
    """Collect sale lines from the user and record the sale"""
    items = []
    print("Enter product id and quantity. Leave product id blank when done.")
    while True:
        raw_id = input("Product id: ").strip()
        if raw_id == "":
            break
        try:
            product_id = int(raw_id)
            qty = _read_int("Quantity: ")
        except ValueError as exc:
            print(exc)
            continue
        items.append((product_id, qty))
    if not items:
        print("No items entered.")
        return
    sale_id = record_sale(conn, items)
    print(f"Sale {sale_id} recorded.")


def _report_stock_value(conn):
    """Print stock value grouped by supplier"""
    for row in report_stock_value_by_supplier(conn):
        print(f"{row['name']}: ${format_cents(row['total_cents'])}")


def _report_low(conn):
    """Print products that are at or below reorder level"""
    rows = report_low_stock(conn)
    if not rows:
        print("No low-stock products.")
        return
    for row in rows:
        print(
            f"{row['sku']} {row['name']}: "
            f"{row['quantity_on_hand']}/{row['reorder_level']} "
            f"(short {row['units_short']})"
        )


def _report_sales(conn):
    """Print units sold and revenue for each product"""
    for row in report_sales_by_product(conn):
        print(
            f"{row['name']}: {row['units_sold']} sold, "
            f"${format_cents(row['revenue_cents'])}"
        )


def _report_never(conn):
    """Print products that have never been sold"""
    rows = report_never_sold(conn)
    if not rows:
        print("Every product has been sold at least once.")
        return
    for row in rows:
        print(f"{row['sku']} — {row['name']}")


def _backup(conn):
    """Ask for a path and write a SQLite backup file"""
    path = input("Backup file path: ").strip() or "inventory-backup.db"
    backup_db(conn, Path(path))
    print(f"Backup written to {path}.")


MENU_ACTIONS = {
    "1": _search,
    "2": _lookup,
    "3": _add,
    "4": _restock,
    "5": _sale,
    "6": _report_stock_value,
    "7": _report_low,
    "8": _report_sales,
    "9": _report_never,
    "10": _backup,
}

def main():
    """Run the menu loop for the user"""
    with closing(connect()) as conn:
        init_db(conn)
        flag = True
        while flag:
            _print_menu()
            try:
                choice = input("Choose an option: ").strip()
                flag = _handle_choice(conn, choice)
            except ValueError as exc:
                print(exc)
            except InventoryError as exc:
                print(exc)
            except sqlite3.IntegrityError as exc:
                print(_friendly_integrity_error(exc))


if __name__ == "__main__":
    main()