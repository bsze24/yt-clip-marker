---
date: 2026-08-19
revised: 2026-08-22 07:10 UTC
time: "16:56"
surface: claude-code-opus-5
project: yt-clip-marker
track: offline-capability
branch: zoom-export-ingest
commit: 5eb55d2f94c357b423eca292510ebb52bd3312d5
task: docs/coordination/CURRENT.md
---

# Session log — 2026-08-19 16:56 (claude-code-opus-5) — local-video-mode-and-field-fixes

## Project context
- PR 8 (local video mode) was specced, built, reviewed by Codex, fixed and **merged** to `main`
  at `71b9d82` during this session. `CURRENT.md` at this commit still reads as the PR 8 review
  spec with the baton on the reviewer — stale now that the PR is merged, and the wrap-up it
  calls for has not run.
- PR 9 (`zoom-export-ingest`) is five commits on top of `main`, all found by *using* PR 8 rather
  than reading it. Open on GitHub as #9, unpushed past `247f7b3` because the last four commits
  landed mid-flight with no service.
- Timestamps below are local at the time of the event, UTC+8 through 13:36. The machine is now
  UTC−7; the session spans a flight, which is also what the whole feature was built for.

## Summary
Built local video mode end to end — the studio now plays from disk and ingests without network —
took it through a full review cycle, merged it, and then spent the second half fixing what real
use exposed: a Zoom export whose transcript was never found, a rerun that could never pick up
late captions, a header that scrolled the run picker out of reach, a silently broken media
pointer, and `k` sticking where two cues share a second.

## What changed
- **PR 8, merged `71b9d82`** — `4b344d5` local video mode (`player.js` dual backend, `local.py`,
  `/media/` byte-range route, `n` key, media resolved on read); `c4de36d` `prefetch.py`;
  `fced73f` review fixes F18/F19; plus `6fbbb0a`, `2bc9e34`, `9880bde`, `51bb7d4` on the
  coordination docs and the PR-number correction.
- **PR 9, open** — `247f7b3` Zoom sidecar matching + captions on rerun; `b0c4dd3` gitignore raw
  exports; `4b3ee5d` header/layout; `cae20a2` missing-media warning; `5eb55d2` `k` sticking.
- **Uncommitted and deliberately so** (`AGENTS.md` rule 5): `labels.jsonl` carrying 52 added
  markers of real annotation work, six run files under `apps/studio/runs/`, and two Zoom
  transcript `.vtt`s under `docs/reference/`.
- Outside the repo: installed `curl_cffi` 0.15.0 into Homebrew's yt-dlp venv while diagnosing
  403s. It was not the cause and can be uninstalled.

## Decisions
- **Media is resolved on every read, never written into the run file.** A run gains offline
  playback because a matching file appeared in `media/` and loses it when the file goes; no
  history is rewritten either way. Keeps `runs/*.json` immutable per [[D-002]] and makes
  attaching a download to an existing YouTube run a rename, not an edit. Owed to `DECISIONS.md`.
- **Local wins over the embed whenever both exist**, so there is no mode for the user to
  remember or for the app to persist.
- **A local file with no YouTube identity keeps the field name `videoId`** with a
  filename-derived value, plus a new `source: "local"`. Readers test `source`, not the shape of
  the id, so the run filename, the `labels.jsonl` key and every existing reader are untouched.
- **Sidecar matching requires a `.` boundary after the stem.** Established fixing F18; when Zoom
  forced a second stem variant, the boundary rule was carried onto the variant rather than
  relaxed. Loosening it is how `Lesson 1.mp4` adopts `Lesson 10.vtt`.
- **Captions arriving after a zero-cue run was built write a NEW run**, and the tool names the
  superseded one. Runs are immutable and label events are keyed by run id, so they cannot follow
  an edit.
- **Byte ranges are a requirement, not an optimisation.** Without 206 responses Chrome can only
  seek inside its buffer, which makes the timeline useless on an hour-long lesson.

## Learning arc
- Asked for a question list, then immediately cut it to "only the breaking questions" — drawing
  the line between what genuinely needs a human decision and what an agent should just default
  and state.
- Sent me to research the Zoom transcript question rather than answering it or letting me guess.
  The answer (cloud-only, paid, opt-in) changed the build: zero-cue had to be a supported path,
  not a failure.
- Rejected the PR-number inconsistency I had rationalised away — "obviously a lot more
  substantial than the codex session log." Substance owns the number; my reason for leaving it
  was convenience dressed as caution.
