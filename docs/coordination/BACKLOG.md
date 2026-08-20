# Backlog

Deferred work and the roadmap. Git is the source of truth for code; this is the source of
truth for what is next and what is parked. It is not a PRD — the product why lives in
`docs/youtube-clip-marker-prd.md`.

Tech-debt ids (`TD-N`) are stable so a commit can say "fixes TD-2". Add new items at the
bottom of that section; never renumber.

## Build order

Merged to `main`:

- **PR 1** — extension skeleton, Shadow DOM panel on watch pages.
- **PR 2** — `[` / `]` coarse capture, in memory.
- **PR 3** (merged `5af3e13`, 2026-08-18) — two-surface refactor: studio promoted to the
  product, extension frozen and moved under `apps/extension/`, in-app ingest, eval mode, clip
  contract, copy-timestamps ([[D-022]]), `gold` → `extracted`. Fifteen review findings closed.
- **PR 4** (merged `43c99dd`, 2026-08-19) — video 1 run file and `labels.jsonl`.
- **PR 8** (merged `71b9d82`, 2026-08-19) — local video mode: play from disk, ingest without
  network, `/media/` byte-range route, `prefetch.py`. Decisions harvested as
  [[D-034]]–[[D-038]]. Two review findings, both resolved.

Open:

- **PR 9** (`5eb55d2` on `zoom-export-ingest`) — Zoom export ingest and four fixes found by
  using PR 8 on a flight. **Under review**; `CURRENT.md` is running it.

Closed unmerged:

- **PR 5** (`949cb7b`) — session log and folded ledger. Superseded.
- **PR 6** (`e158710`) — coordination write-head and `AGENTS.md`. ~1,000 lines stale.

The order is deliberate: the studio came out of an eval harness built to score the
`yt-clipper` skill, and it stayed in daily use until it *was* the product. Nothing below
assumes the extension grows back into an IDE.

