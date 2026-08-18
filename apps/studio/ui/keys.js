// The global keydown dispatcher. One capture-phase listener, routed through an
// explicit priority chain of contexts. Each context function returns true when
// it OWNS the event — meaning no later context may see it — even if it took no
// action (e.g. a plain letter typed into a combo input still belongs to the
// combo context so it can default-type into the field).
//
// Priority order (first owner wins):
//   1. modifier guard   — Cmd/Ctrl/Alt combos are never ours
//   1b. fillerModalKeys — skip-words dialog owns the keyboard while open
//   2. comboKeys        — focus is in a suggest combo input (tags/lane/work)
//                         Tab/Shift+Tab advance fields; Enter confirms work/lane
//                         without submitting the clip
//   3. composerFormKeys — focus is elsewhere in the open add-clip form
//                         Tab advances; Enter on label/why submits
//   4. descInputKeys    — Enter/Escape in a description input blurs back to grid
//   5. typing guard     — any other text field keeps all keys
//   6. tabPrefixKeys    — Tab arms a 900ms prefix; then t/w/l/y edits
//                         tags/work/lane/why
//   7. gridKeys         — j/k rows, J/K marker rows, Enter/s/g/x/h/f/v/Escape
//                         (work before player loads)
//   8. playerKeys       — arrows/space/Home/End/m/digits/</>/ (need a ready player)
import { typingInField, normalizeTag } from "./util.js";
import { S } from "./state.js";
import {
  keepKeysOnPage, togglePlayerLayout, nudge, togglePlay,
  isPlayerReady, seekRaw, getDuration, toggleMute, bumpPlaybackRate,
} from "./player.js";
import { moveRow, moveMarkerRow, renderGrid, toggleFollowPin } from "./grid.js";
import {
  bumpSuggest, acceptSuggest, hideSuggest, addTag, resetSuggestHi,
  removeTag, comboSelectedTags, finishComboEdit, editRowField, renderSuggest,
} from "./suggest.js";
import { submitComposer, onEnter, editWhy } from "./composer.js";
import { toggleStar, toggleCheck, rejectOrDelete } from "./persist.js";
import { closeFillerModal, saveFillerWords, toggleHideFiller } from "./filler.js";

let tabPrefix = false;
let tabPrefixTimer = null;

function fillerModalKeys(e) {
  if (!S.fillerModal) return false;
  if (e.key === "Escape") {
    e.preventDefault();
    closeFillerModal();
    return true;
  }
  if (e.key === "Enter") {
    e.preventDefault();
    saveFillerWords();
    return true;
  }
  return true;
}

function inComposerForm(e) {
  return S.composer && e.target.closest && e.target.closest("[data-add-form]");
}

// Tab/Shift+Tab inside the composer or an in-row taxonomy editor: commit this
// field and move to the next/previous one. Native Tab is not trustworthy here —
// the open suggest list, the YouTube iframe, and the grid's Tab-prefix chord
// all sit in the way. Chips and suggest buttons are tabindex=-1, so they are
// skipped. Past the last field, return to grid shortcuts.
function focusAdjacent(from, dir) {
  const root = from.closest("[data-add-form]") || from.closest("tr");
  if (!root) return;
  const fields = [...root.querySelectorAll("input, button[type='submit']")]
    .filter((el) => el.tabIndex !== -1 && !el.disabled && el.type !== "hidden");
  const i = fields.indexOf(from);
  const next = i < 0 ? null : fields[i + dir];
  hideSuggest();
  if (!next) {
    from.blur();
    if (from.closest("[data-add-form]")) keepKeysOnPage();
    else finishComboEdit();
    return;
  }
  next.focus();
  if (next.dataset.combo) {
    resetSuggestHi();
    renderSuggest(next.dataset.combo, next);
  }
}

function commitComboField(field, input) {
  if (field === "tags") {
    if (!acceptSuggest("tags", input, { requireHi: true })) {
      const typed = normalizeTag(input.value);
      if (typed) addTag(typed);
    }
    return;
  }
  acceptSuggest(field, input, { requireHi: true });
}

// Context 2: a combo input (composer or in-row taxonomy editor) has focus.
// Arrows drive the dropdown, Enter accepts/commits, Escape closes dropdown
// then form/edit, Backspace on empty tags input pops the last chip.
function comboKeys(e) {
  const key = e.key;
  const comboEl = e.target.closest && e.target.closest("[data-combo]");
  const combo = comboEl ? comboEl.dataset.combo : (e.target.dataset && e.target.dataset.combo);
  if (!combo) return false;
  const field = combo;
  const input = comboEl && comboEl.matches("[data-combo]") ? comboEl : e.target;
  const inForm = inComposerForm(e);
  if (key === "ArrowDown" || key === "Down" || e.code === "ArrowDown") {
    e.preventDefault();
    e.stopPropagation();
    bumpSuggest(field, 1, input);
    return true;
  }
  if (key === "ArrowUp" || key === "Up" || e.code === "ArrowUp") {
    e.preventDefault();
    e.stopPropagation();
    bumpSuggest(field, -1, input);
    return true;
  }
  if (key === "Enter") {
    e.preventDefault();
    e.stopPropagation();
    if (field === "tags") {
      if (!acceptSuggest("tags", input, { requireHi: true })) {
        const typed = normalizeTag(input.value);
        if (typed) addTag(typed);
        else if (inForm) submitComposer();
        else finishComboEdit();
      }
      return true;
    }
    acceptSuggest(field, input, { requireHi: true });
    // Work/lane Enter confirms the combo and moves on. Tags already submitted
    // above when empty — that's the fast path past inherited chapter fields.
    if (inForm) focusAdjacent(input, 1);
    else finishComboEdit();
    return true;
  }
  if (key === "Tab") {
    e.preventDefault();
    e.stopPropagation();
    commitComboField(field, input);
    focusAdjacent(input, e.shiftKey ? -1 : 1);
    return true;
  }
  if (key === "Escape") {
    e.preventDefault();
    if (hideSuggest(field)) return true;
    if (inForm) {
      S.composer = null;
      renderGrid();
    }
    finishComboEdit();
    return true;
  }
  if (field === "tags" && key === "Backspace" && !e.target.value) {
    const tags = comboSelectedTags(e.target);
    if (tags.length) {
      e.preventDefault();
      removeTag(tags[tags.length - 1], e.target);
    }
  }
  return true;
}

