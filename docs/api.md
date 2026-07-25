# FastAPI Interface

The API exposes the same deterministic, safe-SQL answer path used by the CLI and evaluation runner. It is intended for local demos, API regression tests, and future UI integration.

## App entry point

The ASGI app is available at:

```text
agentic_bi_copilot.api:app
```

For local development with the FastAPI CLI:

```bash
uv run fastapi dev src/agentic_bi_copilot/api.py
```

The default API database path is `examples/sales_mart.sqlite`. If the file does not exist, the API builds the deterministic demo sales mart before answering the first `/ask` request.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Readiness payload with service name and supported-question count. |
| `GET` | `/questions` | Stable registry of deterministic sample questions. |
| `POST` | `/ask` | Generate safe read-only SQL, execute it, and return rows, answer text, and cited metric context. |

Interactive OpenAPI docs are available at `/docs` when the app is running. The OpenAPI schema also includes request and response examples for the `/ask` contract.

## Health check example

Request:

```bash
curl -s http://127.0.0.1:8000/health
```

Response:

```json
{
  "status": "ok",
  "service": "agentic-bi-copilot",
  "supported_questions": 4
}
```

## List supported questions

Request:

```bash
curl -s http://127.0.0.1:8000/questions
```

Response excerpt:

```json
{
  "count": 4,
  "questions": [
    {
      "id": "segment_revenue",
      "question": "Which customer segment has the highest revenue?",
      "category": "Revenue analytics",
      "supported": true
    },
    {
      "id": "region_revenue",
      "question": "What is revenue by region?",
      "category": "Revenue analytics",
      "supported": true
    }
  ]
}
```

## Ask a BI question

Request:

```bash
curl -s -X POST http://127.0.0.1:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"What is revenue by region?","limit":2}'
```

Response:

```json
{
  "question": "What is revenue by region?",
  "sql": "SELECT\n    c.region,\n    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue\nFROM customers AS c\nJOIN orders AS o ON o.customer_id = c.customer_id\nJOIN order_items AS oi ON oi.order_id = o.order_id\nGROUP BY c.region\nORDER BY revenue DESC",
  "rows": [
    {"region": "North", "revenue": 4200.0},
    {"region": "West", "revenue": 3000.0}
  ],
  "answer": "North is the highest-revenue region with $4,200.00 in the demo sales mart. Metric definition: Revenue [docs/metric_glossary.md#revenue]\nSource snippet:\n- Definition: Gross sales recognized from completed orders before refunds or discounts.\n- Formula: SUM(order_items.quantity * order_items.unit_price)\n- Grain: order item",
  "metric_context": [
    {
      "term": "Revenue",
      "source": "docs/metric_glossary.md#revenue",
      "source_snippet": "- Definition: Gross sales recognized from completed orders before refunds or discounts.\n- Formula: SUM(order_items.quantity * order_items.unit_price)\n- Grain: order item"
    }
  ]
}
```

## Unsupported question response

Unsupported prompts return a structured `400` instead of an unhandled server error. This keeps the API usable for frontends and agents that need to recover by showing the supported-question list.

Request:

```bash
curl -s -X POST http://127.0.0.1:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"Drop the customer table","limit":2}'
```

Response:

```json
{
  "detail": {
    "error": "unsupported_question",
    "message": "Unsupported question. Try one of the published sample questions.",
    "supported_questions": [
      "Which customer segment has the highest revenue?",
      "What is revenue by region?",
      "What is the repeat customer rate?",
      "What is product category mix by revenue?"
    ]
  }
}
```

## Test and smoke commands

```bash
uv run --group dev pytest tests/test_api.py -q
uv run --group dev pytest tests/ -q
```

A lightweight API smoke path can also use FastAPI's in-process `TestClient` to call `/ask`, `/openapi.json`, and the unsupported-question error path without starting a network server.