After PR 9 merges, in priority order (matches the PRD's "Next"):

1. **End collection.** Set `end` from the grid. Required before reel-oriented export is worth
   anything ([[D-012]]).
2. **JSON export.** Copy as JSON — the media-scraper seam. Freeze the schema when this lands
   ([[D-015]]). Description-timestamp copy already shipped in PR 3.
3. **Suggest-markers as a studio action.** Today it is a Claude skill invoke ([[D-011]]).
   Ingest already exists, so this is the remaining piece of skill engineering.

Unscheduled but unblocked:

- **Extension → studio handoff** of coarse `[` / `]` marks. Until it exists the extension is
  a capture scratchpad and its marks die with the tab.
- **Video 2.** The door is the studio header's **Add video** — URL in, cues, gaps and extracted
  markers out, `markers[]` empty. A `/yt-clipper` pass is optional and only needed if you want
  proposed skill markers to score.

## Reducing manual tagging — the path (agreed 2026-08-19)

Brian's goal: **cut manual tagging effort by 75%+**. Recorded here as roadmap because it spans
process, an experiment and code, and because the ordering is evidence-driven rather than
obvious. The evidence is an audit of videos 1 and 2 run on 2026-08-19 against `runs/` and
`labels.jsonl`; the numbers below are measured, not estimated.

**The finding that sets the order.** All 21 clips Brian hand-added to video 1 sit within 90
seconds of a skill marker; 19 within 45s, 10 within 20s. **Zero** regions were missed. The
skill's recall on video 1 is effectively total — the manual work was nudging markers by 5–45
seconds and rewriting labels, not authoring new ones. Recall is not the problem, so the lever
is better inputs plus a review loop, not a better model.

**Second finding.** Of the 24 rejections on video 1, exactly **one** was a genuine disagreement
about what is worth marking. The rest sort into fixable classes: 5 hallucinated YouTube
captions, 5 "me talking, less interesting" (a diarization problem), 4 right-event-wrong-second
(7–17s early), 4 where the silence-gap rule anchored to an empty caption ("Yeah.", "Okay."),
4 structural (lesson start, chapter pivot, continuation), 1 duplicate of an existing human tag.

Stripping those classes moves precision 49% → 62% → 73% → 82%. Caveat that governs everything
below: **n = 1.** The skill has only ever run on video 1.

1. **Record lessons through Zoom cloud, not YouTube.** Zero engineering. Video 2's transcript is
   100% diarized (413 Jake cues / 275 Brian); video 1's is not, and has a 10-minute stretch with
   no captions at all. That one input change removes 10 of 24 rejection causes before any code
   changes.
2. **Run the current skill against video 2 and score it. Do this first.** Video 2 carries 75
   human markers chosen with no model proposal to anchor them, on a clean diarized transcript,
   on a video the skill has never seen. It is the only unanchored ground truth in the store and
   it answers whether the 82% ceiling is real or an artifact of one video. Blocked on one thing:
   the skill's input is a YouTube URL and video 2 is `source: "local"` with no YouTube identity
   ([[D-036]]) — decide whether to teach the skill to read an existing run or to export its cues.
3. **Teach the skill the speaker rule.** Measured limit, so nobody wastes a cycle on it: speaker
   at the marker start does **not** predict the `take` tag — Jake is the speaker at 70 of 75
   video-2 rows, giving 100% recall and 19% precision. Neither does `gapBefore` (4/13 take rows
   near a gap vs 19/62 non-take). Diarization predicts *worth marking*, not *is a demo*.
   Detecting "Jake is demonstrating" needs music-vs-speech detection on the audio.
4. **Fix the taxonomy schema before tagging video 3.** The current tag field is four questions
   in one multi-select: who is playing (`take`), domain (`harmony`, `technique`, `fingering`,
   `comping`, `voicings`, `escapement`, `drums`), pedagogical function (`feedback`, `synthesis`,
   `process`, `polish`, `chord exercise`) and salience (`star`). Split it into a required
   single-select function field and a domain multi-select; make `demo:jake` / `demo:me` its own
   field; drop the singleton tags. See `TD-15` for the vocabulary-scoping half. This saves no
   time directly — it is what makes 5 and 6 learnable.
5. **Build the review loop, not the authoring loop.** The studio is optimised for authoring
   (`n`, seek, type); what actually happened on video 1 was review. Accept, reject and
   nudge-to-next-content-cue should each be one key, and a reject must not leave a stub that
   gets duplicated around — video 1 has two such ghosts (skill markers 57 and 61, untagged,
   sitting 5s and 40s from the real added clips).
6. **Draft labels from the transcript.** This is the load-bearing step for the 75% target —
   typing the label is the expensive part, not placing the marker. Note what the labels actually
   are: only 3 of video 2's 75 are transcript text kept verbatim (one still carrying its
   `Jake Sherman:` speaker prefix, one still carrying a `…` truncation). The other 72 are Brian's
   own compression of what was said. So the draft has to be a *summary*, not an excerpt — a
   suggester that pastes captions will be rewritten every time, and if every label gets rewritten
   the ceiling is nearer 40% than 75%.
7. **`end` collection is a prerequisite for the target being meaningful.** All 700 label events
   have `end: null` ([[D-012]]). Every clip in the store is a point, so "75% less tagging" is
   measured against a job that is not finished. Already item 1 under "Next studio features".

**Rejected: tagging less granularly.** Cutting granularity cuts output one-for-one — it is a
retreat, not leverage. The defensible version is *two passes*: coarse chapter markers on the
first watch, dense clip marking only inside the chapters worth revisiting. Also real: about five
video-2 rows are pure structural bookkeeping ("Line 2 - kick off") that a model should emit.

## Next studio features (detail)

- **End collection ([[D-012]]).** Markers and adds are start-only. The grid should set `end`
  without turning the studio back into a video IDE — likely a keyboard nudge plus an explicit
  range on the selected row. Do not block JSON export on perfect ranges if media-scraper can
  take start-only, but reels want ends.
- **JSON export ([[D-015]]).** An array of clip objects per `docs/clip-schema.md` plus
  `videoUrl` and `videoTitle`. Decide the fold — which of skill, added, extracted survives — against
  the ballpark-`g` item below, not by quietly changing copy-timestamps and letting the two
  exports diverge.
- **Suggest-markers in-app ([[D-011]]).** A studio action that writes `markers[]` onto an
  ingested run. The skill file at `~/.claude/skills/yt-clipper/` stays the prompt and rules
  source. Do not pull model calls into `server.py` until the shape is obvious — a local invoke
  that the page polls is enough ([[D-005]]).

## Deferred design detail

- **Eval chrome removal.** [[D-010]] keeps check, note and rationale behind a toggle until
  roughly five labelled videos. One is labelled. Not yet.
