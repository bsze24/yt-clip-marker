// Every write to the server. All writers surface failures via saveFailed and
// leave in-memory state intact so the user can retry.
import { fbClass, missId, STAR_TAG, isWrong, isCheck, formatWrong, formatCheck, feedbackWhy } from "./util.js";
import { S, setSave, rememberChapter } from "./state.js";
import { api, saveFailed } from "./api.js";
import { renderGrid, updateStats } from "./grid.js";

function scheduleSave(key, delay, work) {
  const pending = S.saveTimers.get(key);
  if (pending) clearTimeout(pending);
  const timer = setTimeout(async () => {
    S.saveTimers.delete(key);
    await work();
  }, delay);
  S.saveTimers.set(key, timer);
}

function cancelScheduled(key) {
  const pending = S.saveTimers.get(key);
  if (!pending) return;
  clearTimeout(pending);
  S.saveTimers.delete(key);
}

export function cancelPendingMarker(index, runId = S.currentId) {
  cancelScheduled(`${runId}:feedback:${index}`);
  cancelScheduled(`${runId}:relabel:${index}`);
  cancelScheduled(`${runId}:taxonomy:${index}`);
}

export function cancelPendingAddition(start, runId = S.currentId) {
  cancelScheduled(`${runId}:miss:${Number(start)}`);
}

function isCurrentRun(runId) {
  return Boolean(runId && S.currentId === runId);
}

function saveFailedForRun(err, runId) {
  if (isCurrentRun(runId)) saveFailed(err);
  else console.error(err);
}

function additionSnapshot(addition) {
  return {
    start: addition.start,
    description: addition.description || "",
    why: addition.why || "",
    tags: [...(addition.tags || [])],
    lane: addition.lane || "",
    work: addition.work || "",
    cueText: addition.cueText || "",
    gapBefore: addition.gapBefore,
  };
}

async function persistAddition(runId, addition) {
  if (!runId || !addition || !(addition.description || "").trim()) return;
  cancelPendingAddition(addition.start, runId);
  if (isCurrentRun(runId)) setSave("saving…");
  let res;
  try {
    res = await api("/api/miss", "PUT", { runId, ...addition });
  } catch (err) {
    saveFailedForRun(err, runId);
    return;
  }
  if (!isCurrentRun(runId)) return;
  S.additions = res.additions || [];
  S.current.additions = S.additions;
  setSave("saved");
}

export async function persistTaxonomy(tax = S.liveTax, runId = S.currentId) {
  if (!tax || tax.type === "none" || !runId) return;
  const snapshot = {
    type: tax.type,
    id: tax.id,
    tags: [...(tax.tags || [])],
    lane: tax.lane || "",
    work: tax.work || "",
  };
  if (snapshot.type === "miss") {
    cancelPendingAddition(snapshot.id, runId);
    const existing = S.additions.find((m) => Number(m.start) === Number(snapshot.id));
    if (!existing) return;
    existing.tags = snapshot.tags;
    existing.lane = snapshot.lane;
    existing.work = snapshot.work;
    await persistAddition(runId, additionSnapshot(existing));
  } else if (snapshot.type === "model") {
    cancelScheduled(`${runId}:taxonomy:${snapshot.id}`);
    if (isCurrentRun(runId)) setSave("saving…");
    let res;
    try {
      res = await api("/api/annotate", "PUT", {
        runId, index: Number(snapshot.id),
        tags: snapshot.tags, lane: snapshot.lane, work: snapshot.work,
      });
    } catch (err) {
      saveFailedForRun(err, runId);
      return;
    }
    if (!isCurrentRun(runId)) return;
    S.annotations = res.annotations || S.annotations;
    S.current.annotations = S.annotations;
    setSave("saved");
  }
  if (isCurrentRun(runId)) rememberChapter(snapshot.lane, snapshot.work);
}

export function queueTaxonomy() {
  if (!S.liveTax || S.liveTax.type === "none" || !S.currentId) return;
  const runId = S.currentId;
  const snapshot = {
    type: S.liveTax.type,
    id: S.liveTax.id,
    tags: [...(S.liveTax.tags || [])],
    lane: S.liveTax.lane || "",
    work: S.liveTax.work || "",
  };
  if (snapshot.type === "miss") {
    const existing = S.additions.find((m) => Number(m.start) === Number(snapshot.id));
    if (!existing) return;
    existing.tags = snapshot.tags;
    existing.lane = snapshot.lane;
    existing.work = snapshot.work;
    const addition = additionSnapshot(existing);
    scheduleSave(`${runId}:miss:${Number(snapshot.id)}`, 400, () => persistAddition(runId, addition));
    return;
  }
  scheduleSave(`${runId}:taxonomy:${snapshot.id}`, 400, () => persistTaxonomy(snapshot, runId));
}

