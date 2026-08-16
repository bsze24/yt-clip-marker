// Every write to the server. All writers surface failures via saveFailed and
// leave in-memory state intact so the user can retry.
import { fbClass, missId, STAR_TAG, isWrong, isCheck, formatWrong, formatCheck, feedbackWhy } from "./util.js";
import { S, setSave, rememberChapter } from "./state.js";
import { api, saveFailed } from "./api.js";
import { renderGrid, updateStats } from "./grid.js";

export async function persistTaxonomy() {
  if (!S.liveTax || S.liveTax.type === "none" || !S.currentId) return;
  setSave("saving…");
  try {
    if (S.liveTax.type === "miss") {
      const existing = S.additions.find((m) => Number(m.start) === Number(S.liveTax.id));
      if (!existing) return;
      const res = await api("/api/miss", "PUT", {
        runId: S.currentId, start: existing.start,
        description: existing.description, why: existing.why || "",
        tags: S.liveTax.tags, lane: S.liveTax.lane, work: S.liveTax.work,
        cueText: existing.cueText || "", gapBefore: existing.gapBefore,
      });
      S.additions = res.additions || [];
      S.current.additions = S.additions;
    } else if (S.liveTax.type === "model") {
      const res = await api("/api/annotate", "PUT", {
        runId: S.currentId, index: Number(S.liveTax.id),
        tags: S.liveTax.tags, lane: S.liveTax.lane, work: S.liveTax.work,
      });
      S.annotations = res.annotations || S.annotations;
      S.current.annotations = S.annotations;
    }
    rememberChapter(S.liveTax.lane, S.liveTax.work);
  } catch (err) {
    saveFailed(err);
    return;
  }
  setSave("saved");
}

export async function persist(index, text) {
  S.current.feedback[String(index)] = text;
  setSave("saving…");
  try {
    await api("/api/feedback", "PUT", { runId: S.currentId, index, text });
  } catch (err) {
    saveFailed(err);
    return;
  }
  setSave("saved");
  updateStats();
  const row = document.querySelector(`tr[data-markers*="${CSS.escape(String(index))}"]`);
  if (row) {
    row.classList.remove("good", "note", "wrong");
    const cls = fbClass(text);
    if (cls) row.classList.add(cls);
  }
}

export function queueSave(index, text) {
  S.current.feedback[String(index)] = text;
  clearTimeout(S.saveTimer);
  S.saveTimer = setTimeout(() => persist(index, text), 280);
}

export function queueWrongReason(index, text) {
  // Empty reason stays "wrong" so the reject glyph doesn't drop while typing.
  const next = formatWrong(text);
  S.current.feedback[String(index)] = next;
  clearTimeout(S.saveTimer);
  S.saveTimer = setTimeout(() => persist(index, next), 400);
}

export async function persistRelabel(index, text) {
  const trimmed = (text || "").trim();
  if (!trimmed) return;
  S.edits[String(index)] = trimmed;
  setSave("saving…");
  let res;
  try {
    res = await api("/api/relabel", "PUT", { runId: S.currentId, index, description: trimmed });
  } catch (err) {
    saveFailed(err);
    return;
  }
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
  clearTimeout(S.saveTimer);
  S.saveTimer = setTimeout(() => persistRelabel(index, text), 400);
}

export async function persistMissDesc(start, text) {
  const existing = S.additions.find((m) => Number(m.start) === Number(start));
  const description = (text || "").trim();
  if (!existing || !description) return;
  setSave("saving…");
  let res;
  try {
    res = await api("/api/miss", "PUT", {
      runId: S.currentId, start: existing.start,
      description, why: existing.why || "",
      tags: existing.tags || [], lane: existing.lane || "", work: existing.work || "",
      cueText: existing.cueText || "",
      gapBefore: existing.gapBefore,
    });
  } catch (err) {
    saveFailed(err);
    return;
  }
  S.additions = res.additions || [];
  S.current.additions = S.additions;
  setSave("saved");
}

export async function persistUnmiss(start) {
  start = Number(start);
  if (!S.additions.some((m) => Number(m.start) === start)) return;
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
