# Agentic BI Copilot

A production-style AI engineering portfolio project: an agentic business-intelligence copilot that turns natural-language analytics questions into safe SQL, explains the answer, and grows into a RAG + evaluation + API product over one focused week.

## Why this project matters

Modern AI engineering roles increasingly expect more than a chatbot demo. This repository is designed to demonstrate:

- **Agentic workflow design** for planning, SQL generation, validation, execution, and explanation.
- **NL2SQL over a realistic analytics mart** with safety checks and reproducible sample data.
- **RAG-backed metric definitions** so business terms are grounded in documented context.
- **LLM evaluation discipline** with deterministic regression tests and answer-quality checks.
- **Production packaging** through FastAPI, Docker, CI, and portfolio-ready documentation.

## Current milestone

The first milestone is a deterministic offline analytics path:

```bash
uv run --group dev pytest
uv run python -m agentic_bi_copilot.cli --list-questions
uv run python -m agentic_bi_copilot.cli "Which customer segment has the highest revenue?"
uv run python -m agentic_bi_copilot.cli "What is revenue by region?" --limit 4
uv run python -m agentic_bi_copilot.cli "What is the repeat customer rate?" --limit 1
```

Expected behavior: the copilot lists supported sample questions, builds a local demo sales mart, generates safe read-only SQL, returns ranked segment or region revenue, calculates a repeat-customer KPI, and explains the top dimension or retention metric.

## CLI example: revenue by region

```bash
uv run python -m agentic_bi_copilot.cli "What is revenue by region?" --limit 4
```

Expected deterministic rows:

```text
region | revenue
--- | ---
North | 4200.0
West | 3000.0
South | 1500.0
East | 800.0
```

The generated SQL groups by `c.region`, orders by revenue descending, and passes the same read-only safety gate used by the segment revenue question.

## CLI example: repeat customer rate

```bash
uv run python -m agentic_bi_copilot.cli "What is the repeat customer rate?" --limit 1
```

Expected deterministic rows:

```text
total_customers | repeat_customers | repeat_customer_rate
--- | --- | ---
6 | 2 | 33.33
```

The metric treats customers with more than one order as repeat customers, so the offline sales mart reports 2 repeat customers out of 6 total customers, or a 33.33% repeat-customer rate.

## One-week build roadmap

See [`docs/roadmap.md`](docs/roadmap.md) for the daily milestone plan. The goal is to complete a polished AI engineering portfolio project in one week with two verified commits per day.

## Planned architecture

```text
User question
   |
   v
Question router -> Metric/RAG context -> SQL generator -> SQL safety validator
   |                                                     |
   |                                                     v
   +-------------------- Explanation composer <- SQLite/DuckDB execution
                                      |
                                      v
                         Tests, evals, traces, API/UI
```

## Repository layout

```text
src/agentic_bi_copilot/   Python package
  data.py                 Deterministic demo sales mart builder
  sql_agent.py            Safe NL2SQL and answer composition path
  questions.py            Supported sample-question registry
  cli.py                  Local command-line smoke path
tests/                    Regression tests
docs/                     Roadmap and architecture notes
examples/                 Local generated demo databases, ignored by git
```
