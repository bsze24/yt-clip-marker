---
date: 2026-08-17
time: "19:14"
revised: 2026-08-19 05:37
surface: grok
project: yt-clip-marker
track: two-surface-land
branch: main
commit: 4c95f9cfb111378bc6bdb47149bf23b1811babbf
task: docs/coordination/CURRENT.md
---

# Session log — 2026-08-17 19:14 (grok) — docs-vocab-extracted-and-clocks

## Project context
- This sitting started on `docs/remove-coordination-md` cutting the coordination README, then
  pushed the `gold` → `extracted` rename onto PR 3. It is the same `two-surface-land` thread as
  `2026-08-19-0528-claude-code-pr3-review-and-docs-reconcile.md`. That later log is the resume
  head. `main` at this write is `4c95f9c`. Baton in `CURRENT.md`: **→ reviewer** on PR 4
  (`43c99dd`). PR 3 merged; PR 5 closed as superseded.
- Working tree has uncommitted edits in `docs/coordination/BACKLOG.md` and `REVIEW.md`. Not
  from this log; left alone.

## Summary
Cleaned the coordination README, renamed the description-stamp lane from gold to extracted, and
spent the long middle of the sitting on why the grid’s time column is not the clip’s time. Ended
with a reference note and a `docs/reference/` home for folds and explainers.

## What changed
- `6ebc21a` — PR 3: write `extracted[]`, still read `gold[]` as a silent fallback. This sitting.
- Later on PR 3, not this agent: `162e2f4` made `gold[]` a visible load fault ([[D-023]]).
- Uncommitted at the time, later in `69ff615`: coordination README vocabulary (skill / added /
  extracted marker), `docs/reference/2026-08-18-1217-stored-vs-displayed.md`, folded ledger
  moved out of `docs/sessions/`.
- Wrote a Codex prompt for the hard deprecation (`attach_extracted.py`, migrate PR 4, fault on
  stragglers). Did not run it here.

## Decisions
- **Call the description-stamp lane extracted, not gold.** Gold collided with the `g` grade.
  Harvested later as [[D-023]].
- **Product names are parallel: skill marker, added marker, extracted marker.** The store is
  still three records, not one `type` field.
- **CSS `--gold` / `--gold-text` stay.** They are a paint color, not the lane.
- **A silent `extracted || gold` fallback is the wrong deprecation.** Own the data, migrate it,
  make a leftover `gold` key a visible fault.
- **Folds and explainers live in `docs/reference/`, not `docs/sessions/`.** Session logs stay
  resume files. The session-log skill only greps `docs/sessions/`.

## Learning arc
- Read **gold** as the few-shot grade. It is the YouTube-description lane. `g` is the grade. The
  rhyme was the trap.
- Proposed one `marker` with a type. That collapses three stores. Delete of an add is `unmiss`,
  not `x`.
- Needed three passes on displayed vs stored time. First was two clocks and a cluster. Second
  was subtitles and a sticky note. Third was: for concepts, drift is not required at all.
- Was sure the skill guessed a word inside a caption. `fetch_transcript.py` keeps only the
  caption-block start. Retracted.
- Isolated takes and extracted, then asked why stored would ever drift. The leftover is
  `R-NEIGHBORHOOD`: the skill emits approximate `M:SS` instead of copying `cue.start`. That is
  slop for concepts, not a word clock.
- Asked whether `docs/reference/` breaks anything. Runtime no. Agent routing yes, until the
  “where things go” table moves.

## Concepts touched
- [concept] displayed-time vs stored identity — solidifying — three explanations; the concept-only case landed when takes and extracted were excluded
- [concept] eval channels vs product keep (g / x / taxonomy / star / delete) — solidifying — star pulled out of the eval list; blank is the default unread skill marker, not a rare edge
- [concept] one-name-per-thing — emerging — gold vs `g`; skill / added / extracted as parallel names for three records
- [concept] skill as suggester not workflow — solidifying — concept times should be caption starts; `R-NEIGHBORHOOD` is the fudge; nailing is the studio

## Coaching hooks
- **I overclaimed, you interrogated the input.** Word-granularity died when we opened
  `fetch_transcript.py`. Next time a placement story appears, show the actual lines the skill
  sees before explaining the clock.
- **Exclude the exception.** The 1:18:50 README cluster is a demo (take-shaped). It cannot prove
  the concept case. You kept cutting takes and extracted until the real question was left.
- **Sticky note after two dense passes.** Mechanism-before-analogy still holds; the analogy only
  worked once the caption-as-row picture was already there.

## Next / open threads
- Resume `two-surface-land` from `2026-08-19-0528-claude-code-pr3-review-and-docs-reconcile.md`
  — PR 4 review is the live baton.
- Open questions on concept timestamps live in
  `docs/reference/2026-08-18-1217-stored-vs-displayed.md`: tighten `R-NEIGHBORHOOD` so concept
  `start` = the firing caption’s start?
