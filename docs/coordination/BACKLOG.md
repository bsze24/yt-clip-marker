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

## The corpus, and the one blocker

Measured 2026-08-19. Four items in this file say "measure a second video." A second video exists.
None of them can run, and the reason is not the one any of them assumes — so it is stated here
once and cited, not re-explained in each.

| Run | Cues | Source | Annotated | Skill markers |
| --- | --- | --- | --- | --- |
| `YYW4Q1Nivg8` — video 1 | 1464 | youtube | 67 rows, 54 judged | 64 |
| `GMT20260730-…-1` — video 2 | 688, **diarized** | local | 75 rows | 0 |
| `GMT20260712-…` | 688, **diarized** | local | 0 | 0 |
| `Oa0wqetkNcg` | **0** | local | 0 | 0 |
| `dYT41doJw2I` | **0** | local | 0 | 0 |
| `glhvfs6OOOE` | **0** | local | 0 | 0 |
| `nWCc3xBSz-0` | **0** | local | 0 | 0 |

**The blocker: the skill's input is a YouTube URL, and no URL in this store has captions.** The
four YouTube uploads had zero `automatic_captions` at download and still had zero when re-checked
a day later. The only two transcripts that exist came from Zoom, through the local door, and carry
no YouTube identity the skill will accept. Waiting is not a plan — and the Zoom transcript is the
better artifact anyway: diarized, and free of the hallucinated captions behind 5 of video 1's 24
rejections and behind the `R-TAKE-GAP` failure above.

**Blocked on this:** `TD-6` (does `R-CUE-EXACT` hold), [[D-032]]'s revert signal (candidate count),
step 2 of the tagging path (score the skill on held-out ground truth), and re-running the rule
grouping on video 2 — which every "not applied" candidate change above is waiting for.

**Unblocking move: teach the skill to read an existing run's `cues[]` instead of fetching a URL.**
One change, four items. It re-opens [[D-011]], which parked this as future work when every lesson
still arrived through YouTube.

**Also true and not yet handled — video 2 is in the store twice.** `Oa0wqetkNcg` is the same lesson
as the local Zoom run: 3883s against a last cue at 3870s, and its YouTube title is literally
`GMT20260730 155336 Recording 640x360`, because the Zoom file was uploaded as-is. `dYT41doJw2I` is
likewise a GMT20260707 lesson. When captions eventually land, ingesting the YouTube twin mints a
second run id for a lesson that already has 75 label events keyed to the local one ([[D-008]]), and
nothing in the store says the two are the same lesson. Decide the relationship before ingesting.

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
   ([[D-036]]). **Blocked; see "The corpus, and the one blocker"** — the fork it named is settled by
   measurement: waiting for a captioned YouTube URL does not terminate, so teach the skill to read
   a run's `cues[]`.
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

