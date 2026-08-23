"""Open the mesh exported by the teaching notebook in compas_viewer."""

from pathlib import Path

from compas.colors import Color
from compas.data import json_load
from compas_viewer import Viewer


HERE = Path(__file__).resolve().parent
MESH_PATH = HERE / "selected_geometry.json"

if not MESH_PATH.exists():
    raise FileNotFoundError(
        f"Run the notebook export cell first; missing {MESH_PATH.name}."
    )

mesh = json_load(str(MESH_PATH))

viewer = Viewer()
viewer.scene.add(
    mesh,
    name="IFC selection",
    show_points=False,
    show_lines=True,
    show_faces=True,
    facecolor=Color.from_hex("#B8CBE4"),
    linecolor=Color.black(),
    linewidth=1.5,
)
viewer.show()