- Point the coordination README table at `docs/reference/` for folds and explainers. Stale
  `docs/sessions/…folded-ledger.md` citations remain in older logs.

## Open questions / blockers
- Should concept markers copy `cue.start`, so stored time equals displayed time for that class?
- Takes (gap clock) and extracted (description clock) still need two times on a caption row, or
  the left column stops matching the subtitle.
- Use discarded json3 word offsets? Probably not, if captions are the right grain.

## Chronology (the record)
- **19:14** — README filler: learning-state bullet does not follow from cold start. Cut it.
- **19:16** — `DECISIONS.md` note was incident-specific (`e158710`, D-001…D-022). Asked to
  generalize in README only.
- **19:20** — `git log --all -- path` lists commits; it does not print the file. Tether
  decisions to the work SHA, not “newest anywhere.”
- **19:30** — Line 40 “gold” looked wrong. You were describing `g`. Gold is the description
  lane. Proposed skill / extracted / added as types with a grade on skill only.
- **19:37** — Understood the collision. Asked if the three are different schema parts, and what
  `unmiss` is. Yes: three records. Delete button writes `unmiss` (eval slang: undo a `miss`).
  README should lead with the grid, then a store footnote.
- **19:39–19:41** — Rename gold globally to extracted or derived. Then align names:
  skill_marker / added_marker / extracted_marker.
- **19:41–19:51** — Picked extracted. Prose names, not underscores. Docs on this branch; studio
  JSON still `gold` on PR 3. CSS `--gold` left as paint. `attach_gold.py` left as filename.
  Star listed as a fifth eval verdict — wrong shelf.
- **19:51** — Append the rename to PR 3; deprecate gold.
- **19:51–20:00** — PR 3 `6ebc21a`: write `extracted[]`, silent read of `gold[]`. Pushed.
- **11:00 (08-18)** — Silent fallback hides stragglers. Best practice here: migrate data, one
  loud shim, then delete the shim. CSS gold is the color.
- **11:00** — Why not rename `attach_gold.py` to something like `extract_ytdescription.py`?
  Stopped to talk, no edits.
- **11:01** — `attach_extracted.py` is the name (pairs with `attach_cues.py`). Asked for a
  Codex prompt covering the whole hard deprecation. Wrote it. Did not run it.
- **11:59** — Is the star eval bullet necessary? No. It is a tag. Four channels: `g`, `x`,
  taxonomy-without-`g`, blank.
- **12:01** — Is blank even possible? Yes: default unread skill marker. Video 1 ended `blank 0`.
- **12:03–12:06** — Standing trap. First pass too dense. Second: grid is subtitles; clip is a
  sticky note on the nearest subtitle.
- **12:06** — Why aren’t markers always caption timestamps? Skill would mark 0:22 if cues are
  0:18 and 0:24?
- **12:09** — Quoted the caption-span paragraph. Exclude takes. Is that word granularity, with
  the skill guessing when the word occurs?
- **12:09** — Checked `fetch_transcript.py`. No. One start per caption block. Retracted.
- **12:12** — Exclude takes and extracted. Then why would stored ever drift? Guessing a word
  inside a short, listed caption feels like a bad design.
- **12:13** — For concepts, drift is not required. The skill emits approximate `M:SS` under
  `R-NEIGHBORHOOD` instead of copying `cue.start`. README 1:18:50 example is a demo.
- **12:13** — Print `R-NEIGHBORHOOD`. Entire rule: “Approximate timestamps; clip-marker nailing
  is downstream.”
- **12:17** — Cut a markdown file of this stretch, summary and open questions at top. Landed
  first under `docs/sessions/`, then moved to `docs/reference/`.
- **16:00** — Any consequence of `docs/reference/` for the ledger and the clocks note? No
  runtime. Stale pointers in CURRENT/REVIEW/README/AGENTS. Session-log skill ignoring
  `docs/reference/` is the point.
- **05:36 (08-19)** — `/session-log`, same track and filename pattern as the Claude 05:28 log.

## Banked artifacts

**`R-NEIGHBORHOOD` as printed.** From `~/.claude/skills/yt-clipper/SKILL.md`: “Approximate
timestamps; clip-marker nailing is downstream.” That is the whole rule.

**What the skill actually sees (concepts).** `fetch_transcript.py` `parse_json3` joins every
`segs[].utf8` in a YouTube caption event and keeps only `tStartMs`. Word offsets, if present,
are thrown away. The skill gets `0:18\tlet's look at this lick` then `0:24\tnow play it slow`.
A concept marker at `0:22` is rounded `M:SS`, not a located word.

**Sticky-note picture (second pass, the one that worked).** The grid is a list of subtitles.
The left column is when those words appeared. A clip is a sticky note on the nearest subtitle.
The note can still have a different time on the back. The trap is treating the subtitle time as
the clip time.