- **`kind` (TAKE/CONCEPT) on old events.** [[D-009]] — readable forever, no migration pass
  unless a consumer chokes on it.
- **`attach_cues.py` / `attach_extracted.py`.** Still useful for skill-written runs; the latter
  attaches extracted markers and is the explicit repair boundary for a deprecated `gold[]` key. In-app ingest
  covers the human-only door. Do not delete the CLIs until suggest-markers is in-app and the
  skill writes through the same ingest path.
- **Skill prompt rules.** The sequential-finger-numbers rule survives: spoken sequential
  numbers mean a fingering clip, tag `fingering`. The "prefer the last mention in a block"
  heuristic died in review — recorded here so a later pass does not revive it from an old
  note.
- **Session-log skill `surface` allowlist** has no value for Grok, so logs written there carry
  `surface: grok` outside the allowlist. Extend the skill or keep documenting the exception;
  it is outside this repo either way.
- **Formal YouTube chapter-rule validation.** If marks happen to satisfy the chapter rules,
  chapter use works as a side effect. Not a feature.
- **Unused import.** `persistTaxonomy` is imported but never called in
  `apps/studio/ui/main.js`. One-line removal whenever that file is next touched; not worth its
  own commit.

## Tech debt (stable `TD-N`)

Moved here from `docs/tech-debt.md`, which is now a pointer.

### TD-1 — the double-injection guard also blocks legitimate re-mounts

**Where:** `content/panel.js:17` (today), `apps/extension/content/panel.js` after PR 3 —
`if (document.getElementById(this.HOST_ID)) return false;` at the top of `mount()`.

**Issue:** It correctly stops stacked panels on double injection, which is what PR 1 needed.
It also silently no-ops a legitimate tear-down and rebuild.

**Trigger:** The first change that adds dynamic re-mount logic. The extension freeze
([[D-006]]) took SPA remount off the table, so revisit only if the extension grows again.

### TD-2 — the match pattern misses `youtube.com` without `www.`

**Where:** `manifest.json:8` — `"matches": ["https://www.youtube.com/watch*"]`.

**Issue:** A bare `https://youtube.com/watch?v=…` does not load the extension. YouTube
redirects most entry paths through `www.`, so the real-world hit rate is near zero.

**Trigger:** The first time it actually fails, or before any public release. Do not reach for
`https://*.youtube.com/watch*` without a decision — that also matches `m.youtube.com`, and V1
is desktop-only.

### TD-3 — label events are re-parsed repeatedly during run polling

**Where:** `apps/studio/server.py` — `read_label_events`, its folded accessors, and
`list_runs`; `apps/studio/ui/main.js` polls the run list every four seconds.

**Issue:** Each accessor reads and parses the append-only event log again, and `list_runs`
folds it once per run. The current 553-line, one-run store makes this effectively free, but
the cost grows with both runs and events.

**Trigger:** When run-list polling becomes measurably slow, or the store grows to several
thousand events across multiple runs. Cache one parsed event list keyed by file mtime, then
keep the existing pure folds and append-only file as the source of truth.

**Update 2026-08-18:** the keep/blank split ([[D-028]]) added `load_annotations` to the
`list_runs` loop, so it now folds the log three times per run rather than twice. Same shape,
trigger arrives sooner.

### TD-4 — `schemaVersion` did not move when the verdict vocabulary changed

**Where:** `apps/studio/server.py` — `schemaVersion: 1` at all five event write sites;
`verdict_for`. Documented in `apps/studio/README.md`, absent from `docs/clip-schema.md`.

**Issue:** [[D-028]] added `wrong` to the `verdict` vocabulary without bumping the version, so
events stamped `schemaVersion: 1` before and after 2026-08-18 carry two different vocabularies.
In video 1's store, 121 of 193 `note` events are actually rejects; nothing in the record marks
where the turnover happened. Recovering them means parsing `feedback` text for `wrong` /
`wrong: …`, which is the ambiguity the change was meant to end.

**Resolved 2026-08-19.** Both halves done, and they were not alternatives. The necessary half
is the rule now written into `docs/clip-schema.md`: pre-2026-08-18 events record a reject as
`verdict: "note"` with `feedback` beginning `wrong`, so an outside reader must derive the channel
from text. The optional half marks the regime machine-readably — new writes carry
`schemaVersion: 2`, so `1` means derive from text and `2` means trust `verdict`. History is not
backfilled ([[D-002]]); video 1 stays entirely version 1.

