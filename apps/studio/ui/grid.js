// The time-aligned grid: row building, alignment, selection, rendering, stats.
// Selection is by row identity (rowKey), never start time alone — duplicate
// timestamps are real.
import { $, hms, fbClass, evalMark, isWrong, isCheck, feedbackWhy, isBackchannel, escapeHtml, escapeAttr, missId, MATCH, typingInField, resolvedLabel, extractedList } from "./util.js";
import { S, rememberCursor, FOLLOW_KEY } from "./state.js";
import { seek, scrubTo, keepKeysOnPage, isPlaying, getCurrentTime } from "./player.js";
import { renderSuggest, resetSuggestHi } from "./suggest.js";
import { renderTimeline } from "./timeline.js";

export function visibleRows() {
  return [...document.querySelectorAll("#tbody tr[data-start]")];
}

export function selectRowEl(row, { seekVideo = false } = {}) {
  if (!row) return;
  S.followPinned = true;
  S.selectedStart = Number(row.dataset.start);
  S.selectedKey = row.dataset.rowKey || "";
  rememberCursor();
  renderGrid();
  const el = document.querySelector("tr.selected");
  if (el) el.scrollIntoView({ block: "center" });
  if (seekVideo) scrubTo(S.selectedStart);
  else keepKeysOnPage();
}

function restoreSelection() {
  const rows = visibleRows();
  if (!rows.length) return;
  const el = rows.find((r) => r.dataset.rowKey === S.selectedKey)
    || rows.find((r) => Number(r.dataset.start) === Number(S.selectedStart))
    || rows[0];
  S.selectedStart = Number(el.dataset.start);
  S.selectedKey = el.dataset.rowKey || "";
  el.classList.add("selected");
}

// j/k origin: when follow is on, the playhead row (where the video is), not a
// pinned selection the video has already walked past. Follow-off (or no
// playhead yet) still walks from the selected row.
function navOriginIndex(rows) {
  if (S.follow) {
    const playhead = rows.findIndex((r) => r.classList.contains("playhead"));
    if (playhead >= 0) return playhead;
  }
  const selected = rows.findIndex((r) => r.classList.contains("selected"));
  return selected >= 0 ? selected : 0;
}

export function moveRow(delta) {
  if (S.composer) {
    S.composer = null;
    renderGrid();
  }
  const rows = visibleRows();
  if (!rows.length) return;
  const i = navOriginIndex(rows);
  const next = Math.max(0, Math.min(rows.length - 1, i + delta));
  selectRowEl(rows[next], { seekVideo: true });
}

// Shift+j/k: jump to the next/previous row that has a marker or added clip,
// skipping bare caption and extracted-only rows. data-markers is the row's
// marker-id list — empty string means none. Stays put if there is no
// populated row in that direction.
export function moveMarkerRow(delta) {
  if (S.composer) {
    S.composer = null;
    renderGrid();
  }
  const rows = visibleRows();
  if (!rows.length) return;
  const i = navOriginIndex(rows);
  for (let j = i + delta; j >= 0 && j < rows.length; j += delta) {
    if (rows[j].dataset.markers) {
      selectRowEl(rows[j], { seekVideo: true });
      return;
    }
  }
}

export function displayMarkers() {
  const extracted = extractedList(S.current.run);
  const model = (S.current.run.markers || []).map((m, index) => {
    const original = m.description || "";
    const edited = S.edits[String(index)];
    return {
      ...m, index, source: "model",
      originalDescription: original,
      description: resolvedLabel(extracted, m.start, edited || original),
      tags: (S.annotations[String(index)] || {}).tags || [],
      lane: (S.annotations[String(index)] || {}).lane || "",
      work: (S.annotations[String(index)] || {}).work || "",
      why: feedbackWhy((S.current.feedback || {})[String(index)] || ""),
    };
  });
  const added = S.additions.map((m) => ({
    start: m.start, end: m.end, kind: m.kind,
    description: resolvedLabel(extracted, m.start, m.description),
    rationale: m.why ? "MISS. " + m.why : "MISS.",
    index: missId(m.start), source: "miss",
    tags: m.tags || [],
    lane: m.lane || "",
    work: m.work || "",
    why: m.why || "",
  }));
  return model.concat(added);
}

