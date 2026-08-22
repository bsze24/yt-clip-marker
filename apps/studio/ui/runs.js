// Run list polling and run switching.
import { $, escapeHtml, escapeAttr, extractedList } from "./util.js";
import { S, setSave, rememberCursor, lastRunId, cursorFor, restoreChapter, seedChapterFromRun } from "./state.js";
import { api } from "./api.js";
import { renderGrid, updateStats } from "./grid.js";
import { loadVideo } from "./player.js";

let offline = false;
const UPLOAD_PREFIX = "upload:";

function uploadsAgeLabel() {
  const seconds = Number(S.uploadsAgeSeconds);
  if (!Number.isFinite(seconds) || seconds < 60) return "YouTube uploads · cached just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `YouTube uploads · cached ${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 48) return `YouTube uploads · cached ${hours}h ago`;
  return `YouTube uploads · cached ${Math.floor(hours / 24)}d ago`;
}

function showRunWarnings(payload, id) {
  const warnings = Array.isArray(payload.warnings) ? payload.warnings : [];
  const messages = warnings.map((warning) => warning && warning.message).filter(Boolean);
  // The deprecated-key fault is also derived straight from the payload, not
  // only from the API's warning list ([[D-023]]): a store fault must stay
  // visible even if the server failed to name it. Kept as its own check rather
  // than folded into the loop above for that reason.
  const directFault = payload.run && Object.prototype.hasOwnProperty.call(payload.run, "gold");
  if (directFault && !warnings.some((warning) => warning && warning.code === "deprecated-run-key")) {
    messages.unshift(`run ${id} has deprecated gold[]; rename gold[] → extracted[]`);
  }
  const message = messages.join(" · ");
  const el = $("runWarning");
  el.textContent = message;
  el.hidden = !message;
  if (message) console.error(message);
}

export function renderRunSelect() {
  const select = $("runSelect");
  const prev = select.value;
  const runOptions = S.runs.map((r) => {
    const offlineMark = r.hasMedia ? "⏏ " : "";
    const label = S.evalMode
      ? `${offlineMark}${r.title} · ${r.markerCount} markers · ${r.checkCount} check`
      : `${offlineMark}${r.title} · ${r.markerCount} markers · ${r.missCount} added`;
    return `<option value="${escapeAttr(r.id)}">${escapeHtml(label)}</option>`;
  }).join("");
  const runIds = new Set(S.runs.map((r) => r.youtubeId).filter(Boolean));
  const uploadOptions = S.uploads
    .filter((upload) => upload && !runIds.has(upload.id))
    .map((upload) => {
      const value = UPLOAD_PREFIX + escapeAttr(upload.id);
      return `<option value="${value}">${escapeHtml(upload.title || upload.id)}</option>`;
    })
    .join("");
  select.innerHTML =
    (runOptions ? `<optgroup label="Runs">${runOptions}</optgroup>` : "") +
    (uploadOptions ? `<optgroup label="${escapeAttr(uploadsAgeLabel())}">${uploadOptions}</optgroup>` : "");
  if (S.currentId && S.runs.some((r) => r.id === S.currentId)) select.value = S.currentId;
  else if (prev && S.runs.some((r) => r.id === prev)) select.value = prev;
  else if (S.runs.length) select.value = S.runs[0].id;
  else select.selectedIndex = -1;
}

export async function refreshRuns() {
  // Both calls only read local files. Keep them independent: the optional
  // uploads cache must never prevent runs from rendering or erase its last
  // good in-memory value when that endpoint fails.
  const [runsResult, uploadsResult] = await Promise.allSettled([
    api("/api/runs", "GET"),
    api("/api/uploads", "GET"),
  ]);
  if (uploadsResult.status === "fulfilled" && Array.isArray(uploadsResult.value.items)) {
    S.uploads = uploadsResult.value.items;
    S.uploadsAgeSeconds = uploadsResult.value.ageSeconds;
  }
  if (runsResult.status === "rejected") {
    if (!offline) {
      offline = true;
      setSave("server unreachable");
    }
    return;
  }
  S.runs = runsResult.value;
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

export function chooseRunOrUpload(value) {
  if (!value.startsWith(UPLOAD_PREFIX)) {
    return openRun(value);
  }
  const videoId = value.slice(UPLOAD_PREFIX.length);
  if (!/^[A-Za-z0-9_-]{11}$/.test(videoId)) return Promise.resolve();
  $("ingestUrl").value = `https://www.youtube.com/watch?v=${videoId}`;
  $("ingestUrl").focus();
  renderRunSelect();
  return Promise.resolve();
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
    showRunWarnings({ run: null, warnings: [] }, id);
    return;
  }
  showRunWarnings(S.current, id);
  S.additions = S.current.additions || [];
  S.edits = S.current.edits || {};
  S.annotations = S.current.annotations || {};
  S.sections = S.current.sections || [];
  const wf = document.getElementById("runWork");
  if (wf) wf.value = (S.sections.find(([at]) => at === 0) || [0, "", ""])[1];
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
  const extractedN = extractedList(run).length;
  // A local run has no watch URL, and an empty href would link to this page.
  const idHtml = run.url
    ? `<a href="${escapeAttr(run.url)}" target="_blank" rel="noreferrer">${escapeHtml(run.videoId || "")}</a>`
    : escapeHtml(run.videoId || "");
  const media = S.current.media || null;
  const sourceHtml = media
    ? ` · <span class="src-local" title="${escapeAttr(media.name)}">local file</span>`
    : "";
  $("meta").innerHTML = `<div>${escapeHtml(run.title || id)}</div><div>${idHtml}${sourceHtml} · ${(run.markers || []).length} markers · ${S.additions.length} added · ${extractedN} YT desc · ${(run.cues || []).length} cues</div>`;
  // The run's `videoId` may be a filename-derived local identity. Only the
  // server-resolved YouTube id is safe to hand to the embed; a local-only run
  // with missing media should stay empty and show its warning, not cue a
  // synthetic id and misleadingly render "video unavailable".
  loadVideo(S.current.youtubeId || null, S.selectedStart, media);
  renderGrid();
  updateStats();
}
