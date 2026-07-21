"""Safe deterministic NL2SQL path for the first BI copilot milestone."""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MUTATING_SQL_PATTERN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|replace|truncate|attach|detach|pragma|vacuum)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class AnalysisResult:
    question: str
    sql: str
    rows: list[dict[str, Any]]
    answer: str


def generate_sql(question: str) -> str:
    """Generate a constrained SQL query for supported business questions."""
    normalized = question.lower()
    if "segment" in normalized and "revenue" in normalized:
        return """
SELECT
    c.segment,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
FROM customers AS c
JOIN orders AS o ON o.customer_id = c.customer_id
JOIN order_items AS oi ON oi.order_id = o.order_id
GROUP BY c.segment
ORDER BY revenue DESC
""".strip()
    if "region" in normalized and "revenue" in normalized:
        return """
SELECT
    c.region,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
FROM customers AS c
JOIN orders AS o ON o.customer_id = c.customer_id
JOIN order_items AS oi ON oi.order_id = o.order_id
GROUP BY c.region
ORDER BY revenue DESC
""".strip()

    raise ValueError(
        "Unsupported question. Try: 'Which customer segment has the highest revenue?' "
        "or 'What is revenue by region?'"
    )


def is_safe_select(sql: str) -> bool:
    """Return True only for a single read-only SELECT statement."""
    stripped = sql.strip()
    if not stripped.lower().startswith("select"):
        return False
    if ";" in stripped:
        return False
    if MUTATING_SQL_PATTERN.search(stripped):
        return False
    return True


def _execute_select(db_path: str | Path, sql: str, limit: int) -> list[dict[str, Any]]:
    if not is_safe_select(sql):
        raise ValueError("Refusing to execute non-read-only SQL")

    safe_limit = max(1, min(int(limit), 100))
    limited_sql = f"{sql}\nLIMIT {safe_limit}"

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(limited_sql).fetchall()

    return [dict(row) for row in rows]


def answer_question(question: str, db_path: str | Path, limit: int = 5) -> AnalysisResult:
    """Generate SQL, execute it, and compose a concise executive answer."""
    sql = generate_sql(question)
    rows = _execute_select(db_path, sql, limit=limit)
    if not rows:
        answer = "No matching revenue records were found in the demo sales mart."
    else:
        top = rows[0]
        if "segment" in top:
            dimension_label = "customer segment"
            dimension_value = top["segment"]
        else:
            dimension_label = "region"
            dimension_value = top["region"]
        answer = (
            f"{dimension_value} is the highest-revenue {dimension_label} "
            f"with ${top['revenue']:,.2f} in the demo sales mart."
        )

    return AnalysisResult(question=question, sql=sql, rows=rows, answer=answer)
