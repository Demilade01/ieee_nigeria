"""
Generates three synchronized 8-frame image sequences (a disaster-progression
storyline) for the flood dashboard's three panels:
  images/ref-map/01.png .. 03.png   (pre-flood reference, 3 frames)
  images/precip/01.png .. 08.png    (spatial rainfall intensity, 8 frames)
  images/main-map/01.png .. 08.png  (roads + flood extent + volunteers, 8 frames)

These are clearly-styled SCHEMATIC renders (not real satellite/radar imagery)
consistent with the dashboard's dark ops-room theme, honestly representing
illustrative/placeholder data as documented in the README.

Run with:  python3 generate_frames.py
Requires:  matplotlib, numpy  (pip install matplotlib numpy)
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.path import Path
import matplotlib.patheffects as pe
import numpy as np
import json
import random
import math
import os

random.seed(11)
np.random.seed(11)

# ---------------- shared palette (matches css tokens) ----------------
BG        = "#0B1220"
SURFACE   = "#131C2E"
SURFACE2  = "#1B2740"
LINE      = "#2A3752"
INK       = "#E9EEF7"
INK_DIM   = "#8B97B3"
AMBER     = "#F2A93B"
GOOD      = "#3EA1F2"
BAD       = "#E5484D"
WATER     = "#2FD4C4"

# ---------------- shared AOI extent (degrees) ----------------
LON_MIN, LON_MAX = 6.675, 6.775
LAT_MIN, LAT_MAX = 7.735, 7.835

FRAME_LABELS = [
    "Day 0, 06:00 -- Baseline",
    "Day 0, 18:00 -- Rain onset",
    "Day 1, 06:00 -- Storm 1 peak",
    "Day 1, 18:00 -- River rising",
    "Day 2, 06:00 -- Storm 2 building",
    "Day 2, 18:00 -- Storm 2 peak (flood trigger)",
    "Day 3, 06:00 -- Peak inundation",
    "Day 3, 18:00 -- Waters receding",
]
N_FRAMES = len(FRAME_LABELS)

NEIGHBOURHOODS = [
    ("Lokoja Town Centre", 7.7999, 6.7337),
    ("Adankolo", 7.7825, 6.7365),
    ("Ganaja", 7.8035, 6.7085),
    ("Felele", 7.8155, 6.7455),
    ("Cement / Ajaokuta Rd", 7.7530, 6.7005),
    ("Otokiti", 7.7965, 6.7405),
    ("Lokongoma", 7.7735, 6.7275),
    ("Zango", 7.8080, 6.7300),
    ("Kabawa", 7.7910, 6.7460),
    ("Gadumo", 7.7690, 6.7150),
    ("Sarkin Noma", 7.8145, 6.7215),
    ("Ganaja Junction", 7.8005, 6.7215),
    ("Phase II", 7.7880, 6.7195),
    ("Bishop Dele Rd", 7.8020, 6.7395),
    ("Ndanaku waterfront", 7.7855, 6.7300),
    ("Court Road", 7.7955, 6.7360),
]

def style_axes(ax, title, tag, badge_color=AMBER):
    ax.set_facecolor(SURFACE2)
    ax.set_xlim(LON_MIN, LON_MAX)
    ax.set_ylim(LAT_MIN, LAT_MAX)
    ax.set_aspect(1 / math.cos(math.radians((LAT_MIN + LAT_MAX) / 2)))
    for spine in ax.spines.values():
        spine.set_color(LINE)
    ax.tick_params(colors=INK_DIM, labelsize=7)
    ax.grid(True, color=LINE, linewidth=0.5, alpha=0.5)
    ax.set_axisbelow(True)
    ax.text(0.015, 0.975, title, transform=ax.transAxes, ha='left', va='top',
            fontsize=12, fontweight='bold', color=INK, family='monospace',
            path_effects=[pe.withStroke(linewidth=3, foreground=SURFACE2)])
    ax.text(0.985, 0.975, tag, transform=ax.transAxes, ha='right', va='top',
            fontsize=8.5, color=badge_color, family='monospace',
            bbox=dict(boxstyle='round,pad=0.35', facecolor=SURFACE, edgecolor=badge_color, linewidth=1))

def draw_rivers(ax, lw_scale=1.0):
    niger = np.array([
        [6.700, 7.835], [6.706, 7.815], [6.712, 7.795], [6.718, 7.775],
        [6.724, 7.755], [6.728, 7.735],
    ])
    benue = np.array([
        [6.775, 7.760], [6.760, 7.758], [6.744, 7.752], [6.730, 7.745],
        [6.724, 7.740], [6.722, 7.736],
    ])
    lower = np.array([
        [6.722, 7.736], [6.715, 7.715], [6.705, 7.695], [6.695, 7.680],
    ])
    for arr, w in [(niger, 9), (benue, 8), (lower, 10)]:
        ax.plot(arr[:, 0], arr[:, 1], color=WATER, linewidth=w * lw_scale,
                solid_capstyle='round', alpha=0.85, zorder=2)
        ax.plot(arr[:, 0], arr[:, 1], color=WATER, linewidth=w * lw_scale * 2.2,
                solid_capstyle='round', alpha=0.12, zorder=1)

def draw_roads(ax):
    roads = [
        np.array([[6.680, 7.760], [6.705, 7.755], [6.724, 7.742], [6.735, 7.760],
                   [6.745, 7.790], [6.752, 7.820]]),
        np.array([[6.734, 7.741], [6.715, 7.725], [6.700, 7.705], [6.690, 7.685]]),
        np.array([[6.712, 7.775], [6.730, 7.782], [6.748, 7.778], [6.760, 7.765]]),
        np.array([[6.700, 7.800], [6.718, 7.805], [6.735, 7.800], [6.745, 7.790]]),
    ]
    for r in roads:
        ax.plot(r[:, 0], r[:, 1], color="#5B6C8F", linewidth=2.0, alpha=0.85, zorder=3)
        ax.plot(r[:, 0], r[:, 1], color="#8595B8", linewidth=0.6, alpha=0.9, zorder=3,
                linestyle=(0, (1, 2.2)))

def draw_labels(ax, fontsize=6.2):
    for name, lat, lon in NEIGHBOURHOODS:
        ax.plot(lon, lat, marker='.', markersize=2, color=INK_DIM, zorder=4)
        ax.text(lon + 0.0025, lat + 0.0015, name, fontsize=fontsize, color=INK_DIM,
                family='sans-serif', zorder=5,
                path_effects=[pe.withStroke(linewidth=2, foreground=SURFACE2)])

def flood_polygons(frame_idx):
    growth = [0.15, 0.35, 0.55, 0.75, 0.95, 1.15, 1.30, 1.10][frame_idx]
    cx, cy = 6.731, 7.742
    base_pts = []
    n = 22
    rng = np.random.default_rng(3)
    for i in range(n):
        ang = 2 * math.pi * i / n
        r = (0.016 + 0.006 * math.sin(3 * ang) + rng.uniform(-0.002, 0.002)) * growth
        base_pts.append((cx + r * math.cos(ang) * 1.3, cy + r * math.sin(ang)))
    base_pts.append(base_pts[0])
    return np.array(base_pts)

def draw_flood(ax, frame_idx):
    poly = flood_polygons(frame_idx)
    ax.fill(poly[:, 0], poly[:, 1], color=WATER, alpha=0.30, zorder=2.5)
    ax.plot(poly[:, 0], poly[:, 1], color=WATER, alpha=0.8, linewidth=1.3, zorder=2.6)

def volunteer_status(frame_idx):
    n = len(NEIGHBOURHOODS)
    rng = random.Random(5)
    bad_schedule = [0, 1, 2, 4, 6, 8, 6]
    bad_schedule.append(bad_schedule[-1])
    order = list(range(n))
    rng.shuffle(order)
    bad_count = bad_schedule[frame_idx]
    bad_set = set(order[:bad_count])
    return [("bad" if i in bad_set else "good") for i in range(n)]

def draw_volunteers(ax, frame_idx):
    statuses = volunteer_status(frame_idx)
    rng = random.Random(7)
    for (name, lat, lon), status in zip(NEIGHBOURHOODS, statuses):
        jlat = lat + rng.uniform(-0.004, 0.004)
        jlon = lon + rng.uniform(-0.004, 0.004)
        color = BAD if status == "bad" else GOOD
        ax.scatter([jlon], [jlat], s=70, color=color, edgecolor="white",
                   linewidth=1.1, zorder=6)
        if status == "bad":
            ax.scatter([jlon], [jlat], s=220, facecolor='none', edgecolor=BAD,
                       linewidth=1.2, alpha=0.55, zorder=5.5)
    return statuses

def add_compass_scale(ax):
    ax.annotate('N', xy=(0.955, 0.14), xytext=(0.955, 0.08), xycoords='axes fraction',
                ha='center', color=INK_DIM, fontsize=8, fontweight='bold',
                arrowprops=dict(arrowstyle='-|>', color=INK_DIM, lw=1.2))
    ax.plot([0.78, 0.90], [0.045, 0.045], transform=ax.transAxes, color=INK_DIM, lw=1.5)
    ax.text(0.84, 0.065, '2 km', transform=ax.transAxes, ha='center', fontsize=6.5, color=INK_DIM)

# ================================================================
# 1. PRE-FLOOD REFERENCE (3 frames, minimal change -- baseline scene)
# ================================================================
os.makedirs("images/ref-map", exist_ok=True)
ref_dates = ["12 Jun 2025", "19 Jul 2025", "03 Sep 2025"]
for i, d in enumerate(ref_dates):
    fig, ax = plt.subplots(figsize=(9, 5.6), dpi=140)
    fig.patch.set_facecolor(SURFACE2)
    draw_rivers(ax, lw_scale=1.0)
    draw_roads(ax)
    draw_labels(ax, fontsize=6.5)
    style_axes(ax, f"PRE-FLOOD REFERENCE", f"NIGCOMSAT (placeholder) \u2022 {d}", badge_color=INK_DIM)
    add_compass_scale(ax)
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    plt.tight_layout(pad=0.4)
    plt.savefig(f"images/ref-map/{i+1:02d}.png", facecolor=SURFACE2)
    plt.close(fig)
print("ref-map frames done")

# ================================================================
# 2. PRECIPITATION -- spatial rainfall intensity over AOI (8 frames)
# ================================================================
os.makedirs("images/precip", exist_ok=True)

frame_rain_mm = [1.2, 9.5, 4.0, 6.5, 18.0, 27.5, 12.0, 3.0]
cum_rain = np.array([22, 48, 61, 95, 168, 248, 296, 318])  # already-cumulative totals per frame

grid_n = 60
lon_grid = np.linspace(LON_MIN, LON_MAX, grid_n)
lat_grid = np.linspace(LAT_MIN, LAT_MAX, grid_n)
LONG, LATG = np.meshgrid(lon_grid, lat_grid)
storm_center = (6.735, 7.775)

for i, (mm, cum) in enumerate(zip(frame_rain_mm, cum_rain)):
    fig, ax = plt.subplots(figsize=(11.4, 5.6), dpi=140)
    fig.patch.set_facecolor(SURFACE2)

    drift_x = 0.01 * math.sin(i * 0.8)
    drift_y = 0.01 * math.cos(i * 0.6)
    cx, cy = storm_center[0] + drift_x, storm_center[1] + drift_y
    sigma = 0.028
    Z = mm * np.exp(-(((LONG - cx) ** 2 + (LATG - cy) ** 2) / (2 * sigma ** 2)))
    Z += 0.4 * mm * np.exp(-(((LONG - (cx - 0.03)) ** 2 + (LATG - (cy + 0.02)) ** 2) / (2 * (sigma*1.4) ** 2)))

    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        "precip", [SURFACE2, "#1E4E63", "#1D7A8C", GOOD, "#7FD9E8", "#FFFFFF"]
    )
    im = ax.pcolormesh(LONG, LATG, Z, cmap=cmap, shading='gouraud', vmin=0, vmax=30, zorder=1)
    draw_rivers(ax, lw_scale=0.6)
    draw_roads(ax)
    style_axes(ax, "RAINFALL INTENSITY", f"ECMWF (placeholder) \u2022 {FRAME_LABELS[i]}", badge_color=GOOD)
    add_compass_scale(ax)
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    cbar = fig.colorbar(im, ax=ax, shrink=0.75, pad=0.02)
    cbar.set_label("mm/h", color=INK_DIM, fontsize=8)
    cbar.ax.yaxis.set_tick_params(color=INK_DIM, labelsize=7)
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color=INK_DIM)
    cbar.outline.set_edgecolor(LINE)

    ax.text(0.015, 0.06, f"This hour: {mm:.1f} mm/h    Cumulative: {cum:d} mm",
            transform=ax.transAxes, fontsize=8.5, color=INK, family='monospace',
            path_effects=[pe.withStroke(linewidth=3, foreground=SURFACE2)])

    plt.tight_layout(pad=0.4)
    plt.savefig(f"images/precip/{i+1:02d}.png", facecolor=SURFACE2)
    plt.close(fig)
print("precip frames done")

# ================================================================
# 3. MAIN OPERATIONS MAP (8 frames: roads + growing flood + volunteers)
# ================================================================
os.makedirs("images/main-map", exist_ok=True)

frame_stats = []
for i in range(N_FRAMES):
    fig, ax = plt.subplots(figsize=(15.5, 9.6), dpi=140)
    fig.patch.set_facecolor(SURFACE2)

    draw_rivers(ax, lw_scale=1.2)
    draw_flood(ax, i)
    draw_roads(ax)
    draw_labels(ax, fontsize=7.5)
    statuses = draw_volunteers(ax, i)

    style_axes(ax, "LIVE OPERATIONS MAP", f"Roads: OSM \u2022 Flood: Sentinel (placeholder) \u2022 {FRAME_LABELS[i]}")
    add_compass_scale(ax)
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    good_n = statuses.count("good")
    bad_n = statuses.count("bad")
    frame_stats.append({"frame": i + 1, "label": FRAME_LABELS[i], "good": good_n, "bad": bad_n,
                         "rain_mm_h": frame_rain_mm[i], "cum_rain_mm": int(cum_rain[i])})

    ax.scatter([], [], s=70, color=GOOD, edgecolor='white', label='Good')
    ax.scatter([], [], s=70, color=BAD, edgecolor='white', label='Bad')
    ax.legend(loc='lower left', frameon=True, fontsize=8, labelcolor=INK,
              facecolor=SURFACE, edgecolor=LINE, framealpha=0.9)

    plt.tight_layout(pad=0.4)
    plt.savefig(f"images/main-map/{i+1:02d}.png", facecolor=SURFACE2)
    plt.close(fig)

print("main-map frames done")

# ---------------- manifest for the frontend ----------------
manifest = {
    "frameCount": N_FRAMES,
    "labels": FRAME_LABELS,
    "panels": {
        "refMap":  {"folder": "images/ref-map",  "count": 3,        "prefix": "", "ext": "png"},
        "precip":  {"folder": "images/precip",   "count": N_FRAMES, "prefix": "", "ext": "png"},
        "mainMap": {"folder": "images/main-map", "count": N_FRAMES, "prefix": "", "ext": "png"},
    },
    "stats": frame_stats,
}
with open("data/manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)

print("\nManifest written. Per-frame stats:")
for s in frame_stats:
    print(" ", s)
