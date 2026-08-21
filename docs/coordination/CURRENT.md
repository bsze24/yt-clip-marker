# Current task

**Score the existing `yt-clipper` skill against video 2.** Baton: **→ Brian**, to run it.

This is an experiment, not a build. No product code changes. The output is a number and a
rejection taxonomy, and it decides how much of the skill gets rewritten — so doing it before
touching `SKILL.md` is the whole point.

---

## 0. State as of 2026-08-20

| Item | Where | Status |
| --- | --- | --- |
| PR 9 — Zoom export ingest | merged `2ee9cc9` | closed; F20-F23 resolved at `8a47c2b` |
| PR 8 — local video mode | merged `71b9d82` | closed; [[D-034]]-[[D-038]] |
| PR 4 — video 1 store | merged `43c99dd` | closed |
| PR 3 | merged `5af3e13` | closed |
| PR 5, PR 6 | `949cb7b`, `e158710` | closed, superseded — do not merge |

No PR is open. `REVIEW.md` has no active thread.

**Why this task and not a code task.** The goal is **0.27x realtime** — 20 minutes to review
a 75-minute lesson, against 2.0x measured today (`BACKLOG.md`, "Reducing manual tagging"). Every remaining engineering step — rewriting the
skill, building the review loop, drafting labels — is sized by one number nobody has: how well
the skill places markers on a video it did not influence. The only measurement so far is video
1, where Brian judged markers the model proposed, so its 100% region recall may be anchoring
rather than skill.

Video 2 is the test, and **it needs no new marking.** Its run holds zero skill markers; all 75
rows are Brian's, chosen with no proposal in front of him.

## 1. The task

Run `/yt-clipper` against video 2's transcript, then score its output against the 75 existing
human markers.

