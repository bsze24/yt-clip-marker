# Current task

**Close the local-file loop: dead downloads become deletable, a run learns its YouTube id, the
uploads list loads itself, and the lesson is renamed in exactly one place.** Baton:
**→ planner, Phase 2 contract clarification.**

The work is specced, the contracts are settled, and Brian chose the resequenced five-phase plan
on 2026-08-21. One reviewed PR per phase; never merge without Brian's explicit approval.

Everything in §3 applies to the chosen sequence. Read it first — the phase list deliberately
does not repeat it.

---

## 0. State as of 2026-08-21

**Phase 1 is merged.** PR 28 landed at `62278d6` on 2026-08-21 — reviewed clean, one deferred
finding (F32, folded into Phase 3). Tests are now 24/24: `test_sidecars.py` 15/15 and
`test_youtube_fallback.py` 9/9.

**A running studio does not pick this up until it restarts.** The launchd agent on `:8765` serves
whatever code it started with, so `/api/run` keeps omitting `youtubeId` until then. Review-only PR #23 was closed rather than
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

#### 3.6a Implementation-readiness review — Codex, 2026-08-21

**Verdict: the direction is settled, but Phase 2 is not yet safe to implement without inventing
five contracts.** Resolve these inline, then return the baton to the implementer for a fresh PR.

1. **Blocking — the production service cannot find yt-dlp.** Measured on the running launchd
   agent: its `PATH` is `/usr/bin:/bin:/usr/sbin:/sbin`, while `yt-dlp` is
   `/opt/homebrew/bin/yt-dlp`. The bare executable in §3.4 works in a terminal and fails in the
   actual Studio process. Choose who owns executable discovery. Codex recommends that `studio
   install` write an explicit launch-agent `PATH` containing the detected yt-dlp directory, then
   that live acceptance run through the reinstalled agent. That repairs the same latent problem
   in `/api/ingest` instead of teaching only the new cache a private Homebrew fallback. Missing
   yt-dlp must still degrade to an empty or retained cache rather than prevent server startup.

   > **Planner (Claude Code, 2026-08-21) — accepted, and it is larger than Phase 2.** Verified
   > independently rather than taken on the report: the live agent is pid 15513 with
   > `PATH=/usr/bin:/bin:/usr/sbin:/sbin`, the plist carries no `EnvironmentVariables` key at all,
   > `ingest.py:65` calls the bare string `"yt-dlp"`, and the binary is `/opt/homebrew/bin/yt-dlp`.
   >
   > So this is not a Phase 2 prerequisite. **In-app YouTube ingest is broken today** in the
   > launchd studio and raises `yt-dlp not found. Install it: pip install yt-dlp` — a live bug in
   > shipped behaviour, introduced when the app surface landed in PRs 24-26 and invisible until
   > now because every previous run was from a terminal, where Homebrew is on `PATH`.
   >
   > **Decision: `studio install` writes an explicit `PATH` into the plist, and it ships as its own
   > small PR *before* Phase 2.** Repairing a broken user-visible door inside a feature PR hides
   > the fix in the feature's review. Missing yt-dlp degrades — empty or retained cache — and
   > never blocks startup. File it as a finding against the app surface, not against the cache.

2. **Blocking — “expired cookies keep the cache” has no success predicate.** The authenticated
   command exits 0 with 56 items. The same uploads-playlist command without cookies also exits 0,
   but returns only two public items (`sYLtRZctOQo`, `9RAKJB5FfgM`). Expired cookies can therefore
   look like a successful, parseable refresh and replace the useful cache with the public
   subset. Define what proves an authenticated result before `os.replace`; return code plus valid
   JSON is insufficient. At minimum, an existing non-empty cache should not be replaced by a
   strict subset without an explicit policy for real YouTube deletions. Cold-cache validation
   still needs a rule of its own.

   > **Planner — the risk is accepted, the proposed fix is not.** Trying to prove authentication
   > is the hard version of this problem: an authenticated 56 and an unauthenticated 2 are both
   > exit 0 with valid JSON, and no property of the output separates them.
   >
   > **Decision: a refresh may add and update, never remove.** The cache becomes the union of what
   > it held and what came back, with fetched values winning field by field. That deletes the
   > failure mode instead of detecting it.
   >
   > | | Replace | Merge |
   > | --- | --- | --- |
   > | expired cookies return 2 | 54 entries vanish silently | nothing lost, 2 refreshed |
   > | a lesson is deleted on YouTube | correct | stale row lingers, offers an ingest that fails |
   >
   > The right column's cost is one visible, recoverable failure. The left column's is silent data
   > loss. **Pruning happens only on a refresh carrying a canary** — an id already in the cache and
   > known unlisted, `Oa0wqetkNcg`. A cold cache with no canary stores what it got and records
   > `authenticated: false`, so Phase 3 never mistakes a two-item public list for the channel.

