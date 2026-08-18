---
date: 2026-08-18
time: "12:17"
surface: grok
project: yt-clip-marker
track: studio-workspace
work: stored vs displayed time; R-NEIGHBORHOOD
branch: docs/remove-coordination-md
resume-of: docs/coordination/README.md standing-trap paragraph
---

# Stored time vs displayed time — 2026-08-18

Learning note from a README walkthrough. Not a product spec. Not a resume head for the studio-workspace track (that is still `2026-08-16-1507-grok-studio-fable-lock.md`).

## Summary

The grid's left column is the **subtitle clock**: when those words appeared. A clip record
carries its own stored start, and when the two differ the row shows the caption's time while
the record's own time appears nowhere on screen.

**Measured on video 1, 2026-08-18** — this replaces the `1:18:50` illustration used in the
first draft of this note, which described earliest-cue-wins alignment that [[D-008]] has since
replaced, and cited an added marker tombstoned on 2026-08-16:

| Class | Stored start is exactly a caption start | |
| --- | --- | --- |
| skill markers, `CONCEPT` | 46 / 46 | never drifts |
| skill markers, `TAKE` | 18 / 18 | never drifts |
| extracted stamps | 5 / 24 | **drifts 19 times** |

Skill marker 53 is stored at `4732` and there is a caption starting at exactly `4732`, so it
displays at `1:18:52` — its own time. Nothing in this cluster demonstrates the trap.

The real example is `Tricky F alt lick fingering`, stored at `280.0` (`4:40`). No caption starts
at 280; the nearest are 278 and 279, so it renders on the `4:39` row. Screen says 4:39, store
says 4:40, and copy-timestamps exports 4:40. Off-cue extracted stamps are mostly ±1s (14 of 19),
with a few real outliers — one sits 24s from its nearest caption, which is a stamp landing in a
long playing stretch where the caption track goes quiet.

There is a second, distinct trap that has nothing to do with time: **an extracted stamp within
2s also wins the row's label**. At `1:18:57` the added marker stored at `4737` displays
"Freedom Demo c1", which is the label of the extracted stamp stored at `4738`. The text you
read and the time beside it can come from two different records.

### Where this note's argument was right, and where it went further than the data

The reasoning in the first draft — the skill is shown one timestamp per caption block and no
finer clock, so concept markers have no reason to drift — is **confirmed, and more strongly
than it claimed**. It hedged with "if a concept marker is not exactly a caption start, the model
is rounding under `R-NEIGHBORHOOD`." On this run there is no such marker. `R-NEIGHBORHOOD`'s
approximate-time licence is a freedom the skill never exercised.

The part that does not survive is the claim that a non-caption time "is expected" for **takes**.
All 18 sit exactly on caption starts. The reason is mechanical: `build_cues` flags a silence gap
on the *following* cue as `gapBefore`, so a gap's timestamp already **is** a caption start. There
is no separate gap clock. 19 of the 64 markers land on one of the run's 27 gap-flagged cues, so
takes do track gaps — they just do it in caption time.

So the three-clock model in the first draft collapses to two, and the boundary is provenance,
not marker class:

- **The caption clock.** Everything the pipeline produces — concepts, takes, and added markers,
  which inherit a row's time when you press Enter on it. Stored always equals displayed.
- **The description clock.** Extracted stamps only, because a human typed them into YouTube
  while watching. This is the sole source of drift in the store.

## Open questions — restated 2026-08-18 against the measurement

1. **Does `0 / 64` hold on a second video?** This is now the only question that matters for the
   `R-NEIGHBORHOOD` item, and it is cheap: ingest video 2, compare `marker.start` against the cue
   set. If drift stays at zero, the rule's approximate-time wording describes a licence the skill
   does not use, and tightening it is documentation rather than behaviour. If drift appears, this
   note's hypothesis about *why* it drifts is the thing to test next. Parked in `BACKLOG.md`
   under open modeling decisions, bound to the next skill-rules pass. **Do not decide from one
   run.**
