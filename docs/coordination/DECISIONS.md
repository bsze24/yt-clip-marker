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
In-app ingest (URL → cues + gaps + extracted markers, **empty `markers[]`**) landed in the
two-surface refactor so a video can be annotated without the skill.

**Flagged 2026-08-19, not re-decided.** "Future work" was true when every lesson arrived through
YouTube. It no longer is: four YouTube uploads have had zero captions for over a day, and the only
two transcripts that exist came from Zoom. The skill's input is a URL, so today it cannot run on
either. Teaching it to read an existing run's cues is now on the critical path for four separate
items — see `BACKLOG.md`, "The corpus, and the one blocker". Re-decide there, not here.

### D-012 — `end` is nullable; range collection is deferred  (Accepted 2026-08-14)
Schema keeps `end` nullable — markers and coarse captures are start-only. Collecting ranges
from the grid is the studio's next feature after the two-surface land, required before
reel-oriented export is useful. Don't sneak it into an unrelated PR.

### D-013 — The extracted lane stays  (Accepted 2026-08-14, vocabulary corrected 2026-08-19)
Published YouTube-description timestamps are a reference lane, and an eval target while eval mode
exists. Copy-timestamps never drops an extracted marker. Reinforced by [[D-033]].

Originally titled "Gold column stays". The word is banned ([[D-023]], `AGENTS.md`) because it
collides with the `g` grade; corrected in place, since only the vocabulary was ever wrong.

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

### D-024 — Debounced writes are keyed per record and carry their run  (Accepted 2026-08-18)
From PR 3 review (F8). The debounce key is `runId:stream:id`; feedback, relabel and model
taxonomy are separate streams. An added marker's description and taxonomy deliberately share
one key and persist one complete snapshot, because they are fields of a single append-only
record. Every queued write captures its `runId` and its payload at queue time, so switching
runs mid-debounce still lands the write against the run it was typed into; only the UI
mutations are gated on that run still being current, never the append.

Never reintroduce a single shared timer handle. The previous one let an edit on any row
cancel a pending write on any other, while the grid and the save status both still showed
the lost value as saved. Related: [[D-002]], [[D-007]], [[D-017]].

### D-025 — Row identity is assigned at build time  (Accepted 2026-08-18)
From PR 3 review (F11). Refines [[D-008]] with the implementation invariant. Each grid row
receives a `rowId` from the collection it came from — `cue:<index>`, `extracted:<id>`,
`marker:<index>` — namespaced so the three spaces cannot collide, and `rowKey` returns it
unchanged.

The key must never contain the filtered-list position or mutable row content. Both change
when `hide filler` or `all captions` toggles and when a clip is added, which silently drops
selection back to start-time matching — exactly what [[D-008]] exists to prevent, and
invisible until two rows share a start.

### D-026 — The player embed is display-only  (Accepted 2026-08-18)
From PR 3 review (F12). `.player-catcher` is absolutely positioned over the whole iframe, so
pointer events never reach the embed, and the dispatcher `preventDefault`s every `Tab`, so
focus cannot walk into it either. Consequence, which is a product choice and not an accident:
YouTube's own scrub bar, captions button and fullscreen control are unreachable, and all
transport is the page's keyboard ([[D-016]]).

This is why no focus-recovery poll is needed. If the catcher is ever removed, shrunk, or made
`pointer-events: none`, focus can land inside the iframe with no event in the parent document
and the dispatcher goes deaf until the next player state change; a `window.blur` listener or a
low-rate focus poll becomes necessary at that point.

### D-029 — Row attributes are a render snapshot, not state  (Accepted 2026-08-18)
From PR 3 review (F14). The `data-tax-*` attributes on a row are written by `renderGrid` and
nothing re-renders after a taxonomy save, so they go stale the moment a combo edit persists.
Any action that writes taxonomy reads the live record on `S` ([[D-017]]) — `toggleStar` reuses
`S.liveTax` when its type and id match the selected row — and falls back to the attributes only
for a genuinely different selection, which is what `followPlayhead` produces when it moves the
selection without re-rendering.

Rebuilding a write's payload from the DOM instead undid an already-saved `lane` on the next
keystroke, and the revert was durable: the stale value was appended over the good one.


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