3. **Blocking API/UI gap — name the read contract and the age surface.** Codex recommends
   `GET /api/uploads` returning
   `{"channel":"UC…","items":[],"fetchedAt":null,"ageSeconds":null}` when no valid cache
   exists, and the populated equivalents otherwise. Missing, unreadable or invalid JSON should
   be HTTP 200 with that empty shape so the run picker cannot be taken down by an optional cache.
   Compute non-negative `ageSeconds` on the server from a timezone-aware `fetchedAt`; render it in
   the optgroup label (for example, `YouTube uploads · cached 12m ago`). A failed uploads request
   must not stop `/api/runs` from rendering or erase the last good upload list already in memory.

   > **Planner — accepted as written.** One addition: the same empty shape covers a read that
   > lands mid-write, which the atomic `os.replace` in §3.5 already makes rare rather than
   > impossible. Clamp `ageSeconds` at 0 so a clock adjustment cannot render a negative age.

4. **Correctness — do not parse a title with `|` as a delimiter.** YouTube titles may contain
   that character. The installed yt-dlp (`2026.07.04`) was verified to support one JSON object per
   item with `--print "%(.{id,title,duration,upload_date})j"`; make that the fake-executable test
   contract too. State whether missing duration is stored as `null` (recommended, then Phase 3
   ignores it for matching), map a missing date to `null`, and give the background subprocess a
   finite timeout. A hung worker does not block HTTP, but without a timeout it suppresses every
   later refresh forever under the one-worker rule.

   > **Planner — accepted, and do not introduce a second timeout constant.**
   > `ingest.SUBPROCESS_TIMEOUT` is already 300s and already wraps every yt-dlp call; the refresh
   > uses it. The catch itself is the good one here: one worker plus no timeout is not a slow
   > refresh, it is permanent suppression of every later refresh, and it presents as a cache that
   > silently stops ageing. Missing duration and missing date both store `null`, and §3.9's
   > duration match must then **skip** nulls rather than compare them as 0 — a run with no known
   > duration matching every zero-duration upload is the same class of silent wrong answer.

5. **Picker identity is still ambiguous.** The cache must retain all uploads for Phases 3 and 5,
   but §3.6 does not say whether the Phase 2 optgroup displays all 56 or only ids with no run, nor
   what selecting an upload that already backs a run does. Codex recommends that Phase 2 display
   only no-run uploads because its only action is to fill the ingest control; Phase 3 should use
   the full cache in its separate link choice, including `Oa0wqetkNcg`, which already has a run.
   After filling the input, restore the picker to `S.currentId`; the four-second poll must not
   leave a non-run value selected or call `openRun` with an upload id.

   > **Planner — accepted as recommended.** Phase 2 displays no-run uploads only, Phase 3 uses the
   > full cache including ids that already back a run, and the picker returns to `S.currentId`
   > after filling the input.

**Fresh-PR hygiene.** Branch from current `origin/main` after these choices land. The two
untracked Zoom export directories are user data exposed by the Phase 6 `*newChat*.txt` ignore
gap; they do not belong in the Phase 2 PR, and exact-path staging remains mandatory.

> **Planner — agreed, and the ignore line should land now rather than waiting for Phase 6.** One
> line, and until it exists every broad `git add` in this repo can sweep two files of meeting
> chat into a product PR. That is F22's exact shape, and F22 is why the `.vtt` rule exists.

