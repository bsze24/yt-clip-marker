# Clipper — Two-Surface PRD

Supersedes the one-surface V1 PRD (Chrome-extension-as-IDE). Side project to media-scraper; media-scraper consumes clips via export only, never shared code. Background on how the model changed: `docs/two-surface-handoff.md`.

## Problem (unchanged)

BZ records sprawling music lessons (30–90 min) and wants to process them ~10x faster. Three pain points compound:

1. **Ingestion.** Exporting recordings, uploading to YouTube, indexing the library. (Lightest; ideally automated later.)
2. **Capture friction.** Watching → catching a moment → switching tabs → editing the description → typing timestamps → returning. (Heaviest.)
3. **Refinement friction.** Nailing clip boundaries takes three to five rewatches per mark.

Net effect: a growing backlog of unannotated videos, and lessons lost to time.

## Product model — one clipper, two surfaces

The V1 PRD assumed annotation happens *on the YouTube watch page*. Building the eval dashboard falsified that: YouTube is a hostile editor (owns `j`/`k`/`space`, CSS fights injected UI, SPA nav remounts content scripts), and the dense grid + taxonomy workflow that actually emerged does not belong there. The dashboard ate the product.

So the product is **one clipper with two clients of one clip record**:

- **Studio** (`apps/studio/`) — the annotating surface and the workspace. A local web app: time-aligned grid of captions, skill markers, added markers, and extracted markers (published YouTube-description timestamps), with keyboard-first clip creation and a taxonomy (work / lane / tags). This is where the PRD's old "refinement" and "export" jobs live.
- **Extension** (`apps/extension/`) — the viewing surface. A thin client on the YouTube watch page: optional coarse capture (`[` / `]`) while watching naturally. It is frozen at that scope — it is not a store, not an editor, and does not grow taxonomy, transcript, or export features.

They share the **clip contract**, not code or screen:

```json
{ "videoId": "…", "start": 12.5, "end": null, "description": "…",
  "work": "Song | Rendition", "lane": "transcription", "tags": ["take", "star"] }
```

`end` is nullable — markers and quick captures are often start-only; ranges are filled in during studio refinement. Full schema and storage notes: `docs/clip-schema.md`.

## Design principles

1. **10x the manual annotation process.** One careful watch (or less — see ingest) should produce publishable timestamps.
2. **A single careful pass in the studio is sufficient.** The grid, the embedded player, and keyboard nav replace manual scrubbing. If the user has to rewatch to find a boundary, the tool has failed.
3. **The transcript is the map.** An empty 90-minute timeline is the old linear watch. Ingest gives every video a caption-grid skeleton before any human or model marker exists.
4. **Append-only truth.** Human judgments are events in `labels.jsonl`; the latest event for a row identity wins. Delete is a tombstone, not a rewrite.

## Users

Just BZ. Single user, single machine, no auth, no sync.

## Surface 1: Studio (the workspace)

Today's `eval/` app, promoted. Python stdlib server (`python3 apps/studio/server.py` → http://127.0.0.1:8765) + one HTML page. No framework, no build step, no database.

### Already built (keep; this is the product)

- **Time-aligned grid.** Captions, skill markers, and extracted markers (published YT description timestamps) share a row when starts are within 2s. Row selection is by **row identity**, not start time (duplicate timestamps broke start-keyed selection).
- **Keyboard-first flow.** `j`/`k` row nav (selects + seeks), `Enter` add/edit clip, `Tab` then `t`/`w`/`l`/`y` for tags/work/lane/why, `x` reject a skill marker or delete an added marker, `f` follow, `space` play/pause.
- **Taxonomy.** `work` (Song | Rendition), `lane` (chapter lane), `tags` (multi, freeform + seeded vocabulary) — replacing exclusive TAKE/CONCEPT.
- **YouTube IFrame embed** — YouTube as *player*, never as IDE.
- **Store.** `runs/{videoId}-{stamp}.json` (immutable model/ingest output) + `labels.jsonl` (append-only human events).

### New in this refactor

- **In-app ingest.** Paste a YouTube URL in the studio → server fetches the caption track and description via `yt-dlp`, flags silence gaps, parses extracted markers from the description, writes a run file with an **empty markers array**, and opens it. The skill runbook is no longer the only door; a video can be annotated with only added markers.
- **Eval mode (toggle, default off).** Check/note feedback, rationales, and check/note stats are skill-eval chrome, not the annotation loop. They stay available behind a header toggle until the suggester is trusted (~5 labeled videos), then we revisit removal.
- **`kind` optional.** `TAKE`/`CONCEPT` remains readable on old markers but is never required on new writes. Tags/lane/work carry the taxonomy.

### Next (in priority order, not this refactor)

Living list: `docs/coordination/BACKLOG.md`. Snapshot at the two-surface lock:

