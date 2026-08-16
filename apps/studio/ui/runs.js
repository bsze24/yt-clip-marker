// Run list polling and run switching.
import { $, escapeHtml, escapeAttr } from "./util.js";
import { S, setSave, rememberCursor, lastRunId, cursorFor, restoreChapter, seedChapterFromRun } from "./state.js";
import { api } from "./api.js";
import { renderGrid, updateStats } from "./grid.js";
import { loadVideo } from "./player.js";

let offline = false;

export function renderRunSelect() {
  const select = $("runSelect");
  const prev = select.value;
  select.innerHTML = S.runs.map((r) => {
    const label = S.evalMode
      ? `${r.title} · ${r.markerCount} markers · ${r.checkCount} check`
      : `${r.title} · ${r.markerCount} markers · ${r.missCount} added`;
    return `<option value="${escapeAttr(r.id)}">${escapeHtml(label)}</option>`;
  }).join("");
  if (S.currentId && S.runs.some((r) => r.id === S.currentId)) select.value = S.currentId;
  else if (prev && S.runs.some((r) => r.id === prev)) select.value = prev;
}

export async function refreshRuns() {
  try {
    S.runs = await api("/api/runs", "GET");
  } catch (err) {
    if (!offline) {
      offline = true;
      setSave("server unreachable");
    }
    return;
  }
  if (offline) {
    offline = false;
    setSave("saved");
  }
  renderRunSelect();
  $("empty").hidden = S.runs.length > 0;
  if (!S.runs.length) return;
  if (!S.currentId) {
    const last = lastRunId();
    const id = (last && S.runs.some((r) => r.id === last)) ? last : $("runSelect").value;
    await openRun(id);
  }
}

export async function openRun(id) {
  S.currentId = id;
  S.activeIndex = null;
  S.selectedStart = null;
  S.selectedKey = null;
  S.composer = null;
  try {
    S.current = await api("/api/run?id=" + encodeURIComponent(id), "GET");
  } catch (err) {
    console.error(err);
    S.current = null;
    S.currentId = null;
    $("meta").textContent = `could not load run ${id}: ${err.message}`;
    $("tbody").innerHTML = "";
    $("stats").textContent = "";
    return;
  }
  S.additions = S.current.additions || [];
  S.edits = S.current.edits || {};
  S.annotations = S.current.annotations || {};
  restoreChapter(id);
  seedChapterFromRun();
  const cur = cursorFor(id);
  if (cur) {
    S.selectedKey = cur.key || null;
    S.selectedStart = Number.isFinite(Number(cur.start)) ? Number(cur.start) : null;
    S.pendingScroll = true;
  }
  rememberCursor();
  const run = S.current.run;
  const goldN = (run.gold || []).length;
  $("meta").innerHTML = `<div>${escapeHtml(run.title || id)}</div><div><a href="${escapeAttr(run.url || "")}" target="_blank" rel="noreferrer">${escapeHtml(run.videoId || "")}</a> · ${(run.markers || []).length} markers · ${S.additions.length} added · ${goldN} YT desc · ${(run.cues || []).length} cues</div>`;
  loadVideo(run.videoId, S.selectedStart);
  renderGrid();
  updateStats();
}
