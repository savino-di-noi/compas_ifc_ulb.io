# ifc.io: a browser course in COMPAS IFC

This course introduces bachelor students to IFC objects and the Python library
`compas_ifc`. Students read the public [course website](https://savino-di-noi.github.io/compas_ifc_ulb.io/)
and run the notebooks in Binder. They do not need Python on their own computers.

Start with `compas_ifc_compas_viewer_intro.ipynb` (what IFC is, why it matters,
what COMPAS IFC does, and how to use Binder). The five independent exercises are:

1. `01_open_and_query.ipynb`: spatial hierarchy, IFC type, Name, GlobalId,
   property sets.
2. `02_geometry_and_viewer.ipynb`: geometry and an interactive **browser** Viewer.
3. `03_edit_save_extract.ipynb`: rename, save a new IFC, reopen, extract a subset.
4. `04_clashes_and_connections.ipynb`: inspect relationships and detect a
   deliberately created clash.
5. `05_create_and_validate.ipynb` (optional): create an object and check a
   simple information requirement.

The notebooks follow the current [COMPAS IFC tutorials](https://compas.dev/compas_ifc/latest/examples.html#tutorials),
with short tasks and explicit questions. The introduction and clash exercise
start with the small public `sample_building.ifc` from the upstream
[`wall-with-opening-and-window.ifc`](https://github.com/compas-dev/compas_ifc/blob/main/data/wall-with-opening-and-window.ifc).
The sample has one wall, one window, and one storey. Its units are millimetres;
its normal clash count is zero. Exercises 1 and 2 instead start with the
instructor-supplied `Duplex_A_20110907.ifc`, which has four storeys and uses
metres. Exercise 4 creates a two-wall model
with a known overlap. A clash result is a geometric observation, not an
engineering judgement.

## Student workflow

Click **Open the live notebook** on the website. Binder opens JupyterLab in a
temporary browser session; the first launch can take several minutes. Select a
cell and press **Shift + Enter**. Run from top to bottom, changing only lines
marked `# CHANGE` initially. The introductory notebook includes the requested
simple `%pip install compas_ifc` cell. Binder already installs its dependencies
from `binder/environment.yml`, including `compas_notebook` for the browser Viewer.

The upstream `compas_viewer` and `model.show()` launch a desktop Qt window and
are not used in Binder. The course instead sends COMPAS meshes computed from
`compas_ifc` elements to `compas_notebook.viewer.Viewer` inside JupyterLab.
Download edited IFC files before closing Binder. Use only public teaching
models on this public service.

## Add the larger class example

For another shareable IFC file, place it at the repository root. Add its filename to the
`models` list in `course.json` so the site build copies it into downloads and
`lesson.zip`. Change the marked `IFC_PATH` line in the relevant exercise
notebooks if it should become their default. Keep the small sample available as
the predictable fallback, especially for the first and fourth exercises.

Check its units, types, spatial structure, property sets, and geometry before
class. The exercises do not assume a larger file has walls, windows, authored
properties, or clashes; adjust the marked selection lines to match it.

## Build and verify

`python build_site.py` creates `site/index.html`, one reading page per exercise,
notebook downloads, model files, and `site/lesson.zip`. The builder uses only
the Python standard library and never executes notebook code. `course.json`
controls the notebook list and model downloads.

`python check_lesson.py` executes all non-Viewer Python cells in isolated
temporary folders against the bundled sample. Run it in an environment with
the versions from `binder/environment.yml`; it intentionally skips the `%pip`
cell and the two browser-only Viewer cells. GitHub Actions installs the course
dependencies, runs this check, builds the static pages, and deploys on `main`.

Before class, launch Binder once and visually check both Viewer cells in
JupyterLab. Verify the edited and extracted IFC downloads and the clash count.
The site is hosted on GitHub Pages; Python executes only in Binder.
