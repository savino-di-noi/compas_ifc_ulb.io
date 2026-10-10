"""Build safe, static HTML reading pages from the teaching notebooks.

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
from urllib.parse import quote


ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = ROOT / "site" / "index.html"
BINDER_BASE = "https://mybinder.org/v2/gh/savino-di-noi/compas_ifc_ulb.io/main?urlpath=lab/tree/"


def binder_url(filename: str) -> str:
    return BINDER_BASE + quote(filename)


def inline_markdown(text: str) -> str:
    """Render a deliberately small, escaped Markdown subset."""

    rendered = escape(text, quote=False)
    rendered = re.sub(r"`([^`]+)`", r"<code>\1</code>", rendered)
    rendered = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", rendered)
    rendered = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", rendered)
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
    list_tag = "ul"

    def flush_paragraph() -> None:
        if paragraph:
            blocks.append(f"<p>{inline_markdown(' '.join(paragraph))}</p>")
            paragraph.clear()

    def flush_list() -> None:
        if list_items:
            blocks.append(f"<{list_tag}>" + "".join(list_items) + f"</{list_tag}>")
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
            if list_tag != "ul":
                flush_list()
                list_tag = "ul"
            list_items.append(f"<li>{inline_markdown(line[2:])}</li>")
        elif match := re.match(r"^\d+\. (.+)$", line):
            flush_paragraph()
            if list_tag != "ol":
                flush_list()
                list_tag = "ol"
            list_items.append(f"<li>{inline_markdown(match.group(1))}</li>")
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


def render_notebook(notebook: dict, filename: str, exercises: list[dict], is_intro: bool) -> str:
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
    cards = ""
    if is_intro:
        entries = []
        for exercise in exercises:
            name = exercise["file"]
            title = escape(exercise["title"])
            description = escape(exercise["description"])
            html_name = Path(name).with_suffix(".html").name
            entries.append(
                '<li class="course-card">'
                f'<h3><a href="{html_name}">{title}</a></h3>'
                f'<p>{description}</p>'
                f'<div><a href="{html_name}">Read exercise</a>'
                f'<a href="{binder_url(name)}" rel="noopener noreferrer">Run in Binder ↗</a></div>'
                '</li>'
            )
        cards = '<section class="course-list" aria-labelledby="course-title"><h2 id="course-title">Exercises</h2><ol>' + "".join(entries) + '</ol></section>'
    back_link = '' if is_intro else '    <p class="back-link"><a href="index.html">← Course introduction and all exercises</a></p>\n'
    start_title = "Work in your browser" if is_intro else "Run this exercise in Binder"
    start_text = (
        "Read the introduction here, then run the notebooks in Binder. The first launch may take several minutes. Download your edited IFC files before the temporary session ends."
        if is_intro else
        "Read this exercise here or open its editable notebook in Binder. Run cells from top to bottom with Shift + Enter. Binder already includes the course packages."
    )
    download_link = '<a href="lesson.zip" download>Download the complete course</a>' if is_intro else f'<a href="{filename}" download>Download this notebook</a>'
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self'; img-src 'self' data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'">
  <meta name="referrer" content="no-referrer">
  <meta name="description" content="A beginner browser course for exploring, editing, viewing, and checking IFC objects with COMPAS IFC.">
  <title>ifc.io — Learn to work with IFC objects</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <main>
    <a class="skip-link" href="#lesson">Skip to lesson</a>
    <div class="sitebar">
      <a class="brand" href="index.html"><span class="brand-name">ifc<span>.io</span></span><small>Learn IFC in your browser</small></a>
      <a class="association" href="https://compas.dev/" rel="noopener noreferrer" aria-label="Visit the COMPAS Association website">
        <img src="assets/compas_default.svg" alt="COMPAS logo" width="251" height="52">
        <span>COMPAS Association</span>
      </a>
    </div>
{back_link}    <header class="hero">{introduction}
      <div class="library-credit" aria-label="COMPAS IFC library attribution">
        <div><span class="credit-label">Open-source library</span><strong><a href="https://compas.dev/compas_ifc/latest/" rel="noopener noreferrer">COMPAS IFC</a></strong></div>
        <div><span class="credit-label">Library author</span><strong><a href="https://github.com/compas-dev/compas_ifc/blob/main/CITATION.cff" rel="noopener noreferrer">Li Chen</a></strong></div>
      </div>
    </header>
    <section class="start" aria-labelledby="start-title">
      <h2 id="start-title">{start_title}</h2>
      <p>{start_text}</p>
      <div class="downloads"><a class="launch" href="{binder_url(filename)}" rel="noopener noreferrer">Open the live notebook ↗</a>{download_link}</div>
    </section>
{cards}
    <nav aria-label="Lesson contents"><strong>Lesson contents</strong><ul>{''.join(navigation)}</ul></nav>
    <article id="lesson">
    {body}
    </article>
    <footer class="footer">An independent teaching course using <a href="https://compas.dev/compas_ifc/latest/">COMPAS IFC</a>, authored by Li Chen and Tom Van Mele, in the <a href="https://compas.dev/">COMPAS Association</a> ecosystem. <a href="https://github.com/compas-dev/compas-graphics">COMPAS logo source</a>.</footer>
  </main>
</body>
</html>
"""


def main() -> None:
    course = json.loads((ROOT / "course.json").read_text(encoding="utf-8"))
    exercises = course["exercises"]
    filenames = [course["intro"], *(entry["file"] for entry in exercises)]
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    for number, filename in enumerate(filenames):
        notebook_path = ROOT / filename
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        if notebook.get("nbformat") != 4:
            raise ValueError(f"Expected a nbformat 4 notebook: {filename}")
        output = OUTPUT_PATH if number == 0 else OUTPUT_PATH.parent / Path(filename).with_suffix(".html").name
        with output.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(render_notebook(notebook, filename, exercises, number == 0))
        shutil.copy2(notebook_path, OUTPUT_PATH.parent / filename)
    shutil.copy2(ROOT / "style.css", OUTPUT_PATH.parent / "style.css")
    (OUTPUT_PATH.parent / "assets").mkdir(exist_ok=True)
    shutil.copy2(ROOT / "assets" / "compas_default.svg", OUTPUT_PATH.parent / "assets" / "compas_default.svg")
    downloads = [*(ROOT / filename for filename in filenames), *(ROOT / filename for filename in course["models"]), ROOT / "README.md"]
    for path in downloads:
        if path.suffix != ".ipynb":
            shutil.copy2(path, OUTPUT_PATH.parent / path.name)
    with zipfile.ZipFile(OUTPUT_PATH.parent / "lesson.zip", "w", zipfile.ZIP_DEFLATED) as bundle:
        for path in downloads:
            bundle.write(path, arcname=path.name)
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
