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

**Why this task and not a code task.** The goal is cutting manual tagging by 75%+
(`BACKLOG.md`, "Reducing manual tagging"). Every remaining engineering step — rewriting the
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

from `runs/GMT20260730-155336_Recording_640x360-1-20260819-0903.json`. A throwaway script did
this on 2026-08-19: 708 lines, 20 GAP flags, speaker names on every line. Hand the skill the
file and run steps 2-6.

**Two ways to destroy this test, both easy:**

1. **Writing skill markers onto video 2's run.** That mixes proposals into ground truth and the
   test can never be run again. `SKILL.md` asks before creating a duplicate run — answer no.
   Score in a scratch file.
2. **Reading the results before recording the deviation.** Write down that steps 2-6 were
   tested and step 1 was substituted, before looking at the output.

## 2. What to measure

Three numbers and one list. The first is the one that matters.

1. **Region recall.** For each of the 75 human markers, distance to the nearest skill proposal.
   Video 1's answer was 21 of 21 within 90s, zero missed. If video 2 comes back materially
   worse, the "recall is not the problem" premise under the whole roadmap is wrong and the
   ordering changes.
2. **Precision.** Proposals with no human marker nearby. Video 1's judged baseline was 49%,
   rising to a projected 82% once four fixable classes are removed.
3. **Candidate count** — [[D-032]]'s revert signal for `R-CUE-EXACT`. A drop means the rule is
   suppressing proposals. Check `marker.start` against the `cues[]` start set at the same time;
   a non-caption start means the rule is being ignored. That closes `TD-6`.
4. **A rejection taxonomy**, in the style of video 1's: sort every false positive into a named
   class rather than counting it. That list, not the percentage, is what rewrites the skill.

**One prediction to falsify, filed 2026-08-19.** `R-TAKE-GAP` should fail here. Zoom transcribes
the playing instead of leaving silence — at a moment Brian labelled `Line 1 - jake demo` the
transcript reads `Jake Sherman: Ba-ba-do da.` Gaps >=30s: 14 on video 1, 5 on video 2. And gaps
do not track his takes (4 of 13 tagged rows near one, against 19 of 62 untagged — identical).
**If `R-TAKE-GAP` fires well anyway, half the rewrite case is wrong and should be dropped.**

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
