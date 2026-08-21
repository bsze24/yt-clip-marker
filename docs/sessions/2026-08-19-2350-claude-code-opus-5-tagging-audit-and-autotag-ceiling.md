---
date: 2026-08-19
time: "23:50"
revised: 2026-08-21 16:00
surface: claude-code-opus-5
project: yt-clip-marker
track: reduce-manual-tagging
branch: main
commit: a9c6cc037ce454ad98a83378ab8442f82a3e3920
task: docs/coordination/CURRENT.md
---

# Session log — 2026-08-19 23:50 (claude-code-opus-5) — tagging-audit-and-autotag-ceiling

## Project context
- New track. Opens with an audit of how Brian tags and ends with the autotagging ceiling scoped
  and the next task specced. `git show 1daecd8:docs/coordination/CURRENT.md` is the eval task
  that came out of it — score the existing skill against video 2, baton on Brian.
- Also carried `offline-capability` to a close mid-session: PR 9's F20-F23 fixed at `8a47c2b`,
  reviewed, merged at `2ee9cc9`. Nothing owed on that thread.
- Repo is clean. Everything below is committed and pushed.

## Summary
Audited two labelled videos, found the ceiling on auto-tagging is three different ceilings, and
scoped which of them are worth chasing. Along the way: fixed four review findings on PR 9, cut
`REVIEW.md` by 80%, and recovered five work items that were living in chat logs and closed
entries.

## What changed
- `c6ebec8` — PR 9 handed to review; PR 8 closed; the tagging-reduction path recorded in
  `BACKLOG.md` with `TD-13`/`TD-14`/`TD-15`.
- `6a3a5e7` — three items that existed nowhere a `BACKLOG.md` reader would find them: skill
  revision from run 1's corpus, the synthetic `0:00 Start` line, and `TD-16`.
- `3fac722` — cleanup pass. `REVIEW.md` 798 → 155 lines, `D-031` collapsed as superseded, the
  banned `gold` vocabulary corrected in `D-011`/`D-013`/`D-020`/`D-022`.
- `8a47c2b` — PR 9 F20-F23, with browser receipts. `0ffb722` threaded the responses.
- `93da38b` — the ceiling table, the finish line, and `CURRENT.md` replaced with the eval task.
- `1daecd8` — video 2's store and five run files. They had never been committed.

## Decisions
- **More hand-tagged videos is not the lever for the 75% goal.** Domain tags separate on
  transcript keywords with zero training examples; `take` and `star` have no text signal at all.
  Labelling improves neither. Recorded in `BACKLOG.md`, "What the ceiling actually is".
- **Run the flawed skill before rewriting it.** No baseline, no way to tell v2 from merely
  different — and the rewrite case rests on predictions that the run would falsify.
- **Skip recoverable tags when marking video 3, keep `star` and who-was-playing.** Anything the
  transcript can reconstruct is not worth his keystrokes; those two it cannot.

## Learning arc
- Came in reading his own inconsistency as the problem. It is not the main one — the tag field
  is four questions in one multi-select, and the drift he noticed is what that produces. Both of
  his specific observations were right, each for a different reason than he assumed.
- Proposed "tag less granularly" as the path to 75%. Dropped it once the measurement landed:
  all 21 hand-added clips on video 1 sat within 90s of a skill marker, so the manual work was
  nudging, not authoring, and cutting granularity would cut output one-for-one.
- Asked "fair to say we're working on 1) here?" against a list he'd been handed elsewhere. It
  was not — the 23 `g` exemplars are used nowhere in the recorded path. Checking whether the
  written plan matched the actual gap is the move; it found three homeless items.
- Named the doc drift himself — "this is becoming a re-organization thread" — and asked for a
  cleanup pass rather than continuing to add on top of it.
- Went from taking `SKILL.md` as given to interrogating a section of it, then found the root
  cause before I did: the skill was developed against an incompletely-marked video **and** the
  workflow has since reversed to Zoom → tool → YouTube.
- Posed the scoping question well — is the ceiling low, so give me guide points, or high, so
  invest up front. That framing is what made the three-way split findable; a single "how good
  can it get" would not have.

## Concepts touched
- [concept] anchored vs unanchored ground truth — solidifying — video 1's 100% recall may be an
  artifact of judging where the model pointed; video 2 he chose blind, which is why it is the test
- [concept] feature problem vs data problem — emerging — `take` has no text signal, so more
  labelled videos cannot fix it; caught the difference before proposing more labelling
- [concept] rule premise vs rule conclusion — emerging — `R-NO-TALK-DETECT`'s stated evidence is
  wrong (43 min claimed, 21.9 real) and its conclusion is still right, confirmed independently
- [concept] stated-principle-vs-enforced-invariant — solid — same shape as `TD-16`: `D-033` says
  every marker reaches the output and the fold never checks label text
- [concept] eval channels vs product keep (g / x / taxonomy / star / delete) — solid — spotted
  that the stored `verdict` disagrees with its own `feedback` on 144 events, now `TD-14`
- [concept] concurrent-writers-on-shared-docs — stuck — bit twice in one session, and the second
  near-miss would have deleted a blocking review finding

## Coaching hooks
- **Measure before asserting — it worked every time and twice changed the answer.** The lexicon
  test produced the ceiling split. Generating the transcript file proved "teach the skill to read
  a run" was overstated. Running the old `local.py` showed the `.info.json` half of F20 fixed
  nothing. Reach for the measurement first, not after he pushes back.
- **Going quiet during multi-step work reads as stalled.** He interrupted F20-F23 with "are we
  all set here? didn't see a summary". Status questions get the answer in the first line, and
  long stretches need a checkpoint.
- **The `/plain-english` failure was ordering, not vocabulary.** The passage led with "there is no
  second video" one turn after establishing that video 2 exists and is fully annotated. Rewording
  would not have reached it; running the thing did.

## Next / open threads
- **Run the existing `yt-clipper` against video 2 and score it.** Spec in `CURRENT.md`, baton on
  Brian. Region recall is the number that matters — video 1 said 21 of 21 within 90s, and if
  video 2 disagrees the premise under the whole roadmap is wrong.
- **Then mark `GMT20260712`** — placement and label only, keeping `star` and who-was-playing in
  the label text. It resolves the lesson-type confound, not training data.
- **Then decide the `SKILL.md` rewrite.** Six rules are keepers on evidence, four are premised on
  YouTube auto-captions and dead on a Zoom transcript. Do not act before the eval returns.
- The junk-caption labelling gap is the highest-leverage single rule change found: 11 TAKE
  markers landed on a stub caption, none earned a `g`, and all three `g` takes landed on a real
  sentence. Not yet filed anywhere.

## Open questions / blockers
- Whether video 1's total region recall is real or anchoring. The eval answers it.
- Whether `R-TAKE-GAP` dies on Zoom transcripts or whether video 2's lesson type is the confound.
  Prediction filed in `CURRENT.md` as falsifiable.
