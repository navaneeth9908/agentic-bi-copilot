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
