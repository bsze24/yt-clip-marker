// The player: one module, two backends behind one interface.
//
// Backend A is the YouTube IFrame embed. Backend B is a plain <video> element
// fed by the studio's own /media/ route, for when there is no network — a
// downloaded lesson or a Zoom recording. Every consumer (keys.js, grid.js,
// timeline.js, composer.js) calls the same exported functions and never learns
// which one is running; that is why adding backend B touched no other module's
// logic. Nothing outside this file touches the YT API or the media element.
import { $, typingInField } from "./util.js";

const LAYOUT_KEY = "yt-clipper-eval-player-layout";
const RATE_KEY = "yt-clipper-studio-rate";
const DEFAULT_RATES = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2];

let mode = "yt";              // "yt" | "local"
let player = null;            // YT.Player handle
let playerReady = false;      // YT backend only
let media = null;             // <video> element, created on first local run
let mediaReady = false;
let ytApiRequested = false;
let pendingSeek = null;
let pendingCue = { videoId: null, start: 0 };
let desiredRate = 1;
try {
  const saved = Number(localStorage.getItem(RATE_KEY));
  if (saved > 0) desiredRate = saved;
} catch (_) {}

export function initPlayer() {
  syncRateLabel();
  try {
    if (localStorage.getItem(LAYOUT_KEY) === "left") applyLayout("left");
  } catch (_) {}
  window.addEventListener("resize", syncPlayerSize);
}

// The IFrame API is fetched the first time a YouTube-backed run is opened, not
// at boot. Offline that request would only fail and log; a local-only session
// never makes it.
function ensureYouTubeApi() {
  if (ytApiRequested) return;
  ytApiRequested = true;
  // Must live on window: the IFrame API calls it by global name.
  window.onYouTubeIframeAPIReady = function () {
    const wrap = $("playerWrap");
    player = new YT.Player("player", {
      height: String(Math.round(wrap.clientWidth * 9 / 16)),
      width: String(wrap.clientWidth),
      playerVars: { rel: 0, modestbranding: 1, fs: 1 },
      events: {
        onReady() {
          playerReady = true;
          syncPlayerSize();
          applyCue();
          applyDesiredRate();
          if (pendingSeek != null) {
            player.seekTo(pendingSeek, true);
            pendingSeek = null;
            keepKeysOnPage();
          }
        },
        onStateChange() {
          applyDesiredRate();
          keepKeysOnPage();
          requestAnimationFrame(keepKeysOnPage);
        }
      }
    });
  };
  const tag = document.createElement("script");
  tag.src = "https://www.youtube.com/iframe_api";
  tag.addEventListener("error", () => {
    console.warn("YouTube IFrame API unreachable — local runs still play");
  });
  document.head.appendChild(tag);
}

function ensureMediaEl() {
  if (media) return media;
  media = document.createElement("video");
  media.id = "localVideo";
  media.playsInline = true;
  media.preload = "metadata";
  // No native controls: the .player-catcher overlay owns click-to-play and the
  // timeline rail owns scrubbing, exactly as with the embed.
  media.addEventListener("loadedmetadata", () => {
    mediaReady = true;
    applyDesiredRate();
    if (pendingSeek != null) {
      media.currentTime = clampTime(pendingSeek);
      pendingSeek = null;
    } else if (pendingCue.start > 0) {
      media.currentTime = clampTime(pendingCue.start);
    }
    keepKeysOnPage();
  });
  media.addEventListener("ratechange", syncRateLabel);
  media.addEventListener("error", () => {
    const err = media.error;
    console.error("local media failed to load", err && err.code, media.currentSrc);
  });
  $("playerWrap").insertBefore(media, $("playerCatcher"));
  return media;
}

function clampTime(seconds) {
  const value = Number(seconds) || 0;
  const dur = media && Number.isFinite(media.duration) ? media.duration : 0;
  if (!dur) return Math.max(0, value);
  return Math.min(dur, Math.max(0, value));
}

function ready() {
  return mode === "local" ? mediaReady : Boolean(pendingCue.videoId && playerReady);
}

function playerLayout() {
  return document.body.classList.contains("player-left") ? "left" : "top";
}