// Exact start first, then the 2s window. Earliest-cue-wins used to park a
// 1:18:52 marker on the 1:18:50 caption, and an added clip 2s later on the
// marker's own caption — the time column then lied about who owned the row.
function takeAt(items, t, used, idFn, maxDelta) {
  const hit = [];
  items.forEach((item, i) => {
    const id = idFn(item, i);
    if (used.has(id)) return;
    if (Math.abs(Number(item.start) - t) <= maxDelta) {
      used.add(id);
      hit.push(item);
    }
  });
  return hit;
}

function takeExact(items, t, used, idFn) {
  return takeAt(items, t, used, idFn, 0);
}

function takeNear(items, t, used, idFn) {
  return takeAt(items, t, used, idFn, MATCH);
}

export function buildRows() {
  const cues = S.current.run.cues || [];
  const extracted = extractedList(S.current.run).map((item, i) => ({ ...item, eid: "e" + i }));
  const markers = displayMarkers();
  const usedM = new Set();
  const usedE = new Set();
  const rows = [];

  cues.forEach((cue, cueIndex) => {
    rows.push({
      rowId: `cue:${cueIndex}`,
      start: cue.start,
      caption: cue.text,
      gapBefore: cue.gapBefore || null,
      markers: takeExact(markers, cue.start, usedM, (m) => m.index),
      extracted: takeExact(extracted, cue.start, usedE, (item) => item.eid),
    });
  });
  const cueCount = rows.length;
  for (let i = 0; i < cueCount; i++) {
    rows[i].markers.push(...takeNear(markers, rows[i].start, usedM, (m) => m.index));
    rows[i].extracted.push(...takeNear(extracted, rows[i].start, usedE, (item) => item.eid));
  }

  extracted.forEach((item) => {
    if (usedE.has(item.eid)) return;
    rows.push({
      rowId: `extracted:${item.eid}`,
      start: item.start,
      caption: "",
      gapBefore: null,
      markers: takeNear(markers, item.start, usedM, (m) => m.index),
      extracted: [item],
    });
    usedE.add(item.eid);
  });

  markers.forEach((m) => {
    if (usedM.has(m.index)) return;
    rows.push({
      rowId: `marker:${String(m.index)}`,
      start: m.start,
      caption: "",
      gapBefore: null,
      markers: [m],
      extracted: takeNear(extracted, m.start, usedE, (item) => item.eid),
    });
    usedM.add(m.index);
  });

  rows.sort((a, b) => a.start - b.start);
  return rows.filter((r) => {
    const keep = r.gapBefore || r.markers.length || r.extracted.length ||
      (S.composer && Number(S.composer.start) === Number(r.start));
    if (keep) return true;
    if (!S.showAllCues) return false;
    if (S.hideFiller && isBackchannel(r.caption, S.fillerWords)) return false;
    return true;
  });
}

export function rowKey(row) {
  return row.rowId || `row:${Number(row.start)}`;
}

function composerOnMarker(m) {
  if (!S.composer || !m) return false;
  if (S.composer.source === "model") return String(m.index) === String(S.composer.index);
  return m.source === "miss" && Number(m.start) === Number(S.composer.start);
}

function composerOnRow(row) {
  if (!S.composer) return false;
  if (S.composer.mode === "add") return Number(S.composer.start) === Number(row.start);
  return (row.markers || []).some(composerOnMarker);
}

function addFormHtml() {
  if (!S.composer) return "";
  const editing = S.composer.mode === "edit";
  const chips = (S.composer.tags || []).map((tag) =>
    `<button type="button" tabindex="-1" class="chip" data-remove-tag="${escapeAttr(tag)}">${escapeHtml(tag)} ×</button>`
  ).join("");
  return `<form class="add-form" data-add-form="1">
    <label class="add-field"><span>Label</span>
      <input id="miss-label" name="label" value="${escapeAttr(S.composer.label || "")}" />
    </label>
    <div class="add-field">
      <span>Tags</span>
      <div class="tag-box">
        <div class="tag-chips">${chips}</div>
        <input id="miss-tags" data-combo="tags" name="tags" autocomplete="off" placeholder="take, fingering, technique, star…" />
        <div class="suggest" id="suggest-tags" hidden></div>
      </div>
    </div>
    <label class="add-field"><span>Why</span>
      <input id="miss-why" name="why" placeholder="why this is a clip" value="${escapeAttr(S.composer.why || "")}" />
    </label>
    <label class="add-field"><span>Work</span>
      <div class="combo">
        <input id="miss-work" data-combo="work" name="work" autocomplete="off" placeholder="Song | Rendition" value="${escapeAttr(S.composer.work || "")}" />
        <div class="suggest" id="suggest-work" hidden></div>
      </div>
    </label>
    <label class="add-field"><span>Lane</span>
      <div class="combo">
        <input id="miss-lane" data-combo="lane" name="lane" autocomplete="off" placeholder="transcription" value="${escapeAttr(S.composer.lane || "")}" />
        <div class="suggest" id="suggest-lane" hidden></div>
      </div>
    </label>
    <div class="add-actions">
      <button type="submit">${editing ? "Save" : "Add clip"}</button>
      ${editing && S.composer.source === "miss"
        ? `<button type="button" data-unmiss="${escapeAttr(S.composer.start)}">delete</button>`
        : ""}
    </div>
  </form>`;
}

