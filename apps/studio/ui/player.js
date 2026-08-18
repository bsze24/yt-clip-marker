// YouTube IFrame player: owns the player handle and its ready/pending state.
// Nothing outside this module touches the YT API directly.
import { $, typingInField } from "./util.js";

const LAYOUT_KEY = "yt-clipper-eval-player-layout";
const RATE_KEY = "yt-clipper-studio-rate";
const DEFAULT_RATES = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2];

let player = null;
let playerReady = false;
let pendingSeek = null;
let pendingCue = { videoId: null, start: 0 };
let desiredRate = 1;
try {
  const saved = Number(localStorage.getItem(RATE_KEY));
  if (saved > 0) desiredRate = saved;
} catch (_) {}

export function initPlayer() {
  syncRateLabel();
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

  try {
    if (localStorage.getItem(LAYOUT_KEY) === "left") applyLayout("left");
  } catch (_) {}

  window.addEventListener("resize", syncPlayerSize);

  const tag = document.createElement("script");
  tag.src = "https://www.youtube.com/iframe_api";
  document.head.appendChild(tag);
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

export function syncPlayerSize() {
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
// focus back to the grid so the keyboard keeps working.
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
  if (!playerReady) {
    pendingSeek = seconds;
    return;
  }
  player.seekTo(seconds, true);
  player.pauseVideo();
  keepKeysOnPage();
}

export function nudge(delta) {
  if (!playerReady) return;
  const duration = player.getDuration() || 0;
  const next = Math.min(duration, Math.max(0, player.getCurrentTime() + delta));
  player.seekTo(next, true);
  keepKeysOnPage();
}

export function togglePlay() {
  if (!playerReady) return;
  const state = player.getPlayerState();
  if (state === YT.PlayerState.PLAYING) player.pauseVideo();
  else player.playVideo();
  keepKeysOnPage();
}

export function loadVideo(videoId, startSeconds) {
  pendingCue = { videoId: videoId || null, start: Number(startSeconds) || 0 };
  if (!playerReady || !pendingCue.videoId) return;
  applyCue();
}

function applyCue() {
  if (!playerReady || !pendingCue.videoId) return;
  const start = pendingCue.start;
  if (start > 0) player.cueVideoById({ videoId: pendingCue.videoId, startSeconds: start });
  else player.cueVideoById(pendingCue.videoId);
  applyDesiredRate();
}

function availableRates() {
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
  if (!playerReady || !player.setPlaybackRate) return;
  try { player.setPlaybackRate(desiredRate); } catch (_) {}
  syncRateLabel();
}

// YouTube's own keys: Shift+, slower / Shift+. faster. The embed never
// receives them (we keep focus on the grid), so the page owns the same
// gesture via the IFrame API.
export function bumpPlaybackRate(dir) {
  if (!playerReady) return;
  const rates = availableRates();
  const current = player.getPlaybackRate ? player.getPlaybackRate() : desiredRate;
  let i = rates.findIndex((r) => Math.abs(r - current) < 0.001);
  if (i < 0) i = rates.findIndex((r) => r >= current);
  if (i < 0) i = rates.length - 1;
  const next = rates[Math.max(0, Math.min(rates.length - 1, i + dir))];
  desiredRate = next;
  try { localStorage.setItem(RATE_KEY, String(next)); } catch (_) {}
  applyDesiredRate();
  keepKeysOnPage();
}

// Primitives for the key dispatcher's player context. seekRaw deliberately
// does not play or re-focus — matching the original Home/End/digit behavior.
export function isPlayerReady() { return playerReady; }
export function isPlaying() {
  return playerReady && player && player.getPlayerState() === YT.PlayerState.PLAYING;
}
export function getCurrentTime() {
  return playerReady && player ? player.getCurrentTime() : 0;
}
export function seekRaw(seconds) { player.seekTo(seconds, true); }
export function scrubTo(seconds) {
  if (!playerReady) {
    pendingSeek = seconds;
    return;
  }
  player.seekTo(seconds, true);
  keepKeysOnPage();
}
export function getDuration() { return player.getDuration() || 0; }
export function toggleMute() {
  if (player.isMuted()) player.unMute();
  else player.mute();
}
