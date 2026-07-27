from agentic_bi_copilot.cli import main


def test_cli_lists_supported_sample_questions(capsys):
    exit_code = main(["--list-questions"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Supported sample questions" in captured.out
    assert "segment_revenue" in captured.out
    assert "Which customer segment has the highest revenue?" in captured.out
    assert "region_revenue" in captured.out
    assert "What is revenue by region?" in captured.out
    assert "repeat_customer_rate" in captured.out
    assert "What is the repeat customer rate?" in captured.out
    assert "product_category_mix" in captured.out
    assert "What is product category mix by revenue?" in captured.out


def test_cli_runs_supported_question_evaluations(capsys, tmp_path):
    exit_code = main(["--run-evals", "--db-path", str(tmp_path / "sales_mart.sqlite")])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Evaluation report: 4/4 passed" in captured.out
    assert "segment_revenue: PASS" in captured.out
    assert "product_category_mix: PASS" in captured.out


def test_cli_renders_static_demo_html_file(capsys, tmp_path):
    output_path = tmp_path / "demo.html"

    exit_code = main(
        [
            "--render-demo",
            str(output_path),
            "--db-path",
            str(tmp_path / "sales_mart.sqlite"),
        ]
    )

    captured = capsys.readouterr()
    html = output_path.read_text(encoding="utf-8")

    assert exit_code == 0
    assert f"Wrote demo page: {output_path}" in captured.out
    assert "Agentic BI Copilot Demo" in html
    assert "What is revenue by region?" in html
    assert "GROUP BY c.region" in html


def test_cli_prints_portfolio_completion_checklist(capsys, tmp_path):
    exit_code = main(
        [
            "--completion-checklist",
            "--db-path",
            str(tmp_path / "sales_mart.sqlite"),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Portfolio completion checklist: READY" in captured.out
    assert "Supported questions: 4" in captured.out
    assert "Quality gates: PASS (4/4 eval cases passing)" in captured.out
    assert "FastAPI: /health, /questions, /ask" in captured.out
    assert "Docker + GitHub Actions CI" in captured.out
    assert "Review commands:" in captured.out
    assert "uv run python -m agentic_bi_copilot.cli --run-evals" in captured.out