- Spotted that the raw Zoom export beat the YouTube copy before I did — "I see a possible
  transcript." The upstream artifact carries speaker names and exists immediately; the derived
  one was still waiting on YouTube's ASR.
- Asked "do you have to update any references/pointers?" after renaming files, anticipating a
  broken indirection instead of waiting to hit it. It was broken, and the reasoning was exactly
  right about why.
- Diagnosed the `k` stick as "possibly another 2 same timestamps issue" before any investigation,
  and was correct — pattern-matched to a failure class from a prior session rather than
  describing symptoms.

## Concepts touched
- [concept] offline-blocker-inventory — solid — the two items that needed network (player,
  ingest) are both closed in code, and the feature was exercised in the air.
- [concept] displayed-time vs stored identity — solidifying — named the `k` stick as a duplicate
  timestamp problem unprompted; the twist he had not seen is that the collision was in the
  *origin* the keys walk from, not in the row identity, which was already correct.
- [concept] resolve-on-read vs write-back — emerging — accepted immediately for the media
  pointer, but the consequence surfaced later: a moved file silently degraded, because resolving
  on read means nothing complains when the answer becomes "none".
- [concept] artifact-boundary matching — emerging — prefix matching adopts neighbours silently;
  a `.` boundary admits real sidecars and excludes `Lesson 10.*`. Held under pressure when Zoom's
  naming tempted a second, looser rule.
- [concept] review-severity-vs-observed-harm — solidifying — both Codex findings were filed
  non-blocking with the reason measured on real data, and both turned out to matter within hours.

## Coaching hooks
- **Brian is now ahead of the investigation twice in one session** (duplicate timestamps, broken
  pointers after a rename). Ask him to predict the failure class before digging — his model of
  this system's failure modes is good enough to shortcut the search.
- **Reproduce before fixing, even when the code reading looks conclusive.** The `k` stick was
  fully explained by reading `navOriginIndex` — and the reading did not reveal that the paused
  case works fine and only the playing case sticks. Driving the poll→keypress loop directly
  produced the actual sequence.
- **Verify the recovery path, not just the happy path.** I told him twice to "delete the run and
  rerun" for late captions. That path was short-circuited by the download check and would not
  have worked. Recovery instructions need the same testing as the feature.

## Next / open threads
- Push `zoom-export-ingest`; only `247f7b3` is on the remote, the last four commits are local.
- Harvest PR 8's decisions into `DECISIONS.md` and reset `REVIEW.md` thread 4 — the PR merged
  without the `README.md` wrap-up running, so `CURRENT.md` and `REVIEW.md` both still describe it
  as under review.
- Decide on fractional cue starts. `build_cues` truncating to `int()` is the upstream cause of the
  `k` stick; storing fractions removes the collisions but changes the stored shape of every
  existing run, video 1 included.
- Two YouTube lessons (`glhvfs6OOOE`, `nWCc3xBSz-0`) still have zero cues — captions never
  arrived. Rerun `prefetch.py` when there is service, or export from Zoom if those exist.
- `dYT41doJw2I` is worth re-exporting from Zoom: 1832x872 native with a transcript, against the
  1280x610 copy downloaded from a still-processing upload.

## Open questions / blockers
- Do Zoom exports exist for the two Jake Sherman lessons, or are they YouTube-only?
- The known gap from the PR 8 handoff — "playback on an actually disconnected machine" — is now
  closed by use rather than by test: the Zoom run played in the air on intermittent service. No
  automated check covers it.

## Chronology (the record)

> **Chronology timestamp key:** All times are UTC. An unmarked minute is anchored to a recovered source event; `≈` marks a source-supported window or rounded prose boundary; `reconstructed` marks preserved ordering where the original source clock is unreliable.
- **2026-08-18 22:27 UTC** — Opens with the goal: local video mode, flight, no YouTube player. Asks for a
  one-shot build, interrupts himself, and asks for a question list to sharpen the spec instead.
- **2026-08-18 22:28 UTC** — I read `player.js`, `ingest.py`, `server.py`, `runs.js` and `clip-schema.md` first,
  then return 16 questions grouped by area, each with the default I would take.
- **2026-08-18 22:30 UTC** — "much shorter list, I have limited time. only the breaking questions." Cut to three:
  do the Zoom recordings have transcripts, which case is real on this flight, and are the files
  already downloaded.