Vocabulary lives in one place — `README.md`'s "Shared vocabulary" table: **skill marker**,
**added marker**, **extracted marker**. This entry originally said the opposite ("stop saying
skill marker", and *gold* for the third kind); corrected 2026-08-19.

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
- Never drop an extracted marker or a human-added clip.
- Nearby rows collapse at 2s; **add beats marker**; an extracted marker's title and start win
  when present.
- `g` still exports (so 20:46 `g` and 21:18 add both copy). Whether ballpark-`g` should be
  export-excluded is an open modeling decision in `BACKLOG.md` — do not change it silently.
- YouTube chapters need a `0:00` stamp; park it under the first work header so that header
  isn't swallowed as the chapter title.

### D-023 — `extracted[]` is the only live description-timestamp key  (Accepted 2026-08-18)
The published-description lane remains, but its only live run key is `extracted[]`. A
deprecated `gold[]` key is a visible load fault, never a read alias: the studio continues to
render captions, skill markers and added markers, returns no extracted data from that key,
and identifies the run in both the UI and stderr. `attach_extracted.py` is the explicit,
lossless repair boundary; conflicting dual keys abort rather than choosing one. Historical
session prose and append-only label feedback are not rewritten.

Vocabulary only — the behaviour in [[D-011]], [[D-013]], [[D-020]] and [[D-022]] is unchanged.
Those four entries were corrected in place on 2026-08-19 so a reader no longer meets the banned
word and has to remember this entry undoes it.

### D-027 — Copy-timestamps: cluster anchor and `0:00` placement  (Accepted 2026-08-18)
From PR 3 review (F6, F7). Refines the last two bullets of [[D-022]], which were both stated
in a way that shipped wrong.

- **The cluster anchor is the first start in the cluster and never moves.** Every candidate is
  compared to that anchor, not to the running merged clip. Letting the anchor adopt the kept
  item's start makes merging transitive, and a chain then folds clips arbitrarily further
  apart than the 2s window — three items at `10.0`, `11.5`, `13.0` collapsed to one line.
- **`0:00 Start` goes under the first work header only when the first clip owns that header.**
  Otherwise it is prepended. [[D-022]]'s unconditional "park it under the first work header"
  searched for the first non-timestamp line, which is a *later* section header whenever the
  earliest clip has no `work` — putting `0:00` mid-list and out of order, which stops YouTube
  treating the description as chapters at all. Taxonomy is optional, so that was the ordinary
  case, not the edge one.

### D-028 — The five eval channels are first-class in the store and the API  (Accepted 2026-08-18)
From PR 3 review (F9, F15). [[D-021]] named the five channels as vocabulary; they now exist in
the durable record rather than only in the UI.

- `verdict: "wrong"` exists. A reject is no longer written as `note`.
- `/api/runs` returns `checkCount`, `wrongCount`, `keepCount`, `noteCount`, `blankCount`. They
  are mutually exclusive with precedence check → wrong → note → keep → blank, and sum to
  `markerCount`. The grid header uses the same precedence, so the API and the screen cannot
  disagree about one run.
- A **keep** is taxonomy (tags, lane or work) with no `g`. An annotation whose tags, lane and
  work are all empty is not a keep. `blank` means genuinely unreviewed and nothing else —
  video 1 reads `check 23 · wrong 24 · keep 14 · note 3 · blank 0`, matching its folded ledger.
- Events written before 2026-08-18 still carry `verdict: "note"` for rejects and are not
  rewritten ([[D-002]]). Recovering them means parsing `feedback` text; see `TD-4`.

### D-030 — what "eval mode" actually gates  (Accepted 2026-08-18)
Recorded from user testing, not decided there. [[D-010]] said check/note feedback, rationales and
their stats are skill-eval tooling kept out of the annotation loop and default off. Half of that
stopped being true and the code was never reconciled with it.

Behind the `eval mode` toggle: the skill's `rationale` line, the freeform note input, the stats
line format, and the run-picker label. Also the `why` note, **inverted** — it renders when eval
mode is *off* and is swapped for the note input when it is on.

Not behind it, and never was: the `g`/`x` column renders on every row, the `g` and `x` keys are
bound unconditionally in `keys.js`, and `keepSkill` in the export fold reads check/wrong whatever
the toggle says. The eval *verdict* is part of the annotation loop. Only the eval *chrome* is
optional.

This is defensible rather than accidental — [[D-021]] treats the five channels as real product
state, [[D-028]] put them in the store and the API, and `x` doubles as delete for an added
marker, so it could never have been hidden. But [[D-010]]'s "revisit removal after ~5 labelled
videos" now applies to a much smaller surface than it reads like: two display elements and two
label formats. Whether that surface is worth a toggle at all is open, and the inverted `why`
swap is the part most likely to confuse someone. Do not resolve it from one testing session.

### D-031 — YouTube chapters stay a goal  (Accepted 2026-08-18) — **SUPERSEDED by [[D-033]]**
Do not read the body of this entry as live. Its substance survives in corrected form: chapters are
**wanted when free**, every marker reaching the output is the hard constraint, and the synthetic
`0:00 Start` line **stays**. [[D-033]] carries all three, plus what this entry got wrong — it
priced chapter compliance as nearly free when the only route to it deletes three of Brian's own
labels.

One caveat outlived the decision and is still unverified: **YouTube's 10-second chapter minimum is
stated from memory**, never checked against documentation. [[D-033]] rests on it. Confirm it
against a real description before treating any chapter claim as settled.

### D-032 — the skill copies caption start times exactly  (Accepted 2026-08-19)
`R-NEIGHBORHOOD` ("Approximate timestamps; clip-marker nailing is downstream") is retired and
replaced in `~/.claude/skills/yt-clipper/SKILL.md` by:

> `R-CUE-EXACT` — Use the caption's exact start time — never a time between captions. Nailing the
> clip boundary is downstream work in the studio.

Same intent, stated positively. The old rule's effort-allocation message was good and survives in
the second sentence; what is gone is the permission to place a marker between two captions.

Three reasons, after Brian argued for keeping the old rule:

- **The replacement asks for less judgement, not more.** "Use the caption's start" removes a
  decision; "approximate is fine" leaves the model to choose where inside a caption the moment
  falls. The worry that demanding exactness would make the skill propose fewer candidates
  (against `R-COPIOUS`) had it backwards.
- **The old text pointed the wrong way.** Read literally it licenses inventing a time between
  captions, which is the one behaviour that breaks auditing a marker against its caption.
- **Today's safety is accidental.** All 64 of video 1's markers sit exactly on caption starts
  only because `fetch_transcript.py` discards YouTube's per-segment timing and keeps the block
  start. If anyone ever wants finer granularity, the model gains a finer clock and the old rule
  immediately licenses using it.

Unchanged: extracted stamps keep their own clock and must never be snapped — they have to match
what is published. Takes ride the caption clock because `build_cues` pins a silence gap to the
following cue; if gap detection ever reports the middle of the silence instead, that needs its
own rule rather than a general licence to approximate.

**Revert signal.** Candidate count on the next video. If `R-CUE-EXACT` suppresses proposals it is
the most visible number in the output, and reverting is one line.

### D-033 — every marker reaches the output; chapters only when they cost nothing  (Accepted 2026-08-19)
Brian's call. The point of the tool is that a moment he marked appears in the exported
description. Nothing may be dropped to satisfy an external constraint.

Supersedes [[D-031]], which kept YouTube chapters as a goal on the false premise that compliance
was nearly free. It is not: the only route to compliance is widening the export fold, and that
deletes three of his descriptions (`TD-9` carries the table).

**The fold window stays at 2 seconds and does not widen.** Measured on video 1: at 2s, 85
candidates fold to 70 lines, and all 10 collapsed candidates have text *identical* to the line
that survives — the same moment marked twice, by the skill and by hand, or already published.
Nothing is lost. At 6s three more collapse and every one of the three carries different text.
Two seconds is the boundary between collapsing a duplicate and deleting work.

**Chapters are pursued only by means that cost no markers.** Corrected 2026-08-19: an earlier
version of this entry said "chapters are abandoned as a goal", which contradicted its own next
sentence and is not what was decided. The two requirements do not conflict in general — only when
a video's spacing violates the rule.

- Every marker reaching the output is a **hard constraint**. Never traded.
- Chapters are **wanted when free**. Timestamps are clickable seek links unconditionally; chapters
  additionally need the whole set to pass four tests, including a 10-second minimum gap.
- So: a means that costs no marker is fair game. A means that drops one is not. Widening the fold
  drops three descriptions — refused. The synthetic `0:00 Start` line adds a line and removes
  nothing — **kept**, and it is the only one of the four requirements obtainable for free.

Video 1 fails the 10-second rule in four places and will never qualify. A future video with
comfortable spacing would qualify, and deleting the `0:00` line would have foreclosed that
permanently to save one line of noise. [[D-027]]'s placement rule therefore stands in full.

**Resolved 2026-08-19 — the `0:00 Start` line stays.** It was briefly removed on the reading that
chapters were abandoned; Brian caught that the two requirements do not conflict and that the line
costs no marker. It is the cheapest of the four chapter requirements and the only one obtainable
without dropping anything, so removing it buys one less line of noise and forecloses chapters on
every future video. [[D-027]] governs its placement and stands.

**Worth considering, not decided:** the fold merges on time and rank, not on text. That all 10
merges are text-identical today is a happy accident of `resolvedLabel` making an added marker
adopt a nearby stamp's label. Merging only when the resolved labels match would make this decision
an enforced invariant rather than an observed one. **Now tracked as `TD-16`** — this decision is
observed, not enforced, and video 2 is the first corpus that can break it.

### D-034 — Media is resolved on every read, never written into the run file  (Accepted 2026-08-19)
Harvested from PR 8 (`71b9d82`). A run gains offline playback because a matching file appeared
in `apps/studio/media/`, and loses it when the file goes. `resolve_run_media` computes the match
on every `/api/run`; no write path gains a `media` key.

Keeps `runs/*.json` immutable ([[D-002]]) and makes attaching a download to an existing YouTube
run a rename rather than an edit. The cost is a stat per read, which is nothing at this scale.

The failure mode this creates is silent: `media/` entries are usually symlinks into wherever the
recording actually lives, so renaming the source breaks playback without touching anything the
studio owns. PR 9's `run_warnings` addition exists to make that failure say so.

### D-035 — Local playback wins over the YouTube embed whenever both exist  (Accepted 2026-08-19)
Harvested from PR 8. There is no mode to toggle, remember or persist. If a matching file is in
`media/`, the `<video>` backend plays it; otherwise the embed does.

The alternative — a user-visible switch — buys nothing. Nobody wants the network path when the
local file is right there, and a persisted preference is a thing to get wrong on the one flight
it matters.

### D-036 — A local file with no YouTube identity keeps the field name `videoId`  (Accepted 2026-08-19)
Harvested from PR 8. `local.py` synthesises a filename-derived id into `videoId` and adds
`source: "local"` beside it. Readers test `source`, never the shape of the id.

Renaming the field would have touched the run filename, the `labels.jsonl` key and every
existing reader, to express something one boolean already says. The run filename and the label
event key stay `{videoId}-{stamp}` and `(runId, …)` respectively, unchanged.

### D-037 — Sidecar matching requires a `.` boundary after the stem  (Accepted 2026-08-19)
Established fixing F18 on PR 8; extended, not relaxed, by PR 9. `find_sidecars` accepts a
sibling only when the remainder after the media stem begins with `.`.

When Zoom forced a second stem variant — strip a trailing `_{W}x{H}`, strip a browser `" (1)"`
duplicate marker — the boundary rule was carried onto each variant rather than loosened. A bare
prefix match is how `Lesson 1.mp4` adopts `Lesson 10.vtt`, which is a wrong transcript silently
attached to a lesson, not a missing one.

Any future variant obeys the same rule. Adding a variant widens the surface F18 was filed
about, so each one owes an adversarial case, not just a happy path.

### D-038 — Captions arriving late write a NEW run; the old one is never edited  (Accepted 2026-08-19)
Harvested from PR 8's `prefetch.py` and completed by PR 9. YouTube generates auto-captions well
after a fresh upload is watchable, so "download now, transcribe later" is the normal path, not an
edge case — four of four videos hit it.

When captions appear and the existing run has zero cues, `prefetch.py` writes a new run and names
the superseded one. It does not edit the old run, because runs are immutable ingest output
([[D-002]]) and label events are keyed by run id ([[D-008]]), so annotations cannot follow an
edit. Deleting the superseded run is safe only if nothing was annotated on it, and the tool says
so rather than deciding for you.


## Process

Git workflow is not a decision entry — it lives in `AGENTS.md` §"Git workflow" and the
pre-SHA checklist in `README.md`. One home per fact.