### TD-5 — four shared documents exist in divergent copies across the open PRs

**Where:** `AGENTS.md`, `README.md`, `docs/youtube-clip-marker-prd.md`,
`docs/two-surface-handoff.md`.

**Issue:** each open branch carries its own version and the working tree holds a fifth,
uncommitted, on `docs/remove-coordination-md`. As of 2026-08-18 the PRD exists in five
mutually different versions; `AGENTS.md` and `two-surface-handoff.md` are absent from `main`
entirely. Whatever order the PRs land in, all four files conflict or silently take the wrong
side. `docs/coordination/` itself is untracked in the working tree while a committed, older
copy sits in PR 6.

**Resolved 2026-08-18** for the four shared docs, after PR 3 merged. Each was reconciled
rather than picked: `README.md` and the PRD took the working-tree wording (skill / added /
extracted vocabulary plus `docs/coordination/` pointers); `docs/two-surface-handoff.md` kept
**main's** body, which was the newer one — the working-tree copy still said `attach_gold.py` —
and gained only the "Historical" banner; `AGENTS.md` was a genuine two-way split, so the
coordination-pointing rewrite won and main's `## File structure` tree was ported into it, its
`## Architecture rules` sections being restatements of `D-002`, `D-005`, `D-007`-`D-010`,
`D-016` and `D-017` that the rewrite deliberately replaced with citations.

**Fully resolved 2026-08-19.** PR 6 closed; PR 5 closed as superseded (`REVIEW.md` thread 3).
Re-checked what the remaining open PR would actually apply, using each branch's merge-base
rather than a tree diff against `main`: **PR 4 touches no `.md` file at all** — it applies
`apps/studio/labels.jsonl` and one run JSON, nothing else. No open PR can now clobber a document.

Method worth reusing, because the naive check reads alarmingly wrong: `git diff main..branch`
shows tree differences and made PR 5 look like it reverted all of `apps/studio/`. What a merge
applies is `git diff $(git merge-base main branch) branch`.

### TD-6 — stored-vs-displayed: measured on one video, needs a second

**Where:** `docs/reference/2026-08-18-1217-stored-vs-displayed.md`, reconciled 2026-08-18.

**Issue:** the note now carries the measurement rather than the stale `1:18:50` illustration,
and `docs/coordination/README.md`'s standing trap matches it. Video 1 says all 64 skill markers
sit exactly on caption starts — both `CONCEPT` and `TAKE` — and 19 of 24 extracted stamps do
not. The three-clock model collapsed to two: everything the pipeline produces rides the caption
clock, and only human-typed description stamps drift.

That is one video. The conclusion that `R-NEIGHBORHOOD`'s approximate-time licence is never
exercised rests entirely on it.

**Re-pointed 2026-08-19.** The modelling choice it fed is decided — [[D-032]] replaced
`R-NEIGHBORHOOD` with `R-CUE-EXACT`. So the question is no longer "does the skill happen to land
on caption starts"; it is "does the new instruction hold". Same one-line check, different meaning.

**Trigger:** the next `/yt-clipper` run. Compare `marker.start` against the `cues[]` start set. A
non-caption start now means the rule is being ignored, which is a finding rather than a curiosity.
Watch candidate count at the same time — that is [[D-032]]'s revert signal. **No labelling
needed**; the ingest and skill pass alone answer this.

### TD-7 — selection jumps to the top when the selected row is filtered out

**Where:** `apps/studio/ui/grid.js` — `restoreSelection`, which falls back to `rows[0]` when
neither the stored `rowKey` nor the stored start matches a visible row.

**Issue:** found in user testing 2026-08-18. Select a row, then toggle `hide filler` or
`all captions` such that the selected row is no longer rendered. The next `j`/`k` walks from the
first row of the grid rather than from where you were. Selection survives a filter change when
the row stays visible ([[D-025]] does its job); it has nowhere to go when the row disappears.

**Trigger:** not before PRs 3-5 land — explicitly held out of PR 3 to keep feature work out of a
review that is closed. The fix is a policy choice, not a bug fix: fall back to the nearest
visible row by start time, or keep the hidden row selected and let `j` resume from its position.
Decide which before writing it.

### TD-8 — combo suggest matches by substring and offers "add" only for tags