2. **~~Keep two clocks in the studio anyway?~~ Answered: yes, but for one reason, not three.**
   Extracted stamps are the only class that drifts, and they must — they are the published
   timestamps the description has to match. Takes and concepts need no separate clock.
3. **~~Ingest snap vs skill snap?~~ Mostly moot.** There is nothing to snap for markers; they
   already sit on caption starts. Snapping *extracted* stamps on ingest would be actively wrong:
   it would overwrite the published times that copy-timestamps has to reproduce.
4. **~~Use discarded word offsets?~~ Dead.** Nothing in the pipeline wants sub-caption precision.
   `fetch_transcript.py` throwing away per-segment timing costs nothing.
5. **~~Rewrite the README trap?~~ Done**, 2026-08-18. `docs/coordination/README.md` now carries
   the measured version, including the label-crossing case, which the first draft did not name.

New question the measurement raises: **is the `1:18:57` label-crossing behaviour wanted?** An
extracted stamp overriding an added marker's typed label is [[D-022]]'s "extracted title and
start win when present" working as specified, but nobody has judged it from the annotator's seat
— you type a label, and the grid shows someone else's. Bound to the export freeze, alongside the
ballpark-`g` item.

## Chronology

1. **README 53–58.** Asked what “time of the caption a marker was aligned onto” means, and why stored would ever differ from displayed — wouldn’t we always want the displayed timestamp?
2. **First pass (too dense).** Two clocks: caption time vs clip time. Grid is caption-first; clips pin onto a ≤2s neighbor. Export and identity use stored start. Example: skill marker 53 stored `1:18:52`, shown on caption `1:18:50`; added marker stored `1:18:54`, shown at `1:18:52`.
3. **Dumb it down.** Grid = list of subtitles. Left column = when those words appeared. Clip = sticky note on the nearest subtitle, own time still on the back. Trap: treating the subtitle time as the clip time.
4. **Why not always caption timestamps?** If captions are the only explicit times, why would the skill place `0:22` when cues are `0:18` and `0:24`?
5. **First answer (overstretched).** A cue at 0:18 spans until 0:24; a moment at 0:22 still “belongs” to that caption. `R-NEIGHBORHOOD` allows approximate times. Also gaps (takes) and description stamps (extracted). Misread as: markers are word-granularity and the skill guesses when the word occurs.
6. **Check the fetch script.** `fetch_transcript.py` joins all words in a YouTube caption event and keeps **only the event start**. No word clock. Retract: for concepts the skill sees a list of caption starts, nothing finer.
7. **Exclude takes and extracted.** Then why would stored ever drift? Guessing a word inside a short, fully listed caption feels like a bad design.
8. **Landed here.** For concepts, drift is not required. It happens because the skill emits approximate `M:SS` instead of copying `cue.start`. That is `R-NEIGHBORHOOD` as slop, not a word locator. Cleaner: concept time = that caption’s start. The README demo example is a take, so it does not prove the concept case.
9. **Print the rule.** Entire text: *Approximate timestamps; clip-marker nailing is downstream.*

## Pointers

- Trap text: `docs/coordination/README.md` (standing trap)
- Alignment: exact start first, then ≤2s (`MATCH`) in studio `grid.js` on PR 3
- Skill rules: `~/.claude/skills/yt-clipper/SKILL.md` (`R-NEIGHBORHOOD`, `R-CONCEPT`, `R-TAKE-GAP`)
- Caption flatten: `~/.claude/skills/yt-clipper/scripts/fetch_transcript.py` `parse_json3`
- Video 1 fold: `docs/reference/2026-08-16-YYW4Q1Nivg8-folded-ledger.md` (skill 53 at 1:18:52)
- Measurement behind the table above: run file `markers[]` / `extracted[]` against the `cues[]`
  start set, video 1 (`YYW4Q1Nivg8-20260814-1248`), 2026-08-18. Reproduce before trusting it.