function applyLayout(mode) {
  const left = mode === "left";
  document.body.classList.toggle("player-left", left);
  document.body.classList.toggle("player-top", !left);
  try { localStorage.setItem(LAYOUT_KEY, left ? "left" : "top"); } catch (_) {}
  requestAnimationFrame(() => {
    syncPlayerSize();
    requestAnimationFrame(syncPlayerSize);
  });
}

export function togglePlayerLayout() {
  applyLayout(playerLayout() === "top" ? "left" : "top");
}

// Only the embed needs pixel sizes pushed at it; the <video> element is sized
// by the same CSS rules as the #player box.
export function syncPlayerSize() {
  if (mode === "local") return;
  if (!playerReady || !player.setSize) return;
  const wrap = $("playerWrap");
  const w = wrap.clientWidth || 640;
  const ratioH = Math.round(w * 9 / 16);
  const h = playerLayout() === "top"
    ? Math.min(ratioH, Math.round(window.innerHeight * 0.52))
    : ratioH;
  player.setSize(w, h);
}

// The iframe steals focus after any interaction with it; blur it and hand
// focus back to the grid so the keyboard keeps working. A <video> element
// never takes focus on click, so in local mode this is only the grid refocus.
export function keepKeysOnPage() {
  const active = document.activeElement;
  if (typingInField(active)) return;
  if (active && active.closest && active.closest("[data-add-form]")) return;
  try {
    const iframe = player && player.getIframe && player.getIframe();
    if (iframe) iframe.blur();
  } catch (_) {}
  if (active && active.tagName === "IFRAME") active.blur();
  const grid = $("gridWrap");
  if (grid && document.activeElement !== grid && !typingInField(document.activeElement)) {
    grid.focus({ preventScroll: true });
  }
}

// Open-editor seek: land paused so fields don't run away.
export function seek(seconds) {
  if (!ready()) {
    pendingSeek = seconds;
    return;
  }
  if (mode === "local") {
    media.currentTime = clampTime(seconds);
    media.pause();
  } else {
    player.seekTo(seconds, true);
    player.pauseVideo();
  }
  keepKeysOnPage();
}

export function nudge(delta) {
  if (!ready()) return;
  const duration = getDuration();
  const next = Math.min(duration || Infinity, Math.max(0, getCurrentTime() + delta));
  seekRaw(next);
  keepKeysOnPage();
}

export function togglePlay() {
  if (!ready()) return;
  if (mode === "local") {
    if (media.paused) {
      const p = media.play();
      if (p && p.catch) p.catch(() => {});
    } else {
      media.pause();
    }
  } else {
    const state = player.getPlayerState();
    if (state === YT.PlayerState.PLAYING) player.pauseVideo();
    else player.playVideo();
  }
  keepKeysOnPage();
}

// Called on every run switch. `mediaSource` is the /api/run `media` object when
// the run has a playable file on disk; it wins over the embed, so a downloaded
// video plays locally without any mode switch to remember.
export function loadVideo(videoId, startSeconds, mediaSource) {
  pendingCue = { videoId: videoId || null, start: Number(startSeconds) || 0 };
  pendingSeek = null;
  if (mediaSource && mediaSource.url) {
    switchMode("local");
    const el = ensureMediaEl();
    if (el.getAttribute("src") !== mediaSource.url) {
      mediaReady = false;
      el.pause();
      el.setAttribute("src", mediaSource.url);
      el.load();
    } else if (mediaReady) {
      el.currentTime = clampTime(pendingCue.start);
    }
    return;
  }
  switchMode("yt");
  // No local file and no resolved YouTube identity is a supported empty
  // backend. Do not fetch the IFrame API for it, and clear a previous embed so
  // switching from another run cannot leave the wrong lesson on screen.
  if (!pendingCue.videoId) {
    const ytBox = $("player");
    if (ytBox) ytBox.hidden = true;
    if (playerReady && player) {
      try {
        if (player.clearVideo) player.clearVideo();
        else if (player.stopVideo) player.stopVideo();
      } catch (_) {}
    }
    return;
  }
  ensureYouTubeApi();
  if (!playerReady || !pendingCue.videoId) return;
  applyCue();
}

