"""FastAPI surface for the deterministic Agentic BI Copilot demo."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from agentic_bi_copilot.data import build_demo_db
from agentic_bi_copilot.questions import list_sample_questions
from agentic_bi_copilot.sql_agent import answer_question

DEFAULT_API_DB_PATH = Path("examples") / "sales_mart.sqlite"
ASK_REQUEST_EXAMPLE = {"question": "What is revenue by region?", "limit": 2}
REVENUE_SOURCE_SNIPPET = (
    "- Definition: Gross sales recognized from completed orders before refunds or discounts.\n"
    "- Formula: SUM(order_items.quantity * order_items.unit_price)\n"
    "- Grain: order item"
)
ASK_RESPONSE_EXAMPLE = {
    "question": "What is revenue by region?",
    "sql": (
        "SELECT c.region, ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue "
        "FROM customers AS c "
        "JOIN orders AS o ON o.customer_id = c.customer_id "
        "JOIN order_items AS oi ON oi.order_id = o.order_id "
        "GROUP BY c.region ORDER BY revenue DESC"
    ),
    "rows": [
        {"region": "North", "revenue": 4200.0},
        {"region": "West", "revenue": 3000.0},
    ],
    "answer": (
        "North is the highest-revenue region with $4,200.00 in the demo sales mart. "
        "Metric definition: Revenue [docs/metric_glossary.md#revenue]"
    ),
    "metric_context": [
        {
            "term": "Revenue",
            "source": "docs/metric_glossary.md#revenue",
            "source_snippet": REVENUE_SOURCE_SNIPPET,
        }
    ],
}
UNSUPPORTED_QUESTION_MESSAGE = (
    "Unsupported question. Try one of the published sample questions."
)


class AskQuestionRequest(BaseModel):
    """Request schema for asking the deterministic BI copilot a question."""

    model_config = ConfigDict(json_schema_extra={"examples": [ASK_REQUEST_EXAMPLE]})

    question: str = Field(..., min_length=1)
    limit: int = Field(default=5, ge=1, le=100)


class MetricContextResponse(BaseModel):
    """Metric glossary card attached to a grounded API answer."""

    model_config = ConfigDict(
        json_schema_extra={"examples": ASK_RESPONSE_EXAMPLE["metric_context"]}
    )

    term: str
    source: str
    source_snippet: str


class AskQuestionResponse(BaseModel):
    """Response schema for a safe SQL-backed BI answer."""

    model_config = ConfigDict(json_schema_extra={"examples": [ASK_RESPONSE_EXAMPLE]})

    question: str
    sql: str
    rows: list[dict[str, Any]]
    answer: str
    metric_context: list[MetricContextResponse]


def _supported_question_texts() -> list[str]:
    return [sample.question for sample in list_sample_questions()]


def _unsupported_question_detail() -> dict[str, object]:
    return {
        "error": "unsupported_question",
        "message": UNSUPPORTED_QUESTION_MESSAGE,
        "supported_questions": _supported_question_texts(),
    }


def create_app(db_path: str | Path | None = None) -> FastAPI:
    """Create the FastAPI app for local API smoke tests and demos."""

    app = FastAPI(title="Agentic BI Copilot", version="0.1.0")
    app.state.db_path = Path(db_path) if db_path is not None else DEFAULT_API_DB_PATH

    @app.get("/health")
    def health() -> dict[str, object]:
        return {
            "status": "ok",
            "service": "agentic-bi-copilot",
            "supported_questions": len(list_sample_questions()),
        }

    @app.get("/questions")
    def questions() -> dict[str, object]:
        samples = list_sample_questions()
        return {
            "count": len(samples),
            "questions": [
                {
                    "id": sample.id,
                    "question": sample.question,
                    "category": sample.category,
                    "supported": sample.supported,
                }
                for sample in samples
            ],
        }

    @app.post(
        "/ask",
        response_model=AskQuestionResponse,
        summary="Ask a supported BI question",
        description=(
            "Run the deterministic answer path with safe read-only SQL against "
            "the local demo sales mart, returning generated SQL, rows, an "
            "executive answer, and cited metric-glossary context."
        ),
        responses={
            400: {
                "description": "Unsupported BI question",
                "content": {
                    "application/json": {
                        "examples": {
                            "unsupported_question": {
                                "summary": "Unsupported BI question",
                                "value": {"detail": _unsupported_question_detail()},
                            }
                        }
                    }
                },
            }
        },
    )
    def ask_question(request: AskQuestionRequest) -> AskQuestionResponse:
        resolved_db_path = _ensure_demo_db(app.state.db_path)
        try:
            result = answer_question(
                request.question,
                db_path=resolved_db_path,
                limit=request.limit,
            )
        except ValueError as exc:
            if str(exc).startswith("Unsupported question"):
                raise HTTPException(
                    status_code=400,
                    detail=_unsupported_question_detail(),
                ) from exc
            raise

        return AskQuestionResponse(
            question=result.question,
            sql=result.sql,
            rows=result.rows,
            answer=result.answer,
            metric_context=[
                MetricContextResponse(
                    term=definition.term,
                    source=definition.source,
                    source_snippet=definition.source_snippet,
                )
                for definition in result.metric_context
            ],
        )

    return app


def _ensure_demo_db(db_path: Path) -> Path:
    if not db_path.exists():
        build_demo_db(db_path)
    return db_path


app = create_app()