**Step 1 is substituted, deliberately.** The skill normally fetches captions from a YouTube URL.
Video 2 came from a Zoom export and has no captioned YouTube identity ([[D-036]]) — and none of
the four YouTube uploads has captions at all, re-checked 2026-08-19 (`BACKLOG.md`, "The corpus,
and the one blocker"). The skill does not need the URL; it needs the text file that script
emits. A run already holds everything in it. Generate:

```
HH:MM:SS<TAB>text
>>> GAP <n>s @ HH:MM:SS
```

from `runs/GMT20260730-155336_Recording_640x360-1-20260819-0903.json` with
`apps/studio/eval/make_transcript.py` (PR 11): **714 lines, 26 GAP flags**, speaker names on
every line. Hand the skill that file and run steps 2-6.

The GAP count has to match the run's own `gapBefore` flags — 26 here, 27 on video 1. An earlier
throwaway version hardcoded a 20s threshold against ingest's 18s, and recomputed gaps from
rounded starts, giving three different answers for one transcript (20, 26, 28). `R-TAKE-GAP`
fires off those exact lines, so the skill would have been scored on a transcript that disagreed
with the studio it is being compared against.

**Two ways to destroy this test, both easy:**

1. **Writing skill markers onto video 2's run.** That mixes proposals into ground truth and the
   test can never be run again. `SKILL.md` asks before creating a duplicate run — answer no.
   Score in a scratch file.
2. **Reading the results before recording the deviation.** Write down that steps 2-6 were
   tested and step 1 was substituted, before looking at the output.

## 2. What to measure

**Star recall is the primary number. Not precision, not overall recall.** Brian's
constraint, 2026-08-20: extra markers are close to costless — flipping past one is a
keypress — but a starred moment with no marker near it puts him back into manual culling,
which is the whole cost being removed. So the tool is bought on recall of the moments he
cared about, and everything else is secondary.

Do not compute this by hand. `apps/studio/eval/score_run.py` produces every number below
from the skill's output plus the ground-truth run id, and refuses to run if the proposals
file is sitting in `runs/`:

```
python3 apps/studio/eval/make_transcript.py GMT20260730-155336_Recording_640x360-1-20260819-0903 > /tmp/video2-transcript.txt
python3 apps/studio/eval/score_run.py /tmp/video2-proposals.json GMT20260730-155336_Recording_640x360-1-20260819-0903
```

**Video 1 baseline, from the same script**, so the comparison is like-for-like:

| | 20s | 30s | 45s | 60s |
| --- | --- | --- | --- | --- |
| **Star recall** (self-created only) | 56% | 89% | **100%** | 100% |
| Region recall (all 67 rows) | 84% | 93% | 97% | 100% |
| Precision (proposals near a human row) | — | 81% | 84% | — |

Two confounds the script already handles, both of which inflate the score if ignored:

1. **A star on a skill marker is covered by definition.** Only stars on clips Brian created
   himself are evidence. On video 1 that cuts the sample from 17 to 9 — and `n = 9` is why
   the 100% needs video 2 before anyone leans on it.
2. **Ground truth folds in file order**, last event per row identity wins. Sorting by
   `recordedAt` eventually picks the wrong record; video 1's store has three pairs written
   out of timestamp order.

Also produced, in descending order of how much they change a decision:

3. **Direction and lead time.** Brian, 2026-08-20: not knowing whether to scrub forward or
   back is its own cost, separate from distance. On video 1 the nearest proposal was earlier
   14 times and later 7 — so a third of the time he moves the wrong way first. The script
   prints what a deliberate lead would buy. Video 1 says **−30s takes it from 7 of 21 down to
   2, at a median 42s of lead-in** — which at 1.5× is 28 seconds of run-up, roughly what a
   clip wants anyway. If video 2 agrees, placing markers early stops being a hack and becomes
   the rule: the marker means "the clip starts here", not "the moment is here".
4. **Candidate count and `R-CUE-EXACT`** — [[D-032]]'s revert signal. The script reports how
   many proposals miss an exact cue start; any that do mean the rule is being ignored, which
   is a finding rather than a curiosity. Closes `TD-6`.
5. **A rejection taxonomy.** The script lists every proposal more than 45s from a human row.
   Sort each into a named class the way video 1's 24 were sorted. That list, not the
   percentage, is what rewrites the skill.

## 2b. Results — three videos scored, 2026-08-21

| | video 1 (anchored) | video 2 | video 3 |
| --- | --- | --- | --- |
| lesson | 91 min, mixed | 64 min, line-by-line polish | 44 min, harmony instruction |
| human rows | 67 | 75 | 51 |
| proposals | 64 (0.70/min) | 65 (1.02/min) | 31 (**0.70/min**) |
| **star recall @45s** | 100% (n=9) | **94%** (n=36) | **81%** (n=21) |
| star recall @60s | 100% | **100%** | 86% |
| region recall @45s | 97% | 89% | 75% |
| precision @45s | 84% | 94% | 81% |
| `R-CUE-EXACT` | 64/64 | 65/65 | 31/31 |

**`R-CUE-EXACT` holds on all three.** [[D-032]] does not revert; `TD-6` is closed by
measurement — every proposal on every video lands on an exact cue start.

**`R-CONCEPT` is the rule that works.** 95% on video 2 and 95% on video 3, on lessons whose
content could hardly differ more. It carried 22 of video 3's 31 proposals.

**`R-TAKE-GAP` is lesson-dependent, which is worse than being wrong.**

| | fires | near a human row | near a **starred** row |
| --- | --- | --- | --- |
| video 2 (demo-dense) | 26 | 92% | 65% |
| video 3 (talk-dense) | 8 | **50%** | **12%** |

The 2026-08-19 prediction said the rule would fail on a Zoom transcript because Zoom writes
down the playing instead of leaving silence. **Wrong mechanism, and the falsification test was
badly specified** — one video could not settle it, and video 2 appeared to refute it outright.

What is actually happening: gaps still exist and the rule still fires. Silence does mean
someone is playing. But playing is only worth marking when it is *Jake demonstrating* — and on
video 3 four of the eight gaps are the **reference track** at the top of the lesson, a Louis
Armstrong recording, correctly detected as music and worth nothing. Tuning the threshold cannot
separate those, because the distinction is not acoustic, it is who is playing and why.

That is the same wall as `take`. See §2's settled note: no text feature predicts it.

**Two named rejection classes**, both from video 3's six false positives:

1. **The lesson has not started** — five of six sit before his first marker at 5:29, four of
   them the reference track. `R-SKIP-INTERRUPT` covers scheduling chatter but not a warm-up
   playthrough.
2. **Under-production.** 0.70 proposals/min against a marking rate of 1.16/min. `R-COPIOUS`
   asks for 20-30 per 90 minutes, which video 3 met — and that guidance is now the ceiling on
   recall. Three starred moments were never proposed within 90s, all in the 33-38 minute
   stretch on triad pairs, the densest teaching in the lesson.

## 3. After this, in order

Neither is part of this task. Recorded so the result has somewhere to go.

- **Mark `GMT20260712`** — placement and label only, keeping `star` and who-was-playing in the
  label text. Scope and reasoning in `BACKLOG.md`. It resolves the lesson-type confound under
  the prediction above; it is *not* for training data, which the ceiling table rules out.
- **Then decide the `SKILL.md` rewrite.** Six rules are keepers on evidence, four are premised
  on YouTube auto-captions and are dead on a Zoom transcript. The split is in the 2026-08-19
  analysis; do not act on it before this task returns.

## 4. Baton

**→ Brian**, to run the skill. Nothing is blocked on an agent.

---

## Handoff notes

### 2026-08-20 — planner, scoping the eval

- **Why an experiment holds the one active-task slot.** Four backlog items and both halves of
  the skill rewrite are waiting on the same measurement, and it is cheap. Building first means
  building against video 1's n=1.
- **The correction this spec carries.** An earlier version of the roadmap put marking a third
  video ahead of this run, on the belief that a held-out placement test needed new marking. It
  does not — video 2 already qualifies. Running the skill is free and may change what is worth
  marking, so it goes first.
- **A second correction.** The roadmap called this step blocked on teaching the skill to read a
  run's `cues[]`. Overstated: the skill consumes a text file, and a run holds everything that
  file needs. The substitution is a scratch script, not a feature.
- **What could make this task worthless.** Merging skill output into video 2's run. Said twice
  above because it is irreversible.
