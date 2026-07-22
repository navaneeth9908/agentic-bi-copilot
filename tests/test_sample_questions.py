from agentic_bi_copilot.questions import list_sample_questions


def test_sample_question_registry_exposes_supported_questions():
    questions = list_sample_questions()

    assert questions
    assert questions[0].id == "segment_revenue"
    assert questions[0].question == "Which customer segment has the highest revenue?"
    assert questions[0].category == "Revenue analytics"
    assert questions[0].supported is True


def test_sample_question_registry_includes_region_revenue_question():
    questions = {sample.id: sample for sample in list_sample_questions()}

    assert questions["region_revenue"].question == "What is revenue by region?"
    assert questions["region_revenue"].category == "Revenue analytics"
    assert questions["region_revenue"].supported is True


def test_sample_question_registry_includes_repeat_customer_rate_question():
    questions = {sample.id: sample for sample in list_sample_questions()}

    assert questions["repeat_customer_rate"].question == "What is the repeat customer rate?"
    assert questions["repeat_customer_rate"].category == "Retention analytics"
    assert questions["repeat_customer_rate"].supported is True


def test_sample_question_registry_includes_product_category_mix_question():
    questions = {sample.id: sample for sample in list_sample_questions()}

    assert questions["product_category_mix"].question == "What is product category mix by revenue?"
    assert questions["product_category_mix"].category == "Product analytics"
    assert questions["product_category_mix"].supported is True
