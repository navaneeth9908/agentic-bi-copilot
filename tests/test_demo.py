from pathlib import Path


def test_render_demo_html_includes_sample_questions_sql_rows_and_citations(tmp_path: Path):
    try:
        from agentic_bi_copilot.demo import render_demo_html
    except ModuleNotFoundError as exc:
        raise AssertionError("agentic_bi_copilot.demo should expose render_demo_html") from exc

    db_path = tmp_path / "sales_mart.sqlite"

    html = render_demo_html(
        db_path=db_path,
        question="What is revenue by region?",
        limit=2,
    )

    assert db_path.exists()
    assert "<title>Agentic BI Copilot Demo</title>" in html
    assert "What is revenue by region?" in html
    assert "product_category_mix" in html
    assert "GROUP BY c.region" in html
    assert "North" in html
    assert "4200.0" in html
    assert "Metric definition: Revenue" in html
    assert "docs/metric_glossary.md#revenue" in html
    assert "uv run python -m agentic_bi_copilot.cli" in html