function markerCell(row) {
  const bits = row.markers.map((m) => {
    if (composerOnMarker(m)) return "";
    const miss = m.source === "miss";
    const fb = miss ? "" : (S.current.feedback[String(m.index)] || "");
    const orig = m.originalDescription || "";
    const changed = !miss && orig && m.description !== orig;
    const desc = miss
      ? `<input data-miss-desc="${m.start}" value="${escapeAttr(m.description || "")}" />${
          m.why && !S.evalMode ? `<div class="why-note">${escapeHtml(m.why)}</div>` : ""
        }`
      : isWrong(fb)
        ? `<input data-wrong-reason="${m.index}" value="${escapeAttr(feedbackWhy(fb))}" placeholder="why reject? e.g. Heat is caption noise" />
          <div class="desc-orig">${escapeHtml(m.description || orig)}</div>`
        : `<input data-desc="${m.index}" value="${escapeAttr(m.description || "")}" />${
            changed ? `<div class="desc-orig">original: ${escapeHtml(orig)}</div>` : ""
          }${m.why && !S.evalMode ? `<div class="why-note">${escapeHtml(m.why)}</div>` : ""}`;
    const feedback = miss
      ? `<div class="miss-actions"><div class="miss-tag">ADDED MARKER</div><button type="button" data-unmiss="${m.start}">delete</button></div>`
      : S.evalMode && !isWrong(fb)
        ? `<div class="fb">
          <input data-i="${m.index}" value="${escapeAttr(fb)}" placeholder="note" />
        </div>`
        : "";
    const rationale = S.evalMode
      ? `<div class="rationale">${escapeHtml(m.rationale || "")}</div>`
      : "";
    return `<div class="marker-block" data-marker="${m.index}">
      <div class="desc">${desc}</div>
      ${rationale}
      ${feedback}
    </div>`;
  }).join("");
  const form = composerOnRow(row) ? addFormHtml() : "";
  return bits + form;
}

function evalCell(row) {
  const model = row.markers.find((m) => m.source === "model");
  if (!model) return `<td class="col-eval"></td>`;
  const mark = evalMark(S.current.feedback[String(model.index)] || "");
  const letter = mark === "g" || mark === "x" ? mark : "";
  const cls = mark === "g" ? "eval-g" : mark === "x" ? "eval-x" : "eval-empty";
  return `<td class="col-eval"><span class="eval-mark ${cls}">${letter}</span></td>`;
}

function isDescOnly(row) {
  return !(row.caption || "").trim() && row.extracted.length > 0;
}

function captionCell(row) {
  if (isDescOnly(row)) {
    return `<span class="desc-tag">YT overview</span><span class="desc-hint">not a caption</span>`;
  }
  return escapeHtml(row.caption);
}

function rowClass(row) {
  const cls = [];
  if (row.gapBefore) cls.push("gap-row");
  if (isDescOnly(row)) cls.push("desc-only");
  const m = row.markers.find((x) => x.index === S.activeIndex);
  if (m) cls.push("active");
  const model = row.markers.find((x) => x.source === "model");
  if (model) {
    const fb = fbClass(S.current.feedback[String(model.index)] || "");
    if (fb) cls.push(fb);
  }
  return cls.join(" ");
}

function taxonomyOf(row) {
  const miss = row.markers.find((m) => m.source === "miss");
  if (miss) {
    return { type: "miss", id: String(miss.start), tags: miss.tags || [], lane: miss.lane || "", work: miss.work || "" };
  }
  const model = row.markers.find((m) => m.source === "model");
  if (model) {
    return { type: "model", id: String(model.index), tags: model.tags || [], lane: model.lane || "", work: model.work || "" };
  }
  return { type: "none", id: String(row.start), tags: [], lane: "", work: "" };
}

