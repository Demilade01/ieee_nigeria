/* ==========================================================
   Lokoja Flood Operations Dashboard
   Image-sequence stepper (no live map/chart libraries; see
   generate_frames.py / README.md for how each panel's frame
   sequence is produced and how to swap in live feeds).
   ========================================================== */

const els = {
  refImg: document.getElementById('refMapImg'),
  precipImg: document.getElementById('precipImg'),
  mainImg: document.getElementById('mainMapImg'),
  mainCaption: document.getElementById('main-caption'),
  refCaption: document.getElementById('ref-caption'),
  precipSummary: document.getElementById('precip-summary'),
  refreshBtn: document.getElementById('refreshBtn'),
  tmVolunteers: document.getElementById('tm-volunteers'),
  tmAlerts: document.getElementById('tm-alerts'),
  tmAlertsItem: document.getElementById('tm-alerts-item'),
  tmPeakRain: document.getElementById('tm-peak-rain'),
  tmFloodArea: document.getElementById('tm-flood-area'),
  tmSync: document.getElementById('tm-sync'),
};

let manifest = null;
let step = 0; // global "press count" -- each panel maps this onto its own frame count

function pad(n) { return String(n).padStart(2, '0'); }

function frameSrc(panelKey, globalStep) {
  const panel = manifest.panels[panelKey];
  const idx = (globalStep % panel.count) + 1; // 1-based filenames, loops per-panel
  return `${panel.folder}/${pad(idx)}.${panel.ext}`;
}

function render() {
  if (!manifest) return;

  const mainFrameIdx = step % manifest.panels.mainMap.count; // 0-based, drives shared stats
  const stats = manifest.stats[mainFrameIdx];

  els.refImg.src = frameSrc('refMap', step);
  els.precipImg.src = frameSrc('precip', step);
  els.mainImg.src = frameSrc('mainMap', step);

  els.mainCaption.textContent = stats.label;
  els.precipSummary.textContent =
    `Frame ${mainFrameIdx + 1} of ${manifest.frameCount} \u2014 ${stats.rain_mm_h.toFixed(1)} mm/h this hour, ${stats.cum_rain_mm} mm cumulative.`;
  els.refCaption.textContent =
    `Baseline imagery captured before onset of flooding (reference frame ${(step % manifest.panels.refMap.count) + 1} of ${manifest.panels.refMap.count}).`;

  els.tmVolunteers.textContent = stats.good + stats.bad;
  els.tmAlerts.textContent = stats.bad;
  els.tmAlertsItem.classList.toggle('has-alerts', stats.bad > 0);
  els.tmPeakRain.textContent = `${stats.rain_mm_h.toFixed(1)} mm/h`;
  els.tmFloodArea.textContent = `${stats.cum_rain_mm} mm`;
  els.tmSync.textContent = `${mainFrameIdx + 1} / ${manifest.frameCount}`;
}

function advance() {
  step += 1;
  render();
  els.refreshBtn.classList.remove('spinning');
  // restart the CSS animation
  void els.refreshBtn.offsetWidth;
  els.refreshBtn.classList.add('spinning');
}

els.refreshBtn.addEventListener('click', advance);

// Optional: allow pressing the "R" key as a shortcut for the Refresh button
document.addEventListener('keydown', (e) => {
  if (e.key === 'r' || e.key === 'R') {
    if (!(e.target instanceof HTMLInputElement)) advance();
  }
});

fetch('data/manifest.json')
  .then((r) => r.json())
  .then((data) => {
    manifest = data;
    render();
  })
  .catch((err) => {
    console.error('Failed to load data/manifest.json:', err);
    els.mainCaption.textContent = 'Failed to load frame manifest -- see console.';
  });
