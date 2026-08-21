# Current task

**Close the local-file loop: a run learns its YouTube id, media becomes disposable, and the
uploads list loads itself.** Baton: **→ implementer**.

Three phases, in order, because each needs the one before it. Phase 1 changes the clip
contract, so it wants a look before it lands.

---

## 0. State as of 2026-08-21

No product PR is open. Review-only PR #23 is open against the already-merged appification range
`5c0c64d..97c0f22`; it must be closed, never merged, when `REVIEW.md` thread 9 lands. `main`
contains the latest product merge, PR #22 at `8d57e37`.

Closed since the last spec: the skill eval (three videos scored, results in `BACKLOG.md`
"Skill eval"), `SKILL.md` v2 ([[D-040]]), and PRs 9-22 — Zoom ingest, export and eval repairs,
the `feel`/taxonomy changes, the launchd app surface, and work/lane section breaks.

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

## 5. Out of scope

Deleting or merging the duplicate runs. Once phase 1 lands, `Oa0wqetkNcg` and the local
GMT20260730 run are visibly the same lesson and the merge is obvious — but it destroys data,
so it is its own task with its own spec. Also out: the YouTube Data API, OAuth, and any
write-back to YouTube ([[D-005]], parking lot).

## 6. Baton

**→ implementer.** Phase 1 first, and it changes `docs/clip-schema.md`, so Brian should see it
before phases 2 and 3 build on it.

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
