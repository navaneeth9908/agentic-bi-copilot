# Evaluation Quality Gates

The deterministic evaluation suite is the local quality gate for the offline Agentic BI Copilot path. It is intentionally small, fast, and CI-friendly so every supported analytics question can be checked before adding API/UI layers.

## Report contract

Run the default suite with:

```bash
uv run python -m agentic_bi_copilot.cli --run-evals
```

Healthy output starts with a portfolio-readable summary:

```text
Evaluation report: 4/4 passed
Quality summary: PASS (100.0% pass rate, 0 failing cases)
- segment_revenue: PASS
- region_revenue: PASS
- repeat_customer_rate: PASS
- product_category_mix: PASS
```

The first line is the aggregate count. The quality-summary line is the go/no-go signal for demos, CI logs, and release notes:

- `PASS` means every case executed and every scoring check passed.
- `FAIL` means at least one case failed execution or missed an expected SQL, row, answer, or metric-context check.
- The pass rate is rounded to one decimal place.
- Failing case IDs are printed on the quality-summary line so the next debugging step is obvious.

## Scored checks

Each supported-question case is loaded from `evals/supported_questions.json` and scored against the same deterministic offline answer path used by the CLI. The current checks are:

| Check | Purpose |
| --- | --- |
| `execution` | The question route executed without raising an exception. |
| `sql_safe` | Generated SQL passed the read-only safety gate. |
| `sql_contains` | SQL includes expected structural fragments, such as grouping and ordering clauses. |
| `expected_rows` | Result rows start with the deterministic expected prefix. |
| `answer_contains` | The executive answer includes required business facts or citations. |
| `metric_terms` | Retrieved metric glossary context includes expected business definitions. |

## Failure-case handling

Unsupported or broken questions should not crash the whole evaluation run. The runner captures exceptions as failed `EvaluationCaseResult` records with:

- the original case ID and question,
- `checks={"execution": False}`,
- empty SQL, rows, and answer payloads,
- a failure message beginning with `execution failed:` and including the exception details.

A one-case unsupported evaluation report is expected to look like this:

```text
Evaluation report: 0/1 passed
Quality summary: FAIL (0.0% pass rate, 1 failing case: unsupported_inventory_aging)
- unsupported_inventory_aging: FAIL
  - execution failed: Unsupported question. Try: ...
```

This keeps regression output actionable: the suite still finishes, the CLI can return a non-zero exit code when failures exist, and the failing question ID is visible without reading a stack trace.