export async function persist(index, text, runId = S.currentId) {
  if (!runId) return;
  cancelScheduled(`${runId}:feedback:${index}`);
  if (isCurrentRun(runId)) {
    S.current.feedback[String(index)] = text;
    setSave("saving…");
  }
  try {
    await api("/api/feedback", "PUT", { runId, index, text });
  } catch (err) {
    saveFailedForRun(err, runId);
    return;
  }
  if (!isCurrentRun(runId)) return;
  setSave("saved");
  updateStats();
  const block = document.querySelector(`[data-marker="${CSS.escape(String(index))}"]`);
  const row = block && block.closest("tr");
  if (row) {
    row.classList.remove("good", "note", "wrong");
    const cls = fbClass(text);
    if (cls) row.classList.add(cls);
  }
}

export function queueSave(index, text) {
  S.current.feedback[String(index)] = text;
  const runId = S.currentId;
  scheduleSave(`${runId}:feedback:${index}`, 280, () => persist(index, text, runId));
}

export function queueWrongReason(index, text) {
  // Empty reason stays "wrong" so the reject glyph doesn't drop while typing.
  const next = formatWrong(text);
  S.current.feedback[String(index)] = next;
  const runId = S.currentId;
  scheduleSave(`${runId}:feedback:${index}`, 400, () => persist(index, next, runId));
}

export async function persistRelabel(index, text, runId = S.currentId) {
  const trimmed = (text || "").trim();
  if (!trimmed || !runId) return;
  cancelScheduled(`${runId}:relabel:${index}`);
  if (isCurrentRun(runId)) setSave("saving…");
  let res;
  try {
    res = await api("/api/relabel", "PUT", { runId, index, description: trimmed });
  } catch (err) {
    saveFailedForRun(err, runId);
    return;
  }
  if (!isCurrentRun(runId)) return;
  S.edits = res.edits || S.edits;
  S.current.edits = S.edits;
  setSave("saved");
  const input = document.querySelector(`input[data-desc="${index}"]`);
  if (input) {
    const orig = (S.current.run.markers[index] || {}).description || "";
    const parent = input.parentElement;
    let hint = parent.querySelector(".desc-orig");
    if (trimmed !== orig) {
      if (!hint) {
        hint = document.createElement("div");
        hint.className = "desc-orig";
        parent.appendChild(hint);
      }
      hint.textContent = "original: " + orig;
    } else if (hint) hint.remove();
  }
}

export function queueRelabel(index, text) {
  const runId = S.currentId;
  scheduleSave(`${runId}:relabel:${index}`, 400, () => persistRelabel(index, text, runId));
}

export function queueMissDesc(start, text) {
  const existing = S.additions.find((m) => Number(m.start) === Number(start));
  const description = (text || "").trim();
  const runId = S.currentId;
  if (!existing || !description || !runId) return;
  existing.description = description;
  const addition = additionSnapshot(existing);
  scheduleSave(`${runId}:miss:${Number(start)}`, 400, () => persistAddition(runId, addition));
}

export async function persistUnmiss(start) {
  start = Number(start);
  if (!S.additions.some((m) => Number(m.start) === start)) return;
  cancelPendingAddition(start);
  if (S.composer && Number(S.composer.start) === start) S.composer = null;
  setSave("saving…");
  let res;
  try {
    res = await api("/api/unmiss", "PUT", { runId: S.currentId, start });
  } catch (err) {
    saveFailed(err);
    return;
  }
  S.additions = res.additions || [];
  S.current.additions = S.additions;
  if (String(S.activeIndex) === String(missId(start))) S.activeIndex = null;
  setSave("saved");
  renderGrid();
  updateStats();
}

function selectedTaxRow() {
  return document.querySelector("tr.selected");
}

export async function toggleStar() {
  const row = selectedTaxRow();
  if (!row || row.dataset.taxType === "none") return;
  const tags = (row.dataset.taxTags || "").split("|").filter(Boolean);
  S.liveTax = {
    type: row.dataset.taxType,
    id: row.dataset.taxId,
    tags: tags.includes(STAR_TAG) ? tags.filter((t) => t !== STAR_TAG) : [...tags, STAR_TAG],
    lane: row.dataset.taxLane || "",
    work: row.dataset.taxWork || "",
  };
  await persistTaxonomy();
  renderGrid();
}

export async function toggleCheck() {
  const row = selectedTaxRow();
  if (!row || row.dataset.taxType !== "model") return;
  const index = Number(row.dataset.taxId);
  const cur = (S.current.feedback[String(index)] || "").trim();
  if (isCheck(cur)) await persist(index, "");
  else await persist(index, formatCheck(isWrong(cur) ? "" : feedbackWhy(cur)));
  renderGrid();
}

// Marker: toggle a "wrong" reject. Added clip: unmiss (this is delete).
export async function rejectOrDelete() {
  const row = selectedTaxRow();
  if (!row) return;
  if (row.dataset.taxType === "miss") {
    await persistUnmiss(row.dataset.taxId);
    return;
  }
  if (row.dataset.taxType !== "model") return;
  const index = Number(row.dataset.taxId);
  const cur = (S.current.feedback[String(index)] || "").trim();
  if (isWrong(cur)) {
    await persist(index, "");
    renderGrid();
    return;
  }
  // Preserve a freeform eval note as the reject reason.
  const reason = cur.toLowerCase() === "check" ? "" : cur;
  await persist(index, formatWrong(reason));
  S.composer = null;
  S.pendingReason = index;
  renderGrid();
}