**Where:** `apps/studio/ui/suggest.js` — `suggestItems`. Matching is
`items.filter(t => t.includes(q))`; `addNew` is gated on `field === "tags"`.

**Issue:** found in user testing 2026-08-18. Two separate problems. Matching is substring with no
ordering, so a prefix match is not preferred over a mid-string one. And lane and work have no
add-new row at all — you create one by typing freeform and letting it save, with no affordance
saying so — while tags have an "Add new tag" row whose treatment reads as the *only* option when
nothing matches. Typing `Tran` in the tags field offers only "Add new tag", because the tag
vocabulary has no `tran*`; the `Transcription` the user wanted is a **lane**, and the three
vocabularies are deliberately separate ([[D-020]]).

**Wanted behaviour, from testing:** arrow keys walk existing values with the typed text treated
as a prefix, and an explicit add row sits at the bottom with clear "add" treatment, for lane and
work as well as tags.

**Trigger:** with the next taxonomy-entry work. Held out of PR 3 deliberately.

### TD-9 — widening the export fold would buy chapters by deleting three labels — CLOSED, wontfix

**Where:** `apps/studio/ui/util.js` — `export const MATCH = 2`, consumed by `grid.js`
(`takeNear`, row alignment) and `export.js` (`mergeNearby`, the copy-timestamps fold).

**Nothing is broken.** Corrected 2026-08-19. Two earlier framings here were wrong. The fold
window is not *for* chapters — YouTube is blind to this repo and simply reads the description
text; chapter compliance is a downstream accident of what the window produces. And the export is
correct as it stands: 71 timestamps faithfully reflecting what Brian marked, with four pairs close
together because he marked two things close together.

**Issue:** [[D-031]] keeps chapters as a goal, and video 1 fails only the 10-second minimum, on
four consecutive pairs. Widening the fold to ~6s makes it qualify — 68 timestamps, every gap ≥10s
— but it is a **trade, not a fix, and it is not free.** `mergePair` unions tags, lane and work
onto the surviving line, so the taxonomy survives. The *labels do not*: three of Brian's
descriptions are deleted and replaced by the published wording of a nearby stamp, and at least two
of the three name a different moment rather than the same one.

| deleted | replaced by |
| --- | --- |
| `54:38 Loop 4-bar chunks (backdoor ii-V)` | `54:42 Finding a few places to really nail` |
| `55:40 *** Hearing vs executing; hand ahead of ear` | `55:43 Is the limitation hearing the line…` |
| `1:18:52 *** Jake demo — melody, harmonized` | absorbed into `1:18:58 Freedom Demo c1` |

An earlier version of this entry said widening "loses nothing". That was checked against tags only
and never against the label text. Measured 2026-08-18:

| fold window | timestamps | gaps under 10s |
| --- | --- | --- |
| 2s (today) | 71 | 4 |
| 3s | 70 | 3 |
| **6s** | **68** | **0** |
| 10s | 66 | 0 |

One constant serves both callers, so raising it would also let the grid snap a marker onto a
caption six seconds away and undo [[D-008]]. The export needs its own window.

**CLOSED 2026-08-19, wontfix.** [[D-033]] settles it: every marker reaches the output, so the fold
never widens and chapters are not a goal. The measurement that closed it — at 2s all 10 collapsed
candidates are text-identical to their survivor, so nothing is lost; at 6s three carry different
text. Two seconds is the boundary between collapsing a duplicate and deleting work. The rest of
this entry is kept as the record of what was priced.

~~**Trigger:** a second *labelled* video.~~ This is the one item that cannot ride along with a plain
ingest — `TD-6` and [[D-032]] need only a `/yt-clipper` pass, but the fold window can only be
judged against a real export, which needs a real annotation pass first. Scope it separately.

Then: give `export.js` a separate constant, leave `MATCH` at 2 for the grid, and pick the window
from the second video rather than fitting it to this one. 6s is the smallest value that works on
video 1, which is exactly the kind of number that overfits. Do not make the code change before
the number is decided — a separate constant still set to 2 is churn.

