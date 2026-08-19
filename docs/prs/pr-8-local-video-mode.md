# PR 8 — Local video mode

> **On the number.** GitHub assigned this **#8**; #7 went to a Codex session-log PR that was
> closed as redundant. The three product commits on this branch are titled `PR 7:` because they
> were written before the PR existed. They are pushed, and rewriting published history to fix a
> label is not worth a force-push — the docs are the corrected reference, the commit titles are
> not.

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
- `apps/studio/prefetch.py` (new) — `prefetch.py <url>` downloads the video, its
  captions and its metadata, then ensures a run exists. The offline path assumes
  yt-dlp is the door, so the door is one command rather than a memorised flag soup.
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
- `prefetch.py` end to end against a real YouTube video: media, `en` captions and
  `.info.json` down, run built with the real video id, real title, real watch URL,
  6 cues and 3 extracted markers, playing in the browser from `/media/`. The rerun
  took the already-exists branch and wrote nothing.

**Found and fixed during verification:** deferring the IFrame API load until a
YouTube run opens widened the window in which the 250ms follow poll calls
`getDuration()` before any player exists. `getDuration`, `seekRaw` and `toggleMute`
now guard on readiness the way the local branch already did.

## Two yt-dlp findings, both fixed in `prefetch.py`

Neither is a defect in this repo, but the offline path depends on both and they cost
an hour to find.

1. **`--sub-langs "en.*,en"` over-fetches.** On a real lesson the only tracks are
   `en-orig` and `en`; the wildcard also pulled auto-translated `en-en` and `en-de`,
   and a 429 on the third of them failed the entire download. Narrowed to
   `en-orig,en`, and success is now judged by whether the media file landed rather
   than by yt-dlp's exit code — one failed subtitle track must not discard a video
   that downloaded fine. `ingest.py` carries the same wildcard but is unaffected: it
   checks for the file rather than the return code, and never downloads media.
2. **The default player client 403s.** `android_vr` lists every format and then
   returns URLs that answer 403 Forbidden for the stream itself. `web_embedded`
   offers the same format list and works; `mweb` works but only offers 360p. Pinned
   as `PLAYER_CLIENTS`, with the re-derivation recipe in the comment, because this
   will rot.

Separately, and outside the repo: yt-dlp installed via Homebrew has no `curl_cffi`,
so it cannot impersonate a browser. Installing one *in the supported range* fixes
it — 0.16 is silently ignored and reported as `(unsupported)` only under `--verbose`.

## Not in scope

Silence-gap detection without a transcript (needs ffmpeg), local transcription,
an `<audio>` element for audio-only files (they play in the video element), and any
change to the copy-timestamps fold ([[D-022]]).
