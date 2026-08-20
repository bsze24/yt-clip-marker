# Current task

**Review PR 9 — Zoom exports ingest, and reruns pick up late captions — clean at
`8a47c2b`.** Baton: **→ planner** to scope the next task.

Roles are reversed again for this round, same as PR 8 and for the same reason: Claude Code
implemented, **Codex reviews**. The code is written, committed and pushed on
`zoom-export-ingest`; nothing here asks anyone to rebuild it.

---

## 0. State as of 2026-08-19

| Item | Where | Status |
| --- | --- | --- |
| **PR 9 — Zoom export ingest** | `zoom-export-ingest`, `5eb55d2` | **under review**, this task |
| PR 8 — local video mode | merged `71b9d82` on `main` | closed; decisions harvested as [[D-034]]–[[D-038]] |
| PR 4 — video 1 store | merged `43c99dd` on `main` | closed |
| PR 3 | merged `5af3e13` | closed |
| PR 5 | `949cb7b` | closed, superseded — do not merge |
| PR 6 + `docs/remove-coordination-md` | `e158710` | **close, do not merge** — ~1,000 lines stale |

`main` is `d2ad793`. PR 9 branches from exactly that commit and carries **five product
commits** plus one duplicate session-log commit and one merge of `main` back in. The branch
head is `6ef767c`; the last product commit is `5eb55d2`. Verify before reviewing:

```bash
git merge-base --is-ancestor 5eb55d2 HEAD
git log --oneline main..zoom-export-ingest
```

**Why this exists.** Every one of the five commits is a defect found by *using* PR 8 on a real
flight, not by reading it. PR 8 shipped the offline path; PR 9 is what happened when the first
real Zoom export met it.

**BugBot did not run.** Seven attempts on PR #9, seven `usage limit reached` failures against
the Cursor spend cap. The automated pass that normally covers this repo produced nothing, so
this review is the only review PR 9 gets.

## 1. The task

Review `5eb55d2` per the `README.md` review loop. `docs/prs/pr-9-zoom-export-ingest.md` is the
spec — **but it is incomplete, and that is itself a finding worth confirming**: it describes
`247f7b3` and `b0c4dd3` only. Three of the five commits are undocumented there. Review the
diff, not the spec:

| Commit | What | Covered by the spec? |
| --- | --- | --- |
| `247f7b3` | Zoom sidecar stem variants; `prefetch.py` fetches subs independently of media and writes a **new** run when late captions arrive | yes |
| `b0c4dd3` | `docs/reference/**` media gitignored; `.aider*` added | partly — the `.aider*` line is not mentioned |
| `4b3ee5d` | Sticky header so the run picker stops scrolling out of reach | **no** |
| `cae20a2` | `run_warnings` reports a declared-but-missing media file | **no** |
| `5eb55d2` | `k` no longer sticks when playhead and selection share a second | **no** |

**Where to look hard.** Places this change could plausibly be wrong, not a generic checklist:

- `local.py` `stem_variants` / `find_sidecars` — this widens F18's matching surface, which is
  the exact thing F18 was filed about. The `.` boundary must hold on **every** variant, not
  just the bare stem. Construct the adversarial cases yourself rather than trusting the ones
  in the spec: `Lesson 1_640x360.mp4` against `Lesson 10.vtt`, a file that legitimately ends
  in `_1920x1080`, a name carrying both ` (1)` and a resolution suffix, and a stem that after
  stripping becomes empty or a prefix of a sibling.
- `prefetch.py` — subtitle fetching now runs independently of the media download, and a
  zero-cue run whose captions arrived later causes a **new** run file to be written. Check
  that the old run is never mutated ([[D-002]]), that the superseded run id is named in the
  output, and that this cannot fire repeatedly and mint a run per invocation. Idempotence was
  an acceptance criterion on PR 8; confirm it survived.
- `server.py` `run_warnings` — it now calls `resolve_run_media` on every warnings pass. Confirm
  that adding a second warning did not change the shape consumers read (`runs.js` renders the
  list), that a run with **both** faults reports both, and that a missing-media warning does not
  fire for a run that never declared media.