**Known property that widening makes worse.** The fold anchors each cluster at the time it
opened, so a cluster spans at most one window and "within the window" does not reliably mean
"same line": `10.0, 12.0, 12.5` prints `[10.0, 12.0]` and then `[12.5]`, splitting a pair half a
second apart. That is the price of the bounded rule [[D-027]] chose, and the alternative —
anchoring on the previous clip — is consistent but lets a cluster grow without limit, which is
the unbounded behaviour F7 removed. Video 1 has zero chains of three or more clips inside the
window, so it never fires today. A wider window gives boundaries more places to fall, so price
this again against real data before settling on a number, and check whether any near pair ends
up split.

### TD-10 — the add-clip form can submit twice before it closes

**Where:** `apps/studio/ui/composer.js` — `submitComposer`, and the model-edit branch above it.

**Issue:** the guard against a second submit is a check that a form is open. The form is not
closed until *after* the server replies, so for the length of that round trip the guard still
sees an open form and a second submit passes. The result is two identical events in
`labels.jsonl`.

Found in the PR 4 review (`REVIEW.md` F17). Video 1's store carries three duplicate pairs written
1.7-2.5 ms apart, byte-identical apart from `recordedAt`. Two came from the taxonomy path and are
already fixed by [[D-024]] — a direct `persistTaxonomy` now cancels the queued duplicate. The
third came from this path, which is unchanged.

Harmless so far: the store is append-only and the fold takes the last matching line, so a
duplicate of an identical event changes no count. It stops being harmless if a duplicate ever
carries different content.

**Trigger:** with the next composer work. Close the form before awaiting the write and restore it
if the write fails, or hold a separate in-flight flag. **Do not** fix this by moving the timestamp
inside the write lock — that only makes the duplicate pair look correctly ordered, which hides
the symptom that revealed it. See the file-order note in `apps/studio/README.md`.

### TD-11 — `ingest.py` carries the same over-broad caption-language wildcard

**Where:** `apps/studio/ingest.py` — `fetch_captions`, `--sub-langs "en.*,en"`.

**Issue:** the wildcard matches auto-translated tracks (`en-en`, `en-de`) as well as the two
that matter (`en-orig`, `en`). Each is an extra request. In `prefetch.py` on 2026-08-19 that
extra traffic drew a 429 on the third track; the same pattern here would do the same.

Not currently harmful: `fetch_captions` picks the first `.json3` in the temp directory and
judges success by whether a file exists, not by yt-dlp's return code, so a failed redundant
track cannot fail the ingest. It is the *only* reason this is latent rather than live.

**Trigger:** with the next `ingest.py` change, or the first time an online ingest fails on a
subtitle 429. Narrow to `en-orig,en` to match `prefetch.py`. Note that `en-orig` sorts before
`en` in the glob, which is the preference we want — but `fetch_captions` currently relies on
sort order rather than saying so, unlike `local.py`'s `find_sidecars`, which ranks explicitly.

### TD-12 — audio-only local files render in a `<video>` element

**Where:** `apps/studio/ui/player.js` — `ensureMediaEl`.

**Issue:** a `.m4a` or `.mp3` run plays correctly but shows a black 16:9 box. `/api/run`
already returns `media.kind` as `"audio"`; nothing reads it.

Cosmetic, and only reachable by ingesting an audio-only file, which nothing does today —
a Zoom recording's `.m4a` is the plausible route.

**Trigger:** if audio-only recordings become a real input. Swap the element on `kind`, or
collapse the player column and let the grid have the width.

### TD-13 — cue starts are truncated to whole seconds, so distinct cues collide

`build_cues` stores `int(start)`. Two cues 0.4s apart collapse onto one second, which is
ordinary in a Zoom transcript and rare in YouTube captions — **25 such pairs in one lesson, 64
in the other, 0 problems on video 1**, which is why it took until 2026-08-19 to surface.

PR 9 (`5eb55d2`) fixed the visible symptom: `k` stuck because the playhead resolves to the last
row at or before now while `j`/`k` seek the video to whatever they select, so a pair trapped the
cursor. `j` was also silently skipping the first row of every pair.

The upstream fix is storing fractional starts. It was deliberately not taken in PR 9 because it
changes the stored shape of every existing run, video 1 included, and runs are immutable
([[D-002]]) — so it is a migration, not an edit. Decide whether the grid's 2-second alignment
window and the standing stored-vs-displayed trap get simpler or harder under fractional starts
before doing it; `TD-6` is the related item.

### TD-14 — `labels.jsonl` history records 144 rejects and keeps as `verdict: "note"`

