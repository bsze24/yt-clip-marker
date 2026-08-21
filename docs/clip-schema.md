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
| `lane` | string | Chapter lane (e.g. `transcription`). Freeform. **Deprecated 2026-08-21** — no longer collected. Existing values are still read and still print, so nothing already recorded is lost. |
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

## Run-level `work`  (2026-08-21)

`work` was stored on every clip and never varied like clip data: across 193 annotated rows it
changed 5 times on one video and **0** on the other two, where the same string was recorded 75
times. It is lesson metadata, not clip metadata.

It now lives once per run. Because `runs/{id}.json` is immutable ingest output ([[D-002]]) it
cannot be written there, so it is a label event — `verdict: "chapter"`, latest wins — and the
server resolves it on read and returns it as `runWork` on `/api/run`. Same shape as media
([[D-034]]).

```json
{"verdict": "chapter", "runId": "...", "work": "Pennies from Heaven | Stan Getz"}
```

**A clip's own `work` still wins.** One lesson covering two pieces is normal — video 1 does
exactly that, and its export keeps both section headers. The run-level value is the default for
every clip that does not say otherwise, which is now every newly added clip.

Consumers should read `clip.work || run.work`.
