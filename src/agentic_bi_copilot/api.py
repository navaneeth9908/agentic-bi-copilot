"""FastAPI surface for the deterministic Agentic BI Copilot demo."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from agentic_bi_copilot.data import build_demo_db
from agentic_bi_copilot.questions import list_sample_questions
from agentic_bi_copilot.sql_agent import answer_question

DEFAULT_API_DB_PATH = Path("examples") / "sales_mart.sqlite"


class AskQuestionRequest(BaseModel):
    """Request schema for asking the deterministic BI copilot a question."""

    question: str = Field(..., min_length=1)
    limit: int = Field(default=5, ge=1, le=100)


class MetricContextResponse(BaseModel):
    """Metric glossary card attached to a grounded API answer."""

    term: str
    source: str
    source_snippet: str


class AskQuestionResponse(BaseModel):
    """Response schema for a safe SQL-backed BI answer."""

    question: str
    sql: str
    rows: list[dict[str, Any]]
    answer: str
    metric_context: list[MetricContextResponse]


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

    @app.post("/ask", response_model=AskQuestionResponse)
    def ask_question(request: AskQuestionRequest) -> AskQuestionResponse:
        resolved_db_path = _ensure_demo_db(app.state.db_path)
        result = answer_question(
            request.question,
            db_path=resolved_db_path,
            limit=request.limit,
        )
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
