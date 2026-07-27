"""Portfolio readiness summary for final reviewer handoff."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from agentic_bi_copilot.evaluation import run_eval_suite
from agentic_bi_copilot.questions import list_sample_questions


@dataclass(frozen=True)
class CompletionChecklistItem:
    """A completed roadmap milestone with concrete reviewer evidence."""

    day: str
    title: str
    status: str
    evidence_commands: tuple[str, ...]
    evidence_artifacts: tuple[str, ...] = ()


@dataclass(frozen=True)
class CompletionChecklist:
    """One-week project readiness evidence for portfolio reviewers."""

    readiness_status: str
    supported_question_count: int
    eval_passed: int
    eval_total: int
    quality_status: str
    delivery_surfaces: tuple[str, ...]
    completed_milestones: tuple[CompletionChecklistItem, ...]
    review_commands: tuple[str, ...]
    next_production_step: str


def get_completion_checklist() -> tuple[CompletionChecklistItem, ...]:
    """Return the completed one-week roadmap mapped to reviewer evidence."""

    return (
        CompletionChecklistItem(
            day="Day 1",
            title="Offline analytics foundation",
            status="complete",
            evidence_commands=(
                "uv run --group dev pytest tests/test_data.py tests/test_sql_agent.py -q",
                "uv run python -m agentic_bi_copilot.cli --list-questions",
            ),
            evidence_artifacts=("src/agentic_bi_copilot/data.py", "src/agentic_bi_copilot/sql_agent.py"),
        ),
        CompletionChecklistItem(
            day="Day 2",
            title="Broader NL2SQL coverage",
            status="complete",
            evidence_commands=(
                "uv run --group dev pytest tests/test_sample_questions.py tests/test_sql_agent.py -q",
                'uv run python -m agentic_bi_copilot.cli "What is revenue by region?" --limit 2',
            ),
            evidence_artifacts=("src/agentic_bi_copilot/questions.py", "evals/supported_questions.json"),
        ),
        CompletionChecklistItem(
            day="Day 3",
            title="RAG-backed metric definitions",
            status="complete",
            evidence_commands=("uv run --group dev pytest tests/test_metric_glossary.py -q",),
            evidence_artifacts=("docs/metric_glossary.md", "src/agentic_bi_copilot/metrics.py"),
        ),
        CompletionChecklistItem(
            day="Day 4",
            title="Evaluation harness",
            status="complete",
            evidence_commands=(
                "uv run --group dev pytest tests/ -q",
                "uv run python -m agentic_bi_copilot.cli --run-evals",
            ),
            evidence_artifacts=("src/agentic_bi_copilot/evaluation.py", "docs/evaluation_quality.md"),
        ),
        CompletionChecklistItem(
            day="Day 5",
            title="FastAPI contract",
            status="complete",
            evidence_commands=("uv run --group dev pytest tests/test_api.py -q",),
            evidence_artifacts=("src/agentic_bi_copilot/api.py", "docs/api.md"),
        ),
        CompletionChecklistItem(
            day="Day 6",
            title="Static demo and recruiter narrative",
            status="complete",
            evidence_commands=(
                "uv run --group dev pytest tests/test_demo.py -q",
                "uv run python -m agentic_bi_copilot.cli --render-demo docs/demo.html --db-path examples/demo_page.sqlite --limit 2",
            ),
            evidence_artifacts=("docs/demo.html", "docs/architecture.md"),
        ),
        CompletionChecklistItem(
            day="Day 7",
            title="Docker + CI packaging",
            status="complete",
            evidence_commands=(
                "docker build -t agentic-bi-copilot .",
                "docker run --rm agentic-bi-copilot",
            ),
            evidence_artifacts=("Dockerfile", ".github/workflows/ci.yml"),
        ),
    )


def build_completion_checklist(
    db_path: str | Path | None = None,
    dataset_path: str | Path | None = None,
) -> CompletionChecklist:
    """Run deterministic evals and assemble a final project handoff checklist."""

    report = run_eval_suite(db_path=db_path, dataset_path=dataset_path)
    readiness_status = "READY" if report.failed == 0 else "NEEDS ATTENTION"
    return CompletionChecklist(
        readiness_status=readiness_status,
        supported_question_count=len(list_sample_questions()),
        eval_passed=report.passed,
        eval_total=report.total,
        quality_status=report.quality_status,
        delivery_surfaces=(
            "CLI: sample-question registry, safe SQL, rows, and grounded answer text",
            "FastAPI: /health, /questions, /ask",
            "Static demo: docs/demo.html self-contained reviewer artifact",
            "Docker + GitHub Actions CI: pytest, CLI smoke, and Docker smoke checks",
        ),
        completed_milestones=get_completion_checklist(),
        review_commands=(
            "uv run --group dev pytest tests/ -q",
            "uv run python -m agentic_bi_copilot.cli --run-evals",
            "uv run python -m agentic_bi_copilot.cli --completion-checklist",
            'uv run python -m agentic_bi_copilot.cli "What is revenue by region?" --limit 2',
        ),
        next_production_step="connect a warehouse and LLM planner behind the same guardrails.",
    )


def format_completion_checklist(
    checklist: CompletionChecklist | Sequence[CompletionChecklistItem],
) -> str:
    """Format completion evidence for CLI smoke output and README docs."""

    if isinstance(checklist, CompletionChecklist):
        lines = [
            f"Portfolio completion checklist: {checklist.readiness_status}",
            f"Supported questions: {checklist.supported_question_count}",
            (
                f"Quality gates: {checklist.quality_status} "
                f"({checklist.eval_passed}/{checklist.eval_total} eval cases passing)"
            ),
            "Delivery surfaces:",
        ]
        lines.extend(f"- {surface}" for surface in checklist.delivery_surfaces)
        lines.extend(_format_milestone_lines(checklist.completed_milestones))
        lines.append("Review commands:")
        lines.extend(f"- {command}" for command in checklist.review_commands)
        lines.append(f"Next production step: {checklist.next_production_step}")
        return "\n".join(lines)

    lines = _format_milestone_lines(tuple(checklist))
    lines.append("Next production step: connect a warehouse and LLM planner behind the same guardrails.")
    return "\n".join(lines)


def _format_milestone_lines(checklist: Sequence[CompletionChecklistItem]) -> list[str]:
    lines = ["One-week completion checklist:"]
    for item in checklist:
        lines.append(f"- {item.day} - {item.title}: {item.status}")
        if item.evidence_commands:
            lines.append("  Evidence commands:")
            lines.extend(f"  - {command}" for command in item.evidence_commands)
        if item.evidence_artifacts:
            lines.append("  Evidence artifacts:")
            lines.extend(f"  - {artifact}" for artifact in item.evidence_artifacts)
    return lines
