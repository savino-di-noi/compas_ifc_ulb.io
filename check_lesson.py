"""Execute the browser course against its bundled IFC without Jupyter UI."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
NOTEBOOK = ROOT / "compas_ifc_compas_viewer_intro.ipynb"
SAMPLE = ROOT / "sample_building.ifc"
LAST_EXERCISE_CELL = "lesson-27"


def main() -> None:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    previous_dir = Path.cwd()
    executed = []

    with tempfile.TemporaryDirectory() as folder:
        try:
            os.chdir(folder)
            shutil.copy2(SAMPLE, "sample_building.ifc")
            variables = {}

            for cell in notebook["cells"]:
                if cell["cell_type"] == "code":
                    source = "".join(cell["source"])
                    if not source.lstrip().startswith("%"):
                        exec(compile(source, cell["id"], "exec"), variables)
                        executed.append(cell["id"])
                if cell["id"] == LAST_EXERCISE_CELL:
                    break

            assert "lesson-20" in executed, "The save/reopen exercise did not run"
            assert LAST_EXERCISE_CELL in executed, "The IFC subset export did not run"
            assert variables["checked"].name == variables["NEW_NAME"]
            assert variables["selected"].global_id == variables["checked"].global_id
            assert variables["SUBSET_PATH"].is_file()
            print("Lesson passed against the bundled IFC sample")
        finally:
            os.chdir(previous_dir)


if __name__ == "__main__":
    main()
