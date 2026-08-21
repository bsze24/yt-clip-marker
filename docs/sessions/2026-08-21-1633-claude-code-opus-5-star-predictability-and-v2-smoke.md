---
date: 2026-08-21
time: "16:33"
surface: claude-code-opus-5
project: yt-clip-marker
track: reduce-manual-tagging
branch: main
commit: b621708e5e051a195ef89e3ee5543e88315fe1ed
task: docs/reference/EVAL.md
---

# Session log — 2026-08-21 16:33 (claude-code-opus-5) — star-predictability-and-v2-smoke

## Project context
- Continues `track: reduce-manual-tagging` from
  `docs/sessions/2026-08-19-2350-claude-code-opus-5-tagging-audit-and-autotag-ceiling.md`. That
  log's 16:00 append lists three next actions; this session did the first two.
- Codex is working the `CURRENT.md` phases 1-4 concurrently. Nothing here touches that path —
  no product code, no `CURRENT.md`, no `REVIEW.md`, no `clip-schema.md`.
- Live docs are `docs/reference/EVAL.md` (eval state) and `DECISIONS.md` (D-040 → D-044).

## Summary
Ran `SKILL.md` v2 for the first time — a smoke test on video 3, per [[D-043]], score not
recorded. Then answered the one open eval question that could subtract from the roadmap: nothing
in the transcript predicts `star`, so rung 4 of the ML ladder loses its target. Recorded as
[[D-044]].

## What changed
- `b621708` (main) — `EVAL.md` §7E answered, §8 reordered, §5 ladder updated, §4's "v2 has never
  been run" closed; `DECISIONS.md` D-044; `BACKLOG.md` guard line against recording the smoke
  test as a v2 result. Also corrected video 1's counts in the §2 corpus table.
- `d8b21f1` (PR 27, open) — `apps/studio/eval/star_predictability.py`, the re-runnable evidence
  behind D-044. Stdlib only, reads the store, writes nothing.
- Not committed, by design: `/tmp/video3-proposals-v2.json` (99 proposals, the smoke test).

## Decisions
- **D-044 — nothing in the transcript predicts `star`; rung 4 loses its target.** The ladder
  stops at rung 3, and rung 2 is the top of it still worth building. Full argument in
  `DECISIONS.md`; the measurement is in `EVAL.md` §7E.
- **The smoke test's numbers are not a v2 result and a guard line now says so in `BACKLOG.md`.**
  They look excellent (100% star recall at 30s) precisely because every v2 rule was derived from
  video 3. Left unmarked, a later session records them as a measurement — which is the error
  [[D-043]] exists to prevent.
- **The evidence script goes in the repo, not `/tmp`.** D-044 deletes planned work. An argument
  for deleting work is worth less when it cannot be re-run.

## Learning arc
- Nothing here yet — this was an execution session against a list Brian had already scoped. The
  learning content is the finding itself, which is in `EVAL.md` §7E and D-044 rather than here.

## Concepts touched
- [concept] feature problem vs data problem — solid — the `star` result is the same shape as the
  `take` result that produced D-040; recognising it before running the test is what made the
  ceiling test the right design rather than a bigger feature table
- [concept] proxy-vs-recorded-fact — solidifying — `demo` in Brian's own label is *evidence about*
  what `star` means, not a feature the skill could ever use; keeping those two apart is what
  stops the 86% number reading as a predictor
- [concept] eval-channels — solid — the fold had to distinguish `miss` / `annotate` / `unmiss`
  from `relabel`, and checking that `relabel` carries no tags is what made the star counts safe

## Coaching hooks
- **A feature table cannot prove a negative; a ceiling test can.** Ten regexes scoring at chance
  proves the regexes are bad. Giving a strong reader a *richer* input than the one in question —
  Brian's own labels — and watching it score 0.513 is what licenses "no". Reach for the ceiling
  framing whenever the answer being defended is "this is not possible".
- **The suspicious number is the one that agrees with you.** `position_in_lesson` came out at
  p<0.001 and would have been a finding. Splitting video 1 into halves — 0 stars in 11 clips,
  then 9 in 10 — is what showed it to be a change in how he was labelling, not the lesson.

## Next / open threads
1. **Use v2 for real on the next few lessons**, recording the four numbers ([[D-043]] §C):
   proposals offered / accepted without playing the video / had to scrub / added unprompted.
   This is now the only open eval item that can change the plan. It needs a lesson that exists —
   blocked on a recording, not on code.
2. **PR 27 is open and unmerged.** Brian's call.
3. `score_run.py`'s `annotated` proxy and **F31**, both one-liners in the same file, same pass.
4. `CURRENT.md` phases 1-4 — Codex's lane.
5. `EVAL.md` §7 A, B, D still open. C and E are now closed.

## Open questions / blockers
- Item 1 above needs a lesson Brian has recorded and not yet marked. Unknown whether one exists.
- **`resolvedLabel` still prefers an extracted description label over the app's own** — flagged
  in the previous log's 15:35 append, still deliberately unchanged.

## Chronology (the record)
- Read the coordination docs, `EVAL.md`, `D-041` → `D-043`, and the previous log's last three
  appends to confirm the thread's state before touching anything.
- Generated video 3's transcript from its run with `make_transcript.py` (696 lines, 8 GAP flags).
- Invoked the `yt-clipper` skill and read the transcript end to end. Produced 99 proposals over
  44 minutes: 2.25/min against `R-COPIOUS`'s floor of 1, 99/99 on exact cue starts, no gap over
  60s. Validated all three programmatically rather than by eye.
- Scored it: 100% star recall at 30s, 78% precision at 30s. **Not recorded as a v2 result.** The
  smoke test's only claim is that v2 executes and obeys its own rules.
- Built the star test. Ten transcript features over a ±window at each of the 147 clips. Best
  pooled AUC 0.603 at p=0.035, which dies under ten comparisons and reverses on video 1.
- `position_in_lesson` came out at 0.671, p<0.001 — the one feature that beat chance. Chased it
  rather than reporting it: video 1 holds 0 stars in its first 11 clips and 9 in its last 10, a
  regime change in his labelling. Video 2, the largest sample, shows nothing at all.
- Ran the ceiling test. Scored all 75 of video 2's labels blind, 0-10, before looking at any
  star tag. Result 0.513, p=0.86. Top 10 picks 60% starred against a 48% base; top 20 below base.
- Read the errors instead of stopping at the number. Ranked *General rule louder for higher
  notes* and *This technique is called a line cliche* at the top — neither starred. Ranked *Line
  2 — jake take* at the bottom — starred. That inverted the working model of what `star` means.
- Tested the inversion: `demo` in his label 86% starred, `take` tag 78%, `chord exercise` 73%,
  against `fingering` 0/7 and `technique` 0/5. `star` marks the demonstration, which D-040
  already established is not text-detectable.
- Spotted `composer.js:47` auto-tagging `take` on gap-created clips, which would have made the
  `take` correlation partly mechanical. Checked: only 8 of 147 clips are gap-created, and landing
  on a gap cue predicts `star` at 38% against a 45% base. Not mechanical, and R-TAKE-GAP's
  retirement holds independently — 8 of 61 gap cues in the whole corpus ever became a clip.
- Audited the fold before trusting any of it: `relabel` events carry no `tags` field, so they
  cannot change a star. Confirmed the counts, and found `EVAL.md` §2's video-1 column disagreed
  with every fold of the store — starred 11 where it is 17, tagged 34 where it is 59. Corrected.
- Consolidated four scratch scripts into one committed file so D-044 is checkable, opened PR 27
  for it, and committed the docs straight to `main` as living records.
