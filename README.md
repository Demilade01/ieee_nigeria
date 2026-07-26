# Flood Operations Dashboard — Lokoja, Kogi State

A static, GitHub-Pages-ready situational dashboard for flood disaster
management, built around the Niger/Benue confluence at Lokoja, Kogi State —
Nigeria's most flood-exposed city (major flood events in 2012 and 2022).

**Layout**
- Top-left: pre-flood satellite reference view (small panel)
- Below it: rainfall-intensity panel over the area of interest
- Main panel: operations map — road network, flood extent overlay, and
  field volunteer status points (good = blue, bad = red)
- Header: live telemetry strip (active volunteers, alerts, this hour's
  rainfall, cumulative rainfall, current frame)
- **Refresh button**, bottom-right of the main map panel: steps all three
  panels forward together through a pre-rendered image sequence (a
  disaster-progression storyline, baseline → storm → flood peak → recede).
  Pressing the `R` key does the same thing.

## How this works

Each panel displays one image from its own folder under `images/`. There is
no live map/chart library and no network calls at runtime except for the
static images and JSON files in this repo — everything renders from
pre-generated frames, which suits both GitHub Pages hosting and
low-bandwidth/field deployment.

```
images/ref-map/01.png … 03.png    (3-frame sequence)
images/precip/01.png … 08.png     (8-frame sequence)
images/main-map/01.png … 08.png   (8-frame sequence)
data/manifest.json                (frame counts + per-frame stats, read by js/app.js)
```

Each press of **Refresh** advances a shared step counter. Panels with
different frame counts loop independently (e.g. the 3-frame reference panel
wraps every 3 presses while the 8-frame main map and rainfall panels wrap
every 8), so all three stay visually in sync over a full cycle. The header
telemetry strip and captions update from `data/manifest.json`'s per-frame
`stats` on every press.

## What's real vs. placeholder in this build

| Element | Status | Notes |
|---|---|---|
| Location / coordinates | **Real** | Lokoja, Kogi State and its constituent localities (Adankolo, Ganaja, Felele, Cement, etc.) at their actual approximate positions |
| River/road geometry | **Illustrative schematic** | Stylised, not traced from survey data — see `generate_frames.py` |
| Pre-flood reference imagery (NIGCOMSAT) | **Placeholder** | Schematic render standing in for a real NIGCOMSAT scene/tile feed |
| Rainfall intensity (ECMWF) | **Placeholder** | Synthetic spatial field, structured so a real forecast can drive the same frame-generation approach |
| Flood extent (Sentinel) | **Placeholder** | Illustrative polygon, not derived from actual SAR analysis |
| Volunteer status points (NEMA) | **Placeholder** | Illustrative points; also shipped separately as `data/volunteer_points.geojson` in case you want to build a live/interactive version later |

## Regenerating or replacing the image sequences

The included `generate_frames.py` (Python, needs `matplotlib` + `numpy`)
produces every image in `images/` plus `data/manifest.json` from scratch —
run `python3 generate_frames.py` to regenerate them, e.g. after changing the
storyline, palette, or frame count.

To use **real imagery** instead of generated frames:
1. Drop your own numbered images (`01.png`, `02.png`, ...) into the relevant
   `images/<panel>/` folder — filenames just need to sort in the order you
   want them stepped through.
2. Update `data/manifest.json`'s `panels.<panel>.count` to match how many
   files you added, and adjust `stats`/`labels` to describe each frame.
3. No changes to `js/app.js` are needed — it reads frame counts and stats
   from the manifest rather than hardcoding them.

Real sources to pull frames from: NIGCOMSAT scene exports for the reference
panel; the free, keyless [Open-Meteo API](https://open-meteo.com/) (serves
real ECMWF IFS forecasts) rendered to an image per hour for the rainfall
panel; Sentinel-1/2 flood-extent exports from the
[Copernicus Emergency Management Service](https://emergency.copernicus.eu/)
or [Sentinel Hub](https://www.sentinel-hub.com/) composited onto a basemap
for the main panel; and NEMA field-report exports for volunteer status.

## Deploying to GitHub Pages

1. Create a new GitHub repository and push this folder's contents to it
   (root of the repo, or a `/docs` folder — either works).
2. In the repo, go to **Settings → Pages**.
3. Under "Build and deployment", set **Source: Deploy from a branch**, pick
   your branch (e.g. `main`) and folder (`/` or `/docs`), then **Save**.
4. GitHub will publish the site at `https://<your-username>.github.io/<repo-name>/`
   within a minute or two.

No build step is required — this is plain HTML/CSS/JS plus static images
and JSON.

## Local development

Because the dashboard loads `data/manifest.json` via `fetch()`, opening
`index.html` directly (`file://`) will fail due to browser CORS
restrictions. Serve it locally instead:
```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

## File structure
```
index.html
css/style.css
js/app.js
generate_frames.py
data/manifest.json
data/precipitation.json          (kept for reference / future live use)
data/flood_extent.geojson        (kept for reference / future live use)
data/volunteer_points.geojson    (kept for reference / future live use)
images/ref-map/   01.png..03.png
images/precip/    01.png..08.png
images/main-map/  01.png..08.png
```

