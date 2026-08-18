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
| `work` | string | What piece/rendition the clip belongs to, e.g. `Song` or `Song \| Rendition`. Freeform. |
| `lane` | string | Chapter lane (e.g. `transcription`). Freeform. |
| `tags` | string[] | Lowercase, deduped. Seeded vocabulary: `take`, `fingering`, `technique`, `star`; freeform additions allowed. |

Legacy: `kind` (`TAKE` \| `CONCEPT`) appears on old markers and old label events. Readable forever, never required on new writes.

## Where clips live today

The studio store is the source of truth (the extension holds marks in memory only):

- `apps/studio/runs/{videoId}-{YYYYMMDD-HHMM}.json` — immutable ingest/model output per video: `videoId`, `url`, `title`, `createdAt`, `markers[]` (suggester output; may be empty), `cues[]` (caption track, `gapBefore` = seconds of silence before the cue), `descriptionText` + `extracted[]` (published YT description timestamps). A `gold[]` key is a visible load fault, not an alias; migrate it with `attach_extracted.py`.
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
