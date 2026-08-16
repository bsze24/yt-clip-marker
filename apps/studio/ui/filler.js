// Caption-density mode chip + the skip-words modal. Words persist in
// localStorage; the run file is never rewritten.
import { $, DEFAULT_FILLER, formatFillerList, parseFillerList } from "./util.js";
import { S, FILLER_KEY, FILLER_WORDS_KEY } from "./state.js";
import { keepKeysOnPage } from "./player.js";
import { renderGrid } from "./grid.js";

export function densityMode() {
  if (!S.showAllCues) return "landmarks";
  if (S.hideFiller) return "hide-filler";
  return "all";
}

export function densityLabel() {
  const mode = densityMode();
  if (mode === "landmarks") return "Landmarks only — gaps, markers, and YT stamps";
  if (mode === "hide-filler") return "Hiding filler — skip words hidden from the grid";
  return "All captions — including yeah / okay / right";
}

export function syncDensity() {
  const mode = densityMode();
  document.body.classList.toggle("density-landmarks", mode === "landmarks");
  document.body.classList.toggle("density-hide-filler", mode === "hide-filler");
  document.body.classList.toggle("density-all", mode === "all");
  const chip = $("density");
  if (chip) chip.textContent = densityLabel();
  const all = $("allCues");
  const hide = $("hideFiller");
  if (all && all.closest) all.closest("label").classList.toggle("on", S.showAllCues);
  if (hide && hide.closest) hide.closest("label").classList.toggle("on", S.hideFiller);
}

export function toggleHideFiller() {
  S.hideFiller = !S.hideFiller;
  const box = $("hideFiller");
  if (box) box.checked = S.hideFiller;
  try { localStorage.setItem(FILLER_KEY, S.hideFiller ? "1" : "0"); } catch (_) {}
  renderGrid();
  syncDensity();
  keepKeysOnPage();
}

export function openFillerModal() {
  S.fillerModal = true;
  const modal = $("fillerModal");
  const input = $("fillerWords");
  if (input) input.value = formatFillerList(S.fillerWords);
  if (modal) modal.hidden = false;
  if (input) input.focus();
}

export function closeFillerModal() {
  S.fillerModal = false;
  const modal = $("fillerModal");
  if (modal) modal.hidden = true;
  keepKeysOnPage();
}

export function saveFillerWords(raw) {
  const words = parseFillerList(raw != null ? raw : ($("fillerWords") && $("fillerWords").value));
  S.fillerWords = words.length ? words : DEFAULT_FILLER.slice();
  try { localStorage.setItem(FILLER_WORDS_KEY, formatFillerList(S.fillerWords)); } catch (_) {}
  closeFillerModal();
  renderGrid();
  syncDensity();
}

export function resetFillerWords() {
  const input = $("fillerWords");
  if (input) input.value = formatFillerList(DEFAULT_FILLER);
}

export function initFiller() {
  syncDensity();
  const openBtn = $("fillerWordsBtn");
  if (openBtn) openBtn.addEventListener("click", () => {
    openFillerModal();
  });
  const chip = $("density");
  if (chip) chip.addEventListener("click", () => openFillerModal());
  const overlay = $("fillerModal");
  if (overlay) overlay.addEventListener("click", (e) => {
    if (e.target === overlay) closeFillerModal();
  });
  const save = $("fillerSave");
  if (save) save.addEventListener("click", () => saveFillerWords());
  const cancel = $("fillerCancel");
  if (cancel) cancel.addEventListener("click", () => closeFillerModal());
  const reset = $("fillerReset");
  if (reset) reset.addEventListener("click", () => resetFillerWords());
}
