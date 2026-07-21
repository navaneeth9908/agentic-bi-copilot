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
uv run python -m agentic_bi_copilot.cli "Which customer segment has the highest revenue?"
```

Expected behavior: the copilot builds a local demo sales mart, generates safe SQL, returns ranked segment revenue, and explains the top segment.

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
  cli.py                  Local command-line smoke path
tests/                    Regression tests
docs/                     Roadmap and architecture notes
examples/                 Local generated demo databases, ignored by git
```