- The ceiling table's `polish` row is the weak one — 86% vs 64%, read as a default class rather
  than a real one. That reading is interpretation, not measurement.

## Chronology (the record)
- **00:35** — "2nd review is in", asking for an audit of videos 1 and 2, a rating as eval/training
  data, and a diagnosis of his tagging. Two observations: `take` really means "jake demo", and
  "chord exercise" never appeared in video 1's dropdown.
- Folded `labels.jsonl`. Star rate 25% on video 1 against 48% on video 2; 1.22 tags/row against
  1.83; 15 distinct tags with only 6 shared.
- Found the structural asymmetry first: video 1 is mostly him judging skill markers, video 2 is
  75 rows he authored with no proposals. Not two samples of the same thing.
- Chased the dropdown report and could not reproduce it — the API returns `chord exercise` on 15
  rows. Real cause is that vocabulary is scoped per run, so any fresh video shows four tags.
  Filed as `TD-15`.
- Found 144 of 240 label events whose stored `verdict` disagrees with their own `feedback` text.
  Later traced to F9, fixed forward-only on purpose. Filed as `TD-14`, not as a new bug.
- Rated it: video 1 strong as an error taxonomy, video 2 strong as placement ground truth, both
  weak for auto-tagging — four axes in one field, no `end` times, no negatives.
- **00:46** — "reducing my manual tagging by 75%+ ... part of it is not tagging so granularly."
  Contested it. Measured all 21 added clips against the 64 skill markers: 21 of 21 within 90s,
  19 within 45s, zero missed regions. Sorted the 24 rejections — exactly one was a genuine
  disagreement about what is worth marking.
- *[~16 hour gap]*
- **17:13** — trace PR 9. Five product commits, spec covering two of them.
- "guessing you built that?" — no, a prior session did. Recommended landing PR 9 before starting
  schema work, since steps 4-6 of the path touch the same three files.
- Wrote the PR 9 review spec, closed `REVIEW.md` thread 4, harvested `D-034`-`D-038`, added the
  tagging path and three `TD`s.
- Committed the coordination docs to the branch instead of `main` — caught it, cherry-picked to
  `main`, re-merged. First instance of the concurrency problem.
- **~18:30** — "fair to say we're working on 1) here?" No. Recorded the missing loop, the `0:00
  Start` decision, and `TD-16`, all of which were living in a session log or inside a closed entry.
- **18:30** — "this is becoming a re-organization thread." Read all four 8/19 logs. Reproduced the
  per-rule reject table from a pasted handoff and found it recorded nowhere. Corrected one claim
  in it — the three largest gaps are not all rejects, the second is a `g`.
- Found the corpus blocker: four YouTube uploads with zero captions, still zero when re-checked.
  And `Oa0wqetkNcg` is video 2 uploaded — 3883s against a last cue at 3870s, title still the Zoom
  filename.
- Cleanup pass. `REVIEW.md` 798 → 155. `D-031` collapsed as superseded by `D-033`. Fixed `D-020`
  telling readers to stop saying "skill marker", which contradicts the mandated vocabulary.
- Mid-cleanup, `main` had moved: Codex had filed F20-F23 including a blocking one, and my
  `REVIEW.md` rewrite was built on the pre-review copy. Stopped before committing, saved to
  scratch, rebuilt. Then found `origin/main` three further commits ahead with a `D-033` correction
  contradicting an edit I had just made.
- **19:22** — "knock out all of F20-F23." F20 fixed and verified against the reviewer's own
  fixture, before and after. F21 took three attempts: capping the media at 100% of a shrink-to-fit
  wrap is circular and collapsed the video to 28px. Verified at 760×520 and 1280×800 — grid height
  0 → 162.
- **19:32** — interrupted with "are we all set here? didn't see a summary." Answered no and gave
  the actual state, including an untested edit sitting in the tree.
- **19:38** — "do it. any reason you paused on F23?" No gate; it was just last in the queue.
  Committed `8a47c2b`, threaded the responses, pushed.
- **22:12** — `/plain-english` on the corpus passage. Rebuilding it by running the thing exposed
  that "teach the skill to read a run" was overstated: the skill eats a text file, and fifteen
  lines produced one from video 2's run — 708 lines, 20 GAP flags, speaker names throughout.
- **22:28** — "what's the point of this section?" about `SKILL.md`'s negative rules. Measured all
  three. `R-NO-TALK-DETECT` confirmed independently on video 2. `R-NO-SPEAKER`'s premise is dead.
  Found the junk-caption labelling gap that accounts for 9 of 24 rejections.
- **23:27** — "should we just start the skill from fresh?" Checked his premise: the 43-minute claim
  in `SKILL.md` is 21.9 minutes in the store. Then found the stronger reason — `R-TAKE-GAP` does
  not transfer, because Zoom transcribes the playing (`Jake Sherman: Ba-ba-do da.`) instead of
  leaving silence.
- **23:34** — scoping the finish line. Ran the lexicon test: `harmony` 89% vs 42%, `comping` 100%
  vs 14%, `polish` 86% vs 64%, and no lexicon at all for `take` or `star`.
- **23:41** — two clarifying questions, and correcting my own ordering: video 2 is already
  unanchored ground truth, so the skill run needs no new marking and goes first.
- **23:43** — landed it. `93da38b` carries the ceiling table, the finish line, and `CURRENT.md`
  replaced with the eval spec.
- **23:46** — asked what was staged in `AGENTS.md`. Unstaged, and it predated the session: the
  rationale sentence naming PRs 5 and 6 had been dropped, probably by an editor reflow. Restored.
- **23:48** — noticed only one of three options rendered a Run button; only one was in a shell
  block. Then committed video 2's store — 147 label events and six run files that had never been
  backed up, and which tomorrow's task scores against.

## Banked artifacts

**Generate the skill's transcript format from a run.** Tomorrow's task needs this and its only
other copy is a scratch file. `>>> GAP` threshold is 20s, matching what produced 20 flags on
video 2.

```python
import json
run='apps/studio/runs/GMT20260730-155336_Recording_640x360-1-20260819-0903.json'
cues=json.load(open(run))['cues']
def hms(s): s=int(s); return '%02d:%02d:%02d'%(s//3600,s%3600//60,s%60)
out=[]; prev=None
for c in cues:
    if prev is not None and c['start']-prev >= 20:
        out.append('>>> GAP %ds @ %s'%(int(c['start']-prev), hms(c['start'])))
    out.append('%s\t%s'%(hms(c['start']), c.get('text','')))
    prev=c['start']
open('/tmp/video2-transcript.txt','w').write('\n'.join(out)+'\n')
```

**Fold `labels.jsonl` the way the server does** — file order, last match wins, never sort by
`recordedAt`. Every measurement in this session used this.

```python
import json
ann={}; add={}
for l in open('apps/studio/labels.jsonl'):
    ev=json.loads(l)
    if ev.get('runId')!=RUN: continue
    v=ev.get('verdict'); s=ev.get('start')
    if v=='annotate' and ev.get('markerIndex') is not None: ann[ev['markerIndex']]=ev
    if s is not None:
        if v=='unmiss': add.pop(float(s),None)
        elif v=='miss': add[float(s)]=ev
```