- `grid.js` `navOriginIndex` — the fix compares `dataset.start` between the playhead row and
  the selected row. `dataset.start` is a render snapshot ([[D-029]]); confirm it is populated on
  every row shape the grid builds, including the synthetic composer row and a
  description-only row, and that a missing/`NaN` value degrades to the old behaviour rather
  than to a stuck cursor. **This one needs a browser.** Reading the dispatcher is not checking
  it — see `README.md`, "Having the source files is not having the tab."
- `styles.css` — the header fix changes the page's scroll container. Check the grid's
  `scrollIntoView` still works, at a non-100% browser zoom (that is how it was found), and that
  the player column cap does not clip the composer at small viewport heights.
- The gitignore has a hole: `docs/reference/**/*.mp4|m4a|mkv|mov` covers 368 MB of media, but
  the `.transcript.vtt` files sit beside them untracked, so both export directories still show
  as `??`. Decide whether transcripts should be tracked reference or ignored; right now they are
  neither. Non-blocking by construction — the exposure is two small text files, not the media.

**Out of scope.** End collection, JSON export, in-app suggest, extension→studio handoff, the
copy-timestamps fold ([[D-022]]), `TD-11`, `TD-12`, and the whole tagging-schema path now on
the `BACKLOG.md` roadmap. None of it is in this diff.

## 2. Acceptance criteria

1. Pointing the ingest at a Zoom cloud export's `.mp4` finds the sibling
   `.transcript.vtt` and produces a run with real cues — and `Lesson 1.mp4` still adopts
   nothing.
2. `prefetch.py` on a video whose captions arrived after the media download leaves a new,
   cue-bearing run behind, names the superseded zero-cue run, and does not edit it.
3. A run whose `media` file has been moved or whose symlink dangles surfaces a warning naming
   the file and the repoint command, and still loads its captions and markers.
4. `k` and `j` step off a pair of cues sharing a start second instead of sticking, with follow
   on and with follow off.
5. The header and run picker stay reachable when the header wraps.
6. No regression on the YouTube path: video 1 loads with a clean console and its counts
   unchanged (64 markers · 21 added · 24 extracted · 1464 cues).

## 3. Baton

**→ implementer**, from `5eb55d2`. Two findings are open in `REVIEW.md` thread 5: F21 is
blocking (the grid collapses at a real small viewport); F20 is non-blocking (an exact
resolution-suffixed sidecar can lose to a normalized-base sibling). F22–F23 are optional
review/documentation polish.

---

## Handoff notes

### 2026-08-19 — implementer, PR 9 Zoom export ingest (`247f7b3` … `5eb55d2`)

Written up after the fact, from the session record at
`docs/sessions/2026-08-19-1656-claude-code-opus-5-local-video-mode-and-field-fixes.md`, by a
later session that did not write the code. Treat the receipts below as that log's claims,
recorded here so the reviewer knows what was and was not exercised. Where the log gives no
receipt, this note says so rather than inventing one.

- **Acceptance criteria and evidence.**
  (1) Verified on the real export: 688 cues with speaker attribution, 26 silence-gap rows,
  playing in the browser. A second export at `docs/reference/GMT20260712` gave 688 cues and 8
  gap rows; both landing on 688 was checked rather than assumed — the raw VTTs hold 690 each
  and the rolling dedupe drops 2. Regression-checked that `Lesson 1.mp4` adopts nothing and
  that `Talk_640x360.mp4` picks up `Talk.transcript.vtt` but not `Talk2.vtt`.
  (2) **No receipt in the log.** The defect is described precisely and the fix is stated, but
  no run of the late-caption path is recorded. Four of four videos hit the defect; whether the
  fix was exercised end to end is not written down. Review this one from the code.
  (3) Found by a real failure: renaming the export left the `media/` symlink dangling and a run
  carrying 52 markers went to a black player. Fixed by repointing the symlink rather than
  re-ingesting, which would have minted a new run id and orphaned the markers. The warning was
  then added so the next occurrence explains itself.
  (4) Reproduced and then driven directly rather than reasoned about: two cues share start
  2018, five presses of `k` produced no movement. Systemic, not a one-off — 25 such pairs in
  one lesson and 64 in the other. A second bug fell out of the same read: `j` had been silently
  skipping the first row of every duplicate pair.
  (5) Found from a screenshot, not a report — the run dropdown was off-screen because
  `calc(100% - 49px)` hardcoded a one-row header, the header wraps at non-default zoom, the
  document became scrollable and the grid's `scrollIntoView` carried the header off the top.
  Body is now a flex column with `html` clipped, and the player column is capped at 62vh
  because `minmax(0, auto)` did not help — an `auto` max still resolves to max-content.
  (6) **No receipt in the log** for a post-`5eb55d2` video-1 regression pass. PR 8's merge
  receipt covers video 1 at `fced73f`; four commits landed after that.