// Context 3: focus is in the add-clip form but not in a combo input
// (label / why). Enter submits, Escape closes; everything else types.
function composerFormKeys(e) {
  if (!inComposerForm(e)) return false;
  const key = e.key;
  if (key === "Tab") {
    e.preventDefault();
    focusAdjacent(e.target, e.shiftKey ? -1 : 1);
    return true;
  }
  if (key === "Enter" && e.target.tagName !== "BUTTON") {
    e.preventDefault();
    submitComposer();
    return true;
  }
  if (key === "Escape") {
    e.preventDefault();
    S.composer = null;
    renderGrid();
    keepKeysOnPage();
  }
  return true;
}

// Context 4: Enter or Escape inside a marker/added-clip description or
// reject-reason input hands focus back to the grid (edits already save on a
// debounce while typing). Blur explicitly — keepKeysOnPage won't steal
// focus from a field.
function descInputKeys(e) {
  if (e.key !== "Enter" && e.key !== "Escape") return false;
  if (!(e.target.matches && e.target.matches("input[data-desc], input[data-miss-desc], input[data-wrong-reason]"))) return false;
  e.preventDefault();
  e.target.blur();
  keepKeysOnPage();
  return true;
}

// Context 6: Tab arms a short-lived prefix; the next t/w/l/y jumps into the
// selected row's tags/work/lane editor or the why field. Any other key disarms
// the prefix and falls through to the remaining contexts.
function tabPrefixKeys(e) {
  if (e.key === "Tab") {
    e.preventDefault();
    tabPrefix = true;
    clearTimeout(tabPrefixTimer);
    tabPrefixTimer = setTimeout(() => { tabPrefix = false; }, 900);
    return true;
  }
  if (tabPrefix) {
    const k = e.key.toLowerCase();
    tabPrefix = false;
    if (k === "t" || k === "w" || k === "l" || k === "y") {
      e.preventDefault();
      if (k === "y") editWhy();
      else editRowField(k === "t" ? "tags" : k === "w" ? "work" : "lane");
      return true;
    }
  }
  return false;
}

// Context 7: grid navigation and row actions. These work even before the
// player is ready.
function gridKeys(e) {
  const key = e.key;
  if (key === "j") { e.preventDefault(); moveRow(1); return true; }
  if (key === "k") { e.preventDefault(); moveRow(-1); return true; }
  if (key === "J") { e.preventDefault(); moveMarkerRow(1); return true; }
  if (key === "K") { e.preventDefault(); moveMarkerRow(-1); return true; }
  if (key === "Enter") {
    // Let a focused button's native click happen.
    if (e.target.closest("button")) return true;
    e.preventDefault();
    onEnter();
    return true;
  }
  if (key === "s") { e.preventDefault(); toggleStar(); return true; }
  if (key === "g") { e.preventDefault(); toggleCheck(); return true; }
  if (key === "x") { e.preventDefault(); rejectOrDelete(); return true; }
  if (key === "h" || key === "H") { e.preventDefault(); toggleHideFiller(); return true; }
  if (key === "f" || key === "F") { e.preventDefault(); toggleFollowPin(); return true; }
  if (key === "v" || key === "V") { e.preventDefault(); togglePlayerLayout(); return true; }
  if (key === "Escape") {
    e.preventDefault();
    if (S.composer) {
      S.composer = null;
      renderGrid();
    }
    keepKeysOnPage();
    return true;
  }
  return false;
}

// Context 8: transport controls. Only when the player is ready.
function playerKeys(e) {
  if (!isPlayerReady()) return;
  const key = e.key;
  if (key === "ArrowLeft") { e.preventDefault(); nudge(-5); }
  else if (key === "ArrowRight") { e.preventDefault(); nudge(5); }
  else if (key === "l") { e.preventDefault(); nudge(10); }
  else if (key === " ") { e.preventDefault(); togglePlay(); }
  else if (key === "Home") { e.preventDefault(); seekRaw(0); }
  else if (key === "End") { e.preventDefault(); seekRaw(getDuration()); }
  else if (key === "m") { e.preventDefault(); toggleMute(); }
  else if (key === "<" || (e.code === "Comma" && e.shiftKey)) {
    e.preventDefault();
    bumpPlaybackRate(-1);
  }
  else if (key === ">" || (e.code === "Period" && e.shiftKey)) {
    e.preventDefault();
    bumpPlaybackRate(1);
  }
  else if (key >= "0" && key <= "9") {
    e.preventDefault();
    seekRaw(getDuration() * (Number(key) / 10));
  }
}

function dispatch(e) {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  if (fillerModalKeys(e)) return;
  if (comboKeys(e)) return;
  if (composerFormKeys(e)) return;
  if (descInputKeys(e)) return;
  if (typingInField(e.target)) return;
  if (tabPrefixKeys(e)) return;
  if (gridKeys(e)) return;
  playerKeys(e);
}

export function initKeys() {
  document.addEventListener("keydown", dispatch, true);
}
