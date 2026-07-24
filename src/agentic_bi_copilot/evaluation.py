"""Deterministic evaluation runner for supported BI copilot questions."""

from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_bi_copilot.data import build_demo_db
from agentic_bi_copilot.sql_agent import answer_question, is_safe_select

DEFAULT_EVAL_DATASET_PATH = Path(__file__).resolve().parents[2] / "evals" / "supported_questions.json"


@dataclass(frozen=True)
class EvaluationCase:
    """Expected behavior for one supported BI copilot question."""

    id: str
    question: str
    limit: int
    expected_sql_fragments: tuple[str, ...]
    expected_rows: tuple[dict[str, Any], ...]
    expected_answer_fragments: tuple[str, ...]
    expected_metric_terms: tuple[str, ...]


@dataclass(frozen=True)
class EvaluationCaseResult:
    """Pass/fail details for one evaluation case."""

    case_id: str
    question: str
    checks: dict[str, bool]
    failures: tuple[str, ...]
    sql: str
    rows: tuple[dict[str, Any], ...]
    answer: str

    @property
    def passed(self) -> bool:
        return not self.failures


@dataclass(frozen=True)
class EvaluationReport:
    """Aggregate evaluation report for deterministic offline checks."""

    dataset_path: Path
    results: tuple[EvaluationCaseResult, ...]

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> int:
        return sum(1 for result in self.results if result.passed)

    @property
    def failed(self) -> int:
        return self.total - self.passed

    @property
    def pass_rate_pct(self) -> float:
        if self.total == 0:
            return 0.0
        return round(100.0 * self.passed / self.total, 1)

    @property
    def quality_status(self) -> str:
        return "PASS" if self.failed == 0 else "FAIL"

    @property
    def failing_case_ids(self) -> tuple[str, ...]:
        return tuple(result.case_id for result in self.results if not result.passed)


def load_eval_cases(dataset_path: str | Path | None = None) -> tuple[EvaluationCase, ...]:
    """Load deterministic evaluation cases from the repository dataset."""

    path = Path(dataset_path) if dataset_path is not None else DEFAULT_EVAL_DATASET_PATH
    raw_cases = json.loads(path.read_text(encoding="utf-8"))["cases"]
    return tuple(
        EvaluationCase(
            id=raw_case["id"],
            question=raw_case["question"],
            limit=int(raw_case.get("limit", 5)),
            expected_sql_fragments=tuple(raw_case.get("expected_sql_fragments", ())),
            expected_rows=tuple(raw_case.get("expected_rows", ())),
            expected_answer_fragments=tuple(raw_case.get("expected_answer_fragments", ())),
            expected_metric_terms=tuple(raw_case.get("expected_metric_terms", ())),
        )
        for raw_case in raw_cases
    )


def run_eval_suite(
    db_path: str | Path | None = None,
    dataset_path: str | Path | None = None,
) -> EvaluationReport:
    """Build the demo mart, run supported questions, and score deterministic checks."""

    if db_path is None:
        with tempfile.TemporaryDirectory(prefix="agentic-bi-evals-") as tmp_dir:
            return run_eval_suite(Path(tmp_dir) / "sales_mart.sqlite", dataset_path=dataset_path)

    built_db_path = build_demo_db(db_path)
    cases = load_eval_cases(dataset_path)
    results = tuple(_evaluate_case(case, built_db_path) for case in cases)
    resolved_dataset_path = Path(dataset_path) if dataset_path is not None else DEFAULT_EVAL_DATASET_PATH
    return EvaluationReport(dataset_path=resolved_dataset_path, results=results)


def format_eval_report(report: EvaluationReport) -> str:
    """Format evaluation results for CLI smoke runs and portfolio logs."""

    lines = [
        f"Evaluation report: {report.passed}/{report.total} passed",
        (
            f"Quality summary: {report.quality_status} "
            f"({report.pass_rate_pct:.1f}% pass rate, {_format_failing_case_summary(report)})"
        ),
    ]
    for result in report.results:
        status = "PASS" if result.passed else "FAIL"
        lines.append(f"- {result.case_id}: {status}")
        for failure in result.failures:
            lines.append(f"  - {failure}")
    return "\n".join(lines)


def _format_failing_case_summary(report: EvaluationReport) -> str:
    failing_case_ids = report.failing_case_ids
    if not failing_case_ids:
        return "0 failing cases"
    if len(failing_case_ids) == 1:
        return f"1 failing case: {failing_case_ids[0]}"
    return f"{len(failing_case_ids)} failing cases: {', '.join(failing_case_ids)}"


def _evaluate_case(case: EvaluationCase, db_path: Path) -> EvaluationCaseResult:
    try:
        result = answer_question(case.question, db_path=db_path, limit=case.limit)
    except Exception as exc:
        return EvaluationCaseResult(
            case_id=case.id,
            question=case.question,
            checks={"execution": False},
            failures=(f"execution failed: {exc}",),
            sql="",
            rows=(),
            answer="",
        )

    rows = tuple(result.rows)
    metric_terms = tuple(definition.term for definition in result.metric_context)
    checks = {
        "execution": True,
        "sql_safe": is_safe_select(result.sql),
        "sql_contains": all(fragment in result.sql for fragment in case.expected_sql_fragments),
        "expected_rows": _rows_start_with(rows, case.expected_rows),
        "answer_contains": all(fragment in result.answer for fragment in case.expected_answer_fragments),
        "metric_terms": all(term in metric_terms for term in case.expected_metric_terms),
    }
    failures = tuple(_failure_messages(case, checks, metric_terms, rows, result.sql, result.answer))
    return EvaluationCaseResult(
        case_id=case.id,
        question=case.question,
        checks=checks,
        failures=failures,
        sql=result.sql,
        rows=rows,
        answer=result.answer,
    )


def _rows_start_with(
    actual_rows: tuple[dict[str, Any], ...],
    expected_rows: tuple[dict[str, Any], ...],
) -> bool:
    return actual_rows[: len(expected_rows)] == expected_rows


def _failure_messages(
    case: EvaluationCase,
    checks: dict[str, bool],
    metric_terms: tuple[str, ...],
    rows: tuple[dict[str, Any], ...],
    sql: str,
    answer: str,
) -> list[str]:
    failures: list[str] = []
    if not checks["sql_safe"]:
        failures.append("generated SQL did not pass the read-only safety gate")
    if not checks["sql_contains"]:
        missing = [fragment for fragment in case.expected_sql_fragments if fragment not in sql]
        failures.append(f"SQL missing expected fragments: {missing}")
    if not checks["expected_rows"]:
        failures.append(f"rows did not match expected prefix: {rows}")
    if not checks["answer_contains"]:
        missing = [fragment for fragment in case.expected_answer_fragments if fragment not in answer]
        failures.append(f"answer missing expected fragments: {missing}")
    if not checks["metric_terms"]:
        missing = [term for term in case.expected_metric_terms if term not in metric_terms]
        failures.append(f"metric context missing expected terms: {missing}")
    return failures
