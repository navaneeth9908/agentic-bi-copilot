# Architecture Notes

## Core loop

1. Accept a natural-language business question.
2. Retrieve metric definitions and schema context.
3. Generate a constrained SQL query.
4. Validate that the query is read-only and references expected tables.
5. Execute against a reproducible local analytics mart.
6. Compose a concise executive answer with result evidence.
7. Record tests/evals so behavior can be improved safely.

## Design principles

- Prefer deterministic offline behavior for portfolio reproducibility.
- Keep SQL execution read-only.
- Make every supported question testable.
- Separate generation, validation, execution, and explanation so future LLM-backed logic can be swapped in without breaking tests.
