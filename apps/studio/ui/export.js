// Fold the current run into YouTube description timestamps and copy them.
// Extracted (already-published stamps) and added markers are never dropped.
// Nearby rows collapse to one line; extracted title and start win when present.
// Taxonomy still comes from the studio clip (added or skill marker) in that cluster.
import { MATCH, STAR_TAG, isCheck, isWrong, resolvedLabel, ytStamp, extractedList } from "./util.js";
import { S, setSave, workAt } from "./state.js";

const RANK = { extracted: 0, miss: 1, skill: 2 };

function keepSkill(index) {
  const text = ((S.current.feedback || {})[String(index)] || "");
  if (isWrong(text)) return false;
  if (isCheck(text)) return true;
  const ann = S.annotations[String(index)] || {};
  return Boolean((ann.tags && ann.tags.length) || ann.lane || ann.work);
}

function unionTags(a, b) {
  const out = [];
  const seen = new Set();
  for (const tag of [...(a || []), ...(b || [])]) {
    const t = String(tag || "").trim();
    if (!t || seen.has(t)) continue;
    seen.add(t);
    out.push(t);
  }
  return out;
}

function skillMeta(index) {
  const ann = S.annotations[String(index)] || {};
  return {
    tags: [...(ann.tags || [])],
    lane: (ann.lane || "").trim(),
    work: (ann.work || "").trim(),
  };
}

function missMeta(m) {
  return {
    tags: [...(m.tags || [])],
    lane: (m.lane || "").trim(),
    work: (m.work || "").trim(),
  };
}

function candidates() {
  const extracted = extractedList(S.current && S.current.run);
  const items = [];
  extracted.forEach((item) => {
    items.push({
      start: Number(item.start),
      label: String(item.label || "").trim(),
      source: "extracted",
      tags: [],
      lane: "",
      work: "",
    });
  });
  (S.additions || []).forEach((m) => {
    items.push({
      start: Number(m.start),
      label: resolvedLabel(extracted, m.start, m.description),
      source: "miss",
      ...missMeta(m),
    });
  });
  (S.current.run.markers || []).forEach((m, i) => {
    if (!keepSkill(i)) return;
    const edited = (S.edits || {})[String(i)];
    items.push({
      start: Number(m.start),
      label: resolvedLabel(extracted, m.start, edited || m.description),
      source: "skill",
      ...skillMeta(i),
    });
  });
  return items.filter((it) => it.label);
}

function mergePair(keep, other) {
  return {
    start: keep.start,
    label: keep.label,
    source: keep.source,
    tags: unionTags(keep.tags, other.tags),
    lane: keep.lane || other.lane,
    work: keep.work || other.work,
  };
}

export function mergeNearby(items) {
  const sorted = items.slice().sort((a, b) => a.start - b.start || RANK[a.source] - RANK[b.source]);
  const clusters = [];
  for (const it of sorted) {
    const cluster = clusters[clusters.length - 1];
    // Two entries only collapse when they would print the same words. Merging on
    // time alone would delete a label (D-033). Video 1 never hits this — every
    // close pair there contains an extracted marker, which rewrites both labels
    // to the same text first — so this condition is a no-op on that data.
    if (cluster && it.start - cluster.firstStart <= MATCH && it.label === cluster.clip.label) {
      const keep = RANK[it.source] < RANK[cluster.clip.source] ? it : cluster.clip;
      const other = keep === it ? cluster.clip : it;
      cluster.clip = mergePair(keep, other);
      continue;
    }
    clusters.push({
      firstStart: it.start,
      clip: { ...it, tags: [...(it.tags || [])] },
    });
  }
  return clusters.map((cluster) => cluster.clip);
}

function formatClip(c, sectionLane) {
  const starred = (c.tags || []).includes(STAR_TAG);
  const tags = (c.tags || []).filter((t) => t !== STAR_TAG).join(", ");
  const star = starred ? "*** " : "";
  const bits = [`${ytStamp(c.start)} ${star}${c.label}`];
  if (tags) bits.push(tags);
  if (c.lane && c.lane !== sectionLane) bits.push(c.lane);
  return bits.join(" | ");
}

function sectionLaneFor(clips, work) {
  const hit = clips.find((c) => workAt(c.start) === work && c.lane);
  return (hit && hit.lane) || "";
}

export function descriptionTimestampText() {
  if (!S.current) return "";
  const clips = mergeNearby(candidates());
  if (!clips.length) return "";
  const lines = [];
  let lastWork = "";
  let sectionLane = "";
  for (const c of clips) {
    // Resolved from the section breaks, never read off the clip. `c.work` is
    // legacy — video 1 stored the string on all 67 of its rows before the
    // breaks existed, and its two rows were migrated to two events.
    const work = workAt(c.start);
    if (work && work !== lastWork) {
      sectionLane = sectionLaneFor(clips, work);
      if (lines.length) lines.push("");
      lines.push(sectionLane ? `${work} | ${sectionLane}` : work);
      lastWork = work;
    }
    lines.push(formatClip(c, sectionLane));
  }
  // YouTube chapters need a 0:00 stamp. Park it under the first work
  // header so that header isn't swallowed as the chapter title.
  if (clips[0].start > 0) {
    const zero = `${ytStamp(0)} Start`;
    if (workAt(clips[0].start)) lines.splice(1, 0, zero);
    else lines.unshift(zero);
  }
  return lines.join("\n");
}

export async function copyTimestamps() {
  const text = descriptionTimestampText();
  if (!text) {
    setSave("nothing to copy");
    return;
  }
  try {
    await navigator.clipboard.writeText(text);
    const n = text.split("\n").filter((l) => /^\d+:\d+/.test(l)).length;
    const over = text.length > 5000 ? " — over 5000" : "";
    setSave(`copied ${n} timestamps · ${text.length} chars${over}`);
  } catch (err) {
    console.error(err);
    setSave("copy failed");
  }
}
