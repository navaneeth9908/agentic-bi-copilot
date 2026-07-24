import importlib
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
    result_map = {result.case_id: result for result in report.results}
    assert result_map["segment_revenue"].checks["sql_safe"] is True
    assert result_map["segment_revenue"].checks["expected_rows"] is True
    assert result_map["segment_revenue"].checks["answer_contains"] is True
    assert result_map["segment_revenue"].failures == ()
    assert "Enterprise" in result_map["segment_revenue"].answer
    assert "GROUP BY c.segment" in result_map["segment_revenue"].sql
