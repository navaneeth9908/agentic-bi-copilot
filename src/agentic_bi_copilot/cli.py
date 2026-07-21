"""Command-line smoke path for the Agentic BI Copilot."""

from __future__ import annotations

import argparse
from pathlib import Path

from agentic_bi_copilot.data import build_demo_db
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ask the local BI copilot a business question.")
    parser.add_argument("question", help="Natural-language business question")
    parser.add_argument(
        "--db-path",
        type=Path,
        default=DEFAULT_DB_PATH,
        help="SQLite database path. If missing, a deterministic demo database is created.",
    )
    parser.add_argument("--limit", type=int, default=5, help="Maximum result rows to display")
    args = parser.parse_args(argv)

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
