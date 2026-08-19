// Add/edit clip composer. The form HTML is rendered by grid.js (addFormHtml).
// Work/lane inherit from the previous-in-time annotated marker, then the last
// saved chapter. Empty existing values fall through to inherit so Enter on a
// marker still fills the chapter. Edit uses the same form as add.
import { $, missId, feedbackWhy, withWhy, resolvedLabel, extractedList } from "./util.js";
import { S, setSave, rememberChapter } from "./state.js";
import { api, saveFailed } from "./api.js";
import { seek, getCurrentTime } from "./player.js";
import { renderGrid, updateStats, scrollToActive, displayMarkers, buildRows, rowKey } from "./grid.js";
import { cancelPendingAddition, cancelPendingMarker, persist } from "./persist.js";

function inheritChapter(start) {
  const markers = displayMarkers()
    .filter((m) => Number(m.start) < Number(start) && (m.work || m.lane))
    .sort((a, b) => a.start - b.start);
  const prev = markers[markers.length - 1];
  if (prev) return { work: prev.work || "", lane: prev.lane || "" };
  return { work: S.lastChapter.work || "", lane: S.lastChapter.lane || "" };
}

function selectMarkerRow(marker) {
  S.followPinned = true;
  S.activeIndex = marker.index;
  S.selectedStart = Number(marker.start);
  const rows = buildRows();
  const i = rows.findIndex((r) => r.markers.some((m) => String(m.index) === String(marker.index)));
  S.selectedKey = i >= 0 ? rowKey(rows[i]) : null;
}

export function openComposer(start, fromGap, cueText, gapBefore, extractedLabel) {
  const existing = S.additions.find((m) => Number(m.start) === Number(start));
  const extracted = extractedList(S.current && S.current.run);
  const fallback = resolvedLabel(extracted, start, "") || (extractedLabel || "").trim() || (cueText || "").trim();
  const inherited = inheritChapter(start);
  S.composer = {
    mode: existing ? "edit" : "add",
    source: "miss",
    index: null,
    start: Number(start),
    fromGap: Boolean(fromGap),
    cueText: cueText || "",
    gapBefore: gapBefore === "" || gapBefore == null ? null : Number(gapBefore),
    tags: existing ? (existing.tags || []) : (fromGap ? ["take"] : []),
    lane: (existing && existing.lane) || inherited.lane,
    work: (existing && existing.work) || inherited.work,
    label: existing ? resolvedLabel(extracted, start, existing.description) : fallback,
    why: existing ? existing.why : "",
  };
  S.followPinned = true;
  seek(Number(start));
  renderGrid();
}

export function openEditor(marker) {
  if (!marker) return;
  const addition = marker.source === "miss"
    ? S.additions.find((m) => Number(m.start) === Number(marker.start))
    : null;
  const inherited = inheritChapter(marker.start);
  S.composer = {
    mode: "edit",
    source: marker.source,
    index: marker.source === "model" ? marker.index : null,
    start: Number(marker.start),
    fromGap: false,
    cueText: addition ? (addition.cueText || "") : "",
    gapBefore: addition ? addition.gapBefore : null,
    tags: [...(marker.tags || [])],
    lane: (marker.lane || "").trim() || inherited.lane,
    work: (marker.work || "").trim() || inherited.work,
    label: resolvedLabel(extractedList(S.current && S.current.run), marker.start, marker.description || ""),
    why: addition
      ? (addition.why || "")
      : feedbackWhy((S.current.feedback || {})[String(marker.index)] || ""),
  };
  selectMarkerRow(marker);
  seek(Number(marker.start));
  renderGrid();
}

export function readComposerFields() {
  if (!S.composer) return;
  if ($("miss-label")) S.composer.label = $("miss-label").value;
  if ($("miss-lane")) S.composer.lane = $("miss-lane").value;
  if ($("miss-work")) S.composer.work = $("miss-work").value;
  if ($("miss-why")) S.composer.why = $("miss-why").value;
}