**Recompute a verdict from its feedback text** — the stored field is wrong on 144 historical
events (`TD-14`), so any scoring pass needs this rather than trusting `verdict`.

```python
def verdict_for(t):
    s=(t or '').strip(); l=s.lower()
    if l=='check' or l.startswith('check:'): return 'check'
    if l=='wrong' or l.startswith('wrong:'): return 'wrong'
    return 'note' if s else 'blank'
```

**Anchored vs unanchored ground truth.** Ground truth is *anchored* when the human judged
something a model already proposed — their attention was steered, so agreement partly measures
the steering. It is *unanchored* when they chose with nothing in front of them. Video 1 is
anchored (he graded 64 skill markers), video 2 is unanchored (75 rows, no proposals). It is NOT
about label quality: an anchored corpus can be perfectly labelled and still overstate recall,
because nobody counted what the model never showed him.

---

# Append — 2026-08-20 23:52

## What changed (second stretch)

- **PRs 10-15, all merged.** `10` merge only entries that print the same words (`TD-16`);
  `11` the eval scripts; `12` `transcriptSource` on the run plus the repo's first test file;
  `13` report the proposals kept in place; `14` star precision is undefined, not zero;
  `15` the eval keys obey the eval toggle.
- `563e5b8` — video 3 marked, 51 rows, star only.
- `4bfc52c` — three videos scored. `1e6a76b` — `D-040`.
- **`SKILL.md` v2**, outside the repo. Twelve rules to ten: `R-TAKE-GAP`, `R-TAKE-CLUSTER`,
  `R-TAKE-LABEL` and `R-NO-MUSIC-TAG` retired; `R-COVERAGE`, `R-LEAD`, `R-SKIP-PREAMBLE`,
  `R-BIZ-BOUNDARY` added; `R-COPIOUS` raised from 20-30 per 90 min to one per minute.
- **Uncommitted:** `labels.jsonl` carries the `polish` → `feel` rename (42 appended events) and
  one event restoring video 1's marker 0 after a UI test overwrote it.

## Decisions (second stretch)

- **The skill detects concepts only** ([[D-040]]). Deleting the three take rules stranded zero
  starred moments across both unanchored lessons. Retired ids stay readable and are never
  reused — `labels.jsonl` cites `R-TAKE-GAP` 130 times.
- **Recall is bought with a spacing cap, not a density target.** `R-COVERAGE`: never more than
  60 seconds without a proposal. The one real recall failure was a single 5-minute unproposed
  stretch holding four of 21 stars.
- **The export merges only entries that would print the same words** ([[D-039]]).
- **Star recall is the primary metric, precision is a budget constraint.** An extra marker is
  one keypress; under review-by-reading the list length is what has to stay inside 20 minutes.
- **Assign a PR number when the PR exists**, not when the commit message is written. Two
  branches claimed "PR 10" and neither was a pull request.

## Learning arc (second stretch)

- Read `SKILL.md`'s negative-rule block and asked what it was for, rather than taking it as
  given. That question found `R-NO-SPEAKER`'s premise had expired.
- Then found the root cause before I did: the skill was developed against an incompletely
  marked video **and** the workflow has since reversed to Zoom → tool → YouTube.
- Caught that 1.07× was not comparable to 1.95× because video 3 skipped work, lane and tags.
  I had swapped one baseline for another without noticing they measured different jobs.
- Pushed back on "playback is the floor" — the tool skips between markers, so the floor is the
  segments actually played, not the lesson. Correct, and it moved the target from unreachable
  to mid-range.
- Argued the 8 excluded stars were being thrown away. Half right: they belong in the score, not
  in recall. The set labels were also swapped — the "nails" are the 8, not the 9.
- Asked whether the skill is shipped and the eval layer can go, which is the right question at
  the right time and closed the thread rather than extending it.

## Concepts touched (second stretch)

- [concept] anchored vs unanchored ground truth — solid — video 2 and 3 both marked before the
  skill ran; that property is what made the recall numbers mean anything
- [concept] feature problem vs data problem — solid — four more angles tested on diarization,
  all dead; stopped proposing rules that assume takes are detectable
- [concept] rule premise vs rule conclusion — solidifying — `R-NO-SPEAKER`'s reason was wrong
  and its advice right; kept the rule, replaced the justification
- [concept] concurrent-writers-on-shared-docs — solidifying — third and fourth instances (two
  branches claiming PR 10, two entries claiming `D-035`), now named inside `D-039` itself
- [concept] eval channels vs product keep (g / x / taxonomy / star / delete) — solid — found
  `g` and `x` writing eval verdicts during ordinary annotation with the toggle off
- [concept] one-name-per-thing — emerging — `polish` → `feel` done as appended events, because
  an append-only store cannot be renamed in place

## Coaching hooks (second stretch)

- **A green test proves nothing until it fails on the bug it guards.** I nearly shipped
  `test_sidecars.py` on a passing run; deliberately reverting F18 and F20 first showed 4 and 1
  failures. Do the reversion before claiming a test works.
- **Run the thing rather than reasoning about it — it changed the answer four times.** The
  lexicon test produced the ceiling split; generating the transcript showed "teach the skill to
  read a run" was overstated; running old `local.py` showed the `.info.json` fix was hardening
  not a bug; scoring video 3 falsified my own `R-TAKE-GAP` prediction.
- **Specify a falsification test so one sample cannot settle it.** I wrote "if `R-TAKE-GAP`
  fires well on video 2, half the rewrite case is wrong" while already knowing lesson type was
  a confound. Video 2 said 92%, video 3 said 50%.
- **`/plain-english` fired three times.** The fix was never vocabulary: wrong order once, an
  undefined term ("sidecar") used all day once, and a table with an empty column once.

## Next / open threads (second stretch)

- **Brian uses v2 on the next few lessons and reports back.** Not an eval — work normally, note
  the clock and roughly what fraction of markers needed playing versus judging from the label.
  That ratio decides whether anything remains.
- **Commit `labels.jsonl`** — the `polish` → `feel` rename and the marker-0 restore are
  uncommitted.
- **Domain auto-tagging is half-working and unsettled.** On video 3 `harmony` fired on 49 of 51
  rows: too loose to discriminate on a harmony lesson. `exercise`, `comping` and `fingering`
  looked right. The untried fix is a relative test — tag when a window is denser in the
  vocabulary than the lesson's own average — rather than an absolute keyword hit.
- **Schema change, specced but not built:** `work` moves to the run, `lane` deprecated, tag
  input narrows to `star`.

## Open questions / blockers (second stretch)

- Whether a review pass lands near 0.27× or 0.67×. Every timing measurement so far is Brian
  authoring markers; none is him reviewing them.
