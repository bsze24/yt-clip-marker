# Clip Studio

The clipper's annotating surface and workspace (see `docs/youtube-clip-marker-prd.md` for the two-surface model). A local stdlib server + one page: time-aligned grid of captions, markers, and published YouTube-description timestamps, with keyboard-first clip creation and a work / lane / tags taxonomy.

It began as an eval harness for the yt-clipper skill; the skill-scoring chrome (check/note feedback, rationales) now lives behind the **eval mode** header toggle.

## Run

```
apps/studio/studio install     # once — writes and loads a launchd agent
apps/studio/studio open        # app window, starts the server if needed
apps/studio/studio app          # builds the dockable app icon beside this script
```

`app` builds `apps/studio/Clip Studio.app` — a real double-clickable bundle
that just runs `studio open`, so it needs no Chrome menu and survives Chrome
changing its UI. Drag it to the Dock, but leave the bundle in this checkout:
its launcher finds `studio` relative to itself, so moving the whole repo keeps
the icon working. Do not copy the bundle into `~/Applications`.

The header's **quit** button stops the server for real: it boots the launch
agent out before exiting, because `KeepAlive` would otherwise restart it a
second later and the button would look broken. Reopen with `studio open`, which
bootstraps a booted-out agent rather than only kickstarting a loaded one.

`install` registers a launch agent that starts the studio at login and restarts
it whenever it exits, so a crash or a stray `kill` does not take it down. `open`
points a Chrome app window at it — dock icon, no URL bar, closest thing to a
native app for a local web app. Also `start`, `stop`, `restart`, `status`,
`logs`, `uninstall`; logs go to `~/Library/Logs/yt-clip-studio.log`.

**Moving the repo is handled.** The app bundle moves with the checkout and finds `studio`
relative to itself. The launch agent still bakes in an absolute path, so `studio status` warns
and `studio open` reinstalls it from wherever the script now lives.

**`/api/quit` and `/api/ingest` require a same-origin JSON request.** Binding to 127.0.0.1 is
not an authorization boundary — any web page can submit a plain form to a fixed localhost URL,
and it needs no CORS permission because it never reads the response. Before the guard, a form
POST carrying `Origin: https://unrelated.example` stopped the server.

**Use `studio restart` after editing `server.py`.** `KeepAlive` means `pkill`
just makes launchd start it again. `index.html` and everything in `ui/` are read
from disk on every request, so those changes only need a browser refresh.

The URL is **http://studio.localhost:8765**. Chrome resolves any `*.localhost`
name to 127.0.0.1 with no hosts-file entry and no sudo, so this needs no setup
and is easier to type than the numbers. `http://127.0.0.1:8765` still works.

To run it in the foreground instead — handy when you want the traceback on
screen — `python3 apps/studio/server.py`, after `studio stop`. Ingesting a YouTube URL needs `yt-dlp` on PATH and network.
Ingesting a file already on disk needs neither — see **Local video mode** below.

## Layout

```
apps/studio/
  studio                                start/stop/open as an app (launchd agent)
  server.py                             HTTP server + label-event store
  ingest.py                             URL → captions, gaps, description, extracted → run file
  uploads.py                            background yt-dlp refresh → uploads.json cache
  local.py                              file on disk + sidecars → run file (no network)
  index.html                            markup only; loads /ui/ assets
  ui/                                   ES modules + stylesheet, served via the
                                        allowlisted /ui/ route (no build step)
    main.js                             entry: event wiring + boot
    keys.js                             global keydown dispatcher (priority contexts)
    state.js                            shared mutable state object (S)
    grid.js                             row building, alignment, selection, rendering
    suggest.js                          taxonomy vocab, dropdown, tag chips
    composer.js                         add-clip form logic
    persist.js                          all server writes + debounces
    player.js                           YouTube embed + local <video>, one interface
    runs.js                             run list polling + switching
    api.js                              fetch wrapper + save-failure surface
    util.js                             pure helpers, constants
    styles.css
  runs/{videoId}-{YYYYMMDD-HHMM}.json   ingest/model output + caption cues (immutable)
  tests/test_sidecars.py                stdlib unittest: sidecar matching, F18 + F20 regressions
  labels.jsonl                          append-only human judgments
  uploads.json                          derived YouTube upload listing (gitignored)
  media/                                video/audio files for offline playback (gitignored)
  attach_cues.py                        CLI: merge a fetch_transcript.py dump into a run
  attach_extracted.py                   CLI: attach or migrate YT description timestamps
```

UI files are read from disk on every request and sent with `Cache-Control: no-store`, so HTML/JS/CSS edits show on a browser refresh — only `server.py`/`ingest.py` changes need a server restart.