- **Assumptions.** (a) Stem variants were added rather than the `.` boundary relaxed — F18
  established that a bare prefix match lets `Lesson 1.mp4` adopt `Lesson 10.vtt`, and the
  boundary was carried onto each new variant instead. (b) Late captions write a **new** run
  rather than editing the old one, because runs are immutable ([[D-002]]) and label events are
  keyed by run id, so annotations cannot follow an edit. (c) The `k` fix prefers the selection
  over the playhead only when both sit on the same second, leaving follow behaviour otherwise
  untouched; the alternative — storing fractional cue starts — was rejected for this PR because
  it changes the stored shape of every existing run, and is filed as `TD-13`.

- **Skips and divergences.** The spec doc was never extended past the first two commits. The
  three later fixes are real product changes with no written spec, which is why §1 above tells
  the reviewer to work from the diff. Nothing was cut from what the spec does describe.

- **What nobody has checked.** A post-`5eb55d2` browser pass over the YouTube path, and the
  late-caption rerun end to end. Both are cheap for a reviewer with network and a tab.

Each turn appends here: role, surface, SHA, what was verified, assumptions made, anything
skipped. See `README.md`, "Before recording a SHA".

### 2026-08-19 — reviewer, PR 9 Zoom export ingest (`5eb55d2`)

- **Acceptance criteria and evidence.** (1) The two real local Zoom runs render with 688
  cues; one contains speaker attribution. A disposable adversarial fixture preserved F18's
  `Lesson 1_640x360.mp4` / `Lesson 10.vtt` boundary and the empty-normalized-stem case. It
  also exposed F20: an exact `Lecture_1920x1080.vtt` loses to `Lecture.vtt`. (2) A disposable
  late-caption fixture left the original zero-cue run byte-for-byte unchanged, printed its id,
  wrote one cue-bearing successor, and returned that successor without writing again on the
  next invocation. (3) Direct `run_warnings` exercise returned both
  `deprecated-run-key` and `missing-media` for a doubly faulty run, and no missing-media
  warning for a run with no declared `media`. (4) In the browser on video 2's real duplicate
  `1:42` pair, follow-on `k` moved the first cue to `1:41` while the playhead sat on the
  second; follow-off `j` moved from the second cue to `1:46`. (5) A 760×520 viewport kept the
  wrapped header fixed and the document unscrollable, but failed F21: the grid had 0px client
  height and the composer was inaccessible. (6) Video 1 loaded with no console errors and
  exactly 64 markers, 21 added, 24 extracted, and 1464 cues.
- **Checks.** `python3 -m compileall -q apps/studio`, `node --check` on the changed JS modules,
  and `git diff --check d2ad793..5eb55d2` passed. The browser was a local real-player pass,
  not a source-only inference.
- **Assumptions.** No new product choice made. F22 recommends ignoring raw `.vtt` source
  exports, because they are local reference artifacts (and full meeting transcripts), not
  product fixtures; Brian can choose to retain them intentionally instead.
- **Skips and divergences.** I exercised a wrapped narrow viewport, not an actual browser zoom
  control. That is enough to expose the stronger F21 failure, but the exact non-100%-zoom
  visual path remains unverified. I made no code changes and preserved all untracked runs,
  labels, source exports, and Aider files.

**Baton: → implementer** — address F21 before another review pass; F20 should travel with that
fix if practical. See thread 5 in `REVIEW.md`.
