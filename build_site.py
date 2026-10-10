"""Build a safe, static HTML reading page from the teaching notebook.

This converter intentionally uses only the Python standard library. It does
not execute notebook cells, preserve notebook outputs, load external scripts,
or interpret raw HTML from notebook content.
"""

from __future__ import annotations

import json
import re
import shutil
import zipfile
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parent
NOTEBOOK_PATH = ROOT / "compas_ifc_compas_viewer_intro.ipynb"
OUTPUT_PATH = ROOT / "site" / "index.html"
BINDER_URL = "https://mybinder.org/v2/gh/savino-di-noi/compas_ifc_ulb.io/main?urlpath=lab/tree/compas_ifc_compas_viewer_intro.ipynb"


def inline_markdown(text: str) -> str:
    """Render a deliberately small, escaped Markdown subset."""

    rendered = escape(text, quote=False)
    rendered = re.sub(r"`([^`]+)`", r"<code>\1</code>", rendered)
    rendered = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", rendered)
    rendered = re.sub(
        r"\[([^\]]+)\]\((https://[^\s)\"'<>]+)\)",
        r'<a href="\2">\1</a>', rendered,
    )
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
    navigation: list[str] = []
    code_number = 0
    for cell in notebook.get("cells", []):
        source = "".join(cell.get("source", []))
        if cell.get("cell_type") == "markdown":
            rendered = render_markdown(source)
            for heading in re.findall(r"^## (.+)$", source, re.MULTILINE):
                anchor = "section-" + str(len(navigation) + 1)
                title = inline_markdown(heading)
                rendered = rendered.replace(f"<h2>{title}</h2>", f'<h2 id="{anchor}">{title}</h2>', 1)
                navigation.append(f'<li><a href="#{anchor}">{title}</a></li>')
            sections.append(rendered)
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
  <meta name="description" content="A beginner lesson: read IFC objects, edit a name, save and verify with COMPAS IFC.">
  <title>ifc.io — Learn to work with IFC objects</title>
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
    a {{ color: #125b91; text-underline-offset: .2em; }}
    a:focus-visible, summary:focus-visible {{ outline: 3px solid #e18b25; outline-offset: 4px; }}
    h2 {{ margin-top: 2.5rem; scroll-margin-top: 1rem; }}
    nav ul {{ columns: 2; padding-left: 1.25rem; }}
    .downloads {{ display: flex; flex-wrap: wrap; align-items: center; gap: 1rem; margin: 1.5rem 0; }}
    .launch {{ display: inline-block; padding: .8rem 1.1rem; border-radius: .5rem; background: #123b66; color: white; font-weight: 700; text-decoration: none; }}
    .launch:hover {{ background: #0b2e53; }}
    .steps {{ padding: 1rem 1.25rem; background: #eef5fb; border-radius: .5rem; }}
    .steps li {{ margin: .35rem 0; }}
    details {{ border-left: 3px solid #dbe2ee; padding-left: .75rem; }}
    @media (max-width: 600px) {{ body {{ padding: .5rem; }} main {{ padding: 1rem; }} nav ul {{ columns: 1; }} }}
    @media print {{ body, main {{ background: white; padding: 0; border: 0; box-shadow: none; }} pre {{ white-space: pre-wrap; background: #eee; color: black; }} nav, .downloads {{ display: none; }} }}
  </style>
</head>
<body>
  <main>
    <a href="#lesson">Skip to lesson</a>
    <p class="notice"><strong>Work entirely in your browser.</strong> Read the lesson here, then open its runnable notebook on the public Binder service. It includes the sample IFC and COMPAS IFC package. The first launch may take several minutes; save any edited IFC or notebook before closing the temporary session.</p>
    <div class="downloads"><a class="launch" href="{BINDER_URL}" rel="noopener noreferrer">Open the live notebook on Binder ↗</a><a href="lesson.zip" download>Download lesson and sample IFC</a></div>
    <ol class="steps"><li>Read the short explanations and predict each result.</li><li>Open Binder and run the matching cell with Shift + Enter.</li><li>Change the sample wall's name, save a new IFC, and download it before the session ends.</li></ol>
    <p>The live notebook opens on mybinder.org. If the launch reports that the repository is unavailable, the course repository must be made public and the Binder image built before class.</p>
    <nav aria-label="Lesson contents"><strong>Lesson contents</strong><ul>{''.join(navigation)}</ul></nav>
    <div id="lesson">
    {body}
    </div>
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
    downloads = [NOTEBOOK_PATH, ROOT / "sample_building.ifc", ROOT / "README.md"]
    for path in downloads:
        shutil.copy2(path, OUTPUT_PATH.parent / path.name)
    with zipfile.ZipFile(OUTPUT_PATH.parent / "lesson.zip", "w", zipfile.ZIP_DEFLATED) as bundle:
        for path in downloads:
            bundle.write(path, arcname=path.name)
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
