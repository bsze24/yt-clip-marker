# Clip Studio

The clipper's annotating surface and workspace (see `docs/youtube-clip-marker-prd.md` for the two-surface model). A local stdlib server + one page: time-aligned grid of captions, markers, and published YouTube-description timestamps, with keyboard-first clip creation and a work / lane / tags taxonomy.

It began as an eval harness for the yt-clipper skill; the skill-scoring chrome (check/note feedback, rationales) now lives behind the **eval mode** header toggle.

## Run

```
python3 apps/studio/server.py
```

Open http://127.0.0.1:8765. Ingest needs `yt-dlp` on PATH.

## Layout

```
apps/studio/
  server.py                             HTTP server + label-event store
  ingest.py                             URL → captions, gaps, description, extracted → run file
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
    player.js                           YouTube IFrame wrapper, focus management
    runs.js                             run list polling + switching
    api.js                              fetch wrapper + save-failure surface
    util.js                             pure helpers, constants
    styles.css
  runs/{videoId}-{YYYYMMDD-HHMM}.json   ingest/model output + caption cues (immutable)
  labels.jsonl                          append-only human judgments
  attach_cues.py                        CLI: merge a fetch_transcript.py dump into a run
  attach_extracted.py                   CLI: attach or migrate YT description timestamps
```

UI files are read from disk on every request and sent with `Cache-Control: no-store`, so HTML/JS/CSS edits show on a browser refresh — only `server.py`/`ingest.py` changes need a server restart.

The durable record is git-tracked JSON here. Commit `runs/` and `labels.jsonl` to back up work. The append-only labels can later score a new skill version against `check` labels, or train auto-mark from `(videoId, start, description, verdict)`.

A run's `cues` array is the YouTube caption track; `gapBefore` on a cue is seconds of silence before it (a likely playing/demo boundary). `extracted[]` holds timestamps parsed from the public YouTube description. A `gold[]` key is a visible load fault, not an alias; migrate it with `attach_extracted.py`. The grid time-aligns all three: caption, marker, and extracted share a row when their starts are within 2 seconds. Selection is by **row identity**, not start time — duplicate timestamps are real.

Runs come from two doors:

1. **In-app ingest** — paste a URL in the header (`POST /api/ingest`). Writes a run with an empty `markers` array: transcript skeleton, no markers yet.
2. **The yt-clipper skill** (`~/.claude/skills/yt-clipper/`) — proposes candidate markers and writes a run with `markers` filled, using the attach CLIs above.

## Label event (`labels.jsonl`)

One JSON object per line. Every save appends; the latest event for a row identity — `(runId, markerIndex)` for markers, `(runId, start)` for added clips — is current. History is kept so revisions are recoverable.

**"Latest" means the last matching line in the file, not the largest `recordedAt`.** The server folds in file order everywhere and never sorts by time. `recordedAt` is stamped while the event is built, before the write lock is taken, so two events written within a few milliseconds can land in the opposite order from their timestamps — video 1's store has three such pairs. Anything reading this log from outside the studio, such as a skill-scoring pass, must read top to bottom and take the last match. Sorting by `recordedAt` will eventually pick the wrong record.

| Field | Point |
|---|---|
| `schemaVersion` | `1` |
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
| `verdict` | `check` \| `wrong` \| `note` \| `blank` \| `miss` \| `unmiss` \| `relabel` \| `annotate` |

`relabel` events store `originalDescription` (suggester output, never mutated on the run file) and `description` (your edit). Latest relabel for `(runId, markerIndex)` is the current label; the grid shows `original: …` under the field when they differ.

`miss` is a human-added clip (the verdict name is legacy eval vocabulary; the UI says "added clip"). `unmiss` is a tombstone for that `(runId, start)` — last event wins, so delete does not rewrite history.

`annotate` stamps `tags` / `lane` / `work` on a marker (`markerIndex`). Latest wins. Added clips store those fields on the `miss` event.

Each line is a standalone example. You do not need the run file to score it.
