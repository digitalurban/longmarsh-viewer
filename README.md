# Longmarsh Data Centre/Solar Farm Viewer

An independent, interactive 3D map of the proposed **Longmarsh Green Energy** scheme in west Norfolk (PINS ref. EN0110048): solar panels, battery storage, the data centre campus, substations, overhead lines and underground cable routes. It is meant to help residents see where each element sits relative to their own home and village during the pre-application consultation (15 October to 26 November 2026).

It is a static site with no build step and no API keys, so it runs on GitHub Pages as it is. The basemap is **OpenStreetMap**, and an aerial view (Esri) is one click away.

## Published facts and presumptions

Every layer is marked with one of two labels:

- **Published**: shapes and figures taken directly from the applicant's documents. These are drawn as flat, solid colours.
- **Awaiting information**: presumptions the map makes because details haven't been published yet. These are drawn with **amber hatching** and are listed in the *Awaiting* tab, together with what the applicant says is still being developed and the paragraph references.

Click any shape to see its source and status.

## What residents can do

- **Map tab**: switch each layer on or off and fly to the Western Site (data centre), the Eastern Site or Walpole. In 3D every element is drawn at its maximum height from the Scoping Report.
- **Near me tab**: enter a postcode (looked up with postcodes.io), use your location, or tap the map. You get the distance to the nearest panels, the data centre, the substations and the overhead line, plus three views:
  - **Street View facing it**: opens Google Street View at that spot, pointing towards the nearest proposed structure. This shows today's view.
  - **Google Earth**: opens Google Earth Web at the same spot and heading.
  - **Stand here in 3D**: puts the camera at eye level in this map, with the proposed structures drawn in.
- **Villages tab**: 45 nearby villages, sorted by distance to the site boundary. Tap one to stand in it and look towards the scheme.
- **Facts tab**: the key numbers, heights, design commitments, timeline and how to respond.
- **Downloads**: a KML file to open in Google Earth (published zones plus presumed height envelopes, in separate folders), and the GeoJSON.

## Detailed Google Earth files (`google-earth/`)

- `longmarsh-infrastructure.kmz` contains:
  - published zone outlines;
  - fencing along presumed lines, drawn at the published heights (2.5 m wire mesh, 3 m palisade);
  - CCTV poles (5 m, spacing presumed);
  - lighting notes;
  - overhead line towers and conductors (heights published, positions presumed);
  - illustrative data-centre massing;
  - worst-case height envelopes.
- `longmarsh-panels-west.kmz` and `longmarsh-panels-east.kmz` contain about 28,000 3D solar tables. They're drawn to the report's parameters: 25° tilt, 0.8 m bottom edge, 4.5 m top edge, south facing, rows 3.5 m apart and 3.2 m inside the fence. The row layout itself is a presumption.

Open them in Google Earth Pro (File → Open), or in Google Earth Web (File → Open local KML file).

## Publish it on GitHub Pages

1. Create a new repository, for example `longmarsh-viewer`.
2. Upload everything in this folder (`index.html`, `data/`, `google-earth/`, `method/`, `README.md`), keeping the folder structure.
3. In the repository, go to **Settings → Pages**, set **Source** to *Deploy from a branch*, pick `main` and `/ (root)`, then save.
4. After a minute the site is live at `https://<your-username>.github.io/longmarsh-viewer/`.

To test it on your own machine first, run `python3 -m http.server` in this folder and open `http://localhost:8000`. The data is also bundled in `data/longmarsh-data.js`, so double-clicking `index.html` works too. OpenStreetMap may refuse map tiles requested from a `file://` page, though, so use the local server or GitHub Pages to check the basemap.

## Where the shapes come from

The red site boundary is the official order-limits file published on the Planning Inspectorate's project page. The other layers come from the developer's layout plan, as described below. The traced outline agrees with the official boundary to a median of about 4 m.

The scheme's layers were extracted from the vector drawing in **Scoping Report Appendix A, Figure 1-3: Layout Plan** (rev 01, 13/10/2026). They were not hand-digitised.

1. The coloured polygons (solar, data centre and BESS zone, substations, cable corridors, biodiversity area, access track) and the red site boundary were read straight from the PDF's vector paths with PyMuPDF.
2. The figures' Ordnance Survey basemaps carry the 1 km British National Grid. The grid lines were found by a periodic line search on the embedded raster (`method/grid4.py`). The basemap turns out to be rotated by 1.0° relative to the page. Grid lines were labelled using the printed northing numbers on Figure 1-2f. This gives an exact page-to-EPSG:27700 transform for each figure (`method/geo.py`).
3. As a check, Figure 1-2f (Eastern Site) and Figure 1-3 were georeferenced independently. Their boundaries agree to a median of **2.5 m**. Areas match the report: the Walpole substation area comes out at 43.4 ha against "approximately 43 ha", and the whole site at 1,978 ha against "approximately 1,980 ha". On Esri aerial imagery the boundary follows field edges and wraps the existing Walpole substation.
4. The overhead line centrelines come from skeletonising each corridor polygon. They measure 8.1 km (West) and 7.4 km (East), against about 8 km and 7 km in the report. **Tower positions are illustrative.** They are evenly spaced (about 350 m West, 300 m East) because no tower locations have been published.

Heights are the maximum parameters from Scoping Report §4.4 and the ZTV assumptions in §10.3 and §11.4:

| Element | Max height |
|---|---|
| Solar panels | 4.5 m |
| Data centre campus, Western 400 kV substation, BESS | 25 m (up to 10 buildings, ≤70 ha footprint) |
| Eastern substation and BESS | 8 m |
| Walpole substation works | 8 m |
| Western Cable Route overhead line | 50 m towers |
| Eastern Cable Route overhead line | 35 m towers |

## Disclaimer

This is an independent, unofficial and non-commercial visualisation. It is not produced or endorsed by EPL Norfolk Limited, Evolution Power, the Planning Inspectorate, the government or any council. It was compiled in a short time from documents published in October 2026 and may contain errors or omissions. The scheme and its documents will change.

Map shapes are approximate. Anything marked "awaiting information" is a presumption made for this viewer. Distances are approximate. The Objections and Respond content summarises published documents and policy; it is not legal, planning or other professional advice. Check everything against the original documents before relying on it. To the extent permitted by law, no responsibility is accepted for any loss or decision arising from its use.

## Caveats

- Ground is flat in the 3D views. Terrain isn't modelled, although the Fens are close to flat.

- The applicant calls the boundary and layout **indicative**. The detailed layout, screening and planting are still being designed and will change before the DCO application, which is expected in April 2027.
- The data centre zone is drawn as a single 25 m block, which is the worst-case envelope used for the visibility assessment. It is not a building design.
- The solar zone includes areas that will end up as access tracks, buffers and planting. Panels will sit at least 30 m from homes.
- Village distances are measured from the OpenStreetMap centre point of each village. Individual properties may be closer.
- This is not an official project product. For the authoritative documents, go to [longmarshgreenenergy.co.uk](https://longmarshgreenenergy.co.uk) and the Planning Inspectorate's project page.

## Credits

Aerial imagery © Esri, Maxar and Earthstar Geographics. Map tiles © OpenStreetMap contributors. Rendering uses MapLibre GL JS 4.7.1. Postcode lookup uses postcodes.io (Open Government Licence). The scheme geometry is derived from documents published by EPL Norfolk Limited and Logika Group for consultation.
