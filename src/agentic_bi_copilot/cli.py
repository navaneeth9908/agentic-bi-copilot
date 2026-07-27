"""Command-line smoke path for the Agentic BI Copilot."""

from __future__ import annotations

import argparse
from pathlib import Path

from agentic_bi_copilot.data import build_demo_db
from agentic_bi_copilot.demo import DEFAULT_DEMO_QUESTION, write_demo_html
from agentic_bi_copilot.evaluation import format_eval_report, run_eval_suite
from agentic_bi_copilot.portfolio import build_completion_checklist, format_completion_checklist
from agentic_bi_copilot.questions import list_sample_questions
from agentic_bi_copilot.sql_agent import answer_question

DEFAULT_DB_PATH = Path("examples") / "sales_mart.sqlite"


def _format_rows(rows: list[dict[str, object]]) -> str:
    if not rows:
        return "(no rows)"
    headers = list(rows[0].keys())
    lines = [" | ".join(headers), " | ".join("---" for _ in headers)]
    for row in rows:
        lines.append(" | ".join(str(row[header]) for header in headers))
    return "\n".join(lines)


def _format_sample_questions() -> str:
    lines = ["Supported sample questions:"]
    for sample in list_sample_questions():
        lines.append(f"- {sample.id} [{sample.category}]: {sample.question}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ask the local BI copilot a business question.")
    parser.add_argument("question", nargs="?", help="Natural-language business question")
    parser.add_argument(
        "--db-path",
        type=Path,
        default=DEFAULT_DB_PATH,
        help="SQLite database path. If missing, a deterministic demo database is created.",
    )
    parser.add_argument("--limit", type=int, default=5, help="Maximum result rows to display")
    parser.add_argument(
        "--list-questions",
        action="store_true",
        help="List supported sample questions and exit",
    )
    parser.add_argument(
        "--run-evals",
        action="store_true",
        help="Run deterministic supported-question evaluation checks and exit",
    )
    parser.add_argument(
        "--render-demo",
        dest="render_demo",
        type=Path,
        help="Write a self-contained static HTML demo page and exit",
    )
    parser.add_argument(
        "--completion-checklist",
        action="store_true",
        help="Run evals and print the one-week portfolio readiness checklist",
    )
    args = parser.parse_args(argv)

    if args.list_questions:
        print(_format_sample_questions())
        return 0

    if args.run_evals:
        report = run_eval_suite(args.db_path)
        print(format_eval_report(report))
        return 0 if report.failed == 0 else 1

    if args.completion_checklist:
        checklist = build_completion_checklist(args.db_path)
        print(format_completion_checklist(checklist))
        return 0 if checklist.quality_status == "PASS" else 1

    if args.render_demo:
        output_path = write_demo_html(
            args.render_demo,
            db_path=args.db_path,
            question=args.question or DEFAULT_DEMO_QUESTION,
            limit=args.limit,
        )
        print(f"Wrote demo page: {output_path}")
        return 0

    if not args.question:
        parser.error("the following arguments are required: question")

    if not args.db_path.exists():
        build_demo_db(args.db_path)

    result = answer_question(args.question, db_path=args.db_path, limit=args.limit)
    print(f"Question: {result.question}")
    print("\nSQL:")
    print(result.sql)
    print("\nRows:")
    print(_format_rows(result.rows))
    print("\nAnswer:")
    print(result.answer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
