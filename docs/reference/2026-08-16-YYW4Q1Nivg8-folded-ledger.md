---
date: 2026-08-16
runId: YYW4Q1Nivg8-20260814-1248
videoId: YYW4Q1Nivg8
track: studio-workspace
companion: docs/sessions/2026-08-16-1507-grok-studio-fable-lock.md
sourceOfTruth: apps/studio/runs/YYW4Q1Nivg8-20260814-1248.json + apps/studio/labels.jsonl
---

# Folded clip ledger — YYW4Q1Nivg8-20260814-1248

A **read-only fold** of the three clip sources on this video, as of 2026-08-16 15:11. Not a store. Reverse-engineer from here; mutate `runs/*.json` (immutable ingest) and `labels.jsonl` (append-only) only.

The studio grid is the same fold, time-aligned to captions. This file is that fold without the caption rows — so a later Claude can see skill markers, published description stamps, and human adds in one timeline, including rejects and the cross-refs that only made sense on the grid.

## How to read a row

| `source` | Who created it | Identity |
|---|---|---|
| `skill` | yt-clipper skill, in the run file `markers[]` | `idx` = `markerIndex` |
| `extracted` | Parsed from the published YouTube description | no label events |
| `added` | Human, via studio Enter / miss event | identity = `(runId, start)` |

| `status` | Meaning |
|---|---|
| `g` | Few-shot exemplar keep (`check`). Stingy. |
| `x` | Reject this **skill marker**. Still in the run file; skipped by copy-timestamps. |
| `keep` | Ordinary keep: taxonomy on a skill marker, no `g`. |
| `note` | Freeform eval note, not g/x. |
| `blank` | Skill marker not reviewed. |
| `added` | Added marker; delete is `unmiss`, not `x`. |
| `extracted` | Extracted marker. Copy-timestamps never drops these. |

`extracted±2s` = a description stamp within 2 seconds (studio `resolvedLabel` / export extracted-wins). `orig` = skill text when the human relabeled.

## Counts

- skill markers: 64 (`g` 23 · `x` 24 · keep 14 · note 3 · blank 0)
- added markers (live): 21
- extracted: 24
- deleted adds (tombstones): 4

## Verdict recipe (do not collapse)

- `g` — few-shot positive for a **skill marker**.
- `star` tag — personal bookmark, not eval.
- taxonomy without `g` — ordinary keep.
- `x` — eval negative on a skill marker.
- delete / `unmiss` — remove an added marker.
- blank — unreviewed.
- Spoken sequential finger numbers (`5 4 3 1`, `2 1 3`) → fingering. Do **not** prefer the last mention in a block.

## Load-bearing pairs (cross-refs)

These are the rows that confused the grid-less transcript. Status is current fold.

| From | To | Shape |
|---|---|---|
| 20:46 skill `g` Double-note… | 21:18 added Double note fingering | ballpark `g` / perfect place. Same clip, ~32s. **Both export.** |
| 29:23 skill `g` F-sharp to D-flat… | 29:09 caption only (“Maybe it’s a good hint”) | ballpark `g` / better place has **no clip**. 29:23 is the keep if you only get one. |
| 35:53 skill `x` Line before the ending | 36:39 added Line before the ending | hunting vs start. `x` the early marker; keep the add. |
| 37:49 skill `x` Ending fingering | 37:56 added Lick fingering | slightly early; sequential numbers at 37:56. |
| 38:55 skill `x` Harmony of the improv | 39:08 skill 2nd-inversion… | chapter change, not a clip. Harmony starts 39:08. |
| 55:40 skill Hearing vs executing | 55:42 added (deleted) | duplicate add; 55:40 is the keep. Extracted 55:43 nearby. |
| 1:18:52 skill `g` Jake demo… | 1:18:54 added (deleted); extracted 1:18:58 Freedom Demo c1 | leftover caption add deleted. No extracted at 52/54. Display used to snap 52 onto 1:18:50 and the add onto 1:18:52. |
| 1:18:57 added Freedom Demo c1 | extracted 1:18:58 Freedom Demo c1 | human add + description stamp; extracted title wins in export fold (≤2s). |

## Timeline

