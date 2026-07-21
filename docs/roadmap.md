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

## Day 3 — RAG-backed metric definitions

- Add a small metric glossary and document loader.
- Retrieve definitions for terms like net revenue, repeat purchase, active customer, and average order value.
- Cite metric definitions in answer explanations.

## Day 4 — Evaluation harness

- Add deterministic test cases for question routing, SQL generation, and answer quality.
- Track pass/fail results in a simple evaluation report.
- Document known limitations and future eval improvements.

## Day 5 — API layer

- Add FastAPI endpoints for asking questions, listing sample questions, and health checks.
- Include request/response schemas and API smoke tests.

## Day 6 — UI and portfolio polish

- Add a lightweight Streamlit or static UI demo.
- Improve README screenshots/examples.
- Add architecture diagram and recruiter-focused feature summary.

## Day 7 — Production packaging

- Add Dockerfile, GitHub Actions CI, and final usage docs.
- Run full verification and polish final portfolio narrative.