The durable record is git-tracked JSON here. Commit `runs/` and `labels.jsonl` to back up work. The append-only labels can later score a new skill version against `check` labels, or train auto-mark from `(videoId, start, description, verdict)`.

A run's `cues` array is the caption track; `gapBefore` on a cue is seconds of silence before it (a likely playing/demo boundary). `transcriptSource` names where that track came from — the sidecar filename for a local run, the yt-dlp track name (`{id}.en-orig.json3` vs `{id}.en.json3`) for a URL run, and `""` for a run with no transcript. Runs written before 2026-08-21 do not carry the key; treat it as absent, not empty. `extracted[]` holds timestamps parsed from the public YouTube description. A `gold[]` key is a visible load fault, not an alias; migrate it with `attach_extracted.py`. The grid time-aligns all three: caption, marker, and extracted share a row when their starts are within 2 seconds. Selection is by **row identity**, not start time — duplicate timestamps are real.

Runs come from two doors:

1. **In-app ingest** — paste a URL in the header (`POST /api/ingest`). Writes a run with an empty `markers` array: transcript skeleton, no markers yet.
2. **The yt-clipper skill** (`~/.claude/skills/yt-clipper/`) — proposes candidate markers and writes a run with `markers` filled, using the attach CLIs above.

The run picker also lists cached YouTube uploads that do not have a run yet. Picking one fills
the Add video field; it never starts ingest on its own. The listing comes from the channel's
uploads playlist through Chrome's YouTube login and is refreshed in one background thread at
startup and every 30 minutes. HTTP requests only read `uploads.json`, so a slow connection,
expired login, or fully offline start cannot delay the Studio. A failed refresh keeps the last
good cache and its visible age. `GET /api/uploads` returns an empty successful response when no
valid cache exists because the listing is optional, while the runs remain the workspace. Refresh
repairs a malformed row without forgetting its valid neighbours, and an authenticated result
smaller than half the prior cache is treated as partial: it merges and logs instead of pruning.

For a local run, the **YouTube link** control writes an append-only `link` event. Enter an
11-character id, paste a watch URL, or choose from the duration-ranked cached candidates; saving
an empty field explicitly clears the fallback. Local media still plays first. The cached YouTube
title is joined on read into the picker and lesson header, so the lesson is renamed on YouTube in
one place and the immutable run file is never edited.

## Label event (`labels.jsonl`)

One JSON object per line. Every save appends; the latest event for a row identity — `(runId, markerIndex)` for markers, `(runId, start)` for added clips — is current. History is kept so revisions are recoverable.

**"Latest" means the last matching line in the file, not the largest `recordedAt`.** The server folds in file order everywhere and never sorts by time. `recordedAt` is stamped while the event is built, before the write lock is taken, so two events written within a few milliseconds can land in the opposite order from their timestamps — video 1's store has three such pairs. Anything reading this log from outside the studio, such as a skill-scoring pass, must read top to bottom and take the last match. Sorting by `recordedAt` will eventually pick the wrong record.

| Field | Point |
|---|---|
| `schemaVersion` | `1` on legacy events; `2` on current writes |
| `recordedAt` | ISO-8601 with offset |
| `runId` | filename stem of the run |
| `videoId` / `videoUrl` / `videoTitle` | YouTube identity |
| `markerIndex` | row in that run (null for added clips) |
| `start` / `end` | seconds (`end` may be null) |
| `kind` | legacy skill `TAKE` / `CONCEPT`; never required on new writes |
| `tags` | `take` \| `fingering` \| `technique` \| `star` plus freeform additions (multi) |
| `lane` | chapter lane, freeform (`transcription`, …) |
| `work` | `Song` or `Song \| Rendition` |
| `description` | clip label |
| `rationale` | rule citation from the skill (eval) |
| `ruleIds` | parsed `R-*` ids from rationale (eval) |
| `feedback` | raw text: `check` or `check: why` = good; `wrong` or `wrong: reason` = reject; anything else = eval note |
| `verdict` | `check` \| `wrong` \| `note` \| `blank` \| `miss` \| `unmiss` \| `relabel` \| `annotate` \| `chapter` \| `link` |

`relabel` events store `originalDescription` (suggester output, never mutated on the run file) and `description` (your edit). Latest relabel for `(runId, markerIndex)` is the current label; the grid shows `original: …` under the field when they differ.

`miss` is a human-added clip (the verdict name is legacy eval vocabulary; the UI says "added clip"). `unmiss` is a tombstone for that `(runId, start)` — last event wins, so delete does not rewrite history.