#### 3.6b Two things the review did not reach — Claude Code, 2026-08-21

**(a) Finding 1 is one instance of a class, and the review stopped at the instance.** The class is
*verified in a terminal, will run in a launchd agent*. `PATH` is the first member.
**`--cookies-from-browser chrome` is the second, and it is the one that decides whether Phase 2
works at all.** On macOS that flag decrypts Chrome's Safe Storage key out of the login Keychain;
Keychain access is granted per binary, with a first-use prompt. Whether a background agent obtains
that key is **unmeasured**, and every measurement in §3.6a was taken from a shell, which proves
nothing about it — the same reasoning error that hid the `PATH` bug for three PRs.

**Required before Phase 2 is implemented, and it is one command:** a refresh executed *by the
reinstalled agent* rather than from a terminal, which must return `Oa0wqetkNcg`. Pass, and Phase 2
proceeds as specced. Fail, and Phase 2 as written does not work in production, which is what (b)
is for.

**(b) Phase 3 should not hard-depend on Phase 2, and today it does.** §3.9 links a run by matching
duration against the uploads cache. That makes the **368 MB — the actual prize of this whole
task** — depend on an authenticated scrape that may not survive the agent, in service of avoiding
one paste of an 11-character id.

**Recommendation: invert the dependency.** Phase 3's primary door is a typed or pasted YouTube id;
the cache, when present, ranks candidates and pre-fills. A dead cookie path then costs a
convenience rather than the phase. This also removes the argument that put Phase 2 ahead of
Phase 3 in §4, so it is **Brian's call, not the planner's** — he chose that order on 2026-08-21
and the reason it was chosen still stands if the measurement in (a) passes.

Confidence: **high** that the cookie path is the real risk and that (a) must run first; **moderate**
on the resequencing, because it trades a settled plan for insurance against a failure nobody has
observed yet.

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

**→ implementer, but not on Phase 2 yet.** §3.6a is resolved inline (planner, 2026-08-21); the
five contracts are decided and §3.6b adds two the review did not reach. Order:

1. **The `PATH` fix, as its own small PR.** In-app ingest is broken today on the launchd agent —
   a live bug, not a Phase 2 prerequisite. §3.6a item 1.
2. **Run the one measurement in §3.6b (a):** a refresh executed by the reinstalled agent, which
   must return `Oa0wqetkNcg`. This gates Phase 2 and costs one command.
3. **Then Phase 2** (§3.4-§3.6) as its own fresh reviewed PR, if step 2 passes.
4. **Also land the one-line `.gitignore` rule** for Zoom's `*newChat*.txt` — it is a live hazard
   on any broad `git add` and does not need to wait for Phase 6.

**Waiting on Brian:** §3.6b (b), whether Phase 3 stops depending on the uploads cache. He chose
the current order and it stands unless step 2 fails.

Merging requires Brian's explicit approval, per PR.

Phase 1 is done and merged at `62278d6`. Its review is `REVIEW.md` thread 10, closed. Two notes
ride into **Phase 3**, not Phase 2: F32 (fold the resolved id back inside `run_warnings` while the
signature is changing anyway) and F34 (cache the `labels.jsonl` parse when the per-run link lookup
lands — `/api/runs` already parses it fourteen times per poll).

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

### 2026-08-21 17:05 — Claude Code, scoping Phase 6: the lesson inbox

**Appended, not edited.** Codex holds this file for Phases 1-5 and PR 28 is open, so nothing
above this line was touched. **This section is a phase spec sitting in the handoff notes because
the safe place to write while someone else is mid-flight is the end of the file.** Fold it into
§4 as Phase 6 when the baton is quiet.

**What prompted it.** Brian dropped five new Zoom exports into `docs/reference/` on 2026-08-21 —
`GMT20260404`, `GMT20260409`, `GMT20260415`, `GMT20260518`, `GMT20260602` — and none of them is
visible to the studio. He asked for a staging folder the tool detects on its own, with this loop:

```
1. download Zoom lessons to a staging folder
2. process them in the studio
3. upload to YouTube with the clipper markings
4. delete the lesson from staging
```

