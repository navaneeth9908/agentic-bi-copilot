from agentic_bi_copilot.questions import list_sample_questions


def test_sample_question_registry_exposes_supported_questions():
    questions = list_sample_questions()

    assert questions
    assert questions[0].id == "segment_revenue"
    assert questions[0].question == "Which customer segment has the highest revenue?"
    assert questions[0].category == "Revenue analytics"
    assert questions[0].supported is True
