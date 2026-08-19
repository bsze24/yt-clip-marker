# PR 9 — Zoom exports ingest, and reruns pick up late captions

Two defects found using PR 8 for real work on 2026-08-19, not by reading it.

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

## Also

`docs/reference/sample_video/` media is gitignored. It is ~200 MB of raw export sitting
in a docs directory, one careless `git add docs/` from being committed.