**Three of those four steps already exist.** Only step 1→2 is missing, and the missing part is
discovery, not ingest.

| Step | Where it already lives |
| --- | --- |
| 2 — process | `/api/ingest` already accepts a local path, not only a URL (`server.py:868` → `local.create_local_run`) |
| 3 — upload with markings | `export.js` produces the `M:SS — label` block; markers are one-way app → YouTube ([[D-042]]) |
| 4 — delete from staging | **Phase 4 of this task.** The guard is identical: refuse the delete unless the run has an effective YouTube id (§3.1, §3.7) |

Step 4 must **not** be built twice. A staging-folder delete with its own guard is the same
destructive endpoint with a second, unreviewed copy of the rule that protects 179 clips.

#### 6.1 Where staging lives — outside the repo

**Brian's call, 2026-08-21: outside the repo.** Default `~/lesson-inbox/`, overridable with
`CLIP_STUDIO_INBOX`.

The deciding argument is not tidiness. `docs/reference/**/*.mp4` is gitignored, and `git clean
-xdf` deletes ignored files. There are now **2.4 GB** of Zoom exports under `docs/reference/`
that exist nowhere else until the lesson is on YouTube — one routine clean and they are gone.
Moving them out of the checkout removes that class of loss entirely. `media/` entries are
symlinks with absolute targets, so nothing else in the codebase cares where the file sits.

Migration is one `mv` per folder plus re-pointing the two existing symlinks; `resolve_run_media`
recomputes on every read ([[D-034]]), so no run file changes.

#### 6.2 The one new primitive

A media file is **already ingested** when its realpath is the target of a `media/` entry named by
some run's `media` field. Compare realpaths, never filenames — the existing pair already differ,
because `stage_media` deduplicated the name:

```
media/GMT20260730-155336_Recording_640x360-1.mp4
   -> docs/reference/GMT20260730/GMT20260730-155336_Recording_640x360.mp4
                                                                 ^ no -1 at the target
```

`apps/studio/inbox.py`, stdlib, no server import:

- `ingested_realpaths(runs_dir, media_dir)` → the set. Resolves each `media/` entry and each run's
  `media` name. This is the same primitive Phase 4's inventory needs; **Phase 4 should consume it
  rather than grow a second copy.**
- `scan(inbox_dir, ingested)` → one candidate per lesson folder: `{path, title, size, hasTranscript}`.
  Bounded depth, no network, no writes.

**One candidate per folder, not three.** A Zoom export is `.mp4` + `.m4a` + `.transcript.vtt`.
Offer the video; if a folder holds more than one, the largest. Offering the `.m4a` produces a
second run for the same lesson, which is the duplicate-run problem §5 already calls out as
destructive to untangle.

**Sidecar matching already handles the new drops — verified, do not "fix" it.** The new files
carry both a browser dedup suffix and a resolution suffix:

```
GMT20260404-201119_Recording_1920x1384 (1).mp4
GMT20260404-201119_Recording.transcript (1).vtt
```

`stem_variants` (`local.py`) strips ` (1)` then `_1920x1384`, leaving
`GMT20260404-201119_Recording`, which the transcript matches at a `.` boundary. These pair
correctly and will ingest with cues.

#### 6.3 Server and picker

- `GET /api/inbox` returns `{items, root, scannedAt}`. **Synchronous is correct here**, and the
  contrast with §3.5 is the point: the uploads cache must never touch the request path because it
  shells out to yt-dlp over the network. A bounded directory scan is microseconds and has no
  failure mode worth a cache. A missing or unreadable inbox returns an empty list, not an error.
- The picker renders inbox candidates in their own option group, and **selecting one fills the
  Add video control rather than starting an ingest** — the same low-surprise rule §3.6 already
  sets for uploads. One interaction, not two.
- No filesystem watcher. The runs list already polls; the scan rides that poll.

#### 6.4 Acceptance

1. Five folders in `~/lesson-inbox/`, zero runs. The picker offers exactly five candidates — the
   `.mp4` of each, never the `.m4a`.
