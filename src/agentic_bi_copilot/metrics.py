"""Metric glossary retrieval for grounded BI answer definitions."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

DEFAULT_GLOSSARY_PATH = Path(__file__).resolve().parents[2] / "docs" / "metric_glossary.md"


@dataclass(frozen=True)
class MetricDefinition:
    """A business metric definition retrieved as lightweight RAG context."""

    term: str
    aliases: tuple[str, ...]
    definition: str
    formula: str
    grain: str
    source: str
    source_snippet: str


def load_metric_glossary(glossary_path: str | Path | None = None) -> tuple[MetricDefinition, ...]:
    """Return metric definitions from a Markdown glossary document."""

    if glossary_path is None:
        return _load_default_metric_glossary()
    return _parse_metric_glossary(Path(glossary_path))


def retrieve_metric_definitions(text: str, limit: int = 3) -> tuple[MetricDefinition, ...]:
    """Retrieve metric definitions whose terms or aliases appear in text.

    This is intentionally deterministic for the offline portfolio milestone: it
    behaves like a tiny keyword retriever over curated BI metric cards, returning
    the most specific matching definitions first.
    """

    normalized = " ".join(text.lower().split())
    scored: list[tuple[int, int, MetricDefinition]] = []
    for position, definition in enumerate(load_metric_glossary()):
        score = _match_score(normalized, definition)
        if score:
            scored.append((score, -position, definition))

    scored.sort(reverse=True)
    safe_limit = max(1, int(limit))
    return tuple(definition for _, _, definition in scored[:safe_limit])


@lru_cache(maxsize=1)
def _load_default_metric_glossary() -> tuple[MetricDefinition, ...]:
    return _parse_metric_glossary(DEFAULT_GLOSSARY_PATH)


def _parse_metric_glossary(path: Path) -> tuple[MetricDefinition, ...]:
    definitions: list[MetricDefinition] = []
    current_term: str | None = None
    current_fields: dict[str, str] = {}

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            if current_term is not None:
                definitions.append(_build_metric_definition(current_term, current_fields))
            current_term = line.removeprefix("## ").strip()
            current_fields = {}
            continue
        if current_term and line.startswith("- ") and ":" in line:
            key, value = line.removeprefix("- ").split(":", 1)
            current_fields[_normalize_field_key(key)] = _clean_field_value(value)

    if current_term is not None:
        definitions.append(_build_metric_definition(current_term, current_fields))

    return tuple(definitions)


def _build_metric_definition(term: str, fields: dict[str, str]) -> MetricDefinition:
    aliases = tuple(
        alias.strip()
        for alias in fields.get("aliases", "").split(",")
        if alias.strip()
    )
    return MetricDefinition(
        term=term,
        aliases=aliases,
        definition=fields["definition"],
        formula=fields["formula"],
        grain=fields["grain"],
        source=fields.get("source", f"docs/metric_glossary.md#{_slugify(term)}"),
        source_snippet=(
            f"- Definition: {fields['definition']}\n"
            f"- Formula: {fields['formula']}\n"
            f"- Grain: {fields['grain']}"
        ),
    )


def _normalize_field_key(raw_key: str) -> str:
    key = raw_key.replace("*", "").strip().lower()
    aliases = {
        "business definition": "definition",
        "common aliases": "aliases",
    }
    return aliases.get(key, key)


def _clean_field_value(raw_value: str) -> str:
    return raw_value.strip().strip("`")


def _slugify(term: str) -> str:
    return "-".join(term.lower().split())


def _match_score(normalized_text: str, definition: MetricDefinition) -> int:
    score = 0
    for phrase in (definition.term, *definition.aliases):
        normalized_phrase = phrase.lower()
        if normalized_phrase in normalized_text:
            score += len(normalized_phrase.split())
            if normalized_phrase == definition.term.lower():
                score += 10
    return score
