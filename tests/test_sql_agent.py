from pathlib import Path

from agentic_bi_copilot.data import build_demo_db
from agentic_bi_copilot.sql_agent import answer_question, generate_sql, is_safe_select


def test_generate_segment_revenue_sql_groups_by_segment():
    sql = generate_sql("Which customer segment has the highest revenue?")

    assert "customers" in sql
    assert "order_items" in sql
    assert "GROUP BY c.segment" in sql
    assert "ORDER BY revenue DESC" in sql


def test_answer_question_identifies_top_revenue_segment(tmp_path: Path):
    db_path = build_demo_db(tmp_path / "sales_mart.sqlite")

    result = answer_question(
        "Which customer segment has the highest revenue?",
        db_path=db_path,
        limit=3,
    )

    assert result.rows[0]["segment"] == "Enterprise"
    assert result.rows[0]["revenue"] == 5000.0
    assert "Enterprise" in result.answer
    assert "5,000.00" in result.answer


def test_is_safe_select_rejects_mutating_sql():
    assert is_safe_select("SELECT * FROM customers")
    assert not is_safe_select("DROP TABLE customers")
    assert not is_safe_select("SELECT * FROM customers; DELETE FROM customers")
