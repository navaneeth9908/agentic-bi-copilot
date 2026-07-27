from agentic_bi_copilot.portfolio import (
    format_completion_checklist,
    get_completion_checklist,
)


def test_completion_checklist_maps_weekly_milestones_to_reviewer_evidence():
    checklist = get_completion_checklist()

    assert [item.day for item in checklist] == [
        "Day 1",
        "Day 2",
        "Day 3",
        "Day 4",
        "Day 5",
        "Day 6",
        "Day 7",
    ]
    assert all(item.status == "complete" for item in checklist)
    assert any(
        "uv run --group dev pytest tests/ -q" in item.evidence_commands
        for item in checklist
    )
    assert any(
        "uv run python -m agentic_bi_copilot.cli --run-evals"
        in item.evidence_commands
        for item in checklist
    )

    rendered = format_completion_checklist(checklist)

    assert "One-week completion checklist" in rendered
    assert "Day 4 - Evaluation harness: complete" in rendered
    assert "FastAPI" in rendered
    assert "Docker + CI packaging" in rendered
    assert "Next production step: connect a warehouse and LLM planner behind the same guardrails." in rendered
