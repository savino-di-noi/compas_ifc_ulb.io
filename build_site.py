"""Build a safe, static HTML reading page from the teaching notebook.

This converter intentionally uses only the Python standard library. It does
not execute notebook cells, preserve notebook outputs, load external scripts,
or interpret raw HTML from notebook content.
"""

from __future__ import annotations

import json
import keyword
import re
import shutil
import tokenize
import zipfile
from html import escape
from io import StringIO
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


def highlight_python(source: str) -> str:
    """Add small, escaped Python highlights without a build-time dependency."""

    lines = source.splitlines(keepends=True)
    line_offsets = [0]
    for line in lines:
        line_offsets.append(line_offsets[-1] + len(line))

    def offset(position: tuple[int, int]) -> int:
        row, column = position
        return line_offsets[row - 1] + column

    fragments: list[str] = []
    cursor = 0
    try:
        for token in tokenize.generate_tokens(StringIO(source).readline):
            if token.type in (tokenize.ENDMARKER, tokenize.INDENT, tokenize.DEDENT):
                continue
            start, end = offset(token.start), offset(token.end)
            if start < cursor:
                continue
            fragments.append(escape(source[cursor:start], quote=False))
            value = escape(source[start:end], quote=False)
            if token.type == tokenize.STRING:
                kind = "string"
            elif token.type == tokenize.COMMENT:
                kind = "comment"
            elif token.type == tokenize.NUMBER:
                kind = "number"
            elif token.type == tokenize.NAME and keyword.iskeyword(token.string):
                kind = "keyword"
            else:
                kind = ""
            fragments.append(f'<span class="tok-{kind}">{value}</span>' if kind else value)
            cursor = end
    except (tokenize.TokenError, IndentationError):
        pass
    fragments.append(escape(source[cursor:], quote=False))
    return "".join(fragments)


def render_notebook(notebook: dict) -> str:
    """Convert notebook markdown and code cells to view-only HTML."""

    sections: list[str] = []
    navigation: list[str] = []
    code_number = 0
    cells = notebook.get("cells", [])
    introduction = ""
    if cells and cells[0].get("cell_type") == "markdown":
        introduction = render_markdown("".join(cells[0].get("source", [])))
        cells = cells[1:]
    for cell in cells:
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
            code = highlight_python(source)
            sections.append(
                '<details class="code-cell" open>'
                f"<summary>Python example <span>Cell {code_number}</span></summary>"
                f"<pre><code>{code}</code></pre>"
                "</details>"
            )

    body = "\n".join(sections)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self'; img-src 'self' data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'">
  <meta name="referrer" content="no-referrer">
  <meta name="description" content="A beginner lesson: read IFC objects, edit a name, save and verify with COMPAS IFC.">
  <title>ifc.io — Learn to work with IFC objects</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <main>
    <a class="skip-link" href="#lesson">Skip to lesson</a>
    <div class="sitebar"><a class="brand" href="#">ifc<span>.io</span></a><small>COMPAS IFC · Beginner course</small></div>
    <header class="hero">{introduction}</header>
    <section class="start" aria-labelledby="start-title">
      <h2 id="start-title">Work in your browser</h2>
      <p>Read the lesson here, then run the examples in the public Binder notebook. It includes the sample IFC. The first launch may take several minutes; download your edited IFC before the temporary session ends.</p>
      <div class="downloads"><a class="launch" href="{BINDER_URL}" rel="noopener noreferrer">Open the live notebook ↗</a><a href="lesson.zip" download>Download lesson and sample IFC</a></div>
      <ol class="steps"><li>Read each explanation and predict the result.</li><li>Open Binder and run the matching cell with Shift + Enter.</li><li>Change the sample wall's name, save a new IFC, and download it.</li></ol>
    </section>
    <nav aria-label="Lesson contents"><strong>Lesson contents</strong><ul>{''.join(navigation)}</ul></nav>
    <article id="lesson">
    {body}
    </article>
    <footer class="footer">ifc.io · An introduction to working with IFC objects using COMPAS IFC</footer>
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
    shutil.copy2(ROOT / "style.css", OUTPUT_PATH.parent / "style.css")
    downloads = [NOTEBOOK_PATH, ROOT / "sample_building.ifc", ROOT / "README.md"]
    for path in downloads:
        shutil.copy2(path, OUTPUT_PATH.parent / path.name)
    with zipfile.ZipFile(OUTPUT_PATH.parent / "lesson.zip", "w", zipfile.ZIP_DEFLATED) as bundle:
        for path in downloads:
            bundle.write(path, arcname=path.name)
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