function taxonomyCells(row, selected) {
  const tax = taxonomyOf(row);
  if (!selected || S.composer) {
    return `<td class="col-tags"><span class="tax-text">${escapeHtml((tax.tags || []).join(" · "))}</span></td>
      <td class="col-work"><span class="tax-text">${escapeHtml(tax.work)}</span></td>
      <td class="col-lane"><span class="tax-text">${escapeHtml(tax.lane)}</span></td>`;
  }
  // Hitchhiking while playing would orphan combo inputs as the playhead
  // walks; pinned selection is the edit target, so show fields even if the
  // video is rolling.
  if (!S.followPinned && isPlaying()) {
    return `<td class="col-tags"><span class="tax-text">${escapeHtml((tax.tags || []).join(" · "))}</span></td>
      <td class="col-work"><span class="tax-text">${escapeHtml(tax.work)}</span></td>
      <td class="col-lane"><span class="tax-text">${escapeHtml(tax.lane)}</span></td>`;
  }
  const chips = (tax.tags || []).map((tag) =>
    `<button type="button" tabindex="-1" class="chip" data-remove-tag="${escapeAttr(tag)}">${escapeHtml(tag)} ×</button>`
  ).join("");
  return `<td class="col-tags"><div class="tag-box">
      <div class="tag-chips">${chips}</div>
      <input data-combo="tags" autocomplete="off" />
      <div class="suggest" hidden></div>
    </div></td>
    <td class="col-work"><div class="combo">
      <input data-combo="work" autocomplete="off" value="${escapeAttr(tax.work)}" />
      <div class="suggest" hidden></div>
    </div></td>
    <td class="col-lane"><div class="combo">
      <input data-combo="lane" autocomplete="off" value="${escapeAttr(tax.lane)}" />
      <div class="suggest" hidden></div>
    </div></td>`;
}

function syncLiveTax(rowEl) {
  if (!rowEl) {
    S.liveTax = null;
    return;
  }
  S.liveTax = {
    type: rowEl.dataset.taxType,
    id: rowEl.dataset.taxId,
    tags: (rowEl.dataset.taxTags || "").split("|").filter(Boolean),
    lane: rowEl.dataset.taxLane || "",
    work: rowEl.dataset.taxWork || "",
  };
}

export function renderGrid() {
  if (!S.current) return;
  const rows = buildRows();
  $("tbody").innerHTML = rows.map((row) => {
    const markerIds = row.markers.map((m) => m.index).join(",");
    const fromGap = Boolean(row.gapBefore);
    const tax = taxonomyOf(row);
    const key = rowKey(row);
    const selected = S.selectedKey ? key === S.selectedKey : Number(row.start) === Number(S.selectedStart);
    return `<tr class="${rowClass(row)}" data-start="${row.start}" data-row-key="${escapeAttr(key)}" data-markers="${escapeAttr(markerIds)}"
        data-tax-type="${tax.type}" data-tax-id="${escapeAttr(tax.id)}" data-tax-tags="${escapeAttr((tax.tags || []).join("|"))}" data-tax-lane="${escapeAttr(tax.lane)}" data-tax-work="${escapeAttr(tax.work)}"
        data-add-start="${row.start}" data-add-text="${escapeAttr(row.caption)}" data-add-extracted="${escapeAttr((row.extracted[0] && row.extracted[0].label) || "")}" data-add-gap="${fromGap ? "1" : ""}" data-add-gapbefore="${row.gapBefore || ""}">
      <td class="sticky"><span class="time" data-seek="${row.start}">${hms(row.start)}</span></td>
      <td class="sticky2 caption">${captionCell(row)}</td>
      <td class="gap">${row.gapBefore ? "GAP " + row.gapBefore + "s" : ""}</td>
      ${evalCell(row)}
      <td class="markers">${markerCell(row)}</td>
      ${taxonomyCells(row, selected)}
      <td class="extracted">${row.extracted.map((item) => `<div class="extracted-label">${escapeHtml(item.label)}</div>`).join("")}</td>
    </tr>`;
  }).join("");
  restoreSelection();
  const selectedRow = document.querySelector("tr.selected");
  syncLiveTax(selectedRow);
  if (S.pendingScroll && selectedRow) {
    S.pendingScroll = false;
    selectedRow.scrollIntoView({ block: "center" });
  }
  if (S.pendingCombo) {
    const field = S.pendingCombo;
    S.pendingCombo = null;
    const el = document.querySelector(S.composer ? `.add-form [data-combo="${field}"]` : `tr.selected [data-combo="${field}"]`);
    if (el) { el.focus(); resetSuggestHi(); renderSuggest(field, el); }
  } else if (S.pendingReason != null) {
    const el = document.querySelector(`input[data-wrong-reason="${S.pendingReason}"]`);
    S.pendingReason = null;
    if (el) el.focus();
  } else if (S.pendingWhy) {
    S.pendingWhy = false;
    const el = $("miss-why");
    if (el) el.focus();
  } else if (S.composer) {
    const label = $("miss-label");
    if (label) label.focus();
  }
  renderTimeline();
}

