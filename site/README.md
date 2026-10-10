# ifc.io: learn to work with IFC objects

A beginner Jupyter lesson for bachelor students: understand IFC information,
select an object, rename it, save a new IFC, and reopen it to check the change.
An optional section inspects the file and exports a smaller IFC. Allow about
45–60 minutes.

## Student access: browser only

Open the course website and choose **Open the live notebook on Binder**. Binder
starts a hosted Python session with the package and sample IFC; students need
only a web browser. It may take several minutes to build or start. Run cells
from top to bottom with **Shift + Enter**. The `%pip install compas_ifc` cell
is kept for portability; Binder already installs the package while building
the session.

Binder sessions are temporary. Download the edited IFC and exercise record
from JupyterLab before leaving. Use only the public teaching sample on this
public service; do not upload restricted building models.

The lesson includes `sample_building.ifc`, copied from the COMPAS IFC repository's
[`wall-with-opening-and-window.ifc`](https://github.com/compas-dev/compas_ifc/blob/main/data/wall-with-opening-and-window.ifc).
It contains one wall, one window, and a storey. The default `IFC_PATH` points
to this sample; an instructor can later provide another shareable model.
The core lesson ends at the checked name edit and exercise record; section 7
is optional.

Existing IFC outputs are protected. For another run, change output filenames
or deliberately remove previous exercise outputs in the hosted session.

## Build and publish the reading page

Run `python build_site.py` and open `site/index.html` to preview. The build uses
Python's standard library, does not execute cells, and omits notebook outputs.
It creates navigation, notebook and sample IFC downloads, and `lesson.zip` with
the notebook, sample IFC, and this README.

The reading page is static GitHub Pages. Its **Open the live notebook on Binder**
link launches the same notebook on mybinder.org, where Python actually runs.
The `binder/environment.yml` file defines Python 3.12 and the tested major
packages for that hosted session. Binder needs this repository to be public.
The current repository was not publicly reachable during this revision, so
the live Binder launch can be tested only after it is published publicly.

The included `.github/workflows/pages.yml` builds and deploys on `main`. In the
repository's Pages settings, choose **GitHub Actions** as the source.
Custom-domain configuration for `ifc.io` is a separate repository/domain-owner
step. This revision does not publish the site or configure DNS.

## Instructor preparation and evidence

Before class:

- Make the course repository public and launch the Binder link once to build
  its image. Check launch time and the notebook's selected kernel.
- Run the lesson on the bundled sample in Binder and record package versions.
- Check the reopened name, GlobalId, and class; inspect the output in an IFC
  application if available.
- Run the optional IFC subset export if you plan to teach it.
- Check that students can download the edited IFC and exercise record.

The revision used COMPAS Brain MCP's IFC skill, cookbook, and workflows, plus
upstream source for the name setter and save/reopen API. The core lesson was
executed with the included sample using Python 3.12.13, COMPAS 2.15.1, and
`compas_ifc` 2.1.0 in the `compas_work` environment on Windows. The optional
IFC subset export also passed on the sample. The public Binder session still
needs a live check after the repository is public.

References:

- [COMPAS IFC source](https://github.com/compas-dev/compas_ifc)
- [BuildingInformationModel API](https://compas.dev/compas_ifc/2.1.0/api/generated/compas_ifc.bim.BuildingInformationModel.html)
- [CLI documentation](https://compas.dev/compas_ifc/latest/cli.html)
