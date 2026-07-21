"""Registry of supported demo questions for the BI copilot."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SampleQuestion:
    """A discoverable business question supported by the offline copilot."""

    id: str
    question: str
    category: str
    supported: bool = True


SAMPLE_QUESTIONS: tuple[SampleQuestion, ...] = (
    SampleQuestion(
        id="segment_revenue",
        question="Which customer segment has the highest revenue?",
        category="Revenue analytics",
    ),
    SampleQuestion(
        id="region_revenue",
        question="What is revenue by region?",
        category="Revenue analytics",
    ),
)


def list_sample_questions() -> tuple[SampleQuestion, ...]:
    """Return supported sample questions in stable CLI display order."""

    return SAMPLE_QUESTIONS
