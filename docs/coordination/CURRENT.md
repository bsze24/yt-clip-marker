# Current task

**Close the local-file loop: dead downloads become deletable, a run learns its YouTube id, the
uploads list loads itself, and the lesson is renamed in exactly one place.** Baton:
**→ reviewer, Phase 1 / PR 28.**

The work is specced, the contracts are settled, and Brian chose the resequenced five-phase plan
on 2026-08-21. One reviewed PR per phase; never merge without Brian's explicit approval.

Everything in §3 applies to the chosen sequence. Read it first — the phase list deliberately
does not repeat it.

---

## 0. State as of 2026-08-21

**Draft PR 28 is open at `05a325c` for Phase 1.** Review-only PR #23 was closed rather than
merged, which was its correct disposition. PRs 24, 25 and 26 have since landed — the app-lifecycle
repair, the move-safe app bundle, and the same-origin guard. Working tree clean, tests 15/15
(`python3 apps/studio/tests/test_sidecars.py`).

Eval state and the roadmap live in `docs/reference/EVAL.md`. Two decisions landed 2026-08-21:
[[D-042]] (markers flow app → YouTube only; the video title is the one field flowing back) and
[[D-043]] (use v2 for real before preserving held-out data, superseding D-041's cadence).

**Step 0 completed 2026-08-21.** `REVIEW.md` thread 9 now records PR 24 at `9ae0345`, F30's
delivery at `02e0dfb`, both findings resolved and PR 23 closed, then collapses the thread per the
`README.md` wrap-up. The review ledger and this baton agree.

## 1. Why this exists, with the real numbers

Brian annotates a Zoom export locally, uploads the lesson to YouTube, and pastes the timestamps
into its description. After that the local video has no job. There is **1.1 GB** on disk he
cannot confidently delete:

```
apps/studio/media/        783 MB   four YouTube downloads
docs/reference/GMT*/      368 MB   two Zoom exports, symlinked into media/
```

Measured 2026-08-21:

| Run | Media | On disk | Clips | Cues | YouTube id today |
| --- | --- | --- | --- | --- | --- |
| `dYT41doJw2I` | real file | 347 MB | 0 | 0 | yes, in the run file |
| `nWCc3xBSz-0` | real file | 271 MB | 0 | 0 | yes, in the run file |
| `Oa0wqetkNcg` | real file | 102 MB | 0 | 0 | yes, in the run file |
| `glhvfs6OOOE` | real file | 101 MB | 0 | 0 | yes, in the run file |
| `GMT20260730…` | symlink | 0 MB here, 193 MB at target | 179 | 688 | **no** |
| `GMT20260712…` | symlink | 0 MB here, 175 MB at target | 87 | 688 | **no** |
| `YYW4Q1Nivg8` | none | 0 | 72 | 1464 | yes, in the run file |

**Two problems wearing one coat, and the table is what separates them.**

**The 783 MB is already safe to delete and nothing says so.** Those four runs hold zero clips,
zero cues and zero label events. Their run files already carry a real watch URL, so `loadVideo`
(`apps/studio/ui/player.js:212`) already falls through to the YouTube embed when the file is
gone. The only obstacle is `run_warnings` (`apps/studio/server.py:290`) shouting about a missing
file that has a working fallback. That is one condition, not a feature. **No new event field
frees a byte of it.**

**The 368 MB is the actual missing link.** The two GMT runs hold 266 clips between them and do
not know their lessons exist on YouTube:

```
GMT20260730 local run:   videoId 'GMT20260730-155336_Recording_640x360-1'
                         url     ''
                         source  'local'
```

Delete that 193 MB target and its 179 clips are unplayable forever. Their `media/` entries are
symlinks, so this is also the case where deleting `media/x.mp4` frees nothing.

**And two lessons are stored locally twice.** `Oa0wqetkNcg` (102 MB) is the same lesson as the
`GMT20260730` symlink target (193 MB); `glhvfs6OOOE` (101 MB) is the same as `GMT20260712`
(175 MB). 571 MB for two lessons.

## 2. Where these corrections came from

The first draft of this spec was reviewed by Codex on 2026-08-21 for implementation readiness,
then checked against the code and the live data by Claude Code. Both passes are folded into §3.

- **Codex found:** the spec named `load_run_work`, which PRs 21–22 replaced; the effective-id
  rule was missing; the phase 2 guard was specified as UI state rather than server enforcement;
  the cache contract had no `fetchedAt`, no atomic write and no cadence; the picker interaction
  was undefined; the review ledger was stale.
- **Claude Code found:** folding the id into the `chapter` verdict silently deletes the lesson's
  work label; the uploads URL in the spec returns only public videos and the fix is a different
  URL, not different flags; `player.js` cues the synthetic id at YouTube today; and phase 1 as
  written frees none of the 783 MB it was justified by.

## 3. Contracts

### 3.1 Effective YouTube id

One server-side resolver, consumed by the player, the warnings, the cleanup guard and the title
join. Precedence:

1. the latest `verdict: "link"` event for the run that carries a `youtubeId` key — an explicit
   empty string clears the link;
2. otherwise the 11-character id parsed out of the immutable run's `url`;
3. otherwise none.

Rule 2 is what makes the four downloads deletable without writing a single event. Rule 1 is what
lets the Zoom runs gain a fallback without rewriting their run files ([[D-002]]). `/api/run` and
every row of `/api/runs` expose the one resolved value as `youtubeId`.

### 3.2 The link event is its own verdict

The first draft said to extend `verdict: "chapter"` — "one fold, one endpoint". That is a
data-loss bug. `load_sections` (`server.py:198`) deletes the section break at `start` when work
and lane are both empty:

```python
if work or lane:
    by_start[start] = {"work": work, "lane": lane}
else:
    by_start.pop(start, None)
```

So a link written as `verdict: "chapter"`, `start: 0`, `work: ""`, `lane: ""` erases the
lesson-level work label that `runs.js:88` reads back into the header field:

| Before | Event written | After |
| --- | --- | --- |
| sections `[[0, "Pennies From Heaven", "comping"]]` | chapter @ 0, id set, work/lane blank | sections `[]` |

Write instead:

```json
{"schemaVersion":2,"recordedAt":"…","runId":"…","verdict":"link",
 "youtubeId":"Oa0wqetkNcg","source":"human-link"}
```

Latest event per run wins ([[D-008]]). **Two regression tests are mandatory:** writing a link
leaves `load_sections` byte-identical, and writing a section leaves the effective id unchanged.
Codex's guard protected the id from section edits; this is the other direction of the same
collision.

### 3.3 Player and warnings

- **`player.js` must be handed the effective id, never `run.videoId`.** Today a GMT run whose
  symlink breaks cues `GMT20260730-155336_Recording_640x360-1` at YouTube and renders "video
  unavailable" — the false symptom recorded in `docs/sessions/2026-08-21-1241-…`. A run with no
  media and no effective id must show the warning, not attempt a broken embed.
- **`run_warnings` keeps `missing-media` only when there is no effective id.** Missing media with
  a fallback is the normal end state and must be silent.
- `docs/clip-schema.md` rides in whichever PR changes this behaviour — `main` must not document
  software that does not exist yet.

### 3.4 The uploads listing — URL, not flags

Verified 2026-08-21. The spec's original URL fails and no flag combination rescues it:

| URL | Cookies | Result |
| --- | --- | --- |
| `@briansf24/videos` | none | 2 public videos |
| `@briansf24/videos` | Chrome | 2 public videos — identical |
| `playlist?list=UU5waNKHe9sqmnjPG78qyjRw` | none | 2 public videos |
| `playlist?list=UU5waNKHe9sqmnjPG78qyjRw` | Chrome | **56 uploads, all five known lesson ids** |

The channel `/videos` tab never lists unlisted uploads, even for the owner. The uploads playlist
does: take the channel id `UC5waNKHe9sqmnjPG78qyjRw` and swap the `UC` prefix for `UU`. Cookies
are required. This keeps [[D-005]] intact — yt-dlp is already the one external tool, and no Data
API or OAuth enters the stack.

```
yt-dlp --flat-playlist --skip-download --cookies-from-browser chrome \
       --extractor-args "youtubetab:approximate_date" \
       --print "%(id)s|%(title)s|%(duration)s|%(upload_date)s" \
       "https://www.youtube.com/playlist?list=UU5waNKHe9sqmnjPG78qyjRw"
```

Durations are exact. **Dates are approximate and must be labelled as such** — `dYT41doJw2I` and
`Oa0wqetkNcg` were uploaded on different days and both report `20260820`. Without the
`approximate_date` extractor arg every date is `NA`, so the field is nullable either way.

### 3.5 The cache contract

**The hard requirement is that this never blocks the app.** The studio opens on a plane. PR 8
exists for that reason and a synchronous network call on load would undo it.

1. Cache at `apps/studio/uploads.json`:
   `{"fetchedAt": iso8601, "channel": "UC…", "items": [{"id", "title", "duration", "uploadDate",
   "dateApproximate": true}]}`. Store `fetchedAt` explicitly rather than deriving age from mtime.
2. The request path reads the file and returns it with its age. yt-dlp is never invoked on a
   request thread.
3. Refresh at server start and every 30 minutes, on a background thread, **one worker at a time**
   — the UI polls every four seconds and must not be able to stack refreshes.
4. Write temp file then `os.replace`, so a killed refresh cannot corrupt the last good cache.
5. No network, expired cookies, renamed channel: keep the cache, show its age, log once per
   failure episode. No dialog, no error state, no retry storm. An empty cache shows nothing at
   all, which is the correct amount of noise.
6. Gitignore `uploads.json`. It is derived, and a tracked copy would produce a diff every 30
   minutes.
7. Put the yt-dlp call and the parse in a small module so a fake `yt-dlp` executable can drive the
   tests: cold fill, retained cache on failure, atomic replacement, deduped refresh, offline start.

### 3.6 Picker interaction

Cached uploads render in their own `<optgroup>`. Choosing an upload that has no run fills the
existing Add video control, where Brian explicitly starts the ingest. **A picker selection must
never launch a network ingest** — the current `runs.js` select assumes every option is a run id
and calls `openRun` immediately.

### 3.7 Inventory and guarded cleanup

A panel listing, per run: the media entry, whether it is a regular file, a live symlink or a
broken one, its size, the target path and target size when it is a link, and whether an effective
id exists.

- **Inventory uses `lstat`**, so the three cases stay distinguishable. Report link size and target
  size as separate numbers. Totals are logical bytes, stated in the panel, so "matches `du`" is
  reproducible.
- **The guard lives on the server.** A disabled button is presentation, not safety. At delete time
  the server re-resolves the run and the media entry, refuses without an effective id, and refuses
  when any other run resolves to the same file.
- **Two named actions, because a symlink and its target are different things.** *Unlink* removes
  `media/x.mp4` only; when it is a symlink it reports that 0 bytes were freed and names the target
  path. *Delete target* removes the file the link points to, then the link.
- **Both move to `~/.Trash` via `shutil.move`, not `unlink`** — recoverable, stdlib, no
  dependency, numeric suffix on name collision. The refuse-without-fallback rule is then a second
  layer rather than the only one.
- Confirmation names the absolute resolved path. `resolve_run_media` already recomputes on every
  read ([[D-034]]), so removing a file changes no run file.
- Test with disposable files: regular, live symlink, broken symlink, and one file two runs claim.

### 3.8 The title join

Resolve one display title **on the server** and use that value in the picker and the header. Rule:
the cached YouTube title wins when the run has an effective id and the cache holds that id;
otherwise the run file's immutable `title`. Never written back to the run file. Offline with a
cold cache falls back to the run title, which is correct behaviour rather than a degradation.

**Direction is not a preference.** Pull (YouTube → studio) is the join above. Push needs the
YouTube Data API and OAuth, parked under [[D-005]]. One direction is nearly free; the other
changes the project's dependency stance. Pull only. Local-only runs keep their filename-derived
title, with nothing to sync and no warning.

### 3.9 Linking by duration, not by typing

Once the cache exists, the link is a choice rather than a paste. Match the uploads-list duration
against the run's last cue:

| Run | Last cue | Upload | Duration |
| --- | --- | --- | --- |
| `GMT20260730…` | 3870 s | `Oa0wqetkNcg` | 3883 s |
| `GMT20260712…` | 2640 s | `glhvfs6OOOE` | 2643 s |

Both are unambiguous against 56 candidates. A free-text id entry stays available for the offline
case.

### 3.10 Fixtures

Do every destructive acceptance on the four zero-clip runs first. The two GMT runs hold 266 clips
between them and are not fixtures.

## 4. Chosen sequence — resequenced, five phases

Ordered by disk freed per line of code. Phase 1 frees 783 MB with a warning condition; the phase
that adds the new event field comes after the cache that makes it usable.

| # | Phase | Contracts delivered | What it frees |
| --- | --- | --- | --- |
| 1 | Warning suppression + effective id | §3.1 rule 2, §3.3 | 783 MB, deleted by hand |
| 2 | Uploads cache | §3.4, §3.5, §3.6 | nothing yet |
| 3 | The link event | §3.1 rule 1, §3.2, §3.9 | makes the 368 MB disposable |
| 4 | Inventory and guarded delete | §3.7 | the 368 MB, safely, in-app |
| 5 | Title join | §3.8 | — |

**Phase 1 acceptance.** Move the four zero-clip `.mp4`s out of `media/`. All four runs still play
from YouTube, the picker's `⏏` marks clear, and no warning appears. Break the GMT20260730 symlink:
the warning appears and the player does not attempt an embed. Restore both and behaviour is
unchanged without touching any run file.

**Phase 2 acceptance, and the second one is the real test.** With network, a cold cache fills and
the picker offers the uploads with no run yet. **With the network off, the studio opens at the
same speed, shows the cached list with its age, and nothing in the console suggests a fault.**

**Phase 3 acceptance.** Link the GMT20260730 run to `Oa0wqetkNcg` from the candidate list. Repoint
its symlink at nothing and the run still plays — from YouTube — with all 179 clips intact and no
warning. Set the lesson's work label, write the link, and confirm the work label survives. Restore
the symlink and it plays locally again.

**Phase 4 acceptance.** The panel's total matches `du`. Delete is refused server-side on a run
with no effective id even when the request is issued directly. Unlinking a symlink reports 0 bytes
freed and names `docs/reference/…`. A deleted file is in `~/.Trash`.

**Phase 5 acceptance.** Rename the lesson on YouTube. Without restarting the studio, the title
updates after the next background refresh. Kill the network and reopen: the last known title, with
the cache's age, and nothing alarming in the console. Cold cache offline falls back to the run
title.

## 5. Out of scope

Deleting or merging the duplicate runs. Once the link lands, `Oa0wqetkNcg` and the local
GMT20260730 run are visibly the same lesson and the merge is obvious — but it destroys data, so it
is its own task with its own spec. Also out: the YouTube Data API, OAuth, and any write-back to
YouTube ([[D-005]], parking lot).

Also out, and now permanently rather than pending a spec: **flowing a renamed *marker label* back
from the YouTube description.** Markers move one way, app → YouTube ([[D-042]], accepted
2026-08-21). The reconciliation problem — match by timestamp, pick a winner when both sides
changed, handle a stamp deleted on YouTube — is closed, not deferred. The title join covers the
lesson title only, and the title is the only field that moves YouTube → app.

## 6. Baton

**→ reviewer.** Review Phase 1 at PR 28 / `05a325c`. Merging requires Brian's explicit approval.

---

## Handoff notes

### 2026-08-21 — planner, scoping the local-file loop

- **Why one field and not three features.** Duplicate runs in the picker, unsafe cleanup, and the
  missing upload→annotate loop are the same defect seen from three angles: the run with the clips
  and the run with the YouTube identity are different objects.
- **Why the uploads list is cheaper than it sounds.** The instinct was the YouTube Data API and
  OAuth, which is a dependency and a parking-lot item. `yt-dlp --flat-playlist` does it with the
  tool already in the stack.
- **The offline requirement is a design constraint, not a nice-to-have.** PR 8 exists because the
  studio has to work on a plane.
- **What makes the cleanup phase dangerous.** It deletes the user's video files. The guard is that
  delete is refused without a YouTube fallback, and the symlink-versus-target distinction is
  stated rather than assumed — deleting a symlink frees nothing, and a user who believes it did
  will delete the run next.

### 2026-08-21 — planner, adding the rename

- **Why the rename is last and not its own task.** It needs the effective id and the uploads
  cache and adds nothing else. Specced separately it would read as new machinery; specced here it
  is a precedence rule over two existing fields.
- **Why pull and not push.** Brian asked "probably YouTube?" as the source of truth. Correct, but
  the deciding factor is that push needs the Data API and OAuth ([[D-005]]) while pull is a join.
  The two options are not comparable in cost.
- **The ambiguity that was flagged rather than assumed.** "Rename" could mean the lesson title or
  a marker label edited in the YouTube description. The first is the title join; the second is a
  reconciliation problem and is closed in §5.

### 2026-08-21 — Brian, choosing the build order

Candidate A accepted. The cache and duration-matched choice land before the link event; guarded
cleanup follows only after that stronger identity check exists. Candidate B is deleted rather
than retained as a second source of implementation order. Baton → implementer, Phase 1.

### 2026-08-21 — Codex, implementation-readiness review

The dependency order and product direction are sound. The task was not yet safe to implement end
to end without making several unstated choices: the metadata fold needed reconciling with the code
now on `main`, the cleanup phase needed destructive-action semantics, and the uploads listing
needed a real authenticated spike before the title join could depend on it. All six findings are
folded into §3 — `load_sections`, the effective-value rule, the server-side guard, `lstat`
inventory, the cache contract, and the picker interaction — along with the process note that
became §0's step 0.

Codex's recommended build sequence was one reviewed PR per phase in the original numbering, which
is candidate B.

### 2026-08-21 — Claude Code, verification pass over the review

Checked every claim against `main` and the live store. Codex's code facts hold. Four things were
still wrong or open:

- **The `chapter` fold deletes the work label** (§3.2). Codex's guard covered one direction of a
  two-way collision.
- **The authenticated listing is a go, and the spec's URL was wrong** (§3.4). Codex correctly
  called this the only technical go/no-go and left it open; the spike ran. `@briansf24/videos`
  returns two public videos with or without cookies. The `UU` uploads playlist with cookies
  returns 56 uploads including all five known lesson ids.
- **`player.js` cues the synthetic id at YouTube today** (§3.3). This is live, not hypothetical —
  it is the "unavailable YouTube video" symptom in the 12:41 session log.
- **The original phase 1 frees none of the 783 MB it was justified by** (§1). That finding is what
  produced candidate A.

Also recorded: the duplicate storage is 571 MB across two lessons, not just a picker annoyance;
and duration matching (§3.9) makes the link selectable rather than typed.

### 2026-08-21 — Codex, implementing Phase 1

Draft PR 28 is open at `05a325c`. No merge was performed.

**Acceptance audit, criterion by criterion.**

- One URL-evidenced identity now serves both read APIs: `effective_youtube_id` validates known
  YouTube hosts and 11-character ids (`server.py:278`), while `/api/runs` and `run_payload`
  expose it as `youtubeId` (`server.py:631,649-654`). Tests cover watch, short, live and embed
  URLs, a foreign host, a synthetic local id, and even a valid-shaped id without a URL
  (`test_youtube_fallback.py:16-48`).
- The player receives only that resolved value (`runs.js:115`). With no local file and no
  effective id, its readiness and time controls stay inert and it hides and clears any prior
  iframe (`player.js:113,229-244,325-360`). This last transition was found in the browser: the
  first implementation refused the new cue but visibly retained the previous lesson.
- Missing declared media is silent only when the same resolver found a fallback
  (`server.py:313`). Tests cover both halves and both API surfaces
  (`test_youtube_fallback.py:51-126`).
- Live acceptance used the real disposable fixtures. Moving all four zero-clip MP4s to a
  temporary directory cleared their picker `⏏` marks; all four opened the YouTube player with
  no warning. Moving only the GMT20260730 symlink produced `missing-media` and, after the stale
  iframe repair, no visible player. All five entries were restored; both GMT entries again show
  `⏏`, local playback returned, and no run file changed.
- The API contract rides in this PR at `docs/clip-schema.md`; local playback documentation was
  corrected in `apps/studio/README.md`.

**Assumptions.** URL evidence means a recognized YouTube host, not an 11-character
`run.videoId`: local filenames can accidentally have the right shape. Local media retains
precedence. The empty backend is represented by a hidden, inert YouTube container rather than a
third player mode; that keeps the two-backend interface intact while preventing stale playback.

**Skips and divergences.** The 783 MB was moved out only for acceptance and then restored, not
permanently deleted; Phase 1 makes manual deletion safe but does not authorize deleting Brian's
files. No immutable run or label data changed. Upload cache, link event, inventory/delete and
title join remain Phases 2-5. No extension or annotation-keyboard loop was exercised because this
PR changes only Studio identity and playback selection.

**Verification.** `python3 apps/studio/tests/test_sidecars.py` (15/15),
`python3 apps/studio/tests/test_youtube_fallback.py` (9/9), `python3 -m py_compile` over the three
Studio Python entry modules, `node --check` over every `apps/studio/ui/*.js`, and
`git diff --check`. Browser half: real Studio run switching, four fallback runs, broken local-only
symlink, restored local playback, and a clean normal-path console; the deliberate broken-media
case logged its existing visible warning as expected.
