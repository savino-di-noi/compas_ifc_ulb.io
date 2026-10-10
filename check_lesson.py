"""Run the course's Python cells against the bundled IFC in an isolated folder."""

from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
COURSE = json.loads((ROOT / "course.json").read_text(encoding="utf-8"))
NOTEBOOKS = [COURSE["intro"], *(item["file"] for item in COURSE["exercises"])]


def run_notebook(filename: str) -> dict:
    notebook = json.loads((ROOT / filename).read_text(encoding="utf-8"))
    variables: dict = {}
    for cell in notebook["cells"]:
        if cell["cell_type"] != "code" or "browser-only" in cell.get("metadata", {}).get("tags", []):
            continue
        source = "".join(cell["source"])
        if source.lstrip().startswith("%pip "):
            continue  # The CI environment installed the dependencies already.
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(source, f"{filename}:{cell['id']}", "exec"), variables)
    return variables


def main() -> None:
    previous_dir = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="ifcio-course-") as folder:
        try:
            os.chdir(folder)
            for model_name in COURSE["models"]:
                shutil.copy2(ROOT / model_name, model_name)
            for filename in NOTEBOOKS:
                variables = run_notebook(filename)
                if filename == "02_geometry_and_viewer.ipynb":
                    assert len(list(variables["wall_mesh"].faces())) > 0
                elif filename == "03_edit_save_extract.ipynb":
                    assert variables["checked"].name == variables["NEW_NAME"]
                    assert variables["subset_path"].is_file()
                elif filename == "04_clashes_and_connections.ipynb":
                    assert variables["new_clashes"] == 1
                elif filename == "05_create_and_validate.ipynb":
                    assert variables["result"].status == "pass"
                print(f"Passed: {filename}")
        finally:
            os.chdir(previous_dir)


if __name__ == "__main__":
    main()
