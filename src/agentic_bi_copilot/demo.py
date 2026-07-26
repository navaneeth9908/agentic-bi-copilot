"""Static local HTML demo page for the Agentic BI Copilot."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

from agentic_bi_copilot.data import build_demo_db
from agentic_bi_copilot.questions import list_sample_questions
from agentic_bi_copilot.sql_agent import answer_question

DEFAULT_DEMO_QUESTION = "What is revenue by region?"
DEFAULT_DEMO_LIMIT = 2


def render_demo_html(
    db_path: str | Path,
    question: str = DEFAULT_DEMO_QUESTION,
    limit: int = DEFAULT_DEMO_LIMIT,
) -> str:
    """Render a self-contained HTML demo for a supported BI question."""

    resolved_db_path = _ensure_demo_db(Path(db_path))
    result = answer_question(question, db_path=resolved_db_path, limit=limit)
    sample_cards = _render_sample_question_cards()
    rows_table = _render_rows_table(result.rows)
    metric_cards = _render_metric_cards(result.metric_context)
    cli_command = f'uv run python -m agentic_bi_copilot.cli "{result.question}" --limit {limit}'
    api_payload = f'{{"question": "{result.question}", "limit": {limit}}}'

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Agentic BI Copilot Demo</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #0f172a;
      --panel: #111827;
      --panel-soft: #1e293b;
      --text: #e5e7eb;
      --muted: #94a3b8;
      --accent: #38bdf8;
      --accent-strong: #22c55e;
      --border: #334155;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: radial-gradient(circle at top left, #1e3a8a 0, transparent 32rem), var(--bg);
      color: var(--text);
      line-height: 1.55;
    }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 48px 24px; }}
    .hero {{ display: grid; gap: 18px; margin-bottom: 28px; }}
    .eyebrow {{ color: var(--accent); font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }}
    h1 {{ margin: 0; font-size: clamp(2.2rem, 4vw, 4.4rem); line-height: .98; }}
    h2 {{ margin-top: 0; }}
    .subtitle {{ max-width: 760px; color: var(--muted); font-size: 1.12rem; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 18px; }}
    .card {{
      background: linear-gradient(180deg, rgba(255,255,255,.045), rgba(255,255,255,.02));
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 22px;
      box-shadow: 0 18px 60px rgba(0,0,0,.28);
    }}
    .stat {{ display: flex; justify-content: space-between; gap: 16px; color: var(--muted); }}
    .stat strong {{ color: var(--accent-strong); }}
    ul {{ padding-left: 1.2rem; }}
    li {{ margin: 8px 0; }}
    table {{ width: 100%; border-collapse: collapse; overflow: hidden; border-radius: 12px; }}
    th, td {{ border-bottom: 1px solid var(--border); padding: 10px 12px; text-align: left; }}
    th {{ color: var(--accent); background: rgba(56,189,248,.08); }}
    pre {{
      white-space: pre-wrap;
      word-break: break-word;
      background: #020617;
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 16px;
      overflow-x: auto;
    }}
    code {{ color: #bae6fd; }}
    .pill {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border: 1px solid rgba(56,189,248,.45);
      border-radius: 999px;
      padding: 6px 10px;
      color: #bae6fd;
      background: rgba(56,189,248,.08);
      font-size: .9rem;
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <div class="eyebrow">Portfolio demo · deterministic NL2SQL</div>
      <h1>Agentic BI Copilot Demo</h1>
      <p class="subtitle">A lightweight local UI artifact for showing how the copilot routes business questions, generates safe read-only SQL, executes against a demo sales mart, and cites metric-glossary context.</p>
      <div class="grid">
        <div class="card stat"><span>Supported questions</span><strong>{len(list_sample_questions())}</strong></div>
        <div class="card stat"><span>Demo question</span><strong>{escape(result.question)}</strong></div>
        <div class="card stat"><span>Rows shown</span><strong>{len(result.rows)}</strong></div>
      </div>
    </section>

    <section class="grid">
      <article class="card">
        <h2>Sample question menu</h2>
        <p class="pill">Ready for recruiter demos</p>
        <ul>
{sample_cards}
        </ul>
      </article>
      <article class="card">
        <h2>Executive answer</h2>
        <pre>{escape(result.answer)}</pre>
      </article>
    </section>

    <section class="card">
      <h2>Generated safe SQL</h2>
      <pre><code>{escape(result.sql)}</code></pre>
    </section>

    <section class="card">
      <h2>Result table</h2>
{rows_table}
    </section>

    <section class="card">
      <h2>Architecture proof points</h2>
      <ul>
        <li><strong>Router → metric context → SQL guardrail → execution → explanation</strong>: one deterministic path answers each supported business question end to end.</li>
        <li><strong>Pytest + eval runner evidence</strong>: regression tests and the supported-question eval suite validate SQL safety, expected rows, metric citations, and answer text.</li>
        <li><strong>FastAPI + static demo packaging</strong>: the same answer path is exposed through API endpoints and this dependency-light reviewer demo.</li>
      </ul>
    </section>

    <section class="grid">
      <article class="card">
        <h2>Metric context</h2>
{metric_cards}
      </article>
      <article class="card">
        <h2>Run it locally</h2>
        <p>CLI smoke command:</p>
        <pre><code>{escape(cli_command)}</code></pre>
        <p>FastAPI payload for <code>POST /ask</code>:</p>
        <pre><code>{escape(api_payload)}</code></pre>
      </article>
    </section>
  </main>
</body>
</html>
"""


def write_demo_html(
    output_path: str | Path,
    db_path: str | Path,
    question: str = DEFAULT_DEMO_QUESTION,
    limit: int = DEFAULT_DEMO_LIMIT,
) -> Path:
    """Write the static demo page and return the generated file path."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    html = render_demo_html(db_path=db_path, question=question, limit=limit)
    path.write_text(html, encoding="utf-8")
    return path


def _ensure_demo_db(db_path: Path) -> Path:
    if not db_path.exists():
        build_demo_db(db_path)
    return db_path


def _render_sample_question_cards() -> str:
    lines: list[str] = []
    for sample in list_sample_questions():
        lines.append(
            "          "
            f"<li><strong>{escape(sample.id)}</strong> "
            f"<span>({escape(sample.category)})</span>: "
            f"{escape(sample.question)}</li>"
        )
    return "\n".join(lines)


def _render_rows_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "      <p>No rows returned.</p>"

    headers = list(rows[0].keys())
    header_cells = "".join(f"<th>{escape(header)}</th>" for header in headers)
    body_rows = []
    for row in rows:
        cells = "".join(f"<td>{escape(str(row[header]))}</td>" for header in headers)
        body_rows.append(f"        <tr>{cells}</tr>")
    body = "\n".join(body_rows)
    return f"""      <table>
        <thead><tr>{header_cells}</tr></thead>
        <tbody>
{body}
        </tbody>
      </table>"""


def _render_metric_cards(metric_context: object) -> str:
    cards = []
    for definition in metric_context:
        cards.append(
            "        <div>"
            f"<h3>Metric definition: {escape(definition.term)}</h3>"
            f"<p><code>{escape(definition.source)}</code></p>"
            f"<pre>{escape(definition.source_snippet)}</pre>"
            "</div>"
        )
    if not cards:
        return "        <p>No metric context retrieved.</p>"
    return "\n".join(cards)
