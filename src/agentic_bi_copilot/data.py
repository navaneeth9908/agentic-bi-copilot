"""Deterministic demo analytics mart for local portfolio runs."""

from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA_SQL = """
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL,
    segment TEXT NOT NULL,
    region TEXT NOT NULL
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date TEXT NOT NULL
);

CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id),
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL
);
"""

CUSTOMERS = [
    (1, "Atlas Labs", "Enterprise", "North"),
    (2, "Bright Retail", "SMB", "West"),
    (3, "Cedar Health", "Mid-Market", "East"),
    (4, "Delta Finance", "Enterprise", "West"),
    (5, "Evergreen Supply", "SMB", "South"),
    (6, "Futura Travel", "Mid-Market", "North"),
]

PRODUCTS = [
    (101, "Analytics Suite", "Software"),
    (102, "Data Pipeline Pack", "Data Engineering"),
    (103, "Forecasting Add-On", "AI"),
    (104, "Support Credits", "Services"),
]

ORDERS = [
    (1001, 1, "2026-01-05"),
    (1002, 2, "2026-01-09"),
    (1003, 3, "2026-01-16"),
    (1004, 4, "2026-02-02"),
    (1005, 5, "2026-02-14"),
    (1006, 6, "2026-03-01"),
    (1007, 1, "2026-03-18"),
    (1008, 4, "2026-03-26"),
]

ORDER_ITEMS = [
    (1, 1001, 101, 2, 1000.0),
    (2, 1002, 102, 1, 750.0),
    (3, 1002, 104, 2, 125.0),
    (4, 1003, 103, 1, 600.0),
    (5, 1003, 104, 2, 100.0),
    (6, 1004, 101, 1, 1000.0),
    (7, 1005, 102, 2, 750.0),
    (8, 1006, 103, 2, 600.0),
    (9, 1007, 104, 4, 250.0),
    (10, 1008, 102, 2, 500.0),
]


def build_demo_db(db_path: str | Path) -> Path:
    """Create a fresh deterministic SQLite sales mart and return its path."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()

    with sqlite3.connect(path) as conn:
        conn.executescript(SCHEMA_SQL)
        conn.executemany(
            "INSERT INTO customers (customer_id, customer_name, segment, region) VALUES (?, ?, ?, ?)",
            CUSTOMERS,
        )
        conn.executemany(
            "INSERT INTO products (product_id, product_name, category) VALUES (?, ?, ?)",
            PRODUCTS,
        )
        conn.executemany(
            "INSERT INTO orders (order_id, customer_id, order_date) VALUES (?, ?, ?)",
            ORDERS,
        )
        conn.executemany(
            """
            INSERT INTO order_items (order_item_id, order_id, product_id, quantity, unit_price)
            VALUES (?, ?, ?, ?, ?)
            """,
            ORDER_ITEMS,
        )
        conn.commit()

    return path
