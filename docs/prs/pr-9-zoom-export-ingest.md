# PR 9 — Zoom exports ingest, and reruns pick up late captions

Five defects found using PR 8 for real work on 2026-08-19, not by reading it. That is the
whole shape of this PR: one feature commit and four things that only appear when a real
Zoom export, a real dangling symlink and a real duplicate cue meet the code.

| Commit | What |
| --- | --- |
| `247f7b3` | §1 Zoom sidecar stem variants · §2 late captions write a new run |
| `b0c4dd3` | §3 gitignore |
| `4b3ee5d` | §4 sticky header |
| `cae20a2` | §5 missing-media warning |
| `5eb55d2` | §6 `k` sticks on duplicate cue starts |
| review round | §7 F20-F22 |

## 1. A Zoom cloud export's transcript was never found

Zoom writes one meeting as three files whose stems do not match:

```
GMT20260730-155336_Recording_640x360.mp4     video, with a resolution suffix
GMT20260730-155336_Recording.m4a             audio
GMT20260730-155336_Recording.transcript.vtt  transcript
```

`find_sidecars` matched siblings against the media file's own stem, so pointing the
ingest at the `.mp4` produced a **zero-cue run with the transcript sitting beside it**.
This is the flagship case for the feature — a Zoom recording with a real transcript —
and it silently produced the empty-grid fallback.

`stem_variants` now also tries the stem with a trailing `_{W}x{H}` and a browser
`" (1)"` duplicate marker removed. Deliberately narrow: F18 established that a bare
prefix match lets `Lesson 1.mp4` adopt `Lesson 10.vtt`, and the `.` boundary rule that
fixed it applies unchanged to every variant here. A file with neither suffix is
unaffected.

Verified on the real export: 688 cues with speaker attribution, 26 silence-gap rows,
playing in the browser. Regression-checked that `Lesson 1.mp4` still adopts nothing and
that `Talk_640x360.mp4` picks up `Talk.transcript.vtt` but not `Talk2.vtt`.

## 2. A rerun could never pick up captions that arrived later

`prefetch.py` skipped subtitle fetching whenever the media file was already present,
then returned early on the existing run. So a video downloaded before YouTube generated
its auto-captions stayed zero-cue permanently, and the documented recovery — delete the
run and rerun — did not work either, because the download short-circuit came first.

This is not an edge case. YouTube generates auto-captions well after a fresh upload is
watchable, so "download now, transcribe later" is the normal path for a video you just
uploaded. Four of four videos hit it.

`fetch_subs` now runs independently of the media download. If captions have appeared and
the existing run has zero cues, a **new** run is written rather than the old one being
edited — runs are immutable ingest output ([[D-002]]) and label events are keyed by run
id, so they cannot follow. The tool says which run is superseded and that deleting it is
safe only if nothing was annotated on it.

## 3. Raw exports were one careless `git add docs/` from being committed

`docs/reference/**/*.{mp4,m4a,mkv,mov}` is gitignored — ~368 MB of raw export sitting in a
docs directory. The rule is generalised across export folders rather than named per folder,
because the per-folder version had already stopped covering the next drop. `.aider*` is
ignored in the same commit for the same reason: it is tooling residue, not product.

## 4. The run picker scrolled out of reach

Reported as "no dropdown visible", from a screenshot rather than a bug report. The layout
height was `calc(100% - 49px)` — a hardcoded one-row header. The header wraps at any browser
zoom or narrow window, so the document became taller than the viewport, and the first time the
grid scrolled a selected row into view it carried the header off the top with it.

`body` is now a flex column with `html` clipped, so nothing can overflow the viewport. The
player column is capped because it sits in an `auto` grid row and `auto` resolves to
max-content — it would otherwise take the whole layout. `minmax(0, auto)` was tried first and
does not help: an `auto` maximum still resolves to max-content.

**Acceptance:** at a wrapped header the run picker stays reachable and the document does not
scroll. See §7 F21 — the first version of this cap was measured against the viewport instead of
the remaining space, which fixed the header and broke the grid.

## 5. A renamed export left a run pointing at nothing

Renaming the source file left `media/`'s symlink dangling, and a run carrying 52 markers went
to a black player with nothing on screen to say why. Repointing the symlink was the right
repair — re-ingesting would have minted a new run id and orphaned the markers ([[D-002]],
[[D-008]]).

`run_warnings` now reports a run that names media it cannot find, with the repoint command, and
leads with "markers are intact" because that is the first question anyone asks.

**Acceptance:** a run whose media has moved surfaces a warning naming the file and the command,
and still loads its captions and markers.

## 6. `k` stuck at 33:38

Reported as the cursor refusing to move, guessed as duplicate timestamps. Correct, and
systemic: `build_cues` truncates starts to whole seconds, and two cues share start 2018 — 25
such pairs in one lesson, 64 in the other, and zero problems on video 1, which is why it took
this long to surface.

Three individually reasonable behaviours combine into the trap: the playhead resolves to the
*last* row at or before now, `j`/`k` take their origin from the playhead, and they seek the
video to whatever they select. Fixed by preferring the selection over the playhead when both
sit on the same second. A second bug fell out of the same read — `j` had been silently skipping
the first row of every duplicate pair.

Storing fractional cue starts is the upstream fix and is deliberately **not** here: it changes
the stored shape of every existing run, video 1 included, so it is a migration rather than an
edit. Filed as `TD-13`.

**Acceptance:** `j` and `k` step off a pair of cues sharing a start second, with follow on and
with follow off.

## 7. Review round — F20, F21, F22

Codex reviewed `5eb55d2` and filed four findings; BugBot filed nothing (seven runs, seven
usage-cap failures), so that review was the only one.

- **F20 — an exact sidecar could lose to the normalized Zoom base.** §1 added the base stem to
  the candidate list, but subtitles were then ranked only by extension and language, so for two
  tied `.vtt` files the directory's lexical order decided. A real title ending in something
  resolution-shaped (`Lecture_1920x1080.mp4` beside both `Lecture.vtt` and
  `Lecture_1920x1080.vtt`) ingested the wrong transcript. Which stem matched now leads the
  ranking. The same ordering is applied to `.info.json` and `.description` for consistency, but
  it changes nothing observable there — the base stem is always a strict prefix of the exact
  one, so the previous last-write-wins already landed on the exact file.
- **F21 — the player cap starved the grid.** §4's cap was `62vh`, measured against the whole
  viewport while the header had already taken a slice of the same viewport. On the real video-2
  run at 760×520 the header took 170.8px, the player took 322.4px, and the caption grid was left
  at **zero** height — the header problem fixed and the annotation surface gone. The cap now
  lives on the grid track as a percentage, which resolves against the viewport *minus* the
  header, so the grid keeps at least 38% of what is actually left.
- **F22 — raw transcripts were neither tracked nor ignored.** §3 ignored the media but not the
  `.transcript.vtt` beside it, so both export folders still showed as `??`. Now ignored: these
  are raw source exports, and a curated parser fixture can be tracked deliberately elsewhere.
