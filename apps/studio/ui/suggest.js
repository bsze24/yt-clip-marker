// Taxonomy vocabulary + the suggest dropdown + tag chips, shared by the
// composer form and the in-row combo editors.
import { $, TAGS, normalizeTag, escapeHtml, escapeAttr, typingInField } from "./util.js";
import { S } from "./state.js";
import { keepKeysOnPage } from "./player.js";
import { persistTaxonomy, persistSection } from "./persist.js";
import { onEnter } from "./composer.js";

let suggestHi = -1;

export function resetSuggestHi() { suggestHi = -1; }

function videoVocab() {
  const lanes = new Set();
  const works = new Set();
  const tags = new Set(TAGS);
  if (S.lastChapter.lane) lanes.add(S.lastChapter.lane);
  if (S.lastChapter.work) works.add(S.lastChapter.work);
  S.additions.forEach((m) => {
    if (m.lane) lanes.add(m.lane);
    if (m.work) works.add(m.work);
    (m.tags || []).forEach((t) => tags.add(t));
  });
  Object.values(S.annotations).forEach((ann) => {
    if (ann.lane) lanes.add(ann.lane);
    if (ann.work) works.add(ann.work);
    (ann.tags || []).forEach((t) => tags.add(t));
  });
  const tagList = [...tags].sort((a, b) => {
    const ai = TAGS.indexOf(a);
    const bi = TAGS.indexOf(b);
    if (ai >= 0 && bi >= 0) return ai - bi;
    if (ai >= 0) return -1;
    if (bi >= 0) return 1;
    return a.localeCompare(b);
  });
  return {
    lanes: [...lanes].sort((a, b) => a.localeCompare(b)),
    works: [...works].sort((a, b) => a.localeCompare(b)),
    tags: tagList,
  };
}

function comboWrap(el) {
  return el && el.closest ? el.closest(".tag-box, .combo") : null;
}

export function comboSelectedTags(input) {
  if (input && input.id === "miss-tags") return (S.composer && S.composer.tags) || [];
  if (S.liveTax) return S.liveTax.tags || [];
  return [];
}

function suggestItems(field, input) {
  const vocab = videoVocab();
  const q = ((input && input.value) || "").trim().toLowerCase();
  const selected = new Set(comboSelectedTags(input));
  let items = field === "tags"
    ? vocab.tags.filter((t) => !selected.has(t))
    : field === "lane" ? vocab.lanes : vocab.works;
  if (q) items = items.filter((t) => t.toLowerCase().includes(q));
  const exact = items.some((t) => t.toLowerCase() === q) || (field === "tags" && selected.has(q));
  const addNew = field === "tags" && q && normalizeTag(q) && !exact;
  return { items, addNew, q: normalizeTag(q) || q };
}

export function renderSuggest(field, input) {
  input = input || document.activeElement;
  const wrap = comboWrap(input);
  const box = wrap && wrap.querySelector(".suggest");
  if (!box) return;
  const { items, addNew, q } = suggestItems(field, input);
  const total = items.length + (addNew ? 1 : 0);
  if (suggestHi >= total) suggestHi = total - 1;
  const rows = items.map((t, i) =>
    `<button type="button" tabindex="-1" class="suggest-item${i === suggestHi ? " hi" : ""}" data-suggest-field="${field}" data-suggest="${escapeAttr(t)}">${escapeHtml(t)}</button>`
  );
  if (addNew) {
    const i = items.length;
    rows.push(`<button type="button" tabindex="-1" class="suggest-item suggest-new${i === suggestHi ? " hi" : ""}" data-suggest-field="${field}" data-suggest-new="${escapeAttr(q)}">Add new tag “${escapeHtml(q)}”</button>`);
  }
  box.innerHTML = rows.join("");
  box.hidden = rows.length === 0;
  const hiEl = box.querySelector(".hi");
  if (hiEl) hiEl.scrollIntoView({ block: "nearest" });
}

export function hideSuggest(field) {
  const input = document.activeElement;
  const wrap = comboWrap(input);
  const box = wrap && wrap.querySelector(".suggest");
  if (field && box && !box.hidden) {
    box.hidden = true;
    suggestHi = -1;
    return true;
  }
  document.querySelectorAll(".suggest").forEach((el) => { el.hidden = true; });
  suggestHi = -1;
  return false;
}

export function bumpSuggest(field, delta, input) {
  input = input || document.activeElement;
  const wrap = comboWrap(input);
  const box = wrap && wrap.querySelector(".suggest");
  if (box && box.hidden) {
    suggestHi = -1;
    renderSuggest(field, input);
  }
  const { items, addNew } = suggestItems(field, input);
  const total = items.length + (addNew ? 1 : 0);
  if (!total) {
    renderSuggest(field, input);
    return;
  }
  if (suggestHi < 0) suggestHi = delta > 0 ? 0 : total - 1;
  else suggestHi = (suggestHi + delta + total) % total;
  renderSuggest(field, input);
}

