# One-Week Roadmap

Project: **Agentic BI Copilot**  
Goal: Complete a market-relevant AI engineering portfolio project in one week with two verified, human-style commits per day.

## Day 1 — Offline analytics foundation

- Scaffold Python package, tests, CLI, and documentation.
- Build deterministic sales mart sample data.
- Add safe SQL generation for the first executive business question.
- Add a discoverable sample-question registry and CLI listing command.
- Verify with pytest and CLI smoke output.

## Day 2 — Broader NL2SQL coverage

- Add more business questions: revenue by region, repeat customers, product mix, and quarter-over-quarter trends.
- Strengthen SQL safety validation.
- Add examples with expected output.
- Session 02 progress: shipped the safe `region_revenue` question with deterministic tests, CLI listing coverage, and README example output.
- Session 03 progress: added `repeat_customer_rate` retention analytics with a safe aggregate SQL path, registry/CLI coverage, and README example output.
- Session 04 progress: added `product_category_mix` analytics with category revenue share, units sold, deterministic tests, CLI listing coverage, and README example output.

## Day 3 — RAG-backed metric definitions

- Add a small metric glossary and document loader.
- Retrieve definitions for terms like revenue, repeat purchase, active customer, and average order value.
- Cite metric definitions in answer explanations.
- Session 05 progress: added a deterministic metric glossary/RAG context layer, answer citations, glossary documentation, and regression coverage for revenue, repeat customer rate, active customer, product category mix, and average order value definitions.
- Session 06 progress: connected retrieved metric definitions to answer explanations with stable glossary citation anchors and definition/formula/grain source snippets in the deterministic CLI path.

## Day 4 — Evaluation harness

- Add deterministic test cases for question routing, SQL generation, and answer quality.
- Track pass/fail results in a simple evaluation report.
- Document known limitations and future eval improvements.
- Session 07 progress: added a deterministic supported-question evaluation dataset and CLI runner that checks SQL safety, expected SQL fragments, deterministic rows, metric context, and answer text for every offline sample question.
- Session 08 progress: added evaluation quality-summary reporting, graceful failed-case capture for unsupported or broken questions, and documentation for the eval quality-gate contract.

## Day 5 — API layer

- Add FastAPI endpoints for asking questions, listing sample questions, and health checks.
- Include request/response schemas and API smoke tests.
- Session 09 progress: added a FastAPI app with `GET /health`, `GET /questions`, and `POST /ask` endpoints backed by the deterministic safe-SQL answer path, Pydantic request/response schemas, API regression tests, and an API smoke path.
- Session 10 progress: strengthened the FastAPI contract with OpenAPI request/response examples, structured unsupported-question `400` errors, expanded API tests, and dedicated API usage documentation.

## Day 6 — UI and portfolio polish

- Add a lightweight Streamlit or static UI demo.
- Improve README screenshots/examples.
- Add architecture diagram and recruiter-focused feature summary.
- Session 11 progress: added a self-contained static HTML demo page plus a CLI renderer so the deterministic BI answer path can be shown locally without extra UI dependencies.
- Session 12 progress: polished the recruiter-facing README narrative, expanded architecture diagrams/docs, and added architecture proof points to the static demo renderer with pytest and CLI verification.

## Day 7 — Production packaging

- Add Dockerfile, GitHub Actions CI, and final usage docs.
- Run full verification and polish final portfolio narrative.
- Session 13 progress: added a production Dockerfile, `.dockerignore`, and GitHub Actions CI that runs pytest, a deterministic CLI smoke query, and Docker build/run smoke coverage.