**The missing loop — skill revision from run 1's corpus.** Recorded here 2026-08-19. It was
first written down that morning, but into a session log
(`docs/sessions/2026-08-19-0528-claude-code-pr3-review-and-docs-reconcile.md`, "Two work items
exist nowhere") — the wrong home for project state, and invisible to anyone reading this file.

`g` is called "the positive training signal" in `README.md`, `AGENTS.md`'s vocabulary table and
`apps/studio/README.md`. **Nothing schedules using it.** Run 1 carries 23 `g` and 24 `x` on 47
judged skill markers and neither channel has ever been fed back into the skill.

The seven steps above do not close this. They use the `x` channel for diagnosis and the added-clip
geometry for the recall finding; the 23 `g` exemplars are used **nowhere**, and there is no
revise-then-rescore cycle — step 2 measures on a different video and step 3 is a single
hand-picked rule change.

What the loop would be: read the 47 judged markers, revise `~/.claude/skills/yt-clipper/`'s rules
and few-shots, re-run on video 1, and compare precision against the 49% baseline. Then re-run on
video 2 as held-out.

**Blocked on `TD-14`.** A scoring pass that reads `labels.jsonl` and trusts `verdict` sees
`check 10 · wrong 0 · note 40` where the text says `check 23 · wrong 24 · note 3`. It would score
the skill against a corpus that has lost every rejection. Fix or document `TD-14` first.

**Needs a sentence from Brian before it can be specced:** are the 23 `g` markers few-shot
*examples* pasted into the skill prompt, or an *eval set* the skill is scored against and never
sees? They cannot be both, and run 1 is the only labelled corpus that exists.

**Which rule to revise — measured 2026-08-19.** The step above says "a single hand-picked rule
change"; it does not have to be hand-picked. Grouping video 1's 64 markers by the rule each one
cited in its rationale:

| rule | `g` | `x` | note | blank | unjudged | reject ÷ all | reject ÷ judged |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `R-CONCEPT` | 20 | 12 | 2 | 4 | 8 | 26% | 38% |
| `R-TAKE-GAP` | 3 | 12 | 1 | 0 | 2 | 67% | 80% |
| `R-TAKE-CLUSTER` | 0 | 7 | 1 | 0 | 0 | 88% | **100%** |
| `R-TAKE-LABEL` | 1 | 0 | 0 | 0 | 0 | 0% | 0% |

Two denominators, because they answer different questions. *Reject ÷ all* is the share of a rule's
proposals Brian explicitly rejected; *reject ÷ judged* is the precision complement over
`g + x` only, ignoring rows he never graded. The second is the one to revise against, and it is
worse: `R-TAKE-CLUSTER` is 100% reject, not 88%.

Concept detection carries the skill. Take detection is where the rejects live, and `R-TAKE-CLUSTER`
has never produced a single `g`.

**Gap size does not predict quality.** Kept takes sat on 22s, 25s and 54s gaps; rejects ran
20-58s. Raising the gap threshold would not have helped. *(Corrected 2026-08-19: an earlier
version said "the three largest gaps are all rejects". The top three are 58s → `x`, 54s → `g`,
54s → `x`. The conclusion holds; that sentence did not.)*

**The caption that ends the gap does predict it.** All three `g` takes land on a real sentence
("Let's stop for a second.", "Let's get that.", "So, I'm going to be focusing on the"). Eleven
takes land on a backchannel or one-word fragment — `Heat. Heat.` ×2, `Wow.`, `Yeah. Yeah.`,
`Yeah.`, `Okay.`, `3.`, `Blueberry.`, `D.` — and **not one of the eleven earned a `g`**: nine
rejected, one ordinary keep, one never graded at all. Brian's own reject reasons name the cause: "heat is reliably
hallucinated", "hallucinated caption" ×3. The gap is real; the resumption is caption noise, so
there is nothing to label the take from.

**Candidate change, not applied:** amend `R-TAKE-GAP` to skip a gap whose ending caption is a
backchannel or single fragment. The studio already models this as `isBackchannel` /
`DEFAULT_FILLER` in `ui/util.js` and the skill does not use it. **Cost:** it trades against
`R-COPIOUS` — suppressing those eleven loses one ordinary keep and one ungraded row along with
nine rejects — and it rests on one video. `isBackchannel` is `ui/util.js:37`, `DEFAULT_FILLER`
is `:9`, both verified present. Re-run this grouping on video 2 before touching the rule.

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

### TD-5 — four shared documents existed in divergent copies — CLOSED 2026-08-19

`AGENTS.md`, `README.md`, the PRD and `docs/two-surface-handoff.md` each existed in up to five
mutually different versions across open branches. All four reconciled after PR 3 merged; PRs 5 and
6 closed rather than merged, removing the remaining divergent copies.

The rule that came out of it is the live artifact, in `AGENTS.md` § Git workflow: **living records
go straight to `main`; docs that describe code ride in the PR that changes the behaviour.** Test:
would this doc be wrong once some open PR merges?

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
needed**; the ingest and skill pass alone answer this. **Blocked** — see "The corpus, and the one
blocker".

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

### TD-9 — widening the export fold to reach chapters — CLOSED 2026-08-19, wontfix

[[D-033]] settles it. Chapters are wanted only by means that cost no marker, and widening the fold
costs three of Brian's own descriptions — so the fold never widens. The measurement that closed
it: at the 2s window all 10 collapsed candidates are text-identical to their survivor, so nothing
is lost; at 6s three carry different text and two name a different moment. **Two seconds is the
boundary between collapsing a duplicate and deleting work.**

The live remainder was lifted out to `TD-16`: the fold merges on time and rank and never compares
label text, so [[D-033]]'s hard constraint is observed rather than enforced.

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

**This blocks the skill-revision loop** under "Reducing manual tagging" above: any scoring pass
that trusts `verdict` scores the skill against a corpus with every rejection erased.

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


### TD-16 — the export fold merges on time and rank, never on label text

Lifted out of `TD-9` (CLOSED, wontfix) and [[D-033]]'s closing prose on 2026-08-19, because a
live item inside a closed one is an item nobody reads.

[[D-033]] is an invariant: every marker Brian made reaches the output. The fold that produces
copy-timestamps merges candidates by time and rank and **never compares their labels**. On video
1 that invariant holds by luck — all 10 collapsed candidates at the 2s window are text-identical
to their survivor, which is a happy accident of `resolvedLabel` making an added marker adopt a
nearby extracted stamp's label. At 6s, three carry different text.

So [[D-033]] is *observed*, not *enforced*. One video where two genuinely different labels land
inside 2 seconds silently deletes one of them, and nothing says so.

**The cheap version is detection, not a code change.** After each newly annotated video, check
whether any merge collapsed two rows whose resolved labels differ; if none ever does, the
enforcement is not worth writing. If one does, merge only when the resolved labels match — which
turns [[D-033]] from an observation into an invariant.

**Trigger: runnable today, and the only measurement here that is.** It needs an annotated video,
not a skill pass. Video 2 qualifies and is the sharpest possible test — 75 clips over 64 minutes,
14 clusters under 45 seconds apart, and **zero extracted stamps**, so `resolvedLabel` cannot
manufacture the text-identity that made video 1 safe.


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

- **~~The synthetic `0:00 Start` line~~ — decided 2026-08-19: keep it.** [[D-033]] carries the
  reasoning. It costs no marker and is the only one of YouTube's four chapter requirements
  obtainable for free, so removing it would foreclose chapters on every future video to save one
  line. Recorded here rather than deleted, because it was briefly removed and should not be
  re-proposed from the same wrong premise.

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
