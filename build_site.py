"""Build a safe, static HTML reading page from the teaching notebook.

This converter intentionally uses only the Python standard library. It does
not execute notebook cells, preserve notebook outputs, load external scripts,
or interpret raw HTML from notebook content.
"""

from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parent
NOTEBOOK_PATH = ROOT / "compas_ifc_compas_viewer_intro.ipynb"
OUTPUT_PATH = ROOT / "site" / "index.html"


def inline_markdown(text: str) -> str:
    """Render a deliberately small, escaped Markdown subset."""

    rendered = escape(text, quote=False)
    rendered = re.sub(r"`([^`]+)`", r"<code>\1</code>", rendered)
    rendered = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", rendered)
    return rendered


def render_markdown(source: str) -> str:
    """Render headings, paragraphs, and unordered lists without raw HTML."""

    blocks: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            blocks.append(f"<p>{inline_markdown(' '.join(paragraph))}</p>")
            paragraph.clear()

    def flush_list() -> None:
        if list_items:
            blocks.append("<ul>" + "".join(list_items) + "</ul>")
            list_items.clear()

    for line in source.splitlines():
        if line.startswith("# "):
            flush_paragraph()
            flush_list()
            blocks.append(f"<h1>{inline_markdown(line[2:])}</h1>")
        elif line.startswith("## "):
            flush_paragraph()
            flush_list()
            blocks.append(f"<h2>{inline_markdown(line[3:])}</h2>")
        elif line.startswith("### "):
            flush_paragraph()
            flush_list()
            blocks.append(f"<h3>{inline_markdown(line[4:])}</h3>")
        elif line.startswith("- "):
            flush_paragraph()
            list_items.append(f"<li>{inline_markdown(line[2:])}</li>")
        elif line.strip():
            flush_list()
            paragraph.append(line.strip())
        else:
            flush_paragraph()
            flush_list()

    flush_paragraph()
    flush_list()
    return "\n".join(blocks)


def render_notebook(notebook: dict) -> str:
    """Convert notebook markdown and code cells to view-only HTML."""

    sections: list[str] = []
    code_number = 0
    for cell in notebook.get("cells", []):
        source = "".join(cell.get("source", []))
        if cell.get("cell_type") == "markdown":
            sections.append(render_markdown(source))
        elif cell.get("cell_type") == "code":
            code_number += 1
            code = escape(source, quote=False)
            sections.append(
                "<details open>"
                f"<summary>Code cell {code_number}</summary>"
                f"<pre><code>{code}</code></pre>"
                "</details>"
            )

    body = "\n".join(sections)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src 'self' data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'">
  <meta name="referrer" content="no-referrer">
  <title>Learn compas_ifc and compas_viewer</title>
  <style>
    :root {{ color-scheme: light; font-family: system-ui, sans-serif; }}
    body {{ margin: 0 auto; max-width: 980px; padding: 2rem 1.25rem 5rem; color: #172033; background: #f7f9fc; line-height: 1.55; }}
    main {{ background: white; padding: 2rem; border: 1px solid #dbe2ee; border-radius: 12px; box-shadow: 0 5px 20px #17203312; }}
    h1, h2, h3 {{ line-height: 1.2; color: #123b66; }}
    code {{ font-family: ui-monospace, SFMono-Regular, Consolas, monospace; background: #eef2f7; padding: .1rem .3rem; border-radius: 4px; }}
    pre {{ overflow-x: auto; padding: 1rem; background: #101827; color: #e8eef8; border-radius: 8px; }}
    pre code {{ background: transparent; padding: 0; color: inherit; }}
    details {{ margin: 1rem 0; }}
    summary {{ cursor: pointer; font-weight: 700; color: #123b66; }}
    .notice {{ padding: 1rem; border-left: 4px solid #e18b25; background: #fff5e6; }}
  </style>
</head>
<body>
  <main>
    <p class="notice"><strong>Static reading version:</strong> this GitHub Pages site displays the lesson and code but does not execute Python, install packages, accept IFC uploads, or open a viewer window. Use a controlled Jupyter environment for execution.</p>
    {body}
  </main>
</body>
</html>
"""


def main() -> None:
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    if notebook.get("nbformat") != 4:
        raise ValueError("Expected a nbformat 4 notebook")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(render_notebook(notebook))
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
