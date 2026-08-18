// Entry point: header controls, grid event delegation, ingest form, boot.
import { $ } from "./util.js";
import { S, EVAL_KEY, FOLLOW_KEY, FILLER_KEY } from "./state.js";
import { api } from "./api.js";
import { initPlayer, togglePlay, keepKeysOnPage, scrubTo, isPlaying, getCurrentTime } from "./player.js";
import { renderGrid, updateStats, selectRowEl, displayMarkers, followPlayhead } from "./grid.js";
import {
  removeTag, pickSuggest, renderSuggest, hideSuggest, resetSuggestHi,
} from "./suggest.js";
import {
  persistUnmiss, queueSave, queueWrongReason, queueRelabel, queueMissDesc, persistTaxonomy,
  queueTaxonomy,
} from "./persist.js";
import { submitComposer, openEditor } from "./composer.js";
import { refreshRuns, openRun, renderRunSelect } from "./runs.js";
import { initKeys } from "./keys.js";
import { initTimeline, updateTimelineHead } from "./timeline.js";
import { initFiller, syncDensity } from "./filler.js";
import { copyTimestamps } from "./export.js";

initPlayer();
initKeys();
initTimeline();
initFiller();

$("playerCatcher").addEventListener("click", () => {
  togglePlay();
  $("gridWrap").focus();
});
$("runSelect").addEventListener("change", (e) => openRun(e.target.value));
$("allCues").addEventListener("change", (e) => {
  S.showAllCues = e.target.checked;
  renderGrid();
  syncDensity();
  keepKeysOnPage();
});
$("hideFiller").checked = S.hideFiller;
$("hideFiller").addEventListener("change", (e) => {
  S.hideFiller = e.target.checked;
  try { localStorage.setItem(FILLER_KEY, S.hideFiller ? "1" : "0"); } catch (_) {}
  renderGrid();
  syncDensity();
  keepKeysOnPage();
});
$("follow").checked = S.follow;
$("follow").addEventListener("change", (e) => {
  S.follow = e.target.checked;
  S.followPinned = false;
  try { localStorage.setItem(FOLLOW_KEY, S.follow ? "1" : "0"); } catch (_) {}
  if (!S.follow) {
    document.querySelectorAll("tr.playhead").forEach((el) => el.classList.remove("playhead"));
  }
  keepKeysOnPage();
});
$("copyTsBtn").addEventListener("click", () => {
  copyTimestamps();
  keepKeysOnPage();
});
$("evalMode").checked = S.evalMode;
$("evalMode").addEventListener("change", (e) => {
  S.evalMode = e.target.checked;
  try { localStorage.setItem(EVAL_KEY, S.evalMode ? "1" : "0"); } catch (_) {}
  renderRunSelect();
  renderGrid();
  updateStats();
  keepKeysOnPage();
});
$("ingestForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const url = $("ingestUrl").value.trim();
  if (!url) return;
  $("ingestBtn").disabled = true;
  $("ingestState").textContent = "ingesting… (fetching captions, ~30s)";
  try {
    const data = await api("/api/ingest", "POST", { url });
    $("ingestUrl").value = "";
    $("ingestState").textContent = `${data.cueCount} cues · ${data.extractedCount} YT desc`;
    await refreshRuns();
    await openRun(data.id);
    renderRunSelect();
  } catch (err) {
    $("ingestState").textContent = "ingest failed: " + err.message;
  } finally {
    $("ingestBtn").disabled = false;
    keepKeysOnPage();
  }
});
$("tbody").addEventListener("click", (e) => {
  // Chips and suggest dropdowns exist in both the composer and the in-row
  // taxonomy editors — don't gate them on the composer being open.
  const chip = e.target.closest("[data-remove-tag]");
  if (chip) {
    removeTag(chip.dataset.removeTag, chip);
    return;
  }
  const pick = e.target.closest("[data-suggest], [data-suggest-new]");
  if (pick) {
    const field = pick.dataset.suggestField;
    pickSuggest(field, pick.dataset.suggestNew || pick.dataset.suggest, Boolean(pick.dataset.suggestNew));
    return;
  }
  const unmissBtn = e.target.closest("[data-unmiss]");
  if (unmissBtn) {
    persistUnmiss(unmissBtn.dataset.unmiss);
    return;
  }
  if (e.target.closest("[data-add-form]")) return;
  if (e.target.closest("input[data-i], input[data-wrong-reason]")) return;
  const timeBtn = e.target.closest("[data-seek]");
  if (timeBtn) {
    const row = timeBtn.closest("tr");
    if (row) selectRowEl(row, { seekVideo: true });
    else scrubTo(Number(timeBtn.dataset.seek));
    return;
  }
  const block = e.target.closest("[data-marker]");
  if (block) {
    const raw = block.dataset.marker;
    const m = displayMarkers().find((x) => String(x.index) === String(raw));
    if (m) openEditor(m);
    return;
  }
  if (e.target.closest("input")) return;
  const row = e.target.closest("tr[data-start]");
  if (row) selectRowEl(row, { seekVideo: true });
});
$("tbody").addEventListener("mousedown", (e) => {
  if (e.target.closest(".suggest")) e.preventDefault();
});
$("tbody").addEventListener("focusin", (e) => {
  if (!e.target.dataset.combo) return;
  resetSuggestHi();
  renderSuggest(e.target.dataset.combo, e.target);
});
$("tbody").addEventListener("focusout", (e) => {
  if (e.target.dataset.combo) hideSuggest(e.target.dataset.combo);
});
$("tbody").addEventListener("input", (e) => {
  if (e.target.matches("input[data-i]")) queueSave(Number(e.target.dataset.i), e.target.value);
  if (e.target.matches("input[data-wrong-reason]")) {
    queueWrongReason(Number(e.target.dataset.wrongReason), e.target.value);
  }
  if (e.target.matches("input[data-desc]")) queueRelabel(Number(e.target.dataset.desc), e.target.value);
  if (e.target.matches("input[data-miss-desc]")) {
    const start = Number(e.target.dataset.missDesc);
    queueMissDesc(start, e.target.value);
  }
  if (e.target.dataset.combo) {
    resetSuggestHi();
    renderSuggest(e.target.dataset.combo, e.target);
    if (S.liveTax && e.target.dataset.combo === "lane") {
      S.liveTax.lane = e.target.value;
      queueTaxonomy();
    }
    if (S.liveTax && e.target.dataset.combo === "work") {
      S.liveTax.work = e.target.value;
      queueTaxonomy();
    }
  }
});
$("tbody").addEventListener("submit", (e) => {
  if (e.target.closest("[data-add-form]")) {
    e.preventDefault();
    submitComposer();
  }
});
$("tbody").addEventListener("keydown", (e) => {
  if (!S.composer) return;
  if (e.key === "Escape") {
    e.preventDefault();
    S.composer = null;
    renderGrid();
  }
});

refreshRuns();
setInterval(refreshRuns, 4000);
setInterval(() => {
  const t = getCurrentTime();
  updateTimelineHead(t);
  if (S.follow && isPlaying()) followPlayhead(t);
}, 250);