`annotate` stamps `tags` / `lane` / `work` on a marker (`markerIndex`). Latest wins. Added clips store those fields on the `miss` event.

`link` carries `youtubeId` and `source: "human-link"`, keyed by `runId`. Latest wins; an empty
`youtubeId` is a deliberate clear. It never shares the `chapter` fold, because clearing a link
must not erase the lesson-level work/lane section at zero.

Each line is a standalone example. You do not need the run file to score it.

## Local video mode

Playback prefers a plain `<video>` element fed by the studio's own `/media/` route,
so a session works with no network at all. Nothing switches modes by hand: a run
plays locally when a matching file sits in `media/`, and falls back to YouTube when
its immutable watch URL supplies a valid YouTube id. A raw local run has neither;
if its file disappears, it warns and leaves the player empty rather than sending
its filename-derived `videoId` to the embed.

**Attaching a file to an existing YouTube run.** Name it after the video id and drop
it in — `media/YYW4Q1Nivg8.mp4` is the whole step. The match is computed on every
read of `/api/run`; the run file is never rewritten, so an immutable ingest record
stays immutable (D-002) and removing the file simply restores the embed.

**Ingesting a file that has no YouTube run.** Paste a path (or a bare name already in
`media/`) into the same header field the URL goes in. `local.py` picks up sidecars
that share the file's stem:

| Sidecar | Comes from | Becomes |
|---|---|---|
| `.json3` | `yt-dlp --sub-format json3` | `cues[]` with `gapBefore` flags |
| `.vtt` | yt-dlp, or a Zoom **cloud** recording | same, parsed from WebVTT |
| `.srt` | anything | same |
| `.info.json` | `yt-dlp --write-info-json` | real `videoId`, title, description, `extracted[]` |

With no `.info.json` the video id is synthesised from the filename and the run
records `source: "local"`. With no subtitle sidecar the run has zero cues — a
supported state, not a failure: press `n` to drop a marker at the playhead, since
there are no caption rows to press Enter on.

Files outside `media/` are symlinked into it rather than copied, and the symlink name
is sanitised. `/media/` serves bare filenames from that one directory only.

**Preparing for an offline session**, while you still have network:

```
python3 apps/studio/prefetch.py <url-or-id> [<url-or-id> ...]
```

Per video that downloads the media, its `en-orig`/`en` captions as `.json3`, and
`.info.json`, then makes sure a run exists — building one only if no run for that
video id is already in `runs/`, since an existing run picks the file up by id on its
own. Rerunning it is cheap and idempotent.

Two flags in there are load-bearing rather than cosmetic:

- **Format.** `avc1` + `mp4a` in MP4. Chrome seeks H.264/AAC far more reliably than
  the VP9 or AV1 streams yt-dlp otherwise prefers, and seeking is the whole job.
- **Player client.** `web_embedded,mweb`. On 2026-08-19 yt-dlp's default choice
  (`android_vr`) listed every format and then answered **403 Forbidden** for the
  actual stream. This is cat-and-mouse and will rot; `PLAYER_CLIENTS` in
  `prefetch.py` carries the note on how to re-derive it, and updating yt-dlp is the
  real fix.

If media downloads fail with 403 even so, check that yt-dlp can impersonate a
browser — `yt-dlp --list-impersonate-targets`. A Homebrew install ships without
`curl_cffi`, and yt-dlp silently ignores a version outside the range it supports
(`0.5.10`, or `0.10.x` through `0.15.x` as of 2026.07.04), reporting it as
`(unsupported)` under `--verbose`.

**Zoom.** Only *cloud* recordings produce a transcript, and only on a paid plan with
"Create audio transcript" enabled; local recordings have none unless "Save closed
caption as a VTT file" was on. Plan on the zero-cue path for anything recorded to
your own disk.

A cloud export drops three files with names that do not share a stem:

```
GMT20260730-155336_Recording_640x360.mp4     the video, with a resolution suffix
GMT20260730-155336_Recording.m4a             audio only
GMT20260730-155336_Recording.transcript.vtt  the transcript
```

Point the ingest at the `.mp4` (or the `.m4a`) and the transcript is found anyway:
sidecar matching also tries the stem with a trailing `_{W}x{H}` and a browser's
`" (1)"` duplicate marker removed. The `.` boundary rule from F18 still applies to
every variant, so `Talk_640x360.mp4` picks up `Talk.transcript.vtt` but never
`Talk2.vtt`.

A Zoom transcript is usually the *better* artifact: it carries speaker names, which
YouTube's auto-captions do not, and it exists as soon as the recording processes
rather than whenever YouTube gets round to it.
