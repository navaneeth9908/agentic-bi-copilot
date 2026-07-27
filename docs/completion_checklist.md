# Portfolio Completion Checklist

This final handoff artifact ties the one-week Agentic BI Copilot roadmap to reviewer-visible evidence. It is intentionally deterministic so a hiring manager or engineer can re-run the same command locally and see the project readiness state without reading every source file first.

## Run the readiness command

```bash
uv run python -m agentic_bi_copilot.cli --completion-checklist
```

For temporary verification with an ignored local SQLite artifact, pass an explicit database path under `examples/` and delete it after the run:

```bash
uv run python -m agentic_bi_copilot.cli --completion-checklist --db-path examples/completion_checklist.sqlite
```

## Expected live summary

Healthy output starts with these fragments:

```text
Portfolio completion checklist: READY
Supported questions: 4
Quality gates: PASS (4/4 eval cases passing)
```

The command runs the deterministic supported-question eval suite before printing readiness, then reports the shipped delivery surfaces:

```text
Delivery surfaces:
- CLI: sample-question registry, safe SQL, rows, and grounded answer text
- FastAPI: /health, /questions, /ask
- Static demo: docs/demo.html self-contained reviewer artifact
- Docker + GitHub Actions CI: pytest, CLI smoke, and Docker smoke checks
```

## Roadmap evidence covered

The checklist maps each daily milestone to concrete review evidence:

- **Day 1 - Offline analytics foundation: complete** — deterministic mart plus first safe NL2SQL route.
- **Day 2 - Broader NL2SQL coverage: complete** — region, repeat-customer, and product/category analytics.
- **Day 3 - RAG-backed metric definitions: complete** — metric glossary definitions cited in answers.
- **Day 4 - Evaluation harness: complete** — supported-question eval dataset and pass/fail quality summary.
- **Day 5 - FastAPI contract: complete** — health, question registry, and ask-question API contract.
- **Day 6 - Static demo and recruiter narrative: complete** — self-contained `docs/demo.html`, README, and architecture docs.
- **Day 7 - Docker + CI packaging: complete** — Docker runtime, GitHub Actions pytest/CLI/Docker smoke checks, and final checklist.

The final line keeps the portfolio honest about the next production step:

```text
Next production step: connect a warehouse and LLM planner behind the same guardrails.
```
