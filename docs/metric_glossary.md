# Metric Glossary

Curated business definitions used as deterministic RAG context for the local Agentic BI Copilot. Each card gives the SQL-facing formula, analysis grain, aliases for retrieval, and a stable citation anchor.

## Revenue
- Aliases: net revenue, sales, highest revenue, revenue by region, segment revenue, category revenue
- Definition: Gross recognized sales in the demo sales mart, calculated from line-item quantity multiplied by unit price before taxes, discounts, or refunds.
- Formula: SUM(order_items.quantity * order_items.unit_price)
- Grain: order item
- Source: docs/metric_glossary.md#revenue

## Repeat customer rate
- Aliases: repeat purchase, repeat customers, retention rate, customer retention
- Definition: The share of unique customers with more than one order during the analysis period.
- Formula: repeat_customers / total_customers * 100
- Grain: customer
- Source: docs/metric_glossary.md#repeat-customer-rate

## Product category mix
- Aliases: category mix, product mix, revenue mix, category revenue, merchandising mix
- Definition: Category revenue contribution across the product catalog, used to compare category revenue, unit volume, and share of total revenue.
- Formula: category_revenue / total_revenue * 100
- Grain: product category
- Source: docs/metric_glossary.md#product-category-mix

## Active customer
- Aliases: active customers, active buyers, active account, active accounts
- Definition: A unique customer with at least one order during the selected reporting window.
- Formula: COUNT(DISTINCT orders.customer_id)
- Grain: customer within reporting window
- Source: docs/metric_glossary.md#active-customer

## Average order value
- Aliases: AOV, average basket, order value
- Definition: Average revenue generated per order, useful for comparing basket size and monetization trends.
- Formula: revenue / order_count
- Grain: order
- Source: docs/metric_glossary.md#average-order-value