function switchMode(next) {
  mode = next;
  const ytBox = $("player");
  const local = next === "local";
  if (ytBox) ytBox.hidden = local;
  if (media) media.hidden = !local;
  if (local && playerReady && player.pauseVideo) {
    try { player.pauseVideo(); } catch (_) {}
  }
  if (!local && media) media.pause();
  document.body.classList.toggle("local-media", local);
}

function applyCue() {
  if (!playerReady || !pendingCue.videoId) return;
  const start = pendingCue.start;
  if (start > 0) player.cueVideoById({ videoId: pendingCue.videoId, startSeconds: start });
  else player.cueVideoById(pendingCue.videoId);
  applyDesiredRate();
}

function availableRates() {
  if (mode === "local") return DEFAULT_RATES;
  const rates = playerReady && player.getAvailablePlaybackRates
    ? player.getAvailablePlaybackRates()
    : null;
  return (rates && rates.length) ? rates : DEFAULT_RATES;
}

function formatRate(rate) {
  const n = Number(rate) || 1;
  return (Number.isInteger(n) ? String(n) : String(n)) + "×";
}

function syncRateLabel() {
  const el = $("playRate");
  if (!el) return;
  el.textContent = formatRate(desiredRate);
}

function applyDesiredRate() {
  if (mode === "local") {
    if (media) media.playbackRate = desiredRate;
    syncRateLabel();
    return;
  }
  if (!playerReady || !player.setPlaybackRate) return;
  try { player.setPlaybackRate(desiredRate); } catch (_) {}
  syncRateLabel();
}

// YouTube's own keys: Shift+, slower / Shift+. faster. The embed never
// receives them (we keep focus on the grid), so the page owns the same
// gesture for both backends.
export function bumpPlaybackRate(dir) {
  if (!ready()) return;
  const rates = availableRates();
  const current = getPlaybackRate();
  let i = rates.findIndex((r) => Math.abs(r - current) < 0.001);
  if (i < 0) i = rates.findIndex((r) => r >= current);
  if (i < 0) i = rates.length - 1;
  const next = rates[Math.max(0, Math.min(rates.length - 1, i + dir))];
  desiredRate = next;
  try { localStorage.setItem(RATE_KEY, String(next)); } catch (_) {}
  applyDesiredRate();
  keepKeysOnPage();
}

function getPlaybackRate() {
  if (mode === "local") return media ? media.playbackRate : desiredRate;
  return player && player.getPlaybackRate ? player.getPlaybackRate() : desiredRate;
}

// Primitives for the key dispatcher's player context. seekRaw deliberately
// does not play or re-focus — matching the original Home/End/digit behavior.
export function isPlayerReady() { return ready(); }

export function isPlaying() {
  if (mode === "local") return Boolean(media && !media.paused && !media.ended);
  return ready() && player && player.getPlayerState() === YT.PlayerState.PLAYING;
}

export function getCurrentTime() {
  if (mode === "local") return media ? media.currentTime || 0 : 0;
  return ready() && player ? player.getCurrentTime() : 0;
}

export function seekRaw(seconds) {
  if (mode === "local") {
    if (mediaReady) media.currentTime = clampTime(seconds);
    return;
  }
  if (!playerReady || !player) return;
  player.seekTo(seconds, true);
}

export function scrubTo(seconds) {
  if (!ready()) {
    pendingSeek = seconds;
    return;
  }
  seekRaw(seconds);
  keepKeysOnPage();
}

// A webm or mkv without a duration index reports Infinity; callers treat 0 as
// "unknown" and fall back to the last cue, so normalise it here.
export function getDuration() {
  if (mode === "local") {
    const d = media ? media.duration : 0;
    return Number.isFinite(d) ? d : 0;
  }
  if (!ready() || !player || !player.getDuration) return 0;
  return player.getDuration() || 0;
}

export function toggleMute() {
  if (mode === "local") {
    if (media) media.muted = !media.muted;
    return;
  }
  if (!playerReady || !player) return;
  if (player.isMuted()) player.unMute();
  else player.mute();
}

export function playerMode() { return mode; }
