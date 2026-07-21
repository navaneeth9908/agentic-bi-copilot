from pathlib import Path
import sqlite3

from agentic_bi_copilot.data import build_demo_db


def test_build_demo_db_creates_sales_mart(tmp_path: Path):
    db_path = tmp_path / "sales_mart.sqlite"

    result_path = build_demo_db(db_path)

    assert result_path == db_path
    assert db_path.exists()

    with sqlite3.connect(db_path) as conn:
        customers = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
        orders = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        items = conn.execute("SELECT COUNT(*) FROM order_items").fetchone()[0]

    assert customers == 6
    assert orders == 8
    assert items == 10