export function followPlayhead(seconds) {
  if (!S.follow) {
    document.querySelectorAll("tr.playhead").forEach((el) => el.classList.remove("playhead"));
    return;
  }
  if (typingInField(document.activeElement)) return;
  const rows = visibleRows();
  if (!rows.length) return;
  let hit = rows[0];
  for (const row of rows) {
    if (Number(row.dataset.start) <= seconds + 0.05) hit = row;
    else break;
  }
  document.querySelectorAll("tr.playhead").forEach((el) => el.classList.remove("playhead"));
  hit.classList.add("playhead");
  // Pinned (or composer): playhead still walks; selection stays put and we
  // don't scroll the current caption over the row being edited.
  if (S.followPinned || S.composer) return;
  if (hit.dataset.rowKey !== S.selectedKey) {
    document.querySelectorAll("tr.selected").forEach((el) => el.classList.remove("selected"));
    hit.classList.add("selected");
    S.selectedStart = Number(hit.dataset.start);
    S.selectedKey = hit.dataset.rowKey || "";
    rememberCursor();
  }
  const wrap = $("gridScroll") || $("gridWrap");
  if (!wrap) return;
  const wr = wrap.getBoundingClientRect();
  const er = hit.getBoundingClientRect();
  if (er.top < wr.top + 8 || er.bottom > wr.bottom - 8) {
    hit.scrollIntoView({ block: "center" });
  }
}

export function recoupleFollow() {
  S.follow = true;
  S.followPinned = false;
  try { localStorage.setItem(FOLLOW_KEY, "1"); } catch (_) {}
  const box = $("follow");
  if (box) box.checked = true;
  followPlayhead(getCurrentTime());
}

// f: if selection is pinned or follow is off, recouple (selection hitchhikes
// again). If already hitchhiking, pin — freeze selection without navigating.
export function toggleFollowPin() {
  if (!S.follow || S.followPinned) recoupleFollow();
  else S.followPinned = true;
}

export function scrollToActive() {
  const row = document.querySelector("tr.active");
  if (row) row.scrollIntoView({ block: "center" });
}

export function activateMarker(index, seconds) {
  S.followPinned = true;
  S.activeIndex = index;
  S.selectedStart = Number(seconds);
  const rows = buildRows();
  const i = rows.findIndex((r) => r.markers.some((m) => Number(m.index) === Number(index)));
  S.selectedKey = i >= 0 ? rowKey(rows[i]) : null;
  rememberCursor();
  seek(seconds);
  renderGrid();
  scrollToActive();
}

export function updateStats() {
  if (!S.current) return;
  const markers = S.current.run.markers;
  const extractedN = extractedList(S.current.run).length;
  if (!S.evalMode) {
    $("stats").innerHTML = `<b>${markers.length}</b> markers · <b>${S.additions.length}</b> added · <b>${extractedN}</b> YT`;
    return;
  }
  let checks = 0, wrongs = 0, notes = 0, keeps = 0;
  markers.forEach((_, i) => {
    const t = (S.current.feedback[String(i)] || "").trim();
    if (isCheck(t)) checks += 1;
    else if (isWrong(t)) wrongs += 1;
    else if (t) notes += 1;
    else {
      const ann = S.annotations[String(i)] || {};
      if ((ann.tags || []).length || ann.lane || ann.work) keeps += 1;
    }
  });
  const blanks = markers.length - checks - wrongs - notes - keeps;
  $("stats").innerHTML = `<b>${checks}</b> check · <b>${wrongs}</b> wrong · <b>${keeps}</b> keep · <b>${notes}</b> notes · <b>${blanks}</b> blank · <b>${S.additions.length}</b> added · <b>${extractedN}</b> YT`;
}
