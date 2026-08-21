# Eval — state and roadmap

What the eval channels are, what they have produced, and what would make the skill better.
Live record: edit in place, commit straight to `main`.

Companion docs: `BACKLOG.md` "Skill eval" holds the scored numbers; `DECISIONS.md` holds
[[D-010]], [[D-021]], [[D-040]], [[D-041]], [[D-043]], [[D-044]]. This file is the one that
answers "where are we".

Numbers below were recomputed from the store on 2026-08-21 at `3f87bd8`. Where they disagree
with an earlier note, this file is right — the store has grown.

---

## 1. What eval is for

Two consumers, and only one of them exists yet.

1. **Revising `SKILL.md` by hand.** Read what the skill got wrong, write a rule, run it again.
   This is the whole loop today.
2. **Training something.** Few-shot examples, retrieval, or a classifier. Nothing built.

Everything in this file is about making 1 cheap enough that 2 becomes reachable.

## 2. The corpus

| | Video 1 `YYW4Q1Nivg8` | Video 2 `GMT20260730` | Video 3 `GMT20260712` |
|---|---|---|---|
| Source | YouTube auto-captions | Zoom, diarized | Zoom, diarized |
| Cues | 1464 | 688 | 688 |
| Length (last cue) | — | 3870s | 2640s |
| Skill markers in the run | 64 | 0 | 0 |
| Human-created clips | 21 | 75 | 51 |
| Starred rows | 17 | 36 | 21 |
| Tagged rows | 59 | 75 | 21 |
| Label events | 566 | 191 | 96 |
| **Anchoring** | **anchored** | **blind** | **blind** |

853 label events total. **147 human-created clips** across three lessons, plus 64 judged
proposals on video 1. **74 starred rows** — 66 on clips he built, 8 on skill markers he
annotated.

Video 1's two counts were corrected on 2026-08-21 (starred 11 → 17, tagged 34 → 59). The
earlier pair matched no fold of the store: 9 of his own clips are starred and 8 of the skill
markers he annotated are, and neither 11 nor any sum reaches it. `eval/star_predictability.py`
recomputes all of these, so the table can be checked rather than trusted.

**Anchored vs blind is the distinction that matters.** Video 1 was marked with the skill's
proposals already on screen, so its negatives only cover places the model spoke — never the
~85 minutes it correctly stayed quiet. Videos 2 and 3 were marked before the skill ever ran,
which is what makes their recall numbers trustworthy and what makes them the only real
held-out data that has ever existed here.

Both Zoom runs report exactly 688 cues. Checked — different lessons, different text, genuine
coincidence, not a sidecar-matching bug. Do not re-chase it.

**Implicit negatives.** Video 2 has 688 caption rows and 75 marked, so 613 rows the eye passed
over. Noisy but usable. The scarce side is positives, not negatives.