- **2026-08-18 22:31 UTC** — Answers: not sure about transcripts, prefers YouTube if downloadable, "do your own
  research." Airport wifi for a couple more hours.
- **2026-08-18 22:32 UTC** — Web research settles it: Zoom audio transcripts are cloud-recording-only, paid plan,
  opt-in. Local recordings have none unless live-caption saving was on. So zero-cue has to be a
  first-class path.
- **≈2026-08-18 22:33–22:50 UTC** — Build. `local.py` (sidecar-aware run builder, VTT/SRT/json3 parsers with a
  rolling-window dedupe), byte-range `/media/` route with a name allowlist that deliberately does
  not `resolve()` symlinks, `resolve_run_media` computed per read, `player.js` split into two
  backends behind one interface, `n` to mark at the playhead, a synthetic composer row so a
  transcript-less run has somewhere to put the form.
- **2026-08-18 22:52 UTC** — Verified against a disposable copy of the store so the real `labels.jsonl` was never
  written: range/416/traversal probes, byte-for-byte `dd` comparison, transport keys, `n` at 0:27
  round-tripping to a `miss` event, run switching, auto-attach by video id and its removal.
- **2026-08-18 22:55 UTC** — Regression on the real store surfaced a bug I had introduced: deferring the IFrame
  API widened the window where the 250ms poll calls `getDuration()` on a null player. Guarded it
  and its siblings.
- **2026-08-18 23:07 UTC** — "assume I'll extract with yt-dlp." Wrote `prefetch.py`. Running it immediately found
  two real yt-dlp problems: `--sub-langs "en.*,en"` pulls auto-translated tracks and a 429 on the
  third killed the whole download; and the default player client `android_vr` lists every format
  then answers 403 for the stream. Narrowed the langs, made success artifact-based rather than
  exit-code-based, pinned `web_embedded,mweb`.
- **≈2026-08-18 23:20 UTC** — Chased the 403 down a wrong path first: installed `curl_cffi`, found yt-dlp silently
  ignores an unsupported version, installed a supported one, and the 403 persisted anyway. The
  player client was the real cause.
- **≈2026-08-18 23:30 UTC** — Same turn asked for the coordination-docs review cycle with roles reversed. Wrote
  `CURRENT.md` as the PR 7 spec with the three-part audit, `REVIEW.md` thread 4, `TD-11`/`TD-12`.
  Baton to the reviewer at `c4de36d`.
- **2026-08-18 23:58 UTC** — Codex filed F18 (sidecar prefix match adopts `Lesson 10.vtt`) and F19 (non-media
  `HEAD` writes a body, desynchronising an HTTP/1.1 keep-alive connection). Both non-blocking.
  Fixed both; F19 deliberately wider than asked, routing HEAD through the same dispatch as GET so
  every route is correct rather than the one branch reported.
- **2026-08-19 00:04 UTC** — "commit/push/pr to a new branch." Found two stale facts in `CURRENT.md` I had
  written myself — PR 4 already merged, wrong `main` SHA — and corrected them before pushing.
  Opened #8.
- **2026-08-19 00:07 UTC** — Flagged the PR-number mismatch as a footnote; he pushed back that substance should
  own the number. Renamed the spec and every reference, leaving the one "PR 7" that really does
  mean the Codex session-log PR, and the published commit titles.
- **2026-08-19 00:39 UTC** — PR 8 merged. Asks how to use the player, and whether ingesting after processing is
  all that's left.
- **2026-08-19 00:50 UTC** — Four YouTube URLs. Checked captions first: none of the four had any. Three of four
  were also still processing video, offering only 360p. Downloaded anyway (~820MB) since that is
  the slow half, and fixed `prefetch.py` so a rerun can pick up captions independently of the
  download — the old code short-circuited on the media file and my earlier recovery advice was
  therefore wrong.
- **2026-08-19 01:01 UTC** — "check out the files I dropped in docs/references/sample_video... I see a possible
  transcript." A full Zoom cloud export: video, audio, and a real 690-cue speaker-attributed
  transcript. Strictly better than the YouTube copy, and available immediately.
- **2026-08-19 01:03 UTC** — It did not work. Zoom names the video `..._Recording_640x360.mp4` and the transcript
  `..._Recording.transcript.vtt`; the stems do not match, so the flagship case for the whole
  feature silently produced an empty grid. Added `stem_variants` — strip a trailing `_{W}x{H}`
  and a browser `" (1)"` marker — keeping F18's `.` boundary on every variant. 688 cues, 26 gap
  rows.
