# Learn `compas_ifc` and `compas_viewer`

This small Jupyter lesson takes students from an IFC file to a filtered COMPAS
mesh and a detached `compas_viewer` window.

## Before starting

Create or activate an environment that contains the packages you want to use:

- `compas_ifc`
- `compas`
- `compas_viewer`
- Jupyter

Dependency installation is intentionally not performed by this deliverable.
Place an IFC file named `building.ifc` beside the notebook, or change
`IFC_PATH` in the first code cell.

## Run the lesson

1. Start Jupyter with this folder as the working directory, then open
   `compas_ifc_compas_viewer_intro.ipynb`.
2. Run the cells from top to bottom.
3. The notebook first inspects the IFC file with the `compas_ifc` CLI.
4. It then uses `BuildingInformationModel` to query elements and property sets.
5. It exports a filtered element class to OBJ, converts it to a COMPAS `Mesh`,
   and serializes that mesh for the viewer.
6. The final cell starts `viewer_detached.py` in a separate process.

`compas_viewer` opens a desktop Qt window. It needs a display and its
`Viewer.show()` call blocks, so the lesson deliberately launches it separately.
If the viewer cannot start, continue with the inspection and mesh-count cells;
those do not require a viewer window.

## Publish a static `github.io` lesson

This folder includes `build_site.py` and `.github/workflows/pages.yml` for a
view-only GitHub Pages site. The converter uses only the Python standard
library, does not execute notebook cells, drops notebook outputs, escapes code
and Markdown, and emits a restrictive Content Security Policy with no scripts.

To publish it:

1. Create a dedicated GitHub repository for the lesson.
2. Copy the contents of this folder into the repository root. The workflow must
   be at `.github/workflows/pages.yml`.
3. Push the `main` branch.
4. In the repository settings, set Pages → Source to **GitHub Actions**.

The workflow uses the official GitHub Pages actions, grants read-only contents
access to the build job, and grants Pages deployment permissions only to the
deployment job. It deploys only the default branch.

The resulting page lets students read and copy the lesson code, but it cannot
run Python or `compas_viewer` in the browser. Do not commit proprietary IFC
files, access tokens, API keys, or student data. If students must execute cells,
use a separately secured JupyterHub or other managed notebook service; do not
add an upload endpoint or server-side execution to this static site.

For a local preview, run `python build_site.py` and open `site/index.html`.

## Suggested student exercises

- Change `ELEMENT_TYPE` from `IfcWall` to `IfcWindow`, `IfcDoor`, or `IfcSlab`.
- Change the `--limit` value in the listing cell and compare the result.
- Add a `--where` predicate to a CLI query.
- Inspect the first element's `property_sets` and explain what is IFC data and
  what is COMPAS geometry.
- Change the viewer colours using `Color.from_hex(...)`.

## Evidence boundary

This notebook is a teaching scaffold. It was not run against a real IFC file in
this workspace, and no package installation or viewer launch was performed.
Package and API guidance is based on the local COMPAS Brain sources, whose
relevant claims are recorded as `declared` or `unknown`, not as verified
execution results.
