import importlib
import json
from pathlib import Path


def test_evaluation_runner_scores_supported_question_dataset(tmp_path: Path):
    evaluation = importlib.import_module("agentic_bi_copilot.evaluation")

    cases = evaluation.load_eval_cases()
    assert {case.id for case in cases} == {
        "segment_revenue",
        "region_revenue",
        "repeat_customer_rate",
        "product_category_mix",
    }

    report = evaluation.run_eval_suite(db_path=tmp_path / "sales_mart.sqlite")

    assert report.total == len(cases)
    assert report.passed == report.total
    assert report.pass_rate_pct == 100.0
    assert report.quality_status == "PASS"
    formatted = evaluation.format_eval_report(report)
    assert "Quality summary: PASS (100.0% pass rate, 0 failing cases)" in formatted
    result_map = {result.case_id: result for result in report.results}
    assert result_map["segment_revenue"].checks["sql_safe"] is True
    assert result_map["segment_revenue"].checks["expected_rows"] is True
    assert result_map["segment_revenue"].checks["answer_contains"] is True
    assert result_map["segment_revenue"].failures == ()
    assert "Enterprise" in result_map["segment_revenue"].answer
    assert "GROUP BY c.segment" in result_map["segment_revenue"].sql


def test_evaluation_runner_reports_unsupported_questions_as_failures(tmp_path: Path):
    evaluation = importlib.import_module("agentic_bi_copilot.evaluation")
    dataset_path = tmp_path / "unsupported_question_eval.json"
    dataset_path.write_text(
        json.dumps(
            {
                "cases": [
                    {
                        "id": "unsupported_inventory_aging",
                        "question": "Show inventory aging by warehouse",
                        "limit": 3,
                        "expected_sql_fragments": ["warehouse"],
                        "expected_rows": [{"warehouse": "North DC", "aging_days": 42}],
                        "expected_answer_fragments": ["North DC"],
                        "expected_metric_terms": ["Inventory aging"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    report = evaluation.run_eval_suite(
        db_path=tmp_path / "sales_mart.sqlite",
        dataset_path=dataset_path,
    )

    assert report.total == 1
    assert report.passed == 0
    assert report.failed == 1
    assert report.pass_rate_pct == 0.0
    assert report.quality_status == "FAIL"
    formatted = evaluation.format_eval_report(report)
    assert "Quality summary: FAIL (0.0% pass rate, 1 failing case: unsupported_inventory_aging)" in formatted
    result = report.results[0]
    assert result.case_id == "unsupported_inventory_aging"
    assert result.checks == {"execution": False}
    assert result.sql == ""
    assert result.rows == ()
    assert result.answer == ""
    assert "execution failed" in result.failures[0]
    assert "Unsupported question" in result.failures[0]


def test_format_eval_report_includes_quality_summary(tmp_path: Path):
    evaluation = importlib.import_module("agentic_bi_copilot.evaluation")

    report = evaluation.run_eval_suite(db_path=tmp_path / "sales_mart.sqlite")
    formatted = evaluation.format_eval_report(report)

    assert "Quality summary: PASS (100.0% pass rate, 0 failing cases)" in formatted
