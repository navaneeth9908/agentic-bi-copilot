"""Safe deterministic NL2SQL path for the first BI copilot milestone."""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_bi_copilot.metrics import MetricDefinition, retrieve_metric_definitions

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
    metric_context: tuple[MetricDefinition, ...] = ()


def generate_sql(question: str) -> str:
    """Generate a constrained SQL query for supported business questions."""
    normalized = question.lower()
    if "category" in normalized and "revenue" in normalized and (
        "product" in normalized or "mix" in normalized
    ):
        return """
SELECT
    p.category,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue,
    SUM(oi.quantity) AS units_sold,
    ROUND(
        100.0 * SUM(oi.quantity * oi.unit_price) / revenue_totals.total_revenue,
        2
    ) AS revenue_share_pct
FROM order_items AS oi
JOIN products AS p ON p.product_id = oi.product_id
CROSS JOIN (
    SELECT SUM(quantity * unit_price) AS total_revenue
    FROM order_items
) AS revenue_totals
GROUP BY p.category, revenue_totals.total_revenue
ORDER BY revenue DESC, p.category
""".strip()
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
    if "repeat" in normalized and "customer" in normalized:
        return """
SELECT
    COUNT(*) AS total_customers,
    SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND(
        100.0 * SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS repeat_customer_rate
FROM (
    SELECT
        c.customer_id,
        COUNT(o.order_id) AS order_count
    FROM customers AS c
    LEFT JOIN orders AS o ON o.customer_id = c.customer_id
    GROUP BY c.customer_id
) AS customer_order_counts
""".strip()

    raise ValueError(
        "Unsupported question. Try: 'Which customer segment has the highest revenue?', "
        "'What is revenue by region?', 'What is the repeat customer rate?', or "
        "'What is product category mix by revenue?'"
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


def _format_metric_context(metric_context: tuple[MetricDefinition, ...]) -> str:
    citations = []
    for definition in metric_context:
        citations.append(
            f"Metric definition: {definition.term} [{definition.source}]\n"
            "Source snippet:\n"
            f"{definition.source_snippet}"
        )
    return "\n\n".join(citations)


def answer_question(question: str, db_path: str | Path, limit: int = 5) -> AnalysisResult:
    """Generate SQL, execute it, and compose a concise executive answer."""
    sql = generate_sql(question)
    rows = _execute_select(db_path, sql, limit=limit)
    metric_context = retrieve_metric_definitions(question, limit=2)
    if not rows:
        answer = "No matching revenue records were found in the demo sales mart."
    else:
        top = rows[0]
        if "repeat_customer_rate" in top:
            total_customers = int(top["total_customers"])
            repeat_customers = int(top["repeat_customers"])
            repeat_rate = float(top["repeat_customer_rate"])
            answer = (
                f"{repeat_customers} of {total_customers} customers are repeat customers, "
                f"a {repeat_rate:.2f}% repeat customer rate in the demo sales mart."
            )
        elif "revenue_share_pct" in top:
            answer = (
                f"{top['category']} leads the product/category mix with "
                f"${top['revenue']:,.2f}, {top['revenue_share_pct']:.2f}% of revenue, "
                f"and {int(top['units_sold'])} units sold in the demo sales mart."
            )
        else:
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

    if metric_context:
        answer = f"{answer} {_format_metric_context(metric_context)}"

    return AnalysisResult(
        question=question,
        sql=sql,
        rows=rows,
        answer=answer,
        metric_context=metric_context,
    )
