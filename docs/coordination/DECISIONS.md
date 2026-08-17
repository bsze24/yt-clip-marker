# Decisions

Accepted decisions that outlive a single task. **IDs are stable — never renumber**;
supersede with a new dated entry rather than editing in place. Grouped by type
(the section is the decision's "type").

Harvested 2026-08-16 from the two-surface PRD, `AGENTS.md`, and the video-1 use-as-design
pass (`docs/sessions/2026-08-16-1507-claude-studio-eval-handoff.md`). Don't relitigate
silently — if a later session contradicts one of these, write a dated refinement.

## Principles — cross-cutting commitments

### D-001 — One clipper, two surfaces  (Accepted 2026-08-14)
Viewing (YouTube) and annotating (studio) are two clients of one clip record. They share
the clip contract (`docs/clip-schema.md`), never panel/hotkey/grid code. media-scraper is
downstream via JSON export only — it never lives in this tree. Related: [[D-006]], [[D-007]].

### D-002 — Append-only truth  (Accepted 2026-08-14)
`runs/{id}.json` is immutable ingest/model output. `labels.jsonl` is append-only human
events. Latest event per row identity wins; deletes are tombstones (`unmiss`). Never rewrite
history in place. Where that store lives: [[D-007]].

### D-003 — The transcript is the map  (Accepted 2026-08-14)
An empty 90-minute timeline is the old linear watch. Ingest gives every video a caption-grid
skeleton before any human or model marker exists. You should be able to annotate with only
human clips (empty `markers[]`).

### D-004 — One careful studio pass is the product  (Accepted 2026-08-14)
10x the manual annotation process. The grid, the embedded player, and keyboard nav replace
manual scrubbing. If the user has to rewatch to find a boundary, the tool has failed.
YouTube is the *player*, never the IDE.

### D-005 — Stay stdlib until it hurts  (Accepted 2026-08-14)
Studio: Python 3 stdlib server (`http.server`) + one vanilla-JS HTML page. No framework, no
database, no npm, no build step. `yt-dlp` on PATH is the one external tool (subprocess).
Extension: Manifest V3, vanilla JS, Shadow DOM, no storage permissions. Don't Next/Vercel
the store to look like an app.

## Choices — architecture & product

### D-006 — Extension frozen at thin client  (Accepted 2026-08-14)
Keep load-on-watch + `[` / `]` coarse capture (already built). Freeze there. Do not build
the original PR 3/4 plans: `chrome.storage` as canonical store, refinement hotkeys, panel
export, taxonomy/transcript UI, SPA remount work for an on-YouTube IDE. Future (unblocked,
unscheduled): a "send to studio" handoff of coarse marks. Related: [[D-001]].

### D-007 — Canonical store is studio JSONL  (Accepted 2026-08-14)
Studio: `apps/studio/runs/` + `apps/studio/labels.jsonl`. Extension stays in-memory /
storeless. Row identity for events: `(runId, markerIndex)` for markers, `(runId, start)`
for human-added clips — never assume start times are unique. Related: [[D-002]], [[D-008]].

### D-008 — Row identity, not start time  (Accepted 2026-08-16)
Duplicate timestamps are real (two markers at 3:19). Selection, event keys, and follow/pin
use row identity. Grid align is **exact start first**, then ≤2s; earliest-cue-wins was lying
about displayed time (the 1:18:50 / 1:18:52 / 1:18:54 cluster). Displayed time is the
caption the clip was aligned onto, not the clip's stored start.

### D-009 — `kind` (TAKE/CONCEPT) is legacy  (Accepted 2026-08-14)
Readable on old markers and old label events. Never required on new writes. Taxonomy is
work / lane / tags. Related: [[D-020]].

### D-010 — Eval chrome stays behind eval mode  (Accepted 2026-08-14)
Check/note feedback, rationales, and their stats are skill-eval tooling, not the annotation
loop. Default off. Revisit removal after ~5 labeled videos. `g` (few-shot keep of a
*marker*) is still a real eval channel — hiding the chrome does not collapse the verdict
recipe. Related: [[D-021]].

### D-011 — Suggest-markers stays a skill invoke for now  (Accepted 2026-08-14)
`~/.claude/skills/yt-clipper` proposes candidate markers (rules + "over-include" prompt).
In-app ingest (URL → cues + gaps + gold, **empty markers**) landed in the two-surface
refactor so a video can be annotated without the skill. Full "Suggest markers" as a studio
action is future work (`BACKLOG.md`).

### D-012 — `end` is nullable; range collection is deferred  (Accepted 2026-08-14)
Schema keeps `end` nullable — markers and coarse captures are start-only. Collecting ranges
from the grid is the studio's next feature after the two-surface land, required before
reel-oriented export is useful. Don't sneak it into an unrelated PR.

### D-013 — Gold column stays  (Accepted 2026-08-14)
Published YouTube-description timestamps as a reference lane (and eval target while eval
mode exists). Copy-timestamps never drops gold. Related: [[D-022]].

### D-014 — Repo layout is `apps/extension/` + `apps/studio/`  (Accepted 2026-08-14)
No `schema/` folder until shared code exists; the contract lives in `docs/clip-schema.md`.
Load the extension unpacked from `apps/extension`. The old `eval/` / `content/` paths are
gone; don't put new work there.

### D-015 — media-scraper JSON is draft until the export button  (Accepted 2026-08-14)
Shape lives in `docs/clip-schema.md`. Freeze when the studio JSON export lands, not before.
Keep it generic (video identity + range + labels) so a future PKM could ingest clips.
Don't block other work on the freeze.

### D-016 — One keyboard dispatcher  (Accepted 2026-08-16)
All global studio hotkeys route through the priority chain of named contexts in
`apps/studio/ui/keys.js` (combo → composer form → desc inputs → typing guard → tab prefix →
grid → player). Never add a second document-level keydown listener; add or change behavior
by editing the owning context. The YouTube IFrame steals focus after interactions —
re-blur it (`keepKeysOnPage`) so hotkeys keep working.

### D-017 — Shared UI state lives on `S`  (Accepted 2026-08-16)
Cross-module mutable state is the `S` object in `apps/studio/ui/state.js`. State owned by
one module (player handle, suggest highlight, tab-prefix timer) stays module-local. No new
top-level `let` globals.

### D-018 — Extension panel UI lives in Shadow DOM  (Accepted 2026-08-01)
YouTube's CSS will override anything mounted directly into the document. Input-focus guard
on every keyboard listener must use `e.composedPath()[0]` (`document.activeElement` can't
see through shadow roots). Also guard modifiers, key repeat, and IME composition.

## Conventions

### D-019 — unused
No decision was ever assigned this id. Kept as a tombstone so nobody hunts for a missing
entry. IDs are stable; the gap stays.

### D-020 — Taxonomy  (Accepted 2026-08-14)
- `work` — piece/rendition, freeform (`Song` or `Song | Rendition`).
- `lane` — chapter lane, freeform (`transcription`, …).
- `tags` — lowercase, deduped. Seeded: `take`, `fingering`, `technique`, `star`; freeform
  additions allowed. `star` is a personal bookmark, not an eval verdict.
Spoken sequential finger numbers (`5 4 3 1`) → tag `fingering`. Do not prefer the last
mention in a caption block — that heuristic died in review.

Language: **marker** (run `markers[]`) vs **added clip** (`miss` / `unmiss`) vs **gold**
(published description stamps). Stop saying "skill marker" in product copy.

### D-021 — Eval / keep channels stay distinct  (Accepted 2026-08-16)
From video 1. Do not collapse these into "just train on x":

| Channel | Meaning |
| --- | --- |
| `g` (`check`) | Stingy few-shot keep of a **marker**. |
| taxonomy without `g` | Ordinary keep (not a skip, not a blank). |
| `x` | Reject this **marker**. Still in the run file; skipped by copy-timestamps. |
| blank + no taxonomy | Unreviewed. |
| `star` tag | Personal bookmark, not eval. |
| delete / `unmiss` | Remove an **added clip**. Same `x` *key* on an added clip already deletes. |

Useful ballpark ≠ perfect place: keep both, or `x` the hunt. Related: [[D-010]], [[D-022]].

### D-022 — Copy-timestamps fold  (Accepted 2026-08-16)
Shipped in PR 3 (`a051667`, `apps/studio/ui/export.js`). Description-timestamp copy is
the near-term YouTube paste; JSON export for media-scraper is still backlog ([[D-015]]).
Rules:
- Never drop gold or human-added clips.
- Nearby rows collapse at 2s; **add beats marker**; gold's title and start win when present.
- `g` still exports (so 20:46 `g` and 21:18 add both copy). Whether ballpark-`g` should be
  export-excluded is an open modeling decision in `BACKLOG.md` — do not change it silently.
- YouTube chapters need a `0:00` stamp; park it under the first work header so that header
  isn't swallowed as the chapter title.

## Process

Git workflow is not a decision entry — it lives in `AGENTS.md` §"Git workflow" and the
pre-SHA checklist in `README.md`. One home per fact.
