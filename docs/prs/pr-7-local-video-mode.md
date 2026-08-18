# PR 7 — Local video mode

**Goal.** The studio works with no network. Playback falls back from the YouTube embed
to a `<video>` element served by the studio itself, and a run can be built from a file
already on disk instead of from a URL.

**Why now.** An airplane. The annotation loop is otherwise complete and the only thing
that needs the internet is the player and the ingest.

## Shape

One module gained a second backend; nothing else learned about it.

- `apps/studio/local.py` (new) — build a run from a media file plus whatever sidecars
  share its stem: `.json3` / `.vtt` / `.srt` for cues, `.info.json` for real YouTube
  identity, title, description and `extracted[]`. Zero sidecars is a supported outcome.
- `apps/studio/server.py` — `/media/<name>` with byte-range support, `/api/media`,
  `media` on the `/api/run` payload, `source` and `hasMedia` on `/api/runs`, and
  `/api/ingest` branching to the local path when its input is a file reference.
- `apps/studio/ui/player.js` — `mode` is `"yt"` or `"local"`; every exported function
  branches inside. `keys.js`, `grid.js`, `timeline.js` and `composer.js` are unchanged
  in their dealings with it.
- `n` — new key: open the add form at the current playhead. The only way to create a
  clip in a run with no transcript, where there are no rows to press Enter on.

## Decisions worth recording

- **Media is resolved on read, never written into the run file.** `runs/{id}.json` is
  immutable ingest output ([[D-002]]). A run gains offline playback because a matching
  file appeared in `media/`, and loses it when the file goes away; no history is
  rewritten in either direction. This is also what makes attaching a downloaded video
  to an existing YouTube run a one-step operation — name it `{videoId}.mp4`.
- **Local wins over the embed when both are available.** One run, two sources, and the
  offline case needs no mode to remember. Online the difference is invisible.
- **Byte ranges are not optional.** Chrome will play a 200 response but can only seek
  inside what it has already buffered, which makes the timeline useless on an
  hour-long lesson. `_send_media` answers 206 with `Content-Range`; the handler moved
  to HTTP/1.1 so the burst of range requests a scrub produces reuses one connection.
- **Files outside `media/` are symlinked in, not copied.** These are gigabytes and the
  studio only reads them. Serving stays confined to one directory whose names are
  allowlisted, so the route has no traversal surface — and the check deliberately does
  not `resolve()`, or every legitimate symlink would read as an escape.
- **A synthetic `videoId` for files with no YouTube identity**, plus `source: "local"`.
  Keeping the field name means the run filename, the `labels.jsonl` key, and every
  existing reader work untouched; `source` is what a reader tests.
- **Still stdlib** ([[D-005]]). Range support is about forty lines of `http.server`.
- **The extension is untouched** ([[D-006]]).

## Verified

Driven in a browser against a disposable copy of the store, so the real
`runs/` and `labels.jsonl` were never written to.

- Range: 206 for `bytes=0-99`, open-ended and suffix forms; 416 with `Content-Range`
  for an unsatisfiable range; 200 with `Accept-Ranges` when no range is asked for;
  served bytes hash-identical to the file. Traversal attempts (`..`, encoded `..`,
  a non-media file, a sibling of `media/`) all 404.
- A run with a VTT: cues, gap flags, row click seeking to the exact second, timeline
  rail scrub, follow tracking the playhead, `<`/`>` rate stepping with the label in
  sync, arrows / digits / Home / End / `m` / space.
- A run with no transcript: empty grid, `n` at the playhead opened the composer at
  0:27, and the submitted clip landed in `labels.jsonl` as a `miss` event at 27.0.
- In-app ingest of a path containing spaces and parentheses: sanitised symlink name,
  title preserved, served and played.
- A YouTube run with `{videoId}.mp4` present resolved to the local file with no change
  to the run record; removing the file restored the embed.
- Regression: video 1 still loads on the real store with a clean console — 64 markers,
  21 added, 24 extracted, 1464 cues, counts matching `CURRENT.md`.

**Found and fixed during verification:** deferring the IFrame API load until a
YouTube run opens widened the window in which the 250ms follow poll calls
`getDuration()` before any player exists. `getDuration`, `seekRaw` and `toggleMute`
now guard on readiness the way the local branch already did.

## Not in scope

Silence-gap detection without a transcript (needs ffmpeg), local transcription,
an `<audio>` element for audio-only files (they play in the video element), and any
change to the copy-timestamps fold ([[D-022]]).