1. **End collection.** Ranges (`end`) settable from the grid — required before reel-oriented export is useful.
2. **JSON export.** Copy as JSON (the media-scraper seam). Freeze the schema when this lands ([[D-015]]). Description-timestamp copy already shipped in PR 3 (`apps/studio/ui/export.js`, [[D-022]]).
3. **Suggest-markers as a studio action** (currently a Claude-skill invoke; see below).

## Surface 2: Extension (thin client, frozen)

What exists after PR 2, kept as is:

- Loads on `youtube.com/watch` pages only.
- Shadow-DOM panel; `[` marks start (−5s backdate, toast), `]` marks end (no pause) and opens an optional description input; marks list in the panel. In-memory only.

**Explicitly frozen — do not build (supersedes the original PR 3 / PR 4 plans):**

- `chrome.storage.local` as a canonical store (the studio's JSONL is the source of truth; the extension must not become a second store).
- Refinement hotkeys, boundary nudging, click-to-preview-as-editor, taxonomy, transcript display.
- Export from the panel.
- SPA-navigation remounting and persistence work whose only purpose was the on-YouTube IDE.

**Future (unblocked, unscheduled):** a "send to studio" handoff — captured coarse marks flow into the studio's store for refinement (clipboard JSON or localhost POST; decide when it hurts). Until then the extension is a capture scratchpad and the studio is where real annotation happens.

## The skill (suggester, not workflow)

`~/.claude/skills/yt-clipper` keeps one job: **propose candidate markers** (the rule IDs, "over-include", label-in-user-vocabulary prompt). The engineering it used to carry moves into the app:

- Transcript fetch / gap flagging / extracted-marker attachment → studio ingest.
- Eval bookkeeping (`check`/`note`, rationales) → studio eval mode.

Invoking the skill still writes markers into a run file the studio reads. When ingest is trusted, "Suggest markers" becomes a studio action and the skill file remains the prompt/rules source.

## Downstream

- **media-scraper** — consumes the studio's JSON export (reels, auto-suggest). Export contract only; media-scraper never lives in this tree. Schema draft in `docs/clip-schema.md`; frozen when the export button lands.
- **Description timestamps** — `M:SS Title` lines pasted into YouTube descriptions remain the primary near-term output.
- **PKM adjacency** — keep the clip JSON generic (video identity + range + labels); don't over-fit to YouTube.

## Decisions log (handoff's open questions, answered)

Living ledger (don't silently revise): `docs/coordination/DECISIONS.md`. Table below is the two-surface lock; later refinements (row identity, copy-timestamps fold, eval channels) live there.

| Question | Decision |
|---|---|
| How thin is the extension? | Keep load-on-watch + `[` `]` coarse capture (already built, zero-cost to keep); freeze there. Not handoff-only, not an editor. |
| Suggest-markers: studio action or skill invoke? | Stays a skill invoke for now; in-app ingest lands first so runs exist without the skill. |
| Eval chrome now or later? | Behind an eval-mode toggle, default off. Revisit removal after ~5 labeled videos. |
| Collect `end` now? | Not in this refactor. Schema keeps `end` nullable; end collection is the studio's next feature. |
| Extracted-marker column? (was: gold) | Keep — published YT description timestamps as a reference lane (and eval target while eval mode exists). |
| Rename layout? | `apps/extension/` + `apps/studio/`. No `schema/` folder until shared code exists; the contract lives in `docs/clip-schema.md`. |
| Freeze media-scraper JSON? | Draft now, freeze when the studio export button lands. Don't block the split on it. |
| Canonical store? | Studio: `runs/` + `labels.jsonl`. The extension stays storeless. |

## Explicit non-goals

- Voice input; YouTube Data API write-back; sync across devices; mobile / in-car; Shorts / playlists / embedded players; multi-user.
- Formal YouTube chapter-rule validation (if marks happen to satisfy the rules, chapter use works as a side effect).
- Live-video annotation (in-flight calls/streams) — a different product; V1+ assumes the recording exists and can be reviewed.
- A framework/database/deploy story for the studio. Local stdlib server + JSONL until it actually hurts.

## Done criteria for this refactor

1. Repo layout is `apps/extension/` + `apps/studio/`; extension still loads unpacked from `apps/extension` with no manifest warnings.
2. `python3 apps/studio/server.py` boots the studio; existing runs and labels load unchanged.
3. Studio UI says studio, not eval; check/note/rationale visible only with eval mode on.
4. Pasting a YouTube URL into the studio creates and opens a run (cues + gaps + extracted markers, empty `markers[]`) with no CLI steps.
5. New label events never require `kind`.
6. AGENTS.md, README, and PR specs describe the two-surface model — a fresh agent session would not rebuild the on-YouTube IDE.
