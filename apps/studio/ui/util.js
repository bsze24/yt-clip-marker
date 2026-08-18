// Pure helpers and constants. No app state, no imports.

export const $ = (id) => document.getElementById(id);
export const MATCH = 2;
export const TAGS = ["take", "fingering", "technique", "star"];
export const STAR_TAG = "star";

// Cue-only backchannels. Tight on purpose — "no" is often a real answer.
export const DEFAULT_FILLER = [
  "yeah", "yep", "yup", "yes", "okay", "ok", "right", "alright",
  "mhm", "mm", "mmhmm", "mhmm", "uhhuh", "huh", "hmm",
  "uh", "um", "ah", "oh", "wow", "cool", "sure", "gotcha",
];

export function normalizeFillerToken(t) {
  return String(t || "").trim().toLowerCase()
    .replace(/^[^\w]+|[^\w]+$/g, "").replace(/-/g, "");
}

export function parseFillerList(s) {
  const seen = new Set();
  const out = [];
  String(s || "").split(/[,]+/).forEach((part) => {
    const t = normalizeFillerToken(part);
    if (t && !seen.has(t)) {
      seen.add(t);
      out.push(t);
    }
  });
  return out;
}

export function formatFillerList(words) {
  return (words || []).join(", ");
}

export function isBackchannel(text, words) {
  const set = words instanceof Set ? words : new Set(words || []);
  if (!set.size) return false;
  const raw = String(text || "").replace(/^>>\s*/g, "").trim().toLowerCase();
  if (!raw) return false;
  const tokens = raw.split(/\s+/).map(normalizeFillerToken).filter(Boolean);
  if (!tokens.length || tokens.length > 2) return false;
  return tokens.every((t) => set.has(t));
}

export function hms(t) {
  t = Math.max(0, Math.floor(Number(t) || 0));
  const h = Math.floor(t / 3600);
  const m = Math.floor((t % 3600) / 60);
  const s = t % 60;
  const pad = (n) => String(n).padStart(2, "0");
  return h ? `${h}:${pad(m)}:${pad(s)}` : `${m}:${pad(s)}`;
}

export function fbClass(text) {
  const v = (text || "").trim().toLowerCase();
  if (v === "check" || v.startsWith("check:")) return "good";
  if (v === "wrong" || v.startsWith("wrong:")) return "wrong";
  if (v) return "note";
  return "";
}

// Compact eval glyph: g = check, x = reject. Empty string = ungraded.
export function evalMark(text) {
  const v = (text || "").trim().toLowerCase();
  if (v === "check" || v.startsWith("check:")) return "g";
  if (v === "wrong" || v.startsWith("wrong:")) return "x";
  return "";
}

export function isCheck(text) {
  const v = (text || "").trim().toLowerCase();
  return v === "check" || v.startsWith("check:");
}

export function isWrong(text) {
  const v = (text || "").trim().toLowerCase();
  return v === "wrong" || v.startsWith("wrong:");
}

export function feedbackWhy(text) {
  const raw = (text || "").trim();
  const lower = raw.toLowerCase();
  if (lower === "check" || lower === "wrong") return "";
  if (lower.startsWith("check:") || lower.startsWith("wrong:")) {
    return raw.slice(raw.indexOf(":") + 1).trim();
  }
  return raw;
}

export function formatCheck(reason) {
  const r = (reason || "").trim();
  return r ? "check: " + r : "check";
}

export function formatWrong(reason) {
  const r = (reason || "").trim();
  return r ? "wrong: " + r : "wrong";
}

export function withWhy(current, reason) {
  if (isWrong(current)) return formatWrong(reason);
  if (isCheck(current)) return formatCheck(reason);
  return (reason || "").trim();
}

export function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
export function escapeAttr(s) { return escapeHtml(s); }

export function missId(start) { return "miss:" + Number(start); }

// Description timestamps on a run. The load boundary reports deprecated keys;
// this pure reader only consumes the supported field.
export function extractedList(run) {
  if (!run) return [];
  return Array.isArray(run.extracted) ? run.extracted : [];
}

// Published YT-description stamp nearest this time. The human title on the
// video wins over marker text and caption fallbacks.
export function extractedNear(extracted, start, window = MATCH) {
  let best = null;
  let bestD = window + 1;
  for (const item of extracted || []) {
    const d = Math.abs(Number(item.start) - Number(start));
    if (d <= window && d < bestD) {
      best = item;
      bestD = d;
    }
  }
  return best;
}

export function resolvedLabel(extracted, start, fallback) {
  const hit = extractedNear(extracted, start);
  const label = hit && String(hit.label || "").trim();
  return label || String(fallback || "").trim();
}

export function ytStamp(t) {
  t = Math.max(0, Math.floor(Number(t) || 0));
  const h = Math.floor(t / 3600);
  const m = Math.floor((t % 3600) / 60);
  const s = t % 60;
  const pad = (n) => String(n).padStart(2, "0");
  return h ? `${h}:${pad(m)}:${pad(s)}` : `${m}:${pad(s)}`;
}

export function normalizeTag(s) {
  const tag = String(s || "").trim().toLowerCase().replace(/\s+/g, " ");
  if (!tag || tag.length > 40) return "";
  if (!/^[a-z0-9][a-z0-9 _-]*$/.test(tag)) return "";
  return tag;
}

export function typingInField(el) {
  if (!el) return false;
  const tag = el.tagName;
  if (tag === "INPUT") {
    // Only text-entry inputs are "typing". A focused checkbox (the header
    // toggles) must not swallow the keyboard shortcuts.
    const type = (el.type || "").toLowerCase();
    return !["checkbox", "radio", "button", "submit", "reset", "range", "file", "color"].includes(type);
  }
  if (tag === "TEXTAREA" || tag === "SELECT") return true;
  return Boolean(el.isContentEditable);
}