- **2026-08-19 01:07 UTC** — Asks how to see it in the tool. Sent him to the dropdown, warning that two entries
  looked nearly identical.
- **2026-08-19 01:08 UTC** — Screenshot: no dropdown visible, and video 1 loaded instead. Not user error. The
  layout height was `calc(100% - 49px)`, a hardcoded one-row header; the header wraps at any zoom,
  the document became scrollable, and the grid's `scrollIntoView` carried the header off the top.
  Made the body a flex column and clipped `html`; capped the player column at 62vh after
  `minmax(0, auto)` turned out not to help, because an `auto` max still resolves to max-content.
- **≈2026-08-19 04:53–04:55 UTC** — Server had died between turns; restarted.
- **2026-08-19 05:00 UTC** — Second Zoom export dropped at `docs/reference/GMT20260712`. Ingested: 688 cues,
  8 gap rows. Both runs landing on exactly 688 was suspicious enough to check — coincidence, both
  raw VTTs have 690 and the dedupe drops 2. Generalised the gitignore to
  `docs/reference/**/*.mp4`, since the per-folder rule had already stopped covering the next drop.
- **2026-08-19 05:24 UTC** — "cleaned up file names... do you have to update any references/pointers?" Yes: the
  `media/` entry is a symlink and the rename left it dangling, so the run with 52 markers had gone
  to a black player. Repointed the symlink rather than re-ingesting, which would have minted a new
  run id and orphaned the markers. Then made the studio say so — `run_warnings` now reports a run
  that names media it cannot find, with the repoint command, and leads with "markers are intact"
  because that is the first question.
- **2026-08-19 05:36 UTC** — Reports `k` sticking at 33:38, guessing duplicate timestamps. Correct: two cues share
  start 2018, and this is systemic — 25 such pairs in one lesson, 64 in the other. Read the code,
  formed the theory, then drove the poll→keypress loop directly rather than trusting it: five
  presses, no movement. The cause is an interaction of three fine-alone behaviours — the playhead
  resolves to the *last* row at or before now, `j`/`k` take their origin from the playhead, and
  they seek the video to whatever they select. Fixed by preferring the selection when both sit on
  the same second. A second bug fell out: `j` had been silently skipping the first row of every
  duplicate pair.
- **2026-08-19 23:56 UTC** — Session log, written after landing. Machine clock has moved from UTC+8 to UTC−7.

## Banked artifacts

**Pre-flight prep, one command per video** (downloads media, `en-orig`/`en` captions as json3,
and `.info.json`, then ensures a run exists; idempotent):

```bash
python3 apps/studio/prefetch.py "https://www.youtube.com/watch?v=<id>" ...
```

**Check whether YouTube has generated captions yet** — the thing that gates everything above:

```bash
for id in dYT41doJw2I Oa0wqetkNcg glhvfs6OOOE nWCc3xBSz-0; do
  printf "%-12s " "$id"
  yt-dlp --list-subs --skip-download "https://www.youtube.com/watch?v=$id" 2>&1 \
    | grep -cE "^(en|en-orig) " | sed 's/^0$/none/;s/^[1-9].*/READY/'
done
```

**Ingest a Zoom export** — point at the `.mp4`, the transcript is found via stem variants:

```bash
python3 apps/studio/local.py "docs/reference/<folder>/<name>_Recording_640x360.mp4"
```

**Repoint a run's media after moving or renaming the source.** Keep the name on the right
unchanged — that is what ties the file to existing markers:

```bash
ln -sf "$(pwd)/docs/reference/<folder>/<file>.mp4" apps/studio/media/<existing-name>.mp4
```

**Re-derive the yt-dlp player client when 403s return.** It is a workaround with a shelf life:

```bash
yt-dlp --extractor-args "youtube:player_client=<client>" -F "<url>"
```

Prefer the client that both lists high formats and actually downloads. On 2026-08-19,
`web_embedded` did both; `mweb` downloaded but offered only 360p; the default `android_vr` listed
everything and served 403.

**resolve-on-read vs write-back** — the studio never stores which file a run plays. It works it
out fresh on every read from what is sitting in `media/`. Like checking the shelf each time you
need a book rather than keeping a card that says where you last put it: the card goes wrong the
moment someone moves the book, and it never tells you. It is NOT caching, and it is NOT a
database pointer — nothing is written down to go stale. The cost is the other half: when the
answer becomes "no file", nothing complains unless you make it, which is exactly the bug that
showed up at 13:24.