**The corpus blocker.** Four runs — `Oa0wqetkNcg`, `dYT41doJw2I`, `glhvfs6OOOE`,
`nWCc3xBSz-0` — hold zero cues and zero clips. They are YouTube uploads whose captions never
generated. `Oa0wqetkNcg` is video 2 uploaded (3883s against video 2's 3870s last cue). The
clips and the YouTube identity are in different objects, which is what `CURRENT.md` phase 1
fixes.

## 3. What has shipped

- **`apps/studio/eval/score_run.py`** and **`make_transcript.py`** (PR 11). The scorer refuses
  to run when the proposals file sits inside `apps/studio/runs/` and exits 1 — that guard is
  why scoring videos 2 and 3 never contaminated ground truth.
- **Star recall as the primary metric** — extra proposals cost a keypress, a missed star costs
  a manual pass. Precision is secondary by design.
- **`SKILL.md` v2** ([[D-040]]): the skill detects concepts from text; takes are not detectable
  from a transcript. Four features were tested against `take` and all four were dead.
- **[[D-041]]** — eval is what you do anyway, not a separate pass. Supersedes [[D-010]].
- **Section breaks** (PRs 21, 22): `work` and `lane` moved off the clip onto the run.
- **`SKILL.md` v2 ran, once, on video 3** (2026-08-21). Smoke test only — the score is not a v2
  result ([[D-043]]). It executes and it obeys its own rules: 99 proposals over 44 minutes
  (2.25/min against `R-COPIOUS`'s floor of 1), 99/99 on exact cue starts (`R-CUE-EXACT`), no
  gap over 60s (`R-COVERAGE`). Artifacts: `/tmp/video3-proposals-v2.json`.
- **`eval/star_predictability.py`** (2026-08-21) — the §7E test, re-runnable. See [[D-044]].
  Open in PR 27, so it is not on `main` yet.

## 4. Current state of the code — verified 2026-08-21

### Eval mode has six consumers, not two

An earlier note said "exactly two consumers, both display-only string interpolation". That is
wrong, and the difference matters for the delete-the-toggle decision.

| Where | What `evalMode` gates | Display only? |
|---|---|---|
| `ui/runs.js:33` | picker label: `· 21 added` → `· 23 check` | yes |
| `ui/grid.js:518` | the stats line's whole eval breakdown | yes |
| `ui/grid.js:277,284` | hides the model's `why` note | yes |
| `ui/grid.js:279,287,292` | reject styling and the rationale block | yes |
| `ui/keys.js:246` | **the `g` key** — `toggleCheck()` is inert with eval off | **no** |
| `ui/persist.js:302` | **`rejectOrDelete` refuses to write a reject on a model row** | **no** |

The last two write to the store. "Delete every `g` and `x` and the app behaves identically" is
true of the display; it is not true of the keyboard. Deleting the toggle means deciding what
those two paths do unconditionally, not just removing four `if`s.

### `keep` is now just "has tags" — confirmed

`ui/grid.js:530`:

```js
if ((ann.tags || []).length || ann.lane || ann.work) keeps += 1;
```

But since PRs 21–22 the row's work and lane inputs are prefilled from `workAt()`/`laneAt()`,
placeholdered *changes work from here*, and commit through `persistSection` (`ui/suggest.js:216`)
— **not** `persistTaxonomy`. So no UI path writes a per-marker `ann.lane` or `ann.work` anymore.

Consequence: video 1's 14 `keep` rows were counted under the old rule and are not comparable to
anything counted today. The bucket silently changed meaning at the PR 21 boundary.

### `score_run.py` guesses at a fact it can read

Line 129 tests `if not annotated:` — where `annotated` means *skill markers you put taxonomy on*
— and concludes the run holds no skill markers. Those two things diverge the moment the skill
proposes markers you don't tag, which is exactly the direction of travel. The honest test is
`if not truth.get("markers"):`, and the run file is already loaded for the `R-CUE-EXACT` check.
One line.

### `miss` is the wrong word on screen

A clip you create stores as `miss` — *the skill missed this*. On videos 2 and 3 the skill never
ran, so nothing was missed. `score_run.py` printed `0 of 65 proposals earned a star in place (0%)`,
which reads as failure and means undefined; a special case now prints "not applicable". Do not
rename in the store — 853 append-only events, and the word is only wrong in the UI.

### `SKILL.md` v2 has now been run once — 2026-08-21

Closed. It had never executed: `SKILL.md` was written 2026-08-20 23:40 and every proposals file
predated it, so every scored number on record came from v1. The smoke test in §3 fixed that.
**There is still no v2 *measurement*, and by [[D-043]] there should not be one until v2 is used
on a lesson it did not help design.**

Also confirmed: `Backdoor dominant is iv–I (plagal)` is already in `SKILL.md` at lines 95 and 105.
The label half of that edit is in v2; the earlier doubt about it was unfounded.

## 5. The ladder — what is beyond hand-editing rules

The R- rules are not the intelligence. `R-CONCEPT` does not define a teaching concept; it says
"where a new instructional idea begins" and a large model decides. It hit 95% on video 2
(dynamics) and 95% on video 3 (harmony theory) with nobody explaining either topic. The rules
steer; the model reasons.

The reason a Radar-style model does not transfer is data economics, not modeling. Radar's labels
are free and arrive automatically. These cost roughly 45 minutes a lesson and exist only because
you sat down.

| Rung | What | When it becomes viable |
|---|---|---|
| 1 — hand-edited rules | where you are | now; saturates ~5–8 lessons |
| 2 — few-shot placement examples | learning from labels, in-context | **available now** |
| 3 — retrieval over past labels | show the model what you did at similar past moments | ~10–15 lessons (700–1000 markers) |
| 4 — classifier / fine-tune | trained on your labels | **off the roadmap for `star` — [[D-044]]** |

Rungs 3 and 4 are estimates from measured rates, not measurements. Confidence: moderate on the
ordering, low on the thresholds.

**Rule insight saturates too.** Video 1's 24 rejections produced 7 named failure classes. Video 3
added 2, both narrower. The well runs mostly dry around 5–8 lessons, which is roughly when rung 3
becomes viable. That overlap is the crossover, and it is the argument for not over-investing in
rule authoring.

**A cheaper rung 3 is available sooner: same-tune retrieval.** Two lessons already touch
*Can't Take That Away* and two touch *Pennies from Heaven*. The material repeats.

**The number that decides all of it.** 15 lessons at 45 minutes of authoring is 11 hours. At 10
minutes of reviewing it is 2.5. The efficiency work is not parallel to the ML future — it decides
whether the data scale is ever reached.

### Rung 2 in detail

A bare list of labels teaches style, not placement. A placement example needs the transcript
window, the timestamp, the label, and why.

| Exemplar set | Size | Teaches |
|---|---|---|
| Skill placed it, you starred it in place | 8 (video 1 only) | "this is a good proposal" |
| You marked it yourself | 147 across three lessons | "this is worth marking" |

The 8 are purest but come entirely from video 1 — YouTube auto-captions, hallucinated lines, no
speaker names. That is not the format you now work in. Build placement examples from the 147,
sampled across all three lessons.

## 6. One thing recordable only at creation

When you build a clip, was a proposal in front of you? Three cases:

| Case | Meaning |
|---|---|
| Kept the nearby proposal | hit |
| Built your own because the nearby one was bad | real miss |
| Built your own with nothing proposed | positive, not a miss |

Today all three store identically as `miss`. One boolean on the write path separates them, and it
is **only** recordable at creation — no later pass can reconstruct what was on screen. Add it
whenever the write path is next touched.

## 7. Open decisions — the roadmap conversation

Framed as questions, with a recommendation and a confidence level. Nothing here is decided.

**A. Delete the eval toggle?** Recommend yes, but it is a two-part change: four display `if`s
come out freely, and then `g` and the model-row reject need a defined unconditional behaviour.
Confidence: high that the toggle should go, moderate on what replaces the two write paths.

**B. Retire `g` and `keep`?** Recommend yes for both. `keep` already changed meaning silently
(§4) and `g` is circular — it marks proposals good, which biases toward what the model already
does. `x` survives and gets reinterpreted as the rejection channel. Confidence: high on `keep`,
moderate on `g`.

**C. Should the next lesson be marked blind?** **Decided 2026-08-21 — no. See [[D-043]].**

Use v2 for real instead and record four numbers per lesson: proposals offered, accepted without
playing the video, had to scrub to check, clips added that nothing proposed. The second is the
one that matters — it is the only number here that could kill the premise, because if authoring
time does not fall from 45 minutes the data scale for rungs 3 and 4 is never reached.

The cost is real and was accepted: zero clean test lessons exist and zero will exist after this.
When v3 needs testing, a lesson gets marked blind then — about 45 minutes, deferred rather than
avoided. D-043 carries the full argument and the two conditions that would reverse it.

**D. Is re-running v2 on videos 2 and 3 worth it?** Recommend a single unmodified v2 run for an
unconfounded baseline, then stop. Beyond that it is near-tautological — every v2 rule was derived
from those two videos. `R-COVERAGE` exists because video 3 had a five-minute hole; re-run it and
the hole fills because the rule was written to fill it. That is a smoke test that the model obeys
its own instructions, not evidence. Confidence: high.

**E. Does anything in the transcript predict `star`? Tested 2026-08-21 — no. See [[D-044]].**

147 clips, 66 of them starred, base rate 45%. Re-run it with
`python3 apps/studio/eval/star_predictability.py`.

| What was tested | Result |
|---|---|
| ten transcript features, pooled AUC | 0.44–0.60; not one keeps its sign across all three lessons |
| best of them, `mean_cue_chars` | 0.603, p=0.035 — which is nothing after ten comparisons, and it reverses on video 1 (0.48) |
| `position_in_lesson` | 0.671, p<0.001 — the only one that beat chance, and it is not text |
| **ceiling: a model reading Brian's own labels** | **AUC 0.513, p=0.86** |

**The ceiling test is what decides it.** The model scored all 75 of video 2's clips from Brian's
own label text with the stars hidden. His label is a *richer* input than the transcript — it is
his description of the moment, written after he watched it. It scored 0.513 against a coin flip's
0.500. Its top 10 picks were 60% starred against a 48% base; its top 20 were 45%, below base.

**`position_in_lesson` is the annotation pass, not the lesson.** On video 1 the first half holds
0 stars in 11 clips and the second holds 9 in 10 — a regime change in how he was working, not a
lesson that got important at the 45-minute mark. Video 2, the largest sample, shows nothing
(0.50). Video 3 shows the drift, but he labelled it 48/50 steps front-to-back, so video position
and labelling order are the same variable there and cannot be separated.

**What `star` actually tracks, and why that closes the question.** It is not the idea, it is the
demonstration:

| Signal | n | starred | lift |
|---|---|---|---|
| `demo` in his own label | 21 | 86% | 1.91× |
| the `take` tag | 18 | 78% | 1.73× |
| the `chord exercise` tag | 15 | 73% | 1.63× |
| `barry` / `harris` in his label | 10 | 40% | 0.89× |
| the `fingering` tag | 7 | 0% | 0.00× |
| the `technique` tag | 5 | 0% | 0.00× |

The model's errors say the same thing from the other side. It ranked *General rule louder for
higher notes*, *Barry Harris advance mode, drop 2* and *This technique is called a line cliche*
at the top; none is starred. It ranked *Line 2 — jake take* and *Line 5 — kick off + jake take*
at the bottom; both are. Star marks where someone played, and [[D-040]] already established that
whether a passage is a demonstration is not recoverable from a transcript, measured four ways.

**Silence gaps are dead here too**, which independently re-confirms `R-TAKE-GAP`'s retirement: a
clip landing exactly on a gap cue is starred 38% of the time against the 45% base, and only 8 of
61 gap cues in the whole corpus ever became a clip.

**The honest limit.** 147 clips with 66 positives cannot rule out a weak real effect of AUC
around 0.58. That is why the ceiling test carries the verdict rather than the feature table — a
signal his own words cannot express is not one a transcript classifier will find.

## 8. Next actions, ordered

~~1. Run `SKILL.md` v2 once~~ — **done 2026-08-21** on video 3. See §3.
~~2. Star predictability test~~ — **done 2026-08-21.** See §7E and [[D-044]]. It did what it was
   supposed to do: it removed work.

1. **Use v2 for real on the next few lessons** and record the four numbers ([[D-043]] §C). This
   is now the only open item that can change the plan, because §7E closed the other one.
2. **Fix `score_run.py`'s `annotated` proxy** — one line, `if not truth.get("markers"):`. Same
   pass as **F31**, which is the other zero-cue crash in that file.
3. **Add the "was a proposal in front of me" boolean** next time the write path is open (§6).
4. **Display fixes**: stop printing `MISS.` under your own clips; show eval counters only when the
   run holds skill markers; then decide A and B above.
5. **Build rung 2 placement examples** from the 147, sampled across all three lessons. This is
   now the top of the ML ladder that is still worth climbing, not a step toward rung 4.

The recall test comes free from normal use — every clip you add is a place the skill proposed
nothing. Biased, because you cannot count what nothing prompted you to notice, but directional and
costless. Mark blind again only when that raises a doubt it cannot settle.
