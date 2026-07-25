def _create_test_client(tmp_path):
    try:
        from agentic_bi_copilot.api import create_app
    except ModuleNotFoundError as exc:
        raise AssertionError("agentic_bi_copilot.api should expose create_app") from exc

    from fastapi.testclient import TestClient

    app = create_app(db_path=tmp_path / "api_sales_mart.sqlite")
    return TestClient(app)


def test_health_endpoint_reports_ready_service(tmp_path):
    client = _create_test_client(tmp_path)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "agentic-bi-copilot",
        "supported_questions": 4,
    }


def test_questions_endpoint_lists_supported_samples(tmp_path):
    client = _create_test_client(tmp_path)

    response = client.get("/questions")

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 4
    assert payload["questions"][0] == {
        "id": "segment_revenue",
        "question": "Which customer segment has the highest revenue?",
        "category": "Revenue analytics",
        "supported": True,
    }
    assert payload["questions"][-1]["id"] == "product_category_mix"


def test_ask_endpoint_builds_demo_db_returns_grounded_answer(tmp_path):
    from agentic_bi_copilot.api import create_app
    from fastapi.testclient import TestClient

    db_path = tmp_path / "api_sales_mart.sqlite"
    client = TestClient(create_app(db_path=db_path))

    response = client.post(
        "/ask",
        json={"question": "What is revenue by region?", "limit": 2},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["question"] == "What is revenue by region?"
    assert "GROUP BY c.region" in payload["sql"]
    assert payload["rows"] == [
        {"region": "North", "revenue": 4200.0},
        {"region": "West", "revenue": 3000.0},
    ]
    assert "North is the highest-revenue region" in payload["answer"]
    assert payload["metric_context"][0]["term"] == "Revenue"
    assert "source_snippet" in payload["metric_context"][0]
    assert db_path.exists()


def test_ask_endpoint_returns_supported_question_error_for_unsupported_prompt(tmp_path):
    from agentic_bi_copilot.api import create_app
    from fastapi.testclient import TestClient

    client = TestClient(
        create_app(db_path=tmp_path / "api_sales_mart.sqlite"),
        raise_server_exceptions=False,
    )

    response = client.post(
        "/ask",
        json={"question": "Drop the customer table", "limit": 2},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": {
            "error": "unsupported_question",
            "message": (
                "Unsupported question. Try one of the published sample questions."
            ),
            "supported_questions": [
                "Which customer segment has the highest revenue?",
                "What is revenue by region?",
                "What is the repeat customer rate?",
                "What is product category mix by revenue?",
            ],
        }
    }


def test_openapi_schema_documents_ask_request_and_response_examples(tmp_path):
    client = _create_test_client(tmp_path)

    response = client.get("/openapi.json")

    assert response.status_code == 200
    payload = response.json()
    ask_operation = payload["paths"]["/ask"]["post"]
    request_schema = payload["components"]["schemas"]["AskQuestionRequest"]
    response_schema = payload["components"]["schemas"]["AskQuestionResponse"]

    assert ask_operation["summary"] == "Ask a supported BI question"
    assert "safe read-only SQL" in ask_operation["description"]
    assert request_schema["examples"] == [
        {"question": "What is revenue by region?", "limit": 2}
    ]
    assert response_schema["examples"][0]["rows"] == [
        {"region": "North", "revenue": 4200.0},
        {"region": "West", "revenue": 3000.0},
    ]
    assert response_schema["examples"][0]["metric_context"][0]["term"] == "Revenue"
    assert "Metric definition: Revenue" in response_schema["examples"][0]["answer"]


def test_openapi_schema_documents_unsupported_question_error_example(tmp_path):
    client = _create_test_client(tmp_path)

    response = client.get("/openapi.json")

    assert response.status_code == 200
    ask_operation = response.json()["paths"]["/ask"]["post"]
    unsupported_response = ask_operation["responses"]["400"]
    unsupported_example = unsupported_response["content"]["application/json"]["examples"][
        "unsupported_question"
    ]["value"]

    assert unsupported_response["description"] == "Unsupported BI question"
    assert unsupported_example["detail"]["error"] == "unsupported_question"
    assert unsupported_example["detail"]["supported_questions"] == [
        "Which customer segment has the highest revenue?",
        "What is revenue by region?",
        "What is the repeat customer rate?",
        "What is product category mix by revenue?",
    ]