| t | source | idx | status | label | tags | work | lane | extracted±2s | why |
|---|---|---|---|---|---|---|---|---|---|
| 0:00 | skill | 0 | x | Lesson start. Performing more transcribed choruses with questions on fingering. _(orig: The Stand — another chorus transcribed, sticky fingerings)_ | chapter | Pennies from Heaven \| Stan Getz | Transcription |  | It's only interesting because it's the start of a lesson / chapter. But actual content is not interesting here. |
| 1:20 | skill | 1 | x | The Stand solo playthrough |  |  |  |  | hallucinated transcript line...heat is reliably hallucinated |
| 2:37 | skill | 2 | x | Solo — later choruses |  |  |  |  | hallucinated transcript line...heat is reliably hallucinatedj |
| 3:12 | skill | 3 | x | Last chorus of the solo |  |  |  |  | Hallucinated caption |
| 3:55 | skill | 4 | g | Sticky parts — the alt lick |  | Pennies from Heaven \| Stan Getz | Transcription |  |  |
| 4:21 | added |  | added | Importance of technique for performance accuracy | technique | Pennies from Heaven \| Stan Getz | Transcription |  | Concept change |
| 4:40 | extracted |  | extracted | Tricky F alt lick fingering |  |  |  |  |  |
| 5:00 | added |  | added | Fingering for hardest line in stan / pennies | fingering | Pennies from Heaven \| Stan Getz | Transcription |  | Sequential finger numbers in a clip range mean fingering. Tag fingering. Do not prefer the last mention in a block — that heuristic did not survive review. |
| 5:10 | skill | 5 | keep | Wrist too high at the start | technique | Pennies from Heaven \| Stan Getz | Transcription |  |  |
| 6:49 | added |  | added | But not too high | fingering | Pennies from Heaven \| Stan Getz | Transcription |  | Correction from earlier point of "raising wrist". |
| 7:08 | skill | 6 | keep | On the F, let go of the muscles | technique | Pennies from Heaven \| Stan Getz | Transcription |  |  |
| 7:34 | skill | 7 | keep | Catch D-flat on the way to A-flat; release the F | technique | Pennies from Heaven \| Stan Getz | Transcription |  |  |
| 8:27 | skill | 8 | keep | A-flat: hover, don't collapse the wrist | technique | Pennies from Heaven \| Stan Getz | Transcription |  |  |
| 8:41 | added |  | added | Good rep finally | technique | Pennies from Heaven \| Stan Getz | Transcription |  | For eval - when Jake (my teacher) exclaims positively, sign of good technique example for me to follow. |
| 11:10 | skill | 9 | g | Whole-chorus take → next sticky lick |  |  |  |  |  |
| 11:47 | skill | 10 | keep | Let go of the thumb / wavy / not glued to A | technique | Pennies from Heaven \| Stan Getz | Transcription |  |  |
| 12:31 | added |  | added | Lick fingering | fingering | Pennies from Heaven \| Stan Getz | Transcription |  |  |
| 12:54 | added |  | added | Lick technique | technique, take | Pennies from Heaven \| Stan Getz | Transcription |  |  |
| 13:51 | skill | 11 | keep | A-flat rotation (slight up); wrist not already turned | technique | Pennies from Heaven \| Stan Getz | Transcription |  |  |
| 16:33 | skill | 12 | keep | One wave — flick vs wave; don't roll too far | technique | Pennies from Heaven \| Stan Getz | Transcription |  |  |
| 17:14 | skill | 13 | keep | Forget the right-turn; wrist falls at F-sharp | technique | Pennies from Heaven \| Stan Getz | Transcription |  |  |
| 18:41 | skill | 14 | keep | Same movement as the harder lick | technique | Pennies from Heaven \| Stan Getz | Transcription |  |  |
| 19:38 | skill | 15 | keep | Hard lick — can do it, not in time | technique | Pennies from Heaven \| Stan Getz | Transcription |  |  |
| 20:46 | skill | 16 | g | Double-note slowing you down; two different fingers | technique | Pennies from Heaven \| Stan Getz | Transcription |  | useful ballpark. If there were no other markers here, 20:46 is a genuine keep — it lands you on the double-note problem. The perfect placement of this same clip is the added marker at 21:18 ("Double note fingering"), when sequential finger numbers are spoken ("2 1 3"). 20:46 is ~32s early, still high-signal. |
| 21:18 | added |  | added | Double note fingering | fingering | Pennies from Heaven \| Stan Getz | Transcription |  | Keep. Perfect placement of the clip the 20:46 marker was aiming at (20:46 is a useful ballpark, ~32s early). Spoken sequential finger numbers (e.g. 5 4 3 1, 2 1 3) mean a fingering clip. Tag fingering. Do not prefer the last mention in a block — that heuristic did not survive review. |
| 21:41 | skill | 17 | note | Double note technique _(orig: After thumb, keep it above B (tilt, don't hold))_ | technique | Pennies from Heaven \| Stan Getz | Transcription |  | Note pattern...he gives me fingering, then after fingering we talk through technique of how to execute it |
| 23:43 | skill | 18 | g | Crossing over is fine if released — it's about not reaching | technique | Pennies from Heaven \| Stan Getz | Transcription |  |  |
| 25:56 | skill | 19 | g | Release the thumb completely (over G) | technique | Pennies from Heaven \| Stan Getz | Transcription |  |  |
| 27:59 | skill | 20 | g | Same as alt lick — catch D-flat on the way to B-flat | fingering | Pennies from Heaven \| Stan Getz | Transcription |  |  |
| 28:45 | skill | 21 | g | Wrist elevated and loose — all the hard places | technique | Pennies from Heaven \| Stan Getz | Transcription |  | skill landed a few captions early; this row (28:45, wrist elevated) is the intended marker. Pattern: almost right, miss by a few lines. |
| 29:23 | skill | 22 | g | F-sharp to D-flat without missing a beat | technique | Pennies from Heaven \| Stan Getz |  |  | useful ballpark. Much better than no marker — this is the F-sharp to D-flat line. The better placement is 14s earlier: caption at 29:09 ("Maybe it's a good hint"), where they name the hint before stating the trick. No clip stored at 29:09; this 29:23 row is the keep if you only get one. |
| 30:01 | added |  | added | Findering confirmation | fingering | Pennies from Heaven \| Stan Getz | Transcription |  |  |
| 31:06 | skill | 23 | g | Upward scale — fingery / rewrite the thumb-under | technique | Pennies from Heaven \| Stan Getz | Transcription |  |  |
| 33:07 | skill | 24 | g | New fingering, skip the slide; cross-under is bad | fingering | Pennies from Heaven \| Stan Getz | Transcription |  | Spoken sequential finger numbers (e.g. 5 4 3 1, 2 1 3) mean a fingering clip. Tag fingering. Do not prefer the last mention in a block — that heuristic did not survive review. |
| 33:28 | added |  | added | Last part of lick | fingering | Pennies from Heaven \| Stan Getz | Transcription |  |  |
| 34:28 | skill | 25 | g | Every hard place: wrist up, flowing, no tension | star | Pennies from Heaven \| Stan Getz | Transcription |  | great one...this isi a summarization "I feel like every example of this..." then some more general concept |
| 35:53 | skill | 26 | x | Line before the ending |  |  |  |  | good hunt, wrong place. At 35:53 they are still looking for the line ("one more line… a little before the ending"). The keep is the added marker at 36:39, when they actually start it. Same clip; 14s early. |
| 36:39 | added |  | added | Line before the ending | technique | Pennies from Heaven \| Stan Getz | Transcription |  | Keep. Same clip the 35:53 marker was aiming at. Place it here — they found the line and say "let's do that one" — not 14s earlier while still searching. |
| 37:49 | skill | 27 | x | Ending fingering — thumb on D |  |  |  |  | slightly early. Right clip is the added marker at 37:56 ("Lick fingering"), where sequential finger numbers are spoken ("5 4 3 1"). Spoken sequential finger numbers (e.g. 5 4 3 1, 2 1 3) mean a fingering clip. Tag fingering. Do not prefer the last mention in a block — that heuristic did not survive review. |
| 37:56 | added |  | added | Lick fingering | fingering | Pennies from Heaven \| Stan Getz | Transcription |  | Keep. Right location vs the 37:49 marker (slightly early). Spoken sequential finger numbers (e.g. 5 4 3 1, 2 1 3) mean a fingering clip. Tag fingering. Do not prefer the last mention in a block — that heuristic did not survive review. |
| 38:33 | skill | 28 | keep | This solo was all about technique | technique | Pennies from Heaven \| Stan Getz | Transcription |  |  |
| 38:55 | skill | 29 | x | Harmony of the improv |  | Pennies from Heaven \| Stan Getz | Transcription |  | chapter change, not a clip. They pivot from fingering/technique into "should we go through the harmony." Don't mark the pivot; harmony clips start at 39:08 (2nd-inversion major triad). |
| 39:08 | skill | 30 | x | 2nd-inversion major triad is a sound |  |  |  |  | first time diarization matters, what I observe is 10x less interesting than what Jake (my teacher) observes |
| 39:55 | skill | 31 | g | iv minor, not backdoor / b7 dominant _(orig: iv minor = backdoor / b7 dominant)_ | harmony | Pennies from Heaven \| Stan Getz | Transcription |  | Good one. but not my correction to the tag (you got th eopposite intent) |
| 40:26 | skill | 32 | g | Backdoor dominant is iv–I (plagal) | star, harmony | Pennies from Heaven \| Stan Getz | Transcription |  | note following. another example diarzation helps. Jake saying "this is big, this is notable"...almost assuredly a clip |
| 41:05 | skill | 33 | x | Two strongest resolutions: V–I and IV–I |  | Pennies from Heaven \| Stan Getz | Transcription |  | continuation of 40:26 (starred: Backdoor dominant is iv–I / plagal), not a new clip. |
| 42:11 | skill | 34 | g | Tritone vs D7 |  | Pennies from Heaven \| Stan Getz | Transcription |  |  |
| 42:36 | skill | 35 | x | Blues + diminished; #11 / sus | harmony | Pennies from Heaven \| Stan Getz | Transcription |  | again diarization would have solved this one, me talking just less inetesting |
| 44:01 | skill | 36 | note | Tritone vs D7#9 / altered | harmony | Pennies from Heaven \| Stan Getz | Transcription |  | The right clip is 45:17 "Skip Am7, go straight to D7". This 44:01 is fine but earlier; diarization would have caught this too. |
| 45:17 | skill | 37 | g | Skip Am7, go straight to D7 | harmony | Pennies from Heaven \| Stan Getz | Transcription |  | Impressed you found this one, it's very subtle. |
| 45:30 | skill | 38 | g | Tritone sub (half-step up and down) over C Alt _(orig: C alt vs tritone sub (half-step up and down))_ | harmony | Pennies from Heaven \| Stan Getz | Transcription |  | Note: great clip, but the label was misleading. |
| 46:54 | skill | 39 | x | Soloed the other tune (half-dim start), not The Stand |  |  |  |  | diarization would have caught this. i don't care about my takes |
| 47:39 | extracted |  | extracted | Crappy sarah solo-ing |  |  |  |  |  |
| 48:03 | skill | 40 | x | Solo take — switch recordings (stops) |  |  |  |  | kinda hard for you to tell, it's a fine false positive. he's talking about how I should swithc to a different reneition to solo over. no durable content to remember here. |
| 48:44 | skill | 41 | x | Solo take |  |  |  |  | seems random |
| 49:05 | extracted |  | extracted | Crappy stan solo-ing |  |  |  |  |  |
| 49:34 | skill | 42 | x | Solo take |  |  |  |  | again random |
| 50:30 | skill | 43 | x | Solo take |  |  |  |  | random |
| 52:21 | skill | 44 | x | Solo take |  |  |  |  | random |
| 53:38 | skill | 45 | g | Speed up — pretend a faster tempo | feedback | Pennies from Heaven \| Stan Getz | Transcription | 53:40 Jake feedback - playing too slow, try different speed | diarization would solve...definitallly feedback can only be teacher talking |
| 53:40 | extracted |  | extracted | Jake feedback - playing too slow, try different speed |  |  |  |  |  |
| 54:29 | extracted |  | extracted | At least making changes |  |  |  |  |  |
| 54:38 | skill | 46 | g | Loop 4-bar chunks (backdoor ii-V) | feedback | Pennies from Heaven \| Stan Getz | Transcription |  | note this is another example where you're almost perfect, but oddly place marker a few turns early. "could be useful..." seems like the most natural marker points between the next 2 captions |
| 54:42 | extracted |  | extracted | Finding a few places to really nail |  |  |  |  |  |
| 55:40 | skill | 47 | g | Hearing vs executing; hand ahead of ear | process, star | Pennies from Heaven \| Stan Getz | Transcription |  | impressive, this is a big one I would have missed |
| 55:43 | extracted |  | extracted | Is the limitation hearing the line or execute the line? |  |  |  |  |  |
| 55:56 | extracted |  | extracted | And if you can hear the line - is it because you can't see it or because your fingers can't do it? |  |  |  |  |  |
| 56:22 | extracted |  | extracted | Gap |  |  |  |  |  |
| 56:53 | skill | 48 | x | LH voicings + horizontal vs vertical |  |  |  |  | interesting - this is the perfect place to put a "concept" change marker, but there's nothing that interesting we're talking about until a bit later. |
| 1:14:31 | skill | 49 | x | Linear (sax) vs vertical (chords); make going-up musical |  |  |  |  | again, diarization solves this. me talking less interesting |
| 1:16:22 | skill | 50 | g | Up / down / from anywhere — nearest good chord | chord exercise, star | Eb Blues \| 1 bar, 1 chord exercise | Melodic harmony | 1:16:24 Going up Eb blues right hand chords |  |
| 1:16:24 | extracted |  | extracted | Going up Eb blues right hand chords |  |  |  |  |  |
| 1:17:37 | extracted |  | extracted | Making going up exercise musical - play with left hand |  |  |  |  |  |
| 1:17:37 | skill | 51 | g | Comp going-up shapes in LH on a track | chord exercise | Eb Blues \| 1 bar, 1 chord exercise | Melodic harmony | 1:17:37 Making going up exercise musical - play with left hand |  |
| 1:18:12 | extracted |  | extracted | How to practice comping. Entering flow making melodies. |  |  |  |  |  |
| 1:18:22 | skill | 52 | keep | Comping 20 min as soloing | star, process, chord exercise | Eb Blues \| 1 bar, 1 chord exercise | Melodic harmony |  |  |
| 1:18:52 | skill | 53 | g | Jake demo — melody, harmonized | chord exercise, star | Eb Blues \| 1 bar, 1 chord exercise | Melodic harmony |  |  |
| 1:18:57 | added |  | added | Freedom Demo c1 | star, chord exercise | Eb Blues \| 1 bar, 1 chord exercise | Melodic harmony | 1:18:58 Freedom Demo c1 | c1 = chorus 1 in the music; nearly impossible for the suggester to hear. added/extracted title at 1:18:58 is Freedom Demo c1 — always prefer that over caption text. |
| 1:18:58 | extracted |  | extracted | Freedom Demo c1 |  |  |  |  |  |
| 1:19:27 | extracted |  | extracted | Freedom Demo c2 |  |  |  |  |  |
| 1:19:27 | added |  | added | Freedom Demo c2 | chord exercise, star | Eb Blues \| 1 bar, 1 chord exercise | Melodic harmony | 1:19:27 Freedom Demo c2 | c2 is second chorus. I'm fine keeping this work manual. In an ideal work. If you limit my tagging mostly to things like this, we're good to go. |
| 1:19:51 | skill | 54 | x | Comping/solo demo |  |  |  |  | hallucinated cpation |
| 1:19:54 | extracted |  | extracted | Freedom Demo c3 |  |  |  |  |  |
| 1:19:54 | added |  | added | Freedom Demo c3 | star, chord exercise | Eb Blues \| 1 bar, 1 chord exercise | Melodic harmony | 1:19:54 Freedom Demo c3 |  |
| 1:20:20 | extracted |  | extracted | Freedom Demo c4 |  |  |  |  |  |
| 1:20:21 | added |  | added | Freedom Demo c4 | chord exercise, star | Eb Blues \| 1 bar, 1 chord exercise | Melodic harmony | 1:20:20 Freedom Demo c4 | Caption was "Where are you?". added/extracted title at 1:20:20 is Freedom Demo c4. |
| 1:20:52 | skill | 55 | x | Comping is soloing; shout choruses |  |  |  |  | if I didn't have a manual tag, this would be perfect. Right location is 1:21:04 added / 1:21:05 extracted "Comping is solo-ing or big band shout choruses" (not 1:21:03). |
| 1:21:04 | added |  | added | Comping is solo-ing or big band shout choruses | chord exercise, star | Eb Blues \| 1 bar, 1 chord exercise | Melodic harmony | 1:21:05 Comping is solo-ing or big band shout choruses |  |
| 1:21:05 | extracted |  | extracted | Comping is solo-ing or big band shout choruses |  |  |  |  |  |
| 1:21:32 | skill | 56 | g | Write simple blues lines and harmonize (12-bar) | chord exercise, star | Eb Blues \| 1 bar, 1 chord exercise | Melodic harmony | 1:21:33 Write a few simple lines out and harmonize them | nailed the manual description at 1:21:33 extracted "Write a few simple lines out and harmonize them". |
| 1:21:33 | extracted |  | extracted | Write a few simple lines out and harmonize them |  |  |  |  |  |
| 1:22:36 | added |  | added | Simpler Demo c1 | star, take, chord exercise | Eb Blues \| 1 bar, 1 chord exercise | Melodic harmony | 1:22:37 Simpler Demo c1 |  |
| 1:22:37 | extracted |  | extracted | Simpler Demo c1 |  |  |  |  |  |
| 1:23:04 | extracted |  | extracted | Simpler Demo c2 |  |  |  |  |  |
| 1:23:04 | added |  | added | Simpler Demo c2 | chord exercise, star, take | Eb Blues \| 1 bar, 1 chord exercise | Melodic harmony | 1:23:04 Simpler Demo c2 |  |
| 1:23:09 | skill | 57 | x | Simpler demo |  |  |  |  | hallucinated caption |
| 1:23:30 | extracted |  | extracted | Simpler Demo c3 |  |  |  |  |  |
| 1:23:30 | added |  | added | Simpler Demo c3 | star, chord exercise, take | Eb Blues \| 1 bar, 1 chord exercise | Melodic harmony | 1:23:30 Simpler Demo c3 |  |
| 1:23:56 | skill | 58 | x | Breakthrough — 4 notes from anywhere |  |  |  |  | diarization - me talking is not useful |
| 1:24:06 | added |  | added | Going up exercise is a macro version of comping demo | chord exercise | Eb Blues \| 1 bar, 1 chord exercise | Melodic harmony | 1:24:08 Going up exercise is a macro version of demos |  |
| 1:24:08 | extracted |  | extracted | Going up exercise is a macro version of demos |  |  |  |  |  |
| 1:24:23 | skill | 59 | keep | Same top note, change chords underneath |  | Eb Blues \| 1 bar, 1 chord exercise | Melodic harmony |  |  |
| 1:24:48 | skill | 60 | x | Pennies — LH rootless voicings |  |  |  |  | close. Right clip is 1:25:05 / extracted 1:25:03 "Pennies 2 Note Rootless Voicings". |
| 1:25:03 | extracted |  | extracted | Pennies 2 Note Rootless Voicings |  |  |  |  |  |
| 1:25:05 | added |  | added | Pennies 2 Note Rootless Voicings | star, take, voicings | Eb Blues \| 1 bar, 1 chord exercise | Melodic harmony | 1:25:03 Pennies 2 Note Rootless Voicings | added/extracted title at 1:25:03. Prefer that over the nearby skill wording. |
| 1:25:45 | skill | 61 | x | Pennies rootless voicings |  | Eb Blues \| 1 bar, 1 chord exercise | Melodic harmony |  | if this was untagged, this would be helpful marker, but real tags are before and after |
| 1:26:45 | skill | 62 | note | Pennies 3 Note Rootless Voicings _(orig: Bigger voicings)_ | star, voicings, take | Eb Blues \| 1 bar, 1 chord exercise | Melodic harmony | 1:26:47 Pennies 3 Note Rootless Voicings | Use the added/extracted label at 1:26:47 "Pennies 3 Note Rootless Voicings". |
| 1:26:47 | extracted |  | extracted | Pennies 3 Note Rootless Voicings |  |  |  |  |  |
| 1:28:38 | skill | 63 | keep | Homework: LH, then solo not-so-slow; call-and-response | chord exercise | Eb Blues \| 1 bar, 1 chord exercise | Melodic harmony |  |  |

## Deleted added markers

Last `unmiss` wins. History stays in `labels.jsonl`.

| t | last label |
|---|---|
| 0:22 | Me performing pennies transcription |
| 3:20 | Performance recap |
| 55:42 | hear a line versus where's the uh limit |
| 1:18:54 | Jake demo — melody, harmonized |

## Export vs eval (copy timestamps)

Copy-timestamps (`apps/studio/ui/export.js`) is a **second fold** on this ledger:

- never drops `extracted` or live `added`
- drops `x` markers
- keeps `g` and taxonomy `keep` markers
- merges starts within 2s; extracted start+title win; **added beats skill** on time+label
- so 20:46 (`g`) and 21:18 (added) **both copy** (32s apart)
- 1:18:54 would have stolen 1:18:52 until it was deleted

## Pointers

- Session handoff: `docs/sessions/2026-08-16-1507-grok-studio-fable-lock.md` (`track: studio-workspace`)
- Store: `apps/studio/runs/YYW4Q1Nivg8-20260814-1248.json`, `apps/studio/labels.jsonl`
- Product: `docs/youtube-clip-marker-prd.md` (working tree, not HEAD), `docs/clip-schema.md`, `AGENTS.md`