- The right `R-LEAD` value. Video 1 says 30s, video 2 says 45s. Two videos disagree.
- Zoom diarization is unreliable, which was not known when "record through Zoom cloud" was
  written as step 1. Video 3 names Brian as speaker for 57% of a lesson Jake taught, and calls
  him `jakesherman` where video 2 says `Jake Sherman`.

## Chronology (second stretch)

- **05:12** — `/plain-english` on the corpus passage. Rebuilding by running the thing showed
  "teach the skill to read a run" was overstated; fifteen lines produced the transcript file.
- **05:28** — asked what `SKILL.md`'s three negative rules were for. Measured all three:
  `R-NO-TALK-DETECT` confirmed on video 2, `R-NO-SPEAKER`'s premise dead. Found the
  junk-caption labelling gap behind 9 of video 1's 24 rejections.
- **06:27** — "should we start the skill from fresh?" Checked his premise: `SKILL.md`'s
  43-minute claim is 21.9 minutes in the store. Then found the stronger reason.
- **06:34** — scoping the finish line. Lexicon test: `harmony` 89% vs 42%, `comping` 100% vs
  14%, no lexicon at all for `take` or `star`.
- **06:41-06:49** — corrected my own ordering (video 2 was already the held-out test, so the
  skill run goes first). Landed the ceiling table and the eval spec. Restored `AGENTS.md`,
  which had lost the rationale sentence naming PRs 5 and 6 to an editor reflow.
- **06:50** — first `/session-log`. Then committed video 2's store, which had never been backed
  up.
- **06:54** — "upside is closer to 50% than 75%?" Measured video 2's annotation at 1.95×
  realtime from `labels.jsonl` timestamps, split it into watching and stopped time.
- **06:57** — the "jake sherman brain" question. Tested whether the repository needs the
  tagging: a finger-number regex finds 8 of 9 fingering rows at 10% false positive, with no
  training examples.
- **07:06** — phone access. Checked `ListAgents` rather than answering from memory: one peer
  session, no cloud, no Remote Control.
- *[~16 hour gap]*
- **23:14** — back on the review-by-reading passage. Built the two eval scripts, found and
  fixed a location-dependence bug by copying one out of the repo and watching it break.
- **23:29-23:50** — three rounds of refresher questions: how the transcript got made, what a
  run file is, the ingestion pipeline end to end, and a restatement of what `local.py` does.
  Rewriting that last one surfaced a real defect — my generator disagreed with the run about
  the gap count, three different answers for one transcript.
- **02:20** — banked the scoring-script explanation as `/plain-english` example 004.
- **02:29** — argued the 8 excluded stars were being discarded. Correct that they were; wrong
  that they belong in recall. Also found the 8 and the 9 were labelled backwards.
- **04:14** — "I don't see PR10." It did not exist. Two branches had claimed the number in
  commit messages and neither was a pull request.
- **04:18-04:29** — opened both, addressed both reviews. PR 10's doc changes stripped out and
  `main` merged in so the diff showed five lines instead of 106. PR 11's `NameError` on a
  zero-cue run fixed.
- **04:55-05:30** — `build_cues` is captions, not markers. Then the sidecar hardening question:
  six adversarial shapes all correct, but no test suite and the provenance note was ephemeral.
  PR 12 fixed both.
- **06:30** — "just simplify — what are the concrete changes?" Measured that deleting
  `R-TAKE-GAP` strands zero stars, and that the 90-second tail is one 325-second hole.
- **06:39** — wrote `SKILL.md` v2. Checked every historical rule id is accounted for.
- **06:42** — work/lane. Measured they never vary per marker: video 2 carries one value 75
  times. They are section metadata on the wrong object.
- **06:44** — "are we shipped?" Yes, with the caveat that no timing measurement is of reviewing.
- **06:46** — pushed back on the playback floor and was right.
- **06:47** — renamed `polish` → `feel` (42 appended events), gated the three eval-chrome leaks,
  and auto-tagged video 3 as a preview. `harmony` fired on 49 of 51 rows — too loose.

---

# Append — 2026-08-21 11:41

## ★ The eval redesign — flagged, at Brian's request

Two reasons he asked for this to stand out. The second is the more important one.

**One: the eval model changed shape, and the record should show why rather than just what.**
It went from "grade the skill's markers in a separate pass" to "eval is what you do anyway."
[[D-041]] carries the decision; this is how it got there.

**Two: this is what it looks like when he does not just ACK a decision he 60% understands.**
His words. He pushed on six separate points and was right or partly right on five. The design
that landed is materially different from the one I proposed, and every difference came from a
question he asked rather than an answer I gave.

**What he caught, in order:**

- **"tags are now autoapplied? so not a good measure of implicit keep?"** — killed my proposal
  to record tag provenance so `keep` would keep working. A signal that depends on a workflow he
  does not run is not a signal.
- **"me editing tags is not a reliable workflow (case in point, i haven't reviewed video 3)"** —
  cited his own behaviour as the evidence. That is the argument that ended `keep`.
- **"the only reliable version of keep is I relabel a skill placed marker right?"** — proposed
  the alternative himself. Checking it killed it too: all five relabels on video 1 are
  byte-identical, because the event fires on save, not on change. Neither of us saw that coming.
- **"are you overly equivocating"** — I had folded on a claim that was correct. The boolean is
  redundant today; my original caution was right and I retracted it under pressure. He was
  checking whether agreement was reasoning or reflex. It was reflex.
- **"what we've done so far is not a good measure of what we might do in the future"** — the
  single best correction of the session. I was answering a twenty-video question with
  three-video evidence. Reasoning forward found that `x` is not a grade at all — `export.js`
  drops a marker marked wrong, so it is the only way to keep junk out of the published
  timestamps. Deprecating it would have removed the most-used action in the product.
- **"g is 'this was a correctly placed marker, irrespective of whether it gets promoted to
  star'"** — a real distinction I had wrong. I said `g` duplicated `star`; it does not. It
  duplicates the *link*. Same conclusion, better reason, his.

**What I got wrong along the way**, kept because the pattern is the lesson: three consecutive
wrong counts on one question — "51 empty rationale blocks" (they say `MISS.`), then "64 + 21"
(it is 75 + 10), then "75 real" (it is 64 real, and 11 of his own notes wearing a `MISS.`
prefix). Each time the data was one command away and I reasoned instead of looking. He asked
"what's going on with your accuracy?" and the honest answer was: asserting from a stale model
of the repo, plus not re-reading what I had just changed.

## What changed (third stretch)

- `36629d9`, `7582052` — the merge rule: default to a PR, merge only on explicit instruction.
  Living records still go straight to `main`. In `AGENTS.md` and in memory.