F9 (thread 1) added `wrong` to `verdict_for` and was resolved forward-only: "existing history is
untouched", deliberately and with the reviewer's agreement. `server.py` recomputes the verdict
from `feedback` text on every read, so the studio and the API are correct.

The residue is that the persisted field disagrees with the persisted text on **144 of 240**
non-taxonomy events (121 `note`→`wrong`, 23 `note`→`check`). Folded for video 1 the stored field
says `check 10 · wrong 0 · note 40`; recomputed it says `check 23 · wrong 24 · note 3`.

This matters because `apps/studio/README.md` says each line is a standalone example that can be
scored without the run file. Any external consumer — a skill-scoring pass, a training-data
export — that trusts `verdict` silently loses all 24 rejections and 13 of 23 approvals. That is
exactly the reader the tagging-reduction path in this file depends on.

Two options: backfill the field with a one-shot rewrite (violates append-only in spirit, though
the events are not being *changed*, only corrected to match their own text), or state in
`README.md` that `verdict` is advisory for pre-2026-08-18 lines and `feedback` is authoritative.
Related to `TD-4` (`schemaVersion` did not move when the vocabulary changed) — same root.

### TD-15 — taxonomy vocabulary is scoped to the loaded run, so it resets per video

`videoVocab()` in `ui/suggest.js` unions the four built-in `TAGS` with the tags on the **current
run's** additions and annotations only. Open a freshly ingested run and the dropdown offers
`take`, `fingering`, `technique`, `star` and nothing else, however many videos have been tagged.

Consequence, measured across videos 1 and 2: 15 distinct tags exist, only 6 appear in both, and
`chord exercise` (15 uses on video 1) is invisible on any other video until it is retyped. Within
a single session on video 1 the same construct was tagged two ways four minutes apart — Freedom
Demo c1–c4 without `take`, Simpler Demo c1–c3 with it, and c1 was *rewritten* seven minutes after
the convention changed and still not updated. Nothing in the UI shows the distribution while you
work.

Fix is a corpus-wide vocabulary with per-video counts beside each entry, so the dropdown both
offers the vocabulary and shows how it is being used. Prerequisite for item 4 of the
tagging-reduction path; there is no point splitting the schema if the split vocabulary still
resets per video.


## Parking lot

- Voice input; YouTube Data API write-back; sync; mobile and in-car; Shorts, playlists,
  embedded players; multi-user.
- Live annotation of in-flight calls or streams. Different product.
- A framework, a database, or a deploy story for the studio ([[D-005]]).
- PKM ingest of the clip JSON. Keep the export generic rather than over-fitting it to YouTube.

## Open modeling decisions

Each is bound to the step that forces it. When the planner specs that step in `CURRENT.md`,
resolving the bound decision is part of the task, and the resolution becomes a dated
`DECISIONS.md` entry.

- **Ballpark-`g` in copy-timestamps — decide at: the export freeze.**
  Today `g` still exports ([[D-022]]), so on video 1 both 20:46 (skill marker, `g`, ballpark) and
  21:18 (added marker, the actually-good placement of the same lick) copy into the description.
  Eval wants the few-shot positive kept; publishable timestamps may not want the early hunt.
  Do not collapse this into "exclude all `g`" — taxonomy-without-`g` is an ordinary keep and
  is unaffected. Options: (a) keep current behaviour, (b) exclude a `g` marker when a nearby
  add exists, (c) `g` never copies and stays eval-only. Bound to the export freeze so
  copy-timestamps and JSON cannot diverge.
  Same shape elsewhere on video 1: 29:23 `g` names a better caption at 29:09 with no clip
  stored there; 35:53 `x` (still hunting) pairs with the 36:39 add that keeps.

- **Extension → studio handoff transport — decide at: when scratchpad friction hurts.**
  Clipboard JSON, a localhost POST, or something else. Constraint: the studio store stays
  canonical ([[D-007]]) and the extension must not grow a second store to make the handoff
  easier ([[D-006]]).

- **media-scraper JSON freeze — decide at: the JSON export button ([[D-015]]).**
  The draft is `docs/clip-schema.md`. Do not freeze it from a conversation.

- **Suggest-markers runtime — decide at: in-app suggest ([[D-011]]).**
  Skill invoke in chat, a studio button that shells out, or something hosted. Constraint: stay
  stdlib until it hurts ([[D-005]]); do not add a model provider to `server.py` as a side
  effect of something else.
