# Current task

**Review PR 7 — local video mode.** Baton: **→ reviewer**, on `c4de36d`.

Roles are reversed for this round at Brian's instruction: Claude Code implemented, Codex
reviews. The code is written and committed on `local-video-mode`; nothing here asks anyone to
rebuild it.

---

## 0. State as of 2026-08-19

| Item | Where | Status |
| --- | --- | --- |
| **PR 7 — local video mode** | `local-video-mode`, `c4de36d` | **under review**, this task |
| PR 4 — video 1 store | `codex/pr-4-video-1-store`, `43c99dd` | review clean → **Brian, merge** |
| PR 3 | merged `5af3e13` | closed |
| PR 5 | `949cb7b` | closed, superseded — do not merge |
| PR 6 + `docs/remove-coordination-md` | `e158710` | **close, do not merge** — ~1,000 lines stale |

`main` is `15571f9`. PR 7 branches from it and carries two commits, `4b344d5` then `c4de36d`,
with two session-log commits interleaved by Brian. Verify before reviewing:

```bash
git merge-base --is-ancestor c4de36d HEAD
```

**Why this exists.** Brian is flying and the annotation loop is otherwise complete. The only
two things in the studio that needed the internet were the player and the ingest.

## 1. The task

Review `c4de36d` per the `README.md` review loop. `docs/prs/pr-7-local-video-mode.md` is the
spec and carries the design rationale; this file carries the baton and the audit.

**Where to look hard.** Places this change could plausibly be wrong, not a generic checklist:

- `server.py` `_send_media` and `_parse_range` — the byte-range path is new and hand-rolled.
  Suffix ranges, `start > end`, a range past EOF, a multi-range header (deliberately ignored,
  first span only), and the switch to `protocol_version = "HTTP/1.1"`, which is only safe
  because every response on every route sets `Content-Length`. Check that claim rather than
  taking it.
- `server.py` `media_file` — the traversal guard deliberately does **not** `resolve()`, because
  files in `media/` are usually symlinks and resolving would read every legitimate one as an
  escape. The safety therefore rests entirely on `MEDIA_FILE` rejecting anything with a slash
  or a dot-dot. If that regex is wrong, the route is wrong.
- `server.py` `resolve_run_media` — runs stay immutable ([[D-002]]); media is matched on every
  read instead of being written back. Confirm nothing on the write paths gained a `media` key,
  and that a run whose file disappears degrades to the embed rather than erroring.
- `ui/player.js` — the whole file changed shape. Both backends must satisfy the same contract:
  every export either works or no-ops when its backend is not ready. The bug found during
  verification was exactly this class (`getDuration` unguarded), so check its siblings.
- `ui/grid.js` `buildRows` — the synthetic composer row. It must not collide with a real row
  at the same start, and must vanish once the marker exists.
- `keys.js` — `n` is the one new binding. Confirm it does not fire while a field has focus and
  that it sits in `gridKeys`, not `playerKeys`, so it works before a player is ready.
- `local.py` `parse_vtt` — the three real input shapes are Zoom's cue-numbered VTT with
  `Speaker: text` bodies, yt-dlp's auto-caption VTT with inline karaoke tags and rolling
  repeated lines, and SRT. The rolling-window dedupe only catches *exact* repeats.

**Out of scope.** End collection, JSON export, in-app suggest, extension→studio handoff, the
copy-timestamps fold ([[D-022]]), and the two items filed as `TD-11` and `TD-12`.

## 2. Acceptance criteria

1. The studio plays a local file with no network: seek, playback rate, follow, and the
   transport keys all drive the `<video>` backend as they drive the embed.
2. A YouTube run gains offline playback from `media/{videoId}.mp4` with no change to its run
   file, and loses it cleanly when the file is removed.
3. A recording with no transcript is usable — empty grid, `n` marks at the playhead, and the
   resulting clip round-trips to `labels.jsonl`.
4. `/media/` serves byte ranges correctly and serves nothing outside `media/`.
5. `prefetch.py <url>` leaves a playable run behind, and re-running it writes nothing new.
6. No regression on the YouTube path: video 1 loads with a clean console and its counts
   unchanged.