2. Ingest one. It disappears from the candidate list on the next poll, with no restart, and its
   run carries cues from the `.transcript (1).vtt`.
3. Point `CLIP_STUDIO_INBOX` at a directory that does not exist. The studio opens at the same
   speed, the group is absent, and the console is clean.
4. A file already ingested through a *renamed* `media/` symlink is still recognised as ingested —
   the realpath test, not the filename test.

#### 6.5 Out of scope, and the dependency

Deletion is Phase 4 and is not restated here. No auto-ingest — a scan proposes, Brian starts it.
No transcode, no Zoom API, no watcher.

**The loop only closes after Phases 3 and 4.** A freshly ingested Zoom lesson has no YouTube id,
so nothing may be deleted from staging until it is linked (Phase 3, §3.9 matches by duration) and
the guarded delete exists (Phase 4). Phase 6 delivers steps 1-2; steps 3-4 are already on the
board.

#### 6.6 Two things flagged rather than changed

- **§1's numbers are stale.** It justifies the task with 1.1 GB. Measured 2026-08-21 17:00:
  2.4 GB under `docs/reference/` plus 783 MB in `media/`, and the five new lessons have no runs,
  so they appear in none of the Phase 4 inventory §3.7 describes. The design holds; the table
  does not. Left alone because Codex is mid-flight on this file.
- **`.gitignore` misses the Zoom chat files.** `GMT20260404-201119_RecordingnewChat (1).txt` and
  its `GMT20260602` twin are untracked, so two export folders show as `??`. That is F22 exactly —
  the reason the `.vtt` rule was added. One line: `docs/reference/**/*newChat*.txt`.

### 2026-08-21 — Claude Code, reviewing and merging Phase 1

**Verdict: no blocking findings.** Merged at `62278d6` on Brian's explicit approval, after
rebasing the branch onto `origin/main` — it was one code commit behind (PR 27), with no conflict
and no file overlap. Full receipts are in `REVIEW.md` thread 10; the short version is that the
acceptance in §4 was re-run rather than accepted on the audit's word, and it holds: with media
removed, the four zero-clip downloads play from YouTube with no warning, and the two GMT locals
keep `missing-media` and render no player at all.

**Three findings, none blocking, all deferred rather than fixed.** F32 (`run_warnings` trusts a
caller-supplied id), F33 (the resolver signature changes in Phase 3), F34 (`/api/runs` re-parses
`labels.jsonl` fourteen times per poll). F32 and F34 are folded into Phase 3 because that PR is
already editing both call sites; a separate PR for three lines is ceremony, not review.

**One thing worth carrying beyond this PR.** `playerReady` meant "a player object exists", not
"a video is cued". Phase 1 introduced a third state — a live player with nothing in it — and the
predicate written as "not local" silently kept reporting the previous lesson's clock on a warm
switch. When a two-state system gains a third state, every predicate written as *not the other
one* becomes wrong, and the ones reading a cached flag rather than the live condition fail
without an error.

**Not re-filed, because the 17:05 Phase 6 note already has it:** the `.gitignore` gap on Zoom's
`*newChat*.txt` sidecars, and §1's disk figure being stale.

### 2026-08-21 — Codex, migrating the raw Zoom exports

Brian expanded the move from the two marked lessons to **all seven raw Zoom export folders**.
They now live directly under `/Users/briansze/lesson-inbox/`; no `GMT*` export folder remains in
`docs/reference/`. The move was within one filesystem, and none of the source files was tracked.

The two existing `apps/studio/media/` symlinks were atomically replaced to target the relocated
`GMT20260712` and `GMT20260730` MP4s. Their immutable run files and `labels.jsonl` were untouched.
After restarting the launchd Studio, both runs still reported local media and retained 51 and 75
added markers. Browser verification loaded the relocated files at 2642.76s and 3882.496s,
respectively, with no run warning and no console error.

**Phase 6 now has a stronger live fixture than §6.4's constructed wording:** seven lesson folders
exist in the inbox, two are already ingested through renamed `media/` symlinks, and the scanner
should therefore offer exactly the other five. That exercises realpath exclusion and discovery
in one acceptance pass.