export function acceptSuggest(field, input, { requireHi = false } = {}) {
  input = input || document.activeElement;
  const { items, addNew, q } = suggestItems(field, input);
  const total = items.length + (addNew ? 1 : 0);
  if (!total) return false;
  const wrap = comboWrap(input);
  const box = wrap && wrap.querySelector(".suggest");
  if (box && box.hidden) return false;
  if (suggestHi < 0 && requireHi) return false;
  const hi = suggestHi < 0 ? 0 : suggestHi;
  if (hi < items.length) pickSuggest(field, items[hi], false, input);
  else if (addNew) pickSuggest(field, q, true, input);
  else return false;
  return true;
}

export function pickSuggest(field, value, isNew, input) {
  if (field === "tags") addTag(value);
  else {
    input = input || (document.activeElement && document.activeElement.dataset.combo === field
      ? document.activeElement
      : document.querySelector(`[data-combo="${field}"]`));
    if (input) input.value = value;
    if (S.liveTax && input && !input.closest("[data-add-form]")) {
      S.liveTax[field] = value;
      persistTaxonomy();
    }
    const wrap = comboWrap(input);
    const box = wrap && wrap.querySelector(".suggest");
    if (box) box.hidden = true;
    suggestHi = -1;
  }
}

export function addTag(tag) {
  tag = normalizeTag(tag);
  if (!tag) return;
  const input = document.activeElement && document.activeElement.dataset.combo === "tags"
    ? document.activeElement
    : $("miss-tags");
  const inComposer = input && input.id === "miss-tags";
  if (inComposer) {
    if (!S.composer) return;
    if (!(S.composer.tags || []).includes(tag)) S.composer.tags = [...(S.composer.tags || []), tag];
  } else if (S.liveTax) {
    if (!(S.liveTax.tags || []).includes(tag)) S.liveTax.tags = [...(S.liveTax.tags || []), tag];
    persistTaxonomy();
  }
  if (input) input.value = "";
  suggestHi = -1;
  renderTagChips(inComposer ? document.querySelector(".add-form .tag-chips") : document.querySelector("tr.selected .tag-chips"));
  renderSuggest("tags", input);
}

// contextEl is any element inside the owning container — the clicked chip or
// the focused tags input. Its DOM location decides composer vs in-row: at
// click time document.activeElement is unreliable (Chrome focuses the chip
// button on mousedown, before the click event fires).
export function removeTag(tag, contextEl) {
  const inComposer = Boolean(contextEl && contextEl.closest && contextEl.closest("[data-add-form]"));
  if (inComposer) {
    if (!S.composer) return;
    S.composer.tags = (S.composer.tags || []).filter((t) => t !== tag);
    renderTagChips(document.querySelector(".add-form .tag-chips"));
    renderSuggest("tags", $("miss-tags"));
    return;
  }
  if (S.liveTax) {
    S.liveTax.tags = (S.liveTax.tags || []).filter((t) => t !== tag);
    renderTagChips(document.querySelector("tr.selected .tag-chips"));
    persistTaxonomy();
    const input = document.querySelector("tr.selected [data-combo=tags]");
    if (input) renderSuggest("tags", input);
  }
}

function renderTagChips(wrap) {
  wrap = wrap || document.querySelector(".tag-chips");
  if (!wrap) return;
  const tags = wrap.closest(".add-form")
    ? ((S.composer && S.composer.tags) || [])
    : ((S.liveTax && S.liveTax.tags) || []);
  wrap.innerHTML = tags.map((tag) =>
    `<button type="button" tabindex="-1" class="chip" data-remove-tag="${escapeAttr(tag)}">${escapeHtml(tag)} ×</button>`
  ).join("");
}

export function finishComboEdit() {
  const input = document.activeElement;
  if (input && (input.dataset.combo === "work" || input.dataset.combo === "lane")) {
    // "work changes from here" — one section break on the run, not a value on
    // this clip. Everything after inherits it by resolution.
    const row = input.closest("tr");
    const start = row ? Number(row.dataset.start) : NaN;
    if (Number.isFinite(start)) {
      persistSection(start, { [input.dataset.combo]: input.value.trim() });
    }
  } else {
    persistTaxonomy();
  }
  document.querySelectorAll(".suggest").forEach((el) => { el.hidden = true; });
  // keepKeysOnPage refuses to steal focus from a text field (that guard exists
  // for real typing), so the combo input must blur itself first or Escape
  // would leave the cursor trapped in the field.
  if (input && typingInField(input)) input.blur();
  keepKeysOnPage();
}

export function editRowField(field) {
  if (S.composer) {
    const el = document.querySelector(`.add-form [data-combo="${field}"]`);
    if (el) { el.focus(); suggestHi = -1; renderSuggest(field, el); }
    return;
  }
  const row = document.querySelector("tr.selected");
  if (!row) return;
  if (row.dataset.taxType === "none") {
    S.pendingCombo = field;
    onEnter();
    return;
  }
  const el = row.querySelector(`[data-combo="${field}"]`);
  if (el) { el.focus(); suggestHi = -1; renderSuggest(field, el); }
}