- `79a598c` — thread 8 widened to PRs 21+22 as one design; thread 9 opened on PRs 18-20 via a
  **review-only PR** (#23), a pattern worth reusing: throwaway base branch at the commit before
  the range, head at the end, so GitHub renders the range and `main` is never touched.
- `355f216` — PR 21 merged (work as a section break).
- `0180557` — **[[D-041]]**, superseding [[D-010]]. Plus the build list and the machine-learning
  answer in `BACKLOG.md`.
- PR 22 open and unmerged — the first held under the new rule.

## Decisions (third stretch)

- **Default to a PR; merge only when told.** Ten PRs reached `main` unreviewed in two days
  because "execute + pr + merge" was read as standing permission.
- **Eval is what you do anyway** ([[D-041]]). `g` and `keep` retired, `x` reinterpreted as
  "remove this from my list", the toggle goes, the note field stays. The link replaces grades.
- **Videos 2 and 3 are spent.** Blind-marked, but every v2 rule came from them. Permanent honest
  v1 baseline; not a test set. Zero unspent blind lessons exist.
- **Machine learning is not the next lever.** The measured failures were specification problems;
  the one thing training cannot fix needs audio. Few-shot label drafting from his own 193 labels
  is the model work that pays.

## Learning arc (third stretch)

- Read the side-chat summary and asked me to reconcile it rather than accepting it — which found
  that its one unverified item (the `keep` bucket) was real but far smaller than stated.
- Worked out the section-break model unprompted and checked it in his own words: "set work on the
  first marker, then that value gets autofilled to all captions below." Behaviour right, storage
  wrong, and the correction — nothing is filled in, it is resolved — is the part that makes a
  retroactive typo fix work.
- Caught that PR 17 had shipped a half-change by **using the app**, not by reading the diff.
- Asked whether I was over-equivocating. That is a different kind of question from the technical
  ones: it is quality control on how the answers are being produced.
- Reversed his own earlier position on deprecating `lane` once the economics changed, and said so
  plainly rather than quietly.

## Concepts touched (third stretch)

- [concept] eval channels vs product keep (g / x / taxonomy / star / delete) — solid — took the
  five apart and found `x` was never only a grade; retired two, reinterpreted one
- [concept] anchored vs unanchored ground truth — solid — extended it to the spent-test-set
  problem: videos 2 and 3 are blind but burned, because v2 was built from them
- [concept] proxy-vs-recorded-fact — emerging — `keep`, `MISS.`, star precision and the boolean
  are all the same shape: a fact knowable at write time, not written down, later guessed
- [concept] one-name-per-thing — solidifying — `MISS.` is a storage word that reached the screen
- [concept] concurrent-writers-on-shared-docs — solidifying — a fifth instance: scope widened in
  `REVIEW.md` and not in the PR body, and the PR body is the more visible copy

## Coaching hooks (third stretch)

- **His pushback is worth more than my first answer.** Five of six challenges landed. The pattern
  in all of them: he reasons from what he actually does, and I reason from what the data shows —
  and when those disagree, his is usually the constraint that matters.
- **"Are you over-equivocating" is a fair check and the answer was yes.** Conceding a correct
  claim is worse than useless: it removes a real caution from the record. Hold the parts that
  were right, change the conclusion if the argument earns it, and say which is which.
- **Three wrong counts in a row on one question.** Each was one command from being right. The
  rule going forward: a claim with a number in it gets a command first, or it gets flagged as an
  inference.
- **After renaming or renumbering, grep for the old name.** Mechanical, not judgment. Would have
  caught the thread-6 pointer left in PR 22's body.

## Next / open threads (third stretch)

- **Codex's review is in on PRs 21+22** (`c2b912c`). Address the findings — that is the next
  action, and it is the reason this log entry exists now rather than later.
- Thread 9 (PRs 18-20, review-only PR #23) still open with Codex.
- Nothing from [[D-041]] is built. The build list is in `BACKLOG.md` under "Eval, after D-041",
  and nothing starts until the review threads clear.
- **Mark the next lesson blind, before running v2 on it.** Zero unspent held-out lessons exist.

## Chronology (third stretch)

- **06:52** — `/session-log`, then the ballpark question: is the upside closer to 50% than 75%?
- **07:00 onward** — measured video 2's annotation at 1.95x realtime from `labels.jsonl`
  timestamps. Brian objected that video 3 skipped taxonomy, which broke the comparison; the split
  was roughly 22 minutes of skipped tagging and the rest bugs and distraction.
- Pushed back on "playback is the floor" — the tool skips between markers, so the floor is the
  segments played. He was right and it moved 0.27x from unreachable to mid-range.
- **Scored video 2, then video 3.** `R-TAKE-GAP` 92% then 50%; the prediction was wrong on one
  and right on the other, and the falsification test had been badly specified.
- Wrote `SKILL.md` v2. Twelve rules to ten.
- **The work/lane cleanup.** Brian: "seems messy to have two work fields". PR 17 had been a half
  change. PR 21 fixed it; PR 22 extended it to lane, reversing my earlier recommendation.
- **"I don't see PR10"** — it did not exist. Two branches had claimed the number in commit
  messages. Opened both properly.
- **The merge rule.** Ten unreviewed merges, corrected twice — first as "never merge", then to
  his actual rule.
- **The eval conversation**, flagged above. Ran from "is eval free?" through three wrong counts,
  the accuracy challenge, the twenty-video reframe, and landed on [[D-041]].
- **11:41** — this log. Codex's review on 21+22 is in and unaddressed.

---

# Append — 2026-08-21 13:05 — side chat: git mechanics

Recorded at Brian's request from a forked chat. **No tools ran there; nothing was written to the
repo.** Explanation only, plus one correction to something I got wrong in the main thread.

The trigger was two questions that exposed the same confusion: "can't merges have multiple
commits? similarly, branches also have multiple commits?" Both came from me describing the
*pointer* while he was thinking about the *contents*.

## What a branch is

`.git/refs/heads/main` is a file containing one 40-character id. That is the whole file.

Every commit separately records its own parent's id, written when the commit was created and
never changed after. So "main has 134 commits" is shorthand for: start at the id in that file,
follow parent links, count what you reach. The 134 links live in the 134 commits — the branch
file contributes only the starting point.

Moving a branch rewrites that one file and touches nothing else. No commit changes; no parent
changes. You just start walking somewhere different. That is why it is instant regardless of
history size — a 40-byte write.

**Corrected a misreading:** moving a branch does not move "the commit and its parent." Parents
are not involved at all.

```
cat .git/refs/heads/main      # the one id
git cat-file -p HEAD          # the commit, with its parent line
git rev-list --count HEAD     # git doing the walk
```

## What a merge commit is

An ordinary commit with two ids in the parent field instead of one.

```
8d57e37
  parent 1 → main's tip just before the merge
  parent 2 → the tip of the branch being merged in
```

Order is fixed by which branch you were on. Parent 1 is "we were here", parent 2 is "and we are
bringing this in". That ordering is what `git log --first-parent` follows to show main's own tips
while skipping everything that arrived via branches.

Always exactly two parents. How many commits the merge brings in is a separate question —
whatever is reachable through parent 2 and was not already reachable through parent 1.

```
git cat-file -p 8d57e37 | head -4       # two parent lines
git log --oneline 8d57e37^1..8d57e37^2  # exactly what it brought in
```

## Correction — why local `main` fell behind

I had framed this in the main thread as "Codex pushed to GitHub while I was editing." **Wrong
mechanism.**

Codex and Claude run on the same Mac, in the same repository, sharing one `.git` and therefore
the same refs. A commit made on `main` would be visible instantly, no fetch needed.

What actually happened: Codex worked in **worktrees on detached HEAD** — separate checkout
directories sharing one `.git`, committing without being on any branch:

```
scratchpad/fix33   54903b8 (detached HEAD)
```

It then pushed that commit straight to origin's `main`. Three refs, two moved:

| Ref | Moved? | Why |
| --- | --- | --- |
| `main` (local) | no | nothing ever checked out `main` and committed |
| `origin/main` (cache) | on fetch | that is what fetch updates |
| GitHub's `main` | yes | the push landed |

So local `main` fell behind not because GitHub is remote, but because the local branch pointer
was never moved. `54903b8` was in the shared object store the whole time — reachable, just not
pointed at.

`origin/main` being a cache of GitHub is still the right model. The staleness just had a
different cause than I said. This is consistent with the `git worktree list` output captured
earlier in the main thread, which showed several detached-HEAD worktrees at exactly those SHAs.

## Branch lists on each side

The two lists do not have to match, and mismatches are usually forgotten cleanup — with one
exception.

- **Leftover on GitHub:** almost always just uncleaned. A merged branch holds nothing `main`
  does not.
- **Leftover locally:** a branch never pushed and never merged holds commits that exist nowhere
  else. This is the only case where deleting can lose work.

`git branch -d` refuses to delete unmerged branches. Use it, not `-D`.

| Marker after the branch name | Meaning | Action |
| --- | --- | --- |
| `[origin/x]` | tracked, still on GitHub | leave |
| `[origin/x: gone]` | pushed, then deleted on GitHub | `git branch -d x` |
| (nothing) | never pushed | check before deleting |

```
git branch -vv                # brackets tell you which is which
git ls-remote --heads origin  # what GitHub actually has
git fetch --prune             # drop stale origin/* caches
```

## Next / open threads (from the side chat)

- **Check `two-surface-refactor`** — local-only on the branch list, so it may hold commits that
  exist nowhere else. `git log --oneline -1 two-surface-refactor` before deleting.
- **Do not delete `review-base-appification` or `review-appification`** until PR 23's review
  closes. They exist to make that PR render the right diff; deleting either breaks it. They are
  deliberate, not leftovers.
- Two one-time settings to stop the accumulation:
  `gh repo edit --delete-branch-on-merge` and `git config --global fetch.prune true`.

## Open questions (from the side chat)

- Why `merge-only-matching-labels` and `two-surface-refactor` ended up asymmetric was **inferred,
  not verified**. `git branch -vv` settles it in one line.
- Whether Codex's worktrees are still lying around. Several were on detached HEAD, and one stale
  worktree already blocked a branch delete earlier today. `git worktree list` and
  `git worktree prune`.

---

# Append — 2026-08-21 13:40 — side chat: worktrees, HEAD, and the reset family

Continues the git mechanics record. Still uncommitted at the time; no tools ran in that fork.

## What `HEAD` actually is

`.git/HEAD` is a persistent one-line text file. Two possible contents:

```
ref: refs/heads/main        ← attached to a branch
54903b8f2a1c...             ← detached, pointing straight at a commit
```

**Correction to the working model:** `HEAD` is not "where the project is." It is where *one
folder* is standing. The project is the shared history; "which commit are my files showing" is a
question about a directory on disk, and you can have several.

So: one repository, one set of branches, but **one `HEAD` per worktree**. Today there were three
at once —

```
/app-projects/yt-clip-marker   HEAD → ref: refs/heads/main
/tmp/.../scratchpad/td16       HEAD → ref: refs/heads/merge-only-matching-labels
/tmp/.../scratchpad/fix33      HEAD → 54903b8...        (detached)
```

"You are on main or a branch, never both" holds inside one folder. It stops holding across
folders.

Also: `HEAD` is not necessarily the latest commit. Detached at an old SHA means your files show
something from days ago.

Naming collision worth knowing: `HEAD` (your position) and `refs/heads/*` (each branch's tip
commit) share a word and mean different things.

## What a worktree is

A folder of checked-out files. You already had one; `git worktree add` makes more.

| Shared — lives in the original `.git` | Separate per worktree |
| --- | --- |
| every commit, tree, blob | the files on disk |
| every branch ref | `HEAD` |
| remotes, config, hooks | the index |

**The rule that bit us:** a branch can be checked out in only one worktree at a time. That is the
error when deleting `merge-only-matching-labels`:

```
fatal: 'merge-only-matching-labels' is already used by worktree at
       /tmp/.../scratchpad/td16
```

Physical giveaway: in the main folder `.git` is a **directory**. In a linked worktree it is a
**file** containing `gitdir: /path/to/real/.git/worktrees/<name>`.

Why it exists: it replaces stash → checkout → look → checkout back → stash pop. Your folder never
moves; you get a second one, look, delete it.

## Detached HEAD — why Codex used it, and where it went wrong

Inferring from directory names, but legible. Checkouts named `studio-test` (at PR 4's SHA),
`fix33`, `d33`, `logmain`, `recover` — task-scoped, disposable.

Three good reasons: isolation (checking out an old commit in the main folder would swap your
files out from under you), reviewing a specific commit, and no branch-name collision since
nothing is claimed. All correct instincts. Detached is the right tool for *reading* a commit.

**The mistake was committing there and pushing to `main`.** Detached is the wrong place to author
something meant to land on a branch, because there is no branch to carry it — GitHub's `main`
moved, local `main` did not, and nothing signalled it. One command would have prevented it:

```
git switch -c some-branch    # attach a name before committing
```

## The four things that move a branch

**`merge`** — two cases, and I had only described one. **Fast-forward** (main has not moved since
the fork) just rewrites main's id, no new commit. When **both sides have moved** that is
impossible, so git creates a merge commit with two parents and points main at that. Every "Merge
pull request #N" here is the second kind. `--ff-only` refuses if a merge commit would be needed.

**`rebase`** — commits are rebuilt, not moved. New ids, same content. Old ones orphaned until GC,
recoverable via reflog. Normally the branch is rebased onto main, not the reverse.

**`pull`** — fetch then merge. Step 1 never moves `main`; step 2 does. "GitHub's main has moved
and mine has not." Note it does not matter *who* moved it — today it was our own other agent on
this same Mac, and from main's point of view that is identical to a stranger pushing.

**`reset`** — point the branch somewhere else, no reconciling. Three flavours differ only in how
much comes along:

| | Branch | Index | Files |
| --- | --- | --- | --- |
| `--soft` | moves | untouched | untouched |
| `--mixed` (default) | moves | cleared | untouched |
| `--hard` | moves | cleared | **overwritten** |

## Soft vs mixed — Brian's framing, which is better than mine

- `--soft` = **squash.** Several commits should be one.
- `--mixed` = **reorganise.** One commit has the wrong stuff in it.

I had described the mechanism ("keeping content vs re-deciding it") when the *situation* is the
useful handle. Worse, "keeping the content" describes both — `--mixed` keeps your content too, it
is sitting in your files.

Why they line up that way: the index is a file, `.git/index`, holding path → content for the next
commit. `--soft` leaves it full with the commit boundaries gone, so the one natural next move is
committing it as one thing. `--mixed` empties it, forcing you to choose what goes in.

Consequence that falls out of this: `--soft` back over three commits then `git commit` gives one
commit, because the index never recorded that there was a boundary.

Reset scoped to a path — `git reset path/to/file` — is `--mixed` on one file. That is the unstage
command, same mechanism.

## What can lose work

Only `git reset --hard` with uncommitted edits. `reflog` recovers orphaned commits for ~90 days;
uncommitted work was never a commit. `git status` before `--hard` is the whole safeguard.

## Fetch — what it actually downloads

The commit **objects**, not just the pointer. After fetching, `git log origin/main` works offline.
It transfers only what you are missing, so fetching three new commits moves three commits, not
134.

It also updates every `origin/*` ref it can see — which is how branches you never checked out
appear in your list. It does not delete stale ones without `--prune`.

## Next / open threads (from the side chat)

Unchanged from the previous record, plus:

- `git worktree list` then `git worktree prune` — two entries showed prunable (folder deleted,
  registration left behind), and one of those already blocked a branch delete.

---

# Append — 2026-08-21 15:05 — PR 24/25 close-out, and eval state pulled into a doc

## What changed

- `docs/coordination/EVAL.md` — new. Eval corpus, current code state, the four-rung ladder,
  five open decisions, seven ordered next actions.
- Pointers added: `README.md` doc table, `BACKLOG.md` "Skill eval" header.
- Commit `3f87bd8` was the prior session-log append; the eval doc lands on top of it.

## Decisions

- **Eval state gets its own coordination doc.** `BACKLOG.md` held the scored numbers,
  `DECISIONS.md` held D-040/D-041, and nothing held "where are we". Split: `BACKLOG.md` keeps
  what was measured, `EVAL.md` holds live state and direction.
- **Nothing in `EVAL.md` §7 is decided.** Five questions, each with a recommendation and a
  confidence level, deliberately left open for the roadmap conversation.

## Learning arc

- **Rebase vs merge, worked to the bottom.** Brian restated the PR 24/25 stack in his own words
  and got the mechanism right — including that `dd4b233` survives a rebase but leaves the chain.
  Two gaps: a PR's base is a *branch name*, not a commit (which is what makes the breakage
  automatic — nobody edits PR 25), and a merge is not a line, it is a commit with two parents,
  which is precisely why the shared point survives. Measured both ways: 3 files/29 insertions
  with the merge, 4 files/80 with the rebase.
- **Asking to be walked through it rather than acking it.** The framing he named earlier in the
  session — "vs just ACKING decisions I 60% understand" — is what produced the restatement, and
  the restatement is what exposed the two gaps. Cheaper than finding them in a broken PR.

## Concepts touched

- [concept] git-object-model — solidifying — restated the fork/stack graph unprompted and
  correctly predicted that rebasing the base orphans `dd4b233`
- [concept] stacked-prs — emerging — understood the base moves automatically once told the base
  is a branch; the two-rebases maintenance cost was new
- [concept] eval-channels — solidifying — drove the corpus/ladder analysis himself in a side
  chat; the corrections needed were factual, not conceptual

## Coaching hooks

- **Verify the side chat, do not transcribe it.** Four claims in the eval side chat were wrong
  against the store: event count (~700 vs 853), consumer count (two vs six, and two of the six
  write), positives (193 vs 147 measured), and one open question that was already answerable.
  Analysis written without tools needs a grounding pass before it becomes a doc.
- **Measured tables beat asserted ones.** The rebase explanation only landed once both diffs
  were computed on the real commits.

## Next / open threads

- **Star predictability test** — an hour, and it gates whether rung 4 exists at all. `take` was
  tested four ways and every feature was dead; if `star` is the same the ladder stops at 3.
- **Run `SKILL.md` v2 once, unmodified.** Confirmed today that v2 has never been run — it was
  written 2026-08-20 23:40 and the newest proposals file is 23:23. Every scored number on record
  is v1.
- Then: use v2 for real on the next lesson (not blind), fix `score_run.py`'s `annotated` proxy,
  add the "was a proposal in front of me" boolean, the three display fixes, rung 2 exemplars.
- Full ordered list in `EVAL.md` §8.

## Open questions / blockers

- Settled today, previously open: `keep` is now effectively "has tags" — the row's work/lane
  inputs commit through `persistSection`, so no path writes `ann.lane`/`ann.work` anymore, and
  video 1's 14 keeps are not comparable to anything counted since PR 21.
- Settled today: both Zoom runs having exactly 688 cues is coincidence, not a sidecar bug —
  different text, different lengths (3870s vs 2640s).
- Still open: everything in `EVAL.md` §7 A–E.

## Chronology (the record)

- Committed the worktrees/HEAD/reset side-chat record from the previous fork; pushed as `3f87bd8`.
- Brian restated the PR 24/25 rebase situation in his own words and asked for the two gaps he had
  marked `[something something]`.
- Walked both ancestries on the real commits. Corrected: base is a branch, not a commit; a merge
  keeps both parents rather than flattening to a line. Showed the two diffs side by side.
- Noted the state had moved underneath the question — `origin/quit-csrf-guard` is at `7e4927e`,
  "Merge pull request #25", so the decision is now history.
- Brian handed over the eval side chat and asked for a session log plus a standalone eval state
  doc, explicitly to set up a roadmap conversation.
- Grounded the side chat against the store before writing: folded `labels.jsonl`, counted markers
  and cues per run, read `score_run.py`, `grid.js`, `persist.js`, `suggest.js`, `keys.js`, and
  compared `SKILL.md`'s mtime against the proposals files.
- Four corrections found (see Coaching hooks). One suspicious number chased and cleared: the
  688/688 cue coincidence.
- Wrote `docs/coordination/EVAL.md`, added two pointers, committed to `main`.

---

# Append — 2026-08-21 15:35 — sync direction fixed, and one live contradiction flagged

Closing state for this thread. Written so the next session does not have to reconstruct it.

## What changed

- `docs/reference/EVAL.md` — Brian moved it out of `docs/coordination/`. The move is now in git;
  the two pointers that named the old path were repointed (`README.md`, `BACKLOG.md`).
- `DECISIONS.md` — **D-042** added.
- `CURRENT.md` §6 — marker-label writeback firmed from "needs its own spec" to closed, citing D-042.
- `EVAL.md` §7C — carries a blockquote flagging that it contradicts D-041.

## Decisions

- **D-042 — markers flow one way, app → YouTube; the video title flows YouTube → app.** Brian's
  call, verbatim: *"markers should always be one way from app to youtube."* Each field flows away
  from the surface that owns it, which is what removes the reconciliation problem rather than
  deferring it. The description-scraping merge is closed, not parked.
- **Phase 4 is the lesson title only.** Confirmed against the ambiguity raised earlier: he meant
  the video name, not marker labels inside the description.

## The thing most likely to be lost — read this first

**`EVAL.md` §7C and `D-041` say opposite things and both are live.**

- D-041: *"the next lesson marked is the held-out one, and it has to be marked before v2 runs on it."*
- EVAL.md §7C: *"Should the next lesson be marked blind? Recommend no — use v2 for real instead."*

I wrote §7C from the eval side chat without noticing it reversed a decision recorded hours
earlier in the same session. `AGENTS.md` requires superseding a decision with a dated entry, not
silently contradicting it. A blockquote now sits in §7C saying so. **Neither has been retired —
this needs Brian's call before the next lesson is marked**, because the two answers lead to
different work on the very next action.

## A second thing that will bite quietly

D-042 has a carve-out that is easy to miss and is **shipped behavior**, not theory:
`ui/util.js:137 resolvedLabel()` prefers an `extracted[]` description label over the studio
clip's own text at export time. So a stamp already published on YouTube does today override the
app's label for that row — which reads like a violation of "markers are one way" and is not one.
It is a record of what was published, read once at ingest.

With markers now formally one-way, that preference is arguably backwards going forward: the app
is canonical, so the app's label should win. It was correct for video 1, whose description stamps
predate the studio. **Deliberately left alone** — changing export behavior is its own PR. Recorded
in D-042 under "Consequence to check".

## Learning arc

- **Brian caught the scope question before it turned into work.** The two readings of "rename"
  were flagged rather than assumed, and his answer collapsed a merge problem into nothing. Cheaper
  than discovering it mid-implementation.
- **Moving a doc is a two-part change.** The move landed in the working tree but the two pointers
  naming the old path did not follow, and `README.md`'s table listed it as a coordination doc it
  no longer is.

## Concepts touched

- [concept] canonical-store — solidifying — extended cleanly from clips to a second field moving
  the other way, without weakening D-002
- [concept] eval-channels — solidifying — no movement this append; the open contradiction above is
  the live edge

## Coaching hooks

- **Check new recommendations against `DECISIONS.md` before writing them down.** The §7C/D-041
  clash came from folding in side-chat analysis without grepping the decisions file. Both were
  written the same day, hours apart.
- **When closing a deferred item, say "closed" not "needs a spec".** `CURRENT.md` §6 read as a
  future task until it was firmed; a later session would have picked it up as work.

## Next / open threads

1. **Resolve D-041 vs EVAL.md §7C.** Blocks the next lesson being marked. Brian's call.
2. **Star predictability test** (`EVAL.md` §7E) — about an hour, and the only item that can
   *remove* work: if nothing predicts `star`, rung 4 is off and the ladder stops at retrieval.
3. **Run `SKILL.md` v2 once, unmodified.** Confirmed it has never been run — written 2026-08-20
   23:40, newest proposals file 23:23. Every scored number on record is v1.
4. **`CURRENT.md` phases 1-4**, baton on implementer. Phase 1 touches `docs/clip-schema.md` and
   wants Brian's eyes before 2-4 build on it.
5. Remaining `EVAL.md` §8 items: `score_run.py`'s `annotated` proxy, the "was a proposal in front
   of me" boolean, three display fixes, rung 2 exemplars.

## Open questions / blockers

- **D-041 vs §7C** — the only real blocker, and it gates item 3 above.
- `EVAL.md` §7 A, B, D, E remain open by design.
- Whether `resolvedLabel` should stop preferring extracted labels — see the carve-out above.

## Chronology (the record)

- Confirmed nothing was blocking: clean tree, no open PRs (PR 23 was closed rather than merged,
  which was correct), 15/15 tests, and all six Codex worktree commits already in `main`.
- Mapped Brian's YouTube asks against `CURRENT.md`: three of four were already phases 1-3; the
  rename was new.
- Worked out that the rename is a join between `run.youtubeId` (phase 1) and `uploads.json`
  (phase 3), not new machinery. Wrote it as phase 4 with a precedence rule and pull-only direction.
- Flagged the two readings of "rename". Brian: the video name only, markers always one-way.
- Discovered he had moved `EVAL.md` to `docs/reference/`. Recorded the move in git and repointed
  `README.md` and `BACKLOG.md`.
- Read `export.js` and `util.js:137` before writing D-042, which is what surfaced the
  `resolvedLabel` carve-out — the decision would otherwise have outlawed shipped behavior.
- Grepped `DECISIONS.md` while numbering D-042 and found the D-041 / §7C contradiction. Flagged
  in place rather than resolving it.

---

# Append — 2026-08-21 16:00 — the D-041 conflict is resolved

The previous append lists "Resolve D-041 vs EVAL.md §7C" as the one blocker. **It is closed.**
Do not pick it up.

- **D-043** supersedes *only* D-041's cadence paragraph; the rest of D-041 stands. The paragraph
  is struck through in place with a pointer, not deleted.
- **Resolution: do not mark the next lesson blind.** Smoke-test v2 on video 2 or 3 first, then use
  it for real while recording four numbers per lesson.
- `EVAL.md` §7C now reads "Decided — no", and §8's ordering follows.

**Brian's framing was what dissolved it.** He proposed running v2 on *a* video because it still
had not run at all — which is neither side of the D-041/§7C argument. Both were arguing about
measurement; the first run is a smoke test. That reframe made the contested part apply only to
the lesson *after* it.

**The argument that decided the contested part:** blind-marked lessons are manufactured on demand,
not a depleting stock, so the choice is now-or-later at equal cost. D-041's "zero unspent today"
implied scarcity that is not there — the scarce resource is Brian's 45 minutes. Given that, measure
the number that could change the plan: held-out recall would not stop him using the skill, but the
judge-without-playing fraction could kill the premise outright.

**Cost accepted, stated in D-043:** zero clean test lessons now, zero after. When v3 needs testing
a lesson gets marked blind then — deferred, not avoided. Two named conditions reverse D-043: a fast
revision cadence, or Brian already knowing he can judge proposals from labels.

## Next / open threads — replaces the previous append's list

1. **Run `SKILL.md` v2 once on video 2 or 3.** Smoke test. Not a measurement, and the score must
   not be recorded as a v2 result — every v2 rule derives from videos 1-3.
2. **Star predictability test** (`EVAL.md` §7E). The only item that can *remove* work: if nothing
   in the transcript predicts `star`, rung 4 loses its target and the ladder stops at retrieval.
   Same shape as the `take` test that produced D-040, where all four features were dead.
3. **Use v2 for real on the next few lessons**, recording proposals offered / accepted without
   playing / had to scrub / added unprompted.
4. `CURRENT.md` phases 1-4, baton on implementer. Phase 1 touches `docs/clip-schema.md`.
5. `EVAL.md` §7 A, B, D still open. §C is closed.

