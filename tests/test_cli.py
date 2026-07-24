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
