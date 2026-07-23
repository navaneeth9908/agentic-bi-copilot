from pathlib import Path

from agentic_bi_copilot import metrics
from agentic_bi_copilot.metrics import load_metric_glossary, retrieve_metric_definitions


def test_load_metric_glossary_reads_markdown_document(tmp_path: Path):
    glossary_path = tmp_path / "metric_glossary.md"
    glossary_path.write_text(
        """
# Metric Glossary

## Revenue
- Aliases: net revenue, sales
- Definition: Recognized demo sales from line items.
- Formula: SUM(order_items.quantity * order_items.unit_price)
- Grain: order item
- Source: docs/metric_glossary.md#revenue
""".strip(),
        encoding="utf-8",
    )

    definitions = load_metric_glossary(glossary_path)

    assert len(definitions) == 1
    assert definitions[0].term == "Revenue"
    assert definitions[0].aliases == ("net revenue", "sales")
    assert definitions[0].definition == "Recognized demo sales from line items."


def test_default_metric_glossary_loads_repository_document():
    assert metrics.DEFAULT_GLOSSARY_PATH.name == "metric_glossary.md"

    definitions = load_metric_glossary()

    assert definitions[0].term == "Revenue"
    assert definitions[0].source == "docs/metric_glossary.md#revenue"
    assert metrics.DEFAULT_GLOSSARY_PATH.exists()
    assert "## Revenue" in metrics.DEFAULT_GLOSSARY_PATH.read_text(encoding="utf-8")


def test_retrieve_metric_definitions_matches_revenue_terms():
    definitions = retrieve_metric_definitions("What is revenue by region?")

    assert definitions
    assert definitions[0].term == "Revenue"
    assert definitions[0].formula == "SUM(order_items.quantity * order_items.unit_price)"
    assert definitions[0].source == "docs/metric_glossary.md#revenue"


def test_retrieve_metric_definitions_prioritizes_specific_product_mix():
    definitions = retrieve_metric_definitions("What is product category mix by revenue?", limit=2)

    assert [definition.term for definition in definitions] == [
        "Product category mix",
        "Revenue",
    ]
    assert "category revenue" in definitions[0].definition


def test_retrieve_metric_definitions_matches_repeat_customer_rate_aliases():
    definitions = retrieve_metric_definitions("Show repeat purchase and retention rate")

    assert definitions[0].term == "Repeat customer rate"
    assert "more than one order" in definitions[0].definition


def test_retrieve_metric_definitions_supports_active_customer_and_aov_terms():
    active_definitions = retrieve_metric_definitions("How many active customers bought this month?")
    aov_definitions = retrieve_metric_definitions("Track AOV and average order value")

    assert active_definitions[0].term == "Active customer"
    assert active_definitions[0].formula == "COUNT(DISTINCT orders.customer_id)"
    assert aov_definitions[0].term == "Average order value"
    assert aov_definitions[0].formula == "revenue / order_count"
