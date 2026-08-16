// Vertical duration rail: ticks at marker times, a playhead at current time.
// Click scrubs without forcing play. Does not import grid.js (renderGrid calls
// us), so the tick list is built from S directly.
import { $, isWrong, isCheck } from "./util.js";
import { S } from "./state.js";
import { getDuration, getCurrentTime, scrubTo } from "./player.js";

const PAD = 8;
let mappedDur = 0;

function durationSeconds() {
  const d = getDuration();
  if (d > 0) return d;
  if (!S.current) return 0;
  let last = 0;
  for (const c of S.current.run.cues || []) last = Math.max(last, Number(c.start) || 0);
  for (const m of S.current.run.markers || []) last = Math.max(last, Number(m.start) || 0);
  for (const m of S.additions || []) last = Math.max(last, Number(m.start) || 0);
  return last;
}

function tickClass(source, tags, fb) {
  const cls = ["timeline-tick"];
  if (source === "miss") cls.push("miss");
  if ((tags || []).includes("star")) cls.push("star");
  const v = (fb || "").trim().toLowerCase();
  if (isCheck(v)) cls.push("check");
  else if (isWrong(v)) cls.push("wrong");
  return cls.join(" ");
}

export function renderTimeline() {
  const track = $("timelineTrack");
  if (!track) return;
  const dur = durationSeconds();
  mappedDur = dur;
  if (!dur || !S.current) {
    track.innerHTML = "";
    return;
  }
  const ticks = [];
  (S.current.run.markers || []).forEach((m, i) => {
    const start = Number(m.start);
    if (!Number.isFinite(start)) return;
    const tags = (S.annotations[String(i)] || {}).tags || [];
    const fb = (S.current.feedback || {})[String(i)] || "";
    ticks.push({ start, cls: tickClass("model", tags, fb) });
  });
  (S.additions || []).forEach((m) => {
    const start = Number(m.start);
    if (!Number.isFinite(start)) return;
    ticks.push({ start, cls: tickClass("miss", m.tags || [], "") });
  });
  track.innerHTML = ticks.map((t) => {
    const pct = Math.min(100, Math.max(0, (t.start / dur) * 100));
    return `<span class="${t.cls}" style="top:${pct}%"></span>`;
  }).join("");
  updateTimelineHead(getCurrentTime());
}

export function updateTimelineHead(seconds) {
  const head = $("timelineHead");
  if (!head) return;
  const dur = durationSeconds();
  if (dur && dur !== mappedDur) {
    renderTimeline();
    return;
  }
  if (!dur) {
    head.style.top = PAD + "px";
    return;
  }
  const pct = Math.min(1, Math.max(0, Number(seconds) / dur));
  head.style.top = `calc(${PAD}px + (100% - ${PAD * 2}px) * ${pct})`;
}

function timeAtClick(e, dur) {
  const rail = e.currentTarget;
  const r = rail.getBoundingClientRect();
  const y = e.clientY - r.top - PAD;
  const h = r.height - PAD * 2;
  if (h <= 0) return 0;
  return Math.min(dur, Math.max(0, (y / h) * dur));
}

export function initTimeline() {
  const rail = $("timeline");
  if (!rail) return;
  rail.addEventListener("click", (e) => {
    const dur = durationSeconds();
    if (!dur) return;
    const t = timeAtClick(e, dur);
    scrubTo(t);
    updateTimelineHead(t);
  });
}
