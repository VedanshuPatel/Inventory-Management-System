from contextlib import closing

from inventory_db import backup_db, connect


def _row_counts(conn):
    tables = ("suppliers", "products", "sales", "sale_items", "stock_movements")
    return {
        name: conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        for name in tables
    }

def test_backup_passes_integrity_check_and_row_counts(seeded_conn, tmp_path):
    dest = tmp_path / "backup.db"
    backup_db(seeded_conn, dest)

    with closing(connect(dest)) as backup_conn:
        assert backup_conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert _row_counts(backup_conn) == _row_counts(seeded_conn)