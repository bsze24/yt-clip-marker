---
date: 2026-08-19
time: "23:50"
surface: claude-code-opus-5
project: yt-clip-marker
track: reduce-manual-tagging
branch: main
commit: 1daecd8e260902ac43a29eea4a27c04121504a41
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
