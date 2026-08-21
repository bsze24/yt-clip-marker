# Current task

**Close the local-file loop: a run learns its YouTube id, media becomes disposable, the
uploads list loads itself, and the lesson is renamed in exactly one place.** Baton:
**→ implementer**.

Four phases, in order, because each needs the one before it. Phase 1 changes the clip
contract, so it wants a look before it lands. Phase 4 is a join between what phases 1 and 3
already build, not new machinery.

---

## 0. State as of 2026-08-21

**No PR is open.** Review-only PR #23 was closed rather than merged, which was its correct
disposition. PRs 24, 25 and 26 have since landed — the app-lifecycle repair, the move-safe app
bundle, and the same-origin guard. Working tree clean, tests 15/15.

Closed since the last spec: the skill eval (three videos scored, results in `BACKLOG.md`
"Skill eval"), `SKILL.md` v2 ([[D-040]]), and PRs 9-26 — Zoom ingest, export and eval repairs,
the `feel`/taxonomy changes, the launchd app surface, and work/lane section breaks.

Eval state and the roadmap moved to `docs/reference/EVAL.md`. Two decisions landed 2026-08-21
after this spec was written: [[D-042]] (markers flow app → YouTube only; the video title is the
one field flowing back) and [[D-043]] (use v2 for real before preserving held-out data,
superseding D-041's cadence).

## 1. Why this exists

Brian annotates a Zoom export locally, uploads the lesson to YouTube, and pastes the
timestamps into its description. After that the local video has no job. There is **1.1 GB** on
disk he cannot safely delete:

```
apps/studio/media/        783 MB   four YouTube downloads
docs/reference/GMT*/      368 MB   two Zoom exports, symlinked into media/
```

He cannot delete it because **the run holding the clips does not know the lesson exists on
YouTube**:

```
GMT20260730 local run:   videoId 'GMT20260730-155336_Recording_640x360-1'
                         url     ''
                         source  'local'
```

Delete that 193 MB file and its 75 clips are unplayable forever. Meanwhile `Oa0wqetkNcg` — the
same lesson, uploaded — is a *separate run* with the YouTube id, zero cues and zero clips. The
right halves are in two places.

That single missing link is also why the run picker shows seven entries when three are useful,
and why "is this safe to delete" has no answer. One field, not three features.

## 2. Phase 1 — a run learns its YouTube id

`runs/{id}.json` is immutable ([[D-002]]), so this goes where `work` went in PR 17: a label
event, latest wins, resolved on read. Extend the existing `verdict: "chapter"` event rather
than adding a second run-metadata event — one fold, one endpoint.

- `load_run_work` becomes `load_run_meta`, returning `{work, youtubeId}`. Existing `chapter`
  events carry no `youtubeId`; treat it as absent, not empty.
- `/api/run` returns it. Header gains a field beside `work`.
- **`player.js` falls back to the embed** when there is no local media and the run has a
  `youtubeId`. This is [[D-034]] in the other direction and is the whole point of the phase.
- **`run_warnings` stops nagging when a fallback exists.** Missing media *and* no `youtubeId`
  is still a warning. Missing media *with* one is silent — that is the normal end state.
- `docs/clip-schema.md` updates with the change, since it describes this code.

**Acceptance.** Set the id on the GMT20260730 local run, delete its media symlink, and the run
still plays — from YouTube — with its 75 clips intact and no warning. Restore the symlink and
it plays locally again without touching the run file.

## 3. Phase 2 — see what is on disk, and delete it safely

A panel listing, per run: the media file, its size, whether it is a symlink and where it
points, and whether a YouTube fallback exists.

- Delete is **enabled only when a fallback exists**. That is the guard the whole phase is for.
- A symlink and its target are different things. Deleting `media/x.mp4` when it is a symlink
  frees nothing — the 368 MB is in `docs/reference/`. Say which, and offer both, explicitly.
- Nothing here rewrites a run file. `resolve_run_media` already computes on every read
  ([[D-034]]), so removing a file is already reversible; this phase only makes it visible.

**Acceptance.** The panel's total matches `du`. Delete is disabled on a run with no fallback.
Deleting a symlink reports that the real file is still in `docs/reference/`.

## 4. Phase 3 — the uploads list loads itself, offline or not

Brian's channel is `@briansf24` and the lessons are **unlisted**, not private.
`yt-dlp --flat-playlist` lists them with no OAuth and no Data API — unlisted needs
`--cookies-from-browser`. That keeps [[D-005]] intact: yt-dlp is already the one external tool.

**The hard requirement is that this never blocks the app.** The studio opens on a plane. So:

1. The list is cached at `apps/studio/uploads.json` — id, title, duration, upload date.
2. On load the server serves the **cache immediately**, with its age.
3. A refresh runs on a background thread, never on the request path. When it lands, the picker
   updates.
4. No network, no yt-dlp, expired cookies, renamed channel: **keep the cache, show its age, log
   once.** No dialog, no error state, no retry storm. An empty cache shows nothing at all,
   which is the correct amount of noise.

**Acceptance, and the second one is the real test.** With network, a cold cache fills and the
picker offers uploads not yet ingested. **With the network off, the studio opens at the same
speed, shows the cached list with its age, and nothing in the console suggests a fault.**

## 5. Phase 4 — one rename, everywhere

The lesson gets its real name on YouTube, after upload. The studio should follow, and the
mechanism is already being built by phases 1 and 3:

```
run.youtubeId (phase 1) ──┐
                          ├── join ──► the current title
uploads.json  (phase 3) ──┘
```

Rename on YouTube, the background refresh lands, the picker and header show the new name. No
new endpoint, no new event type, no new store.

**The one real decision is precedence.** `runs/{id}.json` carries an immutable `title` from
ingest ([[D-002]]). Rule: the cached YouTube title wins when the run has a `youtubeId` *and*
the cache holds that id; otherwise the run file's `title`. Offline with a cold cache falls
back to the run title, which is the correct behaviour rather than a degradation.

**Direction is not a preference.** Pull (YouTube → studio) is the join above. Push (studio →
YouTube) needs the YouTube Data API and OAuth, which is parked under [[D-005]]. One direction
is nearly free; the other changes the project's dependency stance. Pull only.

Local-only runs that never reach YouTube keep their filename-derived title. Nothing to sync,
no warning.

**Acceptance.** Rename the lesson on YouTube. Without restarting the studio, the run's title
updates after the next background refresh. Kill the network and reopen: the studio shows the
last known title, with the cache's age, and logs nothing alarming.

## 6. Out of scope

Deleting or merging the duplicate runs. Once phase 1 lands, `Oa0wqetkNcg` and the local
GMT20260730 run are visibly the same lesson and the merge is obvious — but it destroys data,
so it is its own task with its own spec. Also out: the YouTube Data API, OAuth, and any
write-back to YouTube ([[D-005]], parking lot).

Also out, and now permanently rather than pending a spec: **flowing a renamed *marker label*
back from the YouTube description.** Markers move one way, app → YouTube ([[D-042]], accepted
2026-08-21). The reconciliation problem — match by timestamp, pick a winner when both sides
changed, handle a stamp deleted on YouTube — is closed, not deferred. Phase 4 covers the
lesson title only, and the title is the only field that moves YouTube → app.

## 7. Baton

**→ implementer.** Phase 1 first, and it changes `docs/clip-schema.md`, so Brian should see it
before phases 2, 3 and 4 build on it.

---

## Handoff notes

### 2026-08-21 — planner, scoping the local-file loop

- **Why one field and not three features.** Duplicate runs in the picker, unsafe cleanup, and
  the missing upload→annotate loop are the same defect seen from three angles: the run with the
  clips and the run with the YouTube identity are different objects. Phase 1 is small; phases 2
  and 3 are only sensible once it exists.
- **Why phase 3 is cheaper than it sounds.** The instinct was the YouTube Data API and OAuth,
  which is a dependency and a parking-lot item. `yt-dlp --flat-playlist` does it with the tool
  already in the stack. Checked: both `--flat-playlist` and `--cookies-from-browser` are
  present in the installed yt-dlp.
- **The offline requirement is a design constraint, not a nice-to-have.** PR 8 exists because
  the studio has to work on a plane. A synchronous network call on app load would undo that,
  which is why the cache is served first and the refresh never touches the request path.
- **What could make phase 2 dangerous.** It deletes the user's video files. The guard is that
  delete is disabled without a YouTube fallback, and the symlink-versus-target distinction is
  stated rather than assumed — deleting a symlink frees nothing, and a user who believes it did
  will delete the run next.

### 2026-08-21 — planner, adding phase 4

- **Why the rename is phase 4 and not its own task.** It needs `run.youtubeId` (phase 1) and
  `uploads.json` (phase 3) and adds nothing else. Specced separately it would read as new
  machinery; specced here it is a precedence rule over two existing fields.
- **Why pull and not push.** Brian asked "probably YouTube?" as the source of truth. Correct,
  but the deciding factor is that push needs the Data API and OAuth ([[D-005]]), while pull is
  a join. The two options are not comparable in cost.
- **The ambiguity that was flagged rather than assumed.** "Rename" could mean the lesson title
  or a marker label edited in the YouTube description. The first is phase 4; the second is a
  reconciliation problem and is named in §6. If Brian meant the second, phase 4 is mis-sized.

### 2026-08-21 — Codex, implementation-readiness review

**Assessment:** the dependency order and product direction are sound, and there is enough here
to propose a staged build plan. The task is not yet safe to implement end to end without making
several unstated choices. Phase 1 needs one reconciliation with the code that is now on `main`;
phase 2 needs destructive-action semantics; and phase 3 needs a real authenticated listing spike
before the title join can depend on it.

- **Phase 1 names a function that no longer exists.** §2 says `load_run_work` becomes
  `load_run_meta`, but PRs 21–22 replaced that shape with `load_sections` and timestamped
  `{work, lane}` breaks. `/api/section` is the one writer, and every write must preserve the
  complete pair — the exact regression F26 caught. Recommended reconciliation: one
  `load_run_meta` pass over `chapter` events returns `{sections, youtubeId}`. Section fields keep
  latest-event-per-`start` semantics; `youtubeId` changes only when that key is present, so an old
  event or an ordinary work/lane edit cannot erase it. An explicit empty string clears a link.
- **`youtubeId` needs an effective-value rule, not only a new event field.** The four downloaded
  runs already carry a real YouTube watch URL and 11-character `videoId`, while the two raw Zoom
  runs carry synthetic ids and empty URLs. Recommended precedence: an explicitly recorded
  `chapter.youtubeId` wins; otherwise parse the immutable run's YouTube URL; otherwise there is
  no fallback. That makes the existing downloads correctly deletable and lets the Zoom run gain
  a fallback without rewriting its run file. `/api/run` and `/api/runs` should expose this one
  resolved value, and `player.js`, warnings, cleanup and the title join should all consume it.
- **Phase 2's guard must live on the server.** A disabled button is presentation, not safety.
  At deletion time the server must resolve the exact run and media entry again, refuse the action
  without a YouTube fallback, and check every run that claims the same file. Inventory must use
  `lstat` so regular files, live symlinks and broken symlinks remain distinguishable. The response
  should report link size and target size separately; the total must define whether it means
  logical bytes or allocated bytes so "matches `du`" is reproducible.
- **Target deletion is still a product choice.** "Offer both" distinguishes unlinking
  `media/x.mp4` from deleting the file it points to, but does not say whether target deletion is
  permanent or recoverable, whether deleting the target also removes the link, or what confirmation
  names the exact outside-repo path. Set those semantics before writing the endpoint.
- **Phase 3 is the only technical go/no-go.** A public, unauthenticated
  `yt-dlp --flat-playlist` probe against `@briansf24` returned two public uploads and none of the
  four known lesson ids, so authenticated listing is load-bearing. The installed yt-dlp supports
  the named flags, but flag presence does not prove that the logged-in channel listing exposes
  unlisted owner uploads. Run one `--cookies-from-browser` spike and require it to return at least
  `Oa0wqetkNcg` before making this the source for phase 4. The probe also returned `upload_date=NA`
  without `youtubetab:approximate_date`; cache dates should therefore be nullable unless an
  approximate date is explicitly accepted.
- **The cache contract needs three small decisions.** Store `fetchedAt` alongside `items` rather
  than deriving age implicitly; write by temp-file + atomic replace so a killed refresh cannot
  corrupt the last good cache; and name a refresh/backoff cadence that satisfies "without
  restarting" without retrying every four-second UI poll. Recommended default: refresh once at
  server start and every 30 minutes, allow only one worker, and log once per failure episode while
  retaining the cache.
- **"Picker offers uploads" needs an interaction.** The current select assumes every option is a
  run id and immediately calls `openRun`. Recommended low-surprise behavior: render cached uploads
  in a separate option group; choosing an upload that has no run fills the existing Add video
  control, where Brian explicitly starts ingest. Do not make a picker selection launch a network
  ingest silently.

**Recommended build sequence — one reviewed PR per phase:**

1. **Spec repair and authenticated spike.** Record the effective-id rule, deletion semantics,
   cache schema/cadence and picker action here; verify the authenticated listing against a known
   unlisted lesson.
2. **Phase 1 PR — link and playback fallback.** Implement the combined metadata fold, header
   field, effective id in both read APIs, local-first player selection, warning suppression and
   `docs/clip-schema.md`. Add regression cases for old events, clearing, intrinsic YouTube URLs,
   and work/lane edits preserving the link. Stop for review before using the real file as the
   destructive acceptance fixture.
3. **Phase 2 PR — inventory and guarded cleanup.** Add symlink-aware inventory and totals, the
   server-enforced delete guard, explicit link/target actions and confirmations. Cover regular,
   symlink, broken-link and multiply-claimed-file cases with disposable files.
4. **Phase 3 PR — cache-first uploads.** Put yt-dlp invocation and cache parsing in a small
   testable module; serve cache synchronously and refresh it only on the background worker. Test
   with a fake yt-dlp executable for cold fill, retained-cache failure, atomic replacement,
   deduped refresh and offline startup; then do one browser check with real authenticated data.
5. **Phase 4 PR — one display-title join.** Resolve the title once on the server — cached
   YouTube title when the effective id is present, immutable run title otherwise — and use that
   value in the picker and header. Verify rename-without-restart, last-known-title offline, and
   cold-cache fallback.

**Process note.** `REVIEW.md` still describes PR 25 as a draft with the baton at reviewer, but
`b2a3943` is already an ancestor of `main` through the PR 24–26 repair range. Reset/harvest that
thread before implementation so the review ledger and this baton do not disagree.
