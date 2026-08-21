# The clip — shared contract

The one record both surfaces (and eventually media-scraper) agree on. Share the clip, not the screen: the extension and the studio never share panel/hotkey/grid code, only this shape.

## Clip

```json
{
  "videoId": "YYW4Q1Nivg8",
  "start": 12.5,
  "end": null,
  "description": "The Stand solo playthrough",
  "work": "The Stand | Jake rendition",
  "lane": "transcription",
  "tags": ["take", "star"]
}
```

| Field | Type | Notes |
|---|---|---|
| `videoId` | string | 11-char YouTube id. Video identity; `videoUrl`/`videoTitle` are denormalized alongside where useful. |
| `start` | number | Seconds. Required. |
| `end` | number \| null | Seconds. Nullable — markers and coarse captures are start-only; ranges get filled in during studio refinement. |
| `description` | string | The human label. May be empty at capture time. |
| `work` | string | What piece/rendition the clip belongs to, e.g. `Song` or `Song \| Rendition`. Freeform. **Usually empty on clips written after 2026-08-21** — it is set once per lesson and resolved from the run instead (see below). A clip that carries its own value still wins. |
| `lane` | string | Chapter lane (e.g. `transcription`). Freeform. **A section property since 2026-08-21** — set once per section, resolved from the run, no longer written per clip. |
| `tags` | string[] | Lowercase, deduped. Seeded vocabulary: `take`, `fingering`, `technique`, `star`; freeform additions allowed. |

Legacy: `kind` (`TAKE` \| `CONCEPT`) appears on old markers and old label events. Readable forever, never required on new writes.

## Where clips live today

The studio store is the source of truth (the extension holds marks in memory only):

- `apps/studio/runs/{videoId}-{YYYYMMDD-HHMM}.json` — immutable ingest/model output per video: `videoId`, `url`, `title`, `createdAt`, `markers[]` (suggester output; may be empty), `cues[]` (caption track, `gapBefore` = seconds of silence before the cue), `descriptionText` + `extracted[]` (published YT description timestamps). A `gold[]` key is a visible load fault, not an alias; migrate it with `attach_extracted.py`. A run ingested from a file on disk carries two more keys — `source: "local"` and `media` (the file name under `apps/studio/media/`) — and its `videoId` is a filename-derived id rather than an 11-char YouTube one whenever no `.info.json` sidecar supplied a real one. Readers that need to know which they hold should test `source`, not the shape of `videoId`.
- `apps/studio/labels.jsonl` — append-only human events keyed by `(runId, markerIndex)` for skill markers and `(runId, start)` for added markers. Latest event wins; deletes are tombstones (`unmiss`). Full event field list: `apps/studio/README.md`.

**Reading `verdict` across the 2026-08-18 vocabulary change.** `wrong` became a verdict on
2026-08-18. Events written before that date record a rejected marker as `verdict: "note"` with
`feedback` beginning `wrong` or `wrong:`; events after record `verdict: "wrong"`. History is not
backfilled. Video 1's store is entirely pre-change: 121 of its 193 `note` events are rejects, and
none carries `verdict: "wrong"`.

So any reader outside the studio must derive the channel from `feedback` text, not from the
stored `verdict`. The studio itself already does — `list_runs` recomputes with `verdict_for()` on
every read, which is why its counts are right on old data. `schemaVersion` tells you which regime
a line is in: `1` means derive from text, `2` means the stored `verdict` is authoritative.

**And "latest" means the last matching line, not the largest `recordedAt`.** See the file-order
note in `apps/studio/README.md`.

A "current clip set" for a video is a fold over the run file plus its label events. Don't over-specify this store — it's JSONL until it hurts.

## Exports (future studio buttons)

1. **Description timestamps** — `M:SS Title` lines, ends dropped. YouTube auto-links them. Primary near-term output.
2. **JSON for media-scraper** — array of clip objects as above plus `videoUrl`/`videoTitle`. **Draft** — freeze when the export button lands, not before. Keep it generic enough that a future PKM could ingest clips alongside other annotated content.

## `work` and `lane` are section breaks, not clip fields  (2026-08-21)

`work` was stored on every clip and never behaved like clip data. On video 1 it changed twice
across 67 rows and the string was written on all 67; on video 2 one value was stored 75 times.
A lesson covering two pieces is normal — it is a *section*, and sections have boundaries.

A work change is now one event at a timestamp, on the run. Because `runs/{id}.json` is
immutable ingest output ([[D-002]]) it lives in `labels.jsonl`:

```json
{"verdict": "chapter", "start": 0,    "work": "Pennies from Heaven | Stan Getz",     "lane": "Transcription"}
{"verdict": "chapter", "start": 4582, "work": "Eb Blues | 1 bar, 1 chord exercise", "lane": "Melodic harmony"}
```

`lane` rides the same break. On video 1 the two change at **exactly the same two timestamps**,
which is the tell that they are one thing: a section has a piece and a mode. `lane` was going to
be deprecated when it was a per-clip field costing a keystroke per marker; as a section property
it costs one entry per section, so it stays.

Two events for video 1 instead of 67 copies. Latest event per `start` wins. A break is removed
only when **both** `work` and `lane` are empty — clearing one leaves the other, because a
lane-only section is a state this design supports. Every writer must therefore send the complete
pair; sending `{start, work}` alone blanks the lane it shares the break with.

**A clip's work is resolved, never stored** — the latest break at or before its start.
`/api/run` returns `sections` as `[[start, work, lane], ...]` ascending; consumers resolve from
that. `clip.work` and `clip.lane` still appear on events written before this date and are no
longer read.

Set the lesson's piece once in the header. When it changes, `Tab` then `w` on the row where it
changes — the field is labelled *changes work from here* and is prefilled with what is currently
in effect, so you can see what you are overriding. `Tab` then `l` does the same for the lane, on
the same break.