async function submitModelEdit(description, tags, lane, work, why) {
  const index = Number(S.composer.index);
  cancelPendingMarker(index);
  setSave("saving…");
  try {
    const relabel = await api("/api/relabel", "PUT", {
      runId: S.currentId, index, description,
    });
    S.edits = relabel.edits || S.edits;
    S.current.edits = S.edits;
    const ann = await api("/api/annotate", "PUT", {
      runId: S.currentId, index, tags, lane, work,
    });
    S.annotations = ann.annotations || S.annotations;
    S.current.annotations = S.annotations;
    const cur = (S.current.feedback || {})[String(index)] || "";
    await persist(index, withWhy(cur, why));
  } catch (err) {
    saveFailed(err);
    return;
  }
  S.composer = null;
  S.activeIndex = index;
  setSave("saved");
  renderGrid();
  updateStats();
  scrollToActive();
}

export async function submitComposer() {
  if (!S.composer) return;
  readComposerFields();
  const description = (S.composer.label || "").trim();
  const why = (S.composer.why || "").trim();
  const lane = (S.composer.lane || "").trim();
  const work = (S.composer.work || "").trim();
  const tags = S.composer.tags || [];
  if (!description) {
    const label = $("miss-label");
    if (label) {
      label.classList.add("needed");
      label.focus();
    }
    return;
  }
  rememberChapter(lane, work);
  if (S.composer.mode === "edit" && S.composer.source === "model") {
    await submitModelEdit(description, tags, lane, work, why);
    return;
  }
  const start = S.composer.start;
  cancelPendingAddition(start);
  setSave("saving…");
  let res;
  try {
    res = await api("/api/miss", "PUT", {
      runId: S.currentId, start, description, why, tags, lane, work,
      cueText: S.composer.cueText, gapBefore: S.composer.gapBefore,
    });
  } catch (err) {
    saveFailed(err);
    return; // composer stays open so nothing typed is lost
  }
  S.additions = res.additions || [];
  S.current.additions = S.additions;
  S.composer = null;
  S.activeIndex = missId(start);
  setSave("saved");
  renderGrid();
  updateStats();
  scrollToActive();
}

// Enter on the grid: submit an open composer, open the editor on a row that
// already has a marker, or open the add form for a bare caption/extracted row.
export function onEnter() {
  if (S.composer) {
    submitComposer();
    return;
  }
  const row = document.querySelector("tr.playhead") || document.querySelector("tr.selected");
  if (!row) return;
  const raw = (row.dataset.markers || "").split(",").filter(Boolean)[0];
  if (raw) {
    const m = displayMarkers().find((x) => String(x.index) === String(raw));
    if (m) {
      openEditor(m);
      return;
    }
  }
  const caption = row.dataset.addText || "";
  const extracted = row.dataset.addExtracted || "";
  openComposer(row.dataset.addStart, row.dataset.addGap === "1", caption, row.dataset.addGapbefore, extracted);
}

// Tab then y: jump to Why. If the composer is open, focus the field; if the
// row already has an in-grid note (eval or reject reason), focus that;
// otherwise open the editor on the selected marker.
export function editWhy() {
  if (S.composer) {
    const el = $("miss-why");
    if (el) el.focus();
    return;
  }
  const row = document.querySelector("tr.selected") || document.querySelector("tr.playhead");
  if (!row) return;
  const inline = row.querySelector("input[data-wrong-reason], input[data-i]");
  if (inline) {
    inline.focus();
    return;
  }
  S.pendingWhy = true;
  const raw = (row.dataset.markers || "").split(",").filter(Boolean)[0];
  if (raw) {
    const m = displayMarkers().find((x) => String(x.index) === String(raw));
    if (m) {
      openEditor(m);
      return;
    }
  }
  openComposer(
    row.dataset.addStart,
    row.dataset.addGap === "1",
    row.dataset.addText || "",
    row.dataset.addGapbefore,
    row.dataset.addExtracted || "",
  );
}

// `n`: open the add form at the current playhead, rounded to the second.
// This is the only way to create a clip in a run with no transcript and no
// markers — there is no row to press Enter on. openComposer pauses on the way
// in, which is what you want before typing a label.
export function addAtPlayhead() {
  if (!S.current) return;
  const t = Math.max(0, Math.round(getCurrentTime()));
  openComposer(t, false, "", null, "");
}