## 3. Baton

**→ reviewer**, on `c4de36d`. Findings go in `REVIEW.md` thread 4.

---

## Handoff notes

### 2026-08-19 — implementer, PR 7 local video mode (`4b344d5`, `c4de36d`)

- **Acceptance criteria and evidence.** All six met, browser-driven against a **disposable
  copy** of the store so the real `runs/` and `labels.jsonl` were never written to.
  (1) `player.js` `mode` switches every export; verified in the tab — row click seeking to
  exactly 12.0s, timeline rail scrub to 44.85s of 90, `follow` advancing the playhead row
  across the 0:45 boundary, `<`/`>` stepping 1 → 1.25 → 1.5 → 1.25 with the label in sync,
  and arrows / digits / Home / End / `m` / space each moving the element as specified.
  (2) `resolve_run_media` matched a fabricated run at `YYW4Q1Nivg8` to `media/YYW4Q1Nivg8.mp4`
  with `'media' not in run` still true, and returned `None` once the file was moved away.
  (3) the zero-cue run rendered an empty grid, `n` opened the composer at 0:27 — the video
  paused on 00:00:27.000, confirmed on screen — and the submitted clip landed in
  `labels.jsonl` as `verdict: "miss"`, `start: 27.0`.
  (4) 206 for `bytes=0-99`, open-ended and suffix forms; 416 with `Content-Range: bytes */N`
  when unsatisfiable; 200 with `Accept-Ranges` when no range is asked for; the served span
  hashes identical to `dd` over the same offsets. `..`, percent-encoded `..`, a sibling file
  and a non-media extension all 404.
  (5) `prefetch.py` against a real video produced media, `en` captions and `.info.json`, a run
  with the real id, title, watch URL, 6 cues and 3 extracted markers, playing from `/media/`;
  the rerun took the already-exists branch and wrote nothing.
  (6) video 1 on the **real** store: clean console, YouTube embed cued, 64 markers · 21 added ·
  24 extracted · 1464 cues.
- **Assumptions.** (a) `videoId` keeps its name for a local run, with a filename-derived value
  and a new `source: "local"` beside it, so the run filename, the `labels.jsonl` key and every
  existing reader work untouched — readers test `source`, not the shape of the id. (b) Local
  wins over the embed whenever both are available, so there is no mode to remember. (c) Files
  outside `media/` are symlinked in rather than copied, keeping the served surface to one
  directory. (d) `n` is a new binding rather than a change to `Enter`, because with no
  transcript there is no row for `Enter` to act on. (e) Byte ranges were treated as mandatory,
  not an optimisation: without them Chrome can only seek inside its buffer.
- **Skips and divergences.** Silence-gap detection without a transcript (needs ffmpeg), local
  transcription, and an `<audio>` element for audio-only files were all left out; the last is
  filed as `TD-12`. `ingest.py` was not touched despite sharing the caption-language wildcard
  that caused a real failure in `prefetch.py` — it is latent there for a stated reason, filed
  as `TD-11`. No decision entries were written: per the `README.md` wrap-up, durable outcomes
  are harvested when review lands clean, so the calls above are proposals until then.
- **Two findings outside this repo**, both of which will hit anyone running the offline path.
  yt-dlp's default player client (`android_vr`) lists every format and then answers **403** for
  the stream; pinned to `web_embedded,mweb`. And a Homebrew yt-dlp has no `curl_cffi`, so it
  cannot impersonate a browser — a version outside its supported range is silently ignored and
  shows as `(unsupported)` only under `--verbose`. Both are recorded in `apps/studio/README.md`.
- **What I could not check.** Playback on a genuinely offline machine — the verification ran
  with network available, and the YouTube backend was exercised *because* it was. The offline
  claim rests on the code path (a local run never calls `ensureYouTubeApi`) plus the observed
  fact that a local run's playback issues no external request, not on a disconnected test.

Each turn appends here: role, surface, SHA, what was verified, assumptions made, anything
skipped. See `README.md`, "Before recording a SHA".
