// The one shared mutable state object. Every cross-module read/write goes
// through S so "who owns this" has a single, greppable answer. State that only
// one module touches (player handle, suggest highlight, tab-prefix timer)
// stays module-local in its owner instead.
import { $, DEFAULT_FILLER, parseFillerList } from "./util.js";

export const EVAL_KEY = "yt-clipper-studio-eval-mode";
export const FOLLOW_KEY = "yt-clipper-studio-follow";
export const CURSOR_KEY = "yt-clipper-studio-cursor";
export const FILLER_KEY = "yt-clipper-studio-hide-filler";
export const FILLER_WORDS_KEY = "yt-clipper-studio-filler-words";
export const CHAPTER_KEY = "yt-clipper-studio-chapter";

export const S = {
  runs: [],
  currentId: null,
  current: null,
  additions: [],
  edits: {},
  annotations: {},
  activeIndex: null,
  selectedStart: null,
  selectedKey: null,
  composer: null,
  lastChapter: { lane: "", work: "" },
  runWork: "",
  liveTax: null,
  pendingCombo: null,
  pendingReason: null,
  pendingWhy: false,
  pendingScroll: false,
  showAllCues: true,
  hideFiller: true,
  fillerWords: DEFAULT_FILLER.slice(),
  fillerModal: false,
  evalMode: false,
  follow: true,
  followPinned: false,
  // Debounces are keyed by persistence record. Unrelated rows and event
  // streams must never cancel each other's pending writes.
  saveTimers: new Map(),
};

try { S.evalMode = localStorage.getItem(EVAL_KEY) === "1"; } catch (_) {}
try {
  const v = localStorage.getItem(FILLER_KEY);
  if (v === "0") S.hideFiller = false;
  else if (v === "1") S.hideFiller = true;
} catch (_) {}
try {
  const raw = localStorage.getItem(FILLER_WORDS_KEY);
  if (raw) {
    const words = parseFillerList(raw);
    if (words.length) S.fillerWords = words;
  }
} catch (_) {}
try {
  const v = localStorage.getItem(FOLLOW_KEY);
  if (v === "0") S.follow = false;
  else if (v === "1") S.follow = true;
} catch (_) {}

function readCursor() {
  try {
    return JSON.parse(localStorage.getItem(CURSOR_KEY) || "null") || { lastRunId: null, byRun: {} };
  } catch (_) {
    return { lastRunId: null, byRun: {} };
  }
}

export function lastRunId() {
  return readCursor().lastRunId || null;
}

export function cursorFor(runId) {
  if (!runId) return null;
  return readCursor().byRun[runId] || null;
}

export function rememberCursor() {
  if (!S.currentId) return;
  const data = readCursor();
  data.lastRunId = S.currentId;
  if (S.selectedKey != null && S.selectedStart != null) {
    data.byRun[S.currentId] = { key: S.selectedKey, start: Number(S.selectedStart) };
  }
  try { localStorage.setItem(CURSOR_KEY, JSON.stringify(data)); } catch (_) {}
}

function readChapters() {
  try {
    return JSON.parse(localStorage.getItem(CHAPTER_KEY) || "{}") || {};
  } catch (_) {
    return {};
  }
}

export function restoreChapter(runId) {
  const saved = runId ? readChapters()[runId] : null;
  S.lastChapter = {
    work: (saved && saved.work) || "",
    lane: (saved && saved.lane) || "",
  };
}

export function rememberChapter(lane, work) {
  lane = (lane || "").trim();
  work = (work || "").trim();
  if (lane) S.lastChapter.lane = lane;
  if (work) S.lastChapter.work = work;
  if (!S.currentId) return;
  const all = readChapters();
  all[S.currentId] = { work: S.lastChapter.work, lane: S.lastChapter.lane };
  try { localStorage.setItem(CHAPTER_KEY, JSON.stringify(all)); } catch (_) {}
}

// After a refresh with no saved chapter, pick the latest-in-time annotated
// marker so the first new clip of the session still inherits something.
export function seedChapterFromRun() {
  if (S.lastChapter.work || S.lastChapter.lane || !S.current) return;
  let best = null;
  (S.current.run.markers || []).forEach((m, i) => {
    const ann = S.annotations[String(i)] || {};
    if (!(ann.work || ann.lane)) return;
    if (!best || Number(m.start) >= Number(best.start)) {
      best = { start: m.start, work: ann.work || "", lane: ann.lane || "" };
    }
  });
  (S.additions || []).forEach((m) => {
    if (!(m.work || m.lane)) return;
    if (!best || Number(m.start) >= Number(best.start)) {
      best = { start: m.start, work: m.work || "", lane: m.lane || "" };
    }
  });
  if (best) S.lastChapter = { work: best.work, lane: best.lane };
}

export function setSave(msg) { $("saveState").textContent = msg; }
