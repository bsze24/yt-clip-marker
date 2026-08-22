---
date: 2026-08-21
time: "16:33"
revised: 2026-08-22 06:15
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

---

# Append — 2026-08-22 06:20 — the inbox spec, and two review rounds

The 16:33 log ends with the eval work. Everything after it is coordination and review: Phase 6
specced, Codex's Phase 2 readiness review resolved, and PRs 29 and 30 reviewed. Project state is
already committed — `CURRENT.md`, `REVIEW.md` threads 11-13, `DECISIONS.md`. This append carries
the part that has no home in those.

## What changed

- `c3ff035` — Phase 6, the lesson inbox, appended to `CURRENT.md`. Staging goes **outside the
  repo** (Brian's call): `docs/reference/**/*.mp4` is gitignored and `git clean -xdf` deletes
  ignored files, so 2.4 GB of Zoom exports sat one clean away from gone.
- `633e37e` → `183e836` — Codex's five Phase 2 contracts resolved inline, then the baton synced.
- `f77bdb7` — the review thread collapsed out of §3 into the contracts it changed.
- `1b700c2` → `39e8e04` — PR 29 reviewed; F36/F37 filed; the ledger audit.
- `e3b640c` — PR 30 reviewed; F38/F39 filed.

## Decisions

- **A review thread does not live inside the task spec.** `CURRENT.md` reached 745 lines with 187
  of them a review annotating a 114-line contracts section. The rule that came out of it:
  **fold the decisions into the contracts they change, move the argument to the handoff notes,
  and file anything that is a defect in merged code as its own `REVIEW.md` finding.** 187 lines
  became about 20 in §3 plus a dated note.
- **A spec review has no target SHA, so it does not belong in `REVIEW.md`.** Rule 1 of that file's
  own concurrency protocol is one thread per SHA. I proposed moving the thread there and reversed
  it on re-reading the protocol. Precedent already existed: the earlier readiness review was in
  the handoff notes.

## Learning arc

- **Folding a decision into a contract forced a correction I would not have found by re-reading
  my own argument.** I claimed Phase 3 hard-depends on Phase 2. §3.9 already ended "a free-text id
  entry stays available for the offline case" — the paste door was in the spec the whole time.
  Confidence went moderate → low and the recommendation weakened. Writing the decision *into the
  place it governs* is what surfaced it.
- **Reviewing my own work twice, and naming it both times.** F35 was my finding and I reviewed
  its fix; F39 is a hole in the contract I wrote and I filed it against the contract rather than
  against Codex's implementation. Saying "this one is mine" in the finding is what keeps a
  review from quietly grading its author's own homework.
- **The ledger pointed away from a live finding.** Thread 7 read CLOSED while F31 had been open
  since 2026-08-21. A stale CLOSED is worse than a stale OPEN, because nobody re-reads a closed
  thread.

## Concepts touched

- [concept] concurrent-writers-on-shared-docs — solidifying — was `stuck`. Three practices that
  worked: append at the end of a file someone else holds, insert-only edits with exact-match
  anchors and a zero-deletions check, and writing from a separate git worktree when the main
  checkout is on another agent's branch
- [concept] one-name-per-thing — solidifying — the doc-home rule is the same shape: contracts in
  the spec, findings in the ledger, lessons in the log, and a fact in two places drifts
- [concept] proxy-vs-recorded-fact — solid — the canary proves the login worked, not that the
  listing was complete; F39 is exactly that gap, and I wrote the proxy myself

## Coaching hooks

- **Verify a claim in the environment it will run in, not the one you are typing in.** The
  `PATH` bug hid for three PRs because every check was from a terminal. When the next
  environment-shaped claim appears, the question is "measured where?"
- **Probe, do not reason, when the claim is about behaviour under a bad input.** Both PR 30
  findings came from a 30-line script, not from reading. Reading said `_validated_cache` was
  strict; running it showed strict validation turning into data loss two calls later.

## Next / open threads

1. **PR 30 — Brian's merge call.** F38, F39 optional; both small, both in a file it already
   touches.
2. **F36, F37** open against `main` — next PR that opens `apps/studio/studio`.
3. **F31** still open in thread 7.
4. **Phase 3** after PR 30, carrying F32 and F34.
5. **Phase 6, the lesson inbox** — specced, unbuilt. The 2.4 GB has not moved out of the repo yet.
6. **Use v2 for real on the next lesson** ([[D-043]]) — still the only open eval item, still
   waiting on a lesson existing.

## Chronology (the record)

- Five Zoom exports appeared in `docs/reference/`; Brian asked for a staging folder the tool
  detects. Found three of his four steps already existed and only discovery was missing; specced
  it as Phase 6 and appended rather than edited, since Codex held the file.
- Verified the sidecar matcher already handles the new ` (1)` plus `_1920x1384` filenames, so the
  spec says do not "fix" working code.
- Resolved Codex's five Phase 2 contracts inline. Verified finding 1 rather than accepting it and
  found it was bigger than reported: in-app ingest was already broken on the launchd agent. Filed
  F35 in its own thread.
- Rejected "define an authentication predicate" in favour of merge-never-remove, because an
  authenticated 56 and an unauthenticated 2 are both exit 0 with valid JSON.
- Brian asked whether all of that belonged inline. Measured the file, agreed it did not, and
  collapsed it.
- Reviewed PR 29. Tested the missing-binary branch the audit could only inspect. Filed F36, F37.
- Audited the ledger before the next round: thread 7 mislabelled, thread 11 heading stale, PR 27
  merged unreviewed, two "open in PR 27" pointers stale after it merged. All corrected; PR 27
  recorded as thread 12, unreviewed, with what would justify opening it.
- Reviewed PR 30. Ran the branch's 35 tests, then probed three edge behaviours: truncated
  authenticated refresh, clock skew, and a malformed cache row. Two became F38 and F39.
- Found the main checkout sitting on Codex's branch; wrote every doc commit from a separate
  worktree on `main` and left their tree untouched.

---

# Append — 2026-08-22 06:15 — closing the thread; the build gets its own

Written to close this thread. The next session should start a **new log on a build track**, and
the reason is in Decisions below.

## What changed

Times are **UTC**, from the transcript. Brian set that convention on 2026-08-22 — it is
what `REVIEW.md` and `CURRENT.md` already used, and what makes the review dates there correct
rather than a day ahead. The filename's `1633` is local-at-creation and stays as it is: it is this
file's identity, and `AGENTS.md` points at it by name.

- `0558373` — the inbox migration recorded. `~/lesson-inbox/` now holds 2.3 GB;
  `docs/reference/` is back to 64 KB; both `media/` symlinks re-pointed and verified resolving.
- `1b700c2`, `39e8e04` — PR 29 reviewed, F36/F37 filed, ledger audit.
- `e3b640c` — PR 30 reviewed, F38/F39 filed.
- `cc5f9d5` — the previous append.
- `127d790` — **the PR recut**: §4 rewritten with a PR column, §3.10a added, every open finding
  given a landing PR, both batons repointed.
- Merged in this window by Brian: PR 29 (`255739f`), PR 30 (`9622365`).

## Decisions

- **PR boundaries follow blast radius, not size.** Phase 3 writes a new verdict type into an
  append-only store ([[D-002]]); Phase 4 `shutil.move`s the user's only copy of a recording. Each
  gets a review with nothing else in it. Phase 5 is a string and rides with Phase 3. Recorded in
  `CURRENT.md` §4.
- **Phase numbers are identities, not build order.** §3.7 is "Phase 4" in `REVIEW.md`, in finding
  text and in three handoff notes. §4 gained a PR column instead of a renumber — the same rule
  that forbids renumbering findings.
- **Phase 6 before Phase 4**, because both need the same realpath primitive and the read-only one
  should be reviewed first. Phase 4 must import `inbox.py` rather than grow a second copy.
- **This thread closes on `track: reduce-manual-tagging`; the build starts a new one.** The track
  is the eval thread and roughly 80% of this session was the local-file loop. Continuing to append
  build content to an eval-tracked log is what makes `track:` stop working as a selector.

## Learning arc

- **Asked whether the review notes were actually being archived, not whether they were good.**
  That question found a real gap: reviews were durable, the process reasoning was not. The doc-home
  rule sat in chat for three commits before landing anywhere.
- **Asked whether phases 3-6 were "just polish" rather than accepting the phase list as a plan.**
  They were not — two of the four fail by destroying data. The question surfaced a cut nobody had
  proposed.
- **Asked whether the thread could be closed before closing it.** The answer turned out to be no
  without one fix: `AGENTS.md` names the wrong head for this track.

## Concepts touched

- [concept] pr-as-container-vs-live-document — solidifying — the cut is by what a wrong version
  destroys, not by diff size; two phases fail in different ways and neither may share a review
- [concept] one-name-per-thing — solid — phase numbers kept as identities with order moved to a
  separate column, rather than renumbering and breaking every reference
- [concept] concurrent-writers-on-shared-docs — solidifying — a full session of two agents on the
  same four docs with nothing lost: append-at-end, insert-only anchors, separate worktree
- [concept] active state vs learning state — solidifying — the split held under pressure: findings
  to `REVIEW.md`, contracts to `CURRENT.md` §3, arguments to handoff notes, lessons here

## Coaching hooks

- **Ask "is it recorded?" before "is it right?"** Twice today that question found the gap: review
  notes were durable, process reasoning was not; and the ledger read CLOSED over a live finding.
- **A stale pointer at an entry point costs more than a stale deep doc.** `AGENTS.md` named the
  wrong head for this very track while the track was live. Third instance of this pattern.

## Next / open threads

1. **PR A — Phase 3 + Phase 5**, carrying F32, F34, TD-17, TD-18. `CURRENT.md` §4 and §6.
2. **PR B — Phase 6**, then **PR C — Phase 4**. **PR E** — F31, F36, F37, the `annotated` proxy —
   any time.
3. **Times are UTC from here.** Set 2026-08-22. `REVIEW.md` and `CURRENT.md` were already
   written that way, so their `2026-08-22` review dates are correct and need no sweep. Git's own
   author dates stay local `-0700`, so a commit reading `Aug 21 22:24` and a ledger entry reading
   `2026-08-22` are the same moment — expect that, do not "fix" it.
4. **Use v2 for real on the next lesson** ([[D-043]]) — the only open eval item, waiting on a
   lesson existing. **This is what `track: reduce-manual-tagging` resumes on**, and it is the one
   thing the new build track should not absorb.

## Open questions / blockers

- None blocking. The build can start from `CURRENT.md` alone.

## Chronology (the record)

UTC, anchored to the transcript. The session crosses UTC midnight, which is why the reviews
carry `2026-08-22` dates.

- **08-21 23:16** — session opens with three eval next steps and "check the latest session logs for state".
- **23:18** — `yt-clipper` invoked for real; v2 smoke test on video 3. 99 proposals, 2.25/min,
  99/99 on exact cue starts, no gap over 60s. Score deliberately not recorded ([[D-043]]).
- **~23:25** — star predictability test. Ten features dead; the ceiling test — a model reading
  Brian's own labels — lands at 0.513. D-044 written; PR 27 opened.
- **23:33** — first session log.
- **23:56** — five Zoom exports found in `docs/reference/`; staging-folder question. Phase 6
  specced and appended, since Codex held the file. Staging goes outside the repo.
- **08-22 04:55** — Codex's five Phase 2 contracts resolved inline. Finding 1 verified rather than
  accepted, and it was bigger than reported: in-app ingest already broken. F35 filed.
- **05:00** — "all this inline at current.md?" Measured: 187 lines of review inside a 114-line
  contracts section. Agreed it did not belong.
- **05:01** — collapse executed. Decisions into contracts, argument into handoff notes, F35 into
  `REVIEW.md`. Reversed my own proposal on re-reading rule 1: a spec review has no target SHA.
- **05:24** — PR 29 reviewed. Tested the missing-binary branch the audit could only inspect.
  F36, F37 filed.
- **05:33** — "make sure your notes are in review.md". Ledger audit found four stale things,
  including thread 7 reading CLOSED over an open F31.
- **05:46** — PR 30 reviewed. 35 tests run, three edge behaviours probed. F38, F39 filed; F39 is a
  hole in my own §3.5 5a.
- **05:54** — "are you consistently posting these?" Grepped rather than asserted: reviews yes,
  session log no. Append written.
- **05:57** — state-of-the-app assessment, measured from disk and the live API rather than the
  plan. Headline: nothing about marking clips changed and no disk has been freed.
- **06:04** — "are 3-6 polish?" No: two of them destroy data when wrong. PR cut proposed.
- **06:08** — Brian agreed the ordering. §4 recut, §3.10a promoted, findings assigned homes.
- **06:11** — `/session-log`, asking whether the thread can close.
- **06:12** — asked for timestamps on the chronology. Converting them exposed that this file mixed
  UTC and local; Brian set **UTC** as the convention, so the previous append's `06:20` heading was
  right the first time and the "local" correction was the error.
