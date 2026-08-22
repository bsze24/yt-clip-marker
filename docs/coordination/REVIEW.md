# Review

Active target: **thread 14** (PR 31, `8eab5e7`) — reviewed 2026-08-22, no blocking findings, baton with the implementer. **Thread 11** stays open for F36/F37. Thread 13 closed after PR 30 merged at `9622365`; its non-blocking
F38 and F39 are deferred as TD-17 and TD-18. Thread 11's F35 is **resolved** — PR 29 merged at
`255739f` on 2026-08-22 — while the two non-blocking findings it recommended folding in,
**F36 and F37, remain open against `main`**. Thread 10 closed
2026-08-21 — Phase 1 reviewed clean and merged at `62278d6`; its one finding, F32, is deferred
into Phase 3 by Brian's call. Threads 1-9 remain closed. Durable outcomes live in `DECISIONS.md`
and `BACKLOG.md`.

### Where the open findings land — assigned 2026-08-22

`CURRENT.md` §4 recut the PR sequence, so every open item now has a home rather than a status.

| Item | Thread | Lands in |
| --- | --- | --- |
| F31 — `score_run.py` crashes instead of refusing on a run with no human rows | 7 | **PR E**, with the `annotated` proxy fix |
| F36 — `stale_plist` sees a stale path, not a stale PATH | 11 | **PR E** |
| F37 — the finder looks in Homebrew while three places advise pip | 11 | **PR E** |
| F32, F34 | 10 | **PR A** (Phase 3), already assigned |
| `TD-17`, `TD-18` (ex-F38, F39) | 13 | **PR A** — both in `uploads.py`, which Phase 3 opens anyway |
| F40, F42, F43, F44, F45 | 14 | **PR A** — the review round on the PR that introduced them |
| F46 | 14 | **PR E** — PR 30's code, and the clause it contradicts is §3.5's |

PR E exists because no remaining phase opens `apps/studio/studio` or `apps/studio/eval/score_run.py`.
Without it those three findings sit in the ledger indefinitely, which is how F31 stayed open for a
day behind a thread heading that read CLOSED.

> ## Concurrency protocol — read before editing
>
> More than one review can be in flight, and these branches are stacked. The rules stop two
> turns from clobbering each other.
>
> 1. **One thread per target SHA.** A thread is self-contained: its own scope, findings,
>    verification, baton. Never move a finding between threads, never renumber another
>    thread's items.
> 2. **Edit only the thread whose baton you hold.** The ledger's `Baton` column decides.
>    Leave every other thread byte-for-byte alone.
> 3. **Verify the SHA is on the branch first:** `git merge-base --is-ancestor <sha> HEAD`.
>    A cited SHA that is not an ancestor is stale — re-anchor rather than review the wrong tree.
>    Check `origin/main` too: on 2026-08-19 three sessions wrote to these files in one evening and
>    `main` diverged from its remote.
> 4. **Findings are append-only.** Add the response or verdict *under* the finding; do not
>    rewrite its text. Ladder: `open → addressed → resolved`, or `deferred` / `wontfix`.
>    Optional findings never hold a baton.
> 5. **Close, don't delete.** When a thread goes clean, collapse it to a one-line CLOSED
>    banner and harvest durable outcomes per the `README.md` wrap-up.

### Ledger

| Thread | Target | Status | Baton |
| --- | --- | --- | --- |
| 1 — two-surface product | `eea83b8` (PR 3) | **CLOSED** 2026-08-18 — no open findings | — |
| 2 — video 1 store | `43c99dd` (PR 4) | **CLOSED** 2026-08-19 — merged; F17's cause is `TD-10` | — |
| 3 — session write-head | `949cb7b` (PR 5) | **CLOSED** 2026-08-19 — superseded, do not merge | — |
| 4 — local video mode | `fced73f` (PR 8) | **CLOSED** 2026-08-19 — merged `71b9d82`, F18/F19 resolved | — |
| 5 — Zoom export ingest | `5eb55d2` → `8a47c2b` (PR 9) | **CLOSED** — merged `2ee9cc9` | — |
| 6 — matching-label export fold | `e8d206c` (PR 10) | **CLOSED** — F24 repaired, merged `be32232` | — |
| 7 — eval scoring scripts | `e8943cd` (PR 11) | **OPEN** — F25 fixed at `ea698a3`, merged `70b343d`; **F31 still open** | implementer |
| 8 — work and lane as sections | PRs 21 + 22, `355f216~1..2b9bba5` | **CLOSED** — merged `8d57e37` | — |
| 9 — running the studio as an app | PRs 18-20 + PRs 24-26, `5c0c64d..02e0dfb` | **CLOSED** 2026-08-21 — F29/F30 resolved; PR 23 closed unmerged | — |
| 10 — effective YouTube fallback | `05a325c` → `758460c` (PR 28) | **CLOSED** 2026-08-21 — no blocking findings; merged `62278d6`; F32 deferred to Phase 3 | — |
| 11 — launchd app surface, ingest | `1052b5a` → `735ff6a` (PR 29) | **OPEN** — reviewed clean, merged `255739f`; F35 resolved, **F36/F37 open against `main`** | implementer |
| 12 — eval star predictability | `d8b21f1` (PR 27) | **UNREVIEWED** — merged `2026-08-21` with no thread. Author was the only reader. | — |
| 13 — background uploads cache | `e13e3e6` (PR 30) | **CLOSED** 2026-08-22 — merged `9622365`; F38/F39 deferred → TD-17/TD-18 | — |
| 14 — link event + title join | `8eab5e7` (PR 31) | **OPEN** 2026-08-22 — no blocking findings; F40-F46 filed, F41 applied | implementer |

---

## Thread 14 — the link event and the title join (`8eab5e7`, PR 31) — OPEN (no blocking findings)

**Target.** One code commit, `8eab5e7`, draft PR 31 on `codex/pr-a-link-title`; verify with
`git merge-base --is-ancestor 8eab5e7 origin/codex/pr-a-link-title`. Scope is `CURRENT.md` §3.1
rule 1, §3.2, §3.8 and §3.9, plus the assigned debt `TD-17` / `TD-18` and the deferred `F32` /
`F34`. Inventory, guarded delete and the lesson inbox are out of scope and untouched.

**Verdict: no blocking findings.** Seven findings follow. **One would bite Brian the first time
he performs §4's Phase 3 acceptance** (F40); one corrects the numbers that acceptance is checked
against (F41, already applied to `CURRENT.md` §1 and §4); the other five are for the record.

**Reviewer verification — re-run against the real store, not taken on the audit's word.**

- Suite 45/45 in a clean worktree at `8eab5e7`.
- **Isolated live server on `:8799`** over a disposable copy of the real `runs/` and the real
  853-event `labels.jsonl`, with a 56-row cache shaped like production. Linking
  `GMT20260730…-0903` → `Oa0wqetkNcg`: **75 added clips, 688 cues and the section
  `Can't Take That Away From Me | Louis and Ella / Solo` all survive byte-identical**, the
  `missing-media` warning goes silent, the joined title appears in both the picker row and the
  header, and `run["title"]` on disk is untouched. Writing a section afterwards leaves the
  effective id intact. Clearing restores the immutable title, the warning and the hidden player,
  still with 75 clips. Three events appended, nothing rewritten; the live store was never opened
  for writing.
- **Both refusal paths write nothing.** `{"youtubeId": "nope"}` → 400 and
  `{"runId": …}` with no key → 400, with the label log byte-count unchanged.
- **Browser half** on the same isolated server. §3.9 ranks `Oa0wqetkNcg` **first at "13s apart"**
  against 56 candidates; the null-duration uploads sort last as "duration unknown" and are never
  compared as zero. The uploads group correctly drops an id once a run claims it. The typing
  guard holds — `typingInField` sees the new `<input>`, so `g` / `x` / `s` do not reach the grid
  while an id is being typed, and a 13-second poll window left the typed text and the focus in
  place. No new console diagnostics after a link.
- **Blast-radius check on the append-only store.** The two new event shapes are inert to every
  existing fold: `current_feedback_map` skips them (no `markerIndex`), `load_additions` skips
  them (no `start`), and both eval readers (`score_run.py`, `star_predictability.py`) filter on
  explicit verdicts, so a `link` line cannot become a phantom clip or a phantom grade.
- **The join is a no-op on today's data**, measured across all seven runs: every cached YouTube
  title already equals the run's ingest title. Nothing in the picker changes until Brian renames
  a lesson on YouTube or links a Zoom run — which is also why F40 does not show up until he does.

**On TD-18's chosen shape.** Half-the-previous-count is the threshold the contract asked for and
§3.5 5a now records it, so this is not a finding. The consequence worth knowing: once a shrink is
treated as partial the cache merges forever, so if Brian ever really does delete a large batch of
uploads, the stale rows stay in the picker until `uploads.json` is deleted by hand. The stderr
line is the only signal, and it does not say that.

### F40 — the title join makes the two duplicate runs byte-identical in the picker — non-blocking · **would bite you** · open

Measured on the real store, not constructed. Today the picker distinguishes the Zoom run from its
YouTube twin by their titles:

| | Before this PR | After linking, on today's cache |
| --- | --- | --- |
| local Zoom run | `GMT20260730-155336_Recording_640x360 (1)` | `GMT20260730 155336 Recording 640x360` |
| the `Oa0wqetkNcg` download | `GMT20260730 155336 Recording 640x360` | `GMT20260730 155336 Recording 640x360` |

The YouTube title of `Oa0wqetkNcg` *is* the Zoom filename, so joining it collapses the only thing
that told the two rows apart. What is left is the suffix: `· 0 markers · 75 added` against
`· 0 markers · 0 added`. Confirmed live in the browser — two adjacent options reading the same
string.

**What it costs.** Brian opens the wrong row, sees an empty grid, and backs out. Annoying, not
destructive — *today*. Phase 4 is the reason to fix it now: that phase puts runs in a delete
panel, and two identical titles in a delete confirmation is a different class of mistake.

**Why it is this PR's problem and not the merge task's.** §5 keeps the duplicates deliberately.
This PR is what makes them indistinguishable, and the cheapest fix is one line where the label is
built (`runs.js:118`): when more than one row resolves to the same `youtubeId`, keep something
that differs — the run's own immutable title, its `source`, or its ingest date. Reviewer's
preference is the immutable title in parentheses, because that is the string Brian has been
reading for a week.

### F41 — §1's clip counts were event counts, not clips — non-blocking · **applied** 2026-08-22

`CURRENT.md` §1 said the two GMT runs hold 179 and 87 clips, "266 between them", and §4's Phase 3
acceptance said "all 179 clips intact". The store says 75 and 51.

| Run | `miss` events | `unmiss` | old figure (`miss − unmiss`) | live clips |
| --- | --- | --- | --- | --- |
| `GMT20260730…` | 184 | 5 | 179 | **75** |
| `GMT20260712…` | 89 | 2 | 87 | **51** |

`load_additions` keys by `start` and takes the latest event ([[D-008]]), so editing one clip's
label writes a second `miss` at the same start; the old method counted the edit as a clip. The
implementer's note called the 179 "stale". It was not stale, it was computed the wrong way, which
matters because the same method would misreport any future count. Corrected in `CURRENT.md` §1
and §4 with the measurement recorded inline. No code implication — the API and the app have
always shown the folded number.

### F42 — a scheme-less YouTube URL is refused — non-blocking · open

`youtubeIdFromInput` (`runs.js:75`) hands the raw string to `new URL`, which throws without a
scheme, so `youtube.com/watch?v=Oa0wqetkNcg` returns "invalid YouTube id or URL". Reproduced in
the browser. The free-text field exists precisely for the offline case where the id is typed or
pasted by hand, so this is the input most likely to arrive without `https://`. Fix is
`new URL(value, "https://")`, or prefixing when there is no `://`; the host allowlist still
rejects everything else, so nothing new is admitted.

### F43 — a saved link keeps the raw URL in the field — non-blocking · open

`syncLinkControl` refuses to overwrite the input while it has focus, which is right for the poll
and wrong for the save that just succeeded: paste a watch URL, press Save, and the field still
reads `https://www.youtube.com/watch?v=…` while the stored value is the 11-character id.
Reproduced in the browser. `saveYoutubeLink` should set the field to the canonical id it just
wrote, focus or not.

### F44 — the candidate list is rebuilt on every four-second poll — non-blocking · open

`refreshRuns` calls `renderLinkCandidates()` unconditionally, so all 56 `<option>` nodes are
replaced every poll whether or not the cache changed — measured at 5 rebuilds in 13 seconds with
the field focused. Nothing breaks: the typed text and the focus both survive, verified. Guard it
on the uploads list actually having changed, the same way the title repaint should be guarded
(`refreshRuns` also repaints `#meta` every poll for an unchanged title).

### F45 — a `link` event carries no video identity — non-blocking · open

Every other writer stamps `videoId` / `videoUrl` / `videoTitle` from the run; `append_link` does
not, because it is the one appender that never receives `run`. `README.md` claims each line is a
standalone example, and a `link` line is the one line where knowing *which lesson was linked to
what* is the entire content. The handler already has `run` loaded two lines up. Costs nothing
today — no reader needs it — and costs a forensic pass later if the log is ever audited by hand.

### F46 — `authenticated` is written but never read — non-blocking · open · **not this PR's code**

§3.5 justifies the flag with "so §3.9 never mistakes a two-item public list for the whole
channel", but nothing reads it: `api_payload` omits it from `/api/uploads`, no UI module mentions
it, and `merge_items` recomputes authentication from the canary rather than consulting it. The
protection the contract describes does not exist on the read side. Landed in PR 30, surfaced here
because PR A is the PR that opens `uploads.py`. Either expose it and let the picker say the list
is public-only, or drop the clause from §3.5 — but the two should not disagree.

**Baton: implementer.** No merge without Brian's explicit approval.

---

## Thread 10 — effective YouTube fallback (`05a325c` → `758460c`, PR 28) — CLOSED 2026-08-21

**Verdict: no blocking findings. Merged at `62278d6`** on Brian's explicit approval, after a
rebase onto `origin/main` (the branch was one code commit behind, PR 27; `git merge-tree` showed
no conflict and the files did not overlap).

**Scope reviewed.** `CURRENT.md` §3.1 rule 2 and §3.3 only: URL-derived effective YouTube
identity, both read API surfaces, missing-media warning suppression when a fallback exists, and
player selection that never sends a local synthetic id to YouTube.

**Reviewer verification — re-run, not taken on the audit's word.** Tests 24/24 (`test_sidecars`
15/15, `test_youtube_fallback` 9/9), before and after the rebase. Server half exercised headlessly
against all seven real run files with `MEDIA_DIR` patched to an empty directory: the four
zero-clip downloads resolve an id and fall silent, the two GMT locals resolve nothing and keep
`missing-media`. Browser half on a second instance at `:8799` with two media entries removed —
deleted download cues the embed and reports `getDuration() === 3883`, matching the uploads-list
duration for `Oa0wqetkNcg`; the dead local run computes `display: none` on `#player`, shows its
warning, reports `isPlayerReady() === false`, and keeps all 688 grid rows. Five run transitions
leave no stale lesson on screen. Cold boot on a dead run never fetches the IFrame API, and the
deferred load on a later switch cues correctly. Console clean apart from the intended warning.
All 24 `player.` dereferences are guarded; `D-034` and `D-035` citations resolve; `git diff
--check` clean.

**Why the `ready()` change is load-bearing, not cosmetic.** `playerReady` means "a player object
exists", not "a video is cued". Those were the same thing until this PR introduced a third state —
a live player with nothing in it. On a warm switch from a YouTube run to a dead local run the old
predicate stayed `true`, so `togglePlay` would drive a cleared player and `getDuration` /
`getCurrentTime` would report the *previous* lesson's clock. Hiding the iframe alone would not have
caught that. General principle, worth carrying: when a two-state system gains a third state, every
predicate written as "not the other one" becomes wrong, and the ones reading a cached flag rather
than the live condition fail silently.

### F32 — `run_warnings` takes the resolved id as a parameter — DEFERRED to Phase 3

`run_warnings(run_id, run, youtube_id)` (`server.py:311`) depends on its caller passing the right
id. The one caller, `run_payload`, is correct; a future one can suppress a real warning by passing
a stale value. Calling `effective_youtube_id(run)` inside the function costs one `urlparse` and
removes the way to be wrong.

**Disposition, 2026-08-21:** deferred, not fixed on its own. Phase 3 changes the resolver's
signature anyway (F33), so the parameter question resolves there in code that is already being
touched. Not worth a PR for three lines.

### F33 — the resolver signature changes in Phase 3 — NOTE, no action

`effective_youtube_id(run)` takes no `run_id`, so the link event forces `effective_youtube_id(run_id,
run)` and a rewrite of the nine tests that call it positionally. Expected and cheap. Recorded so the
Phase 3 reviewer does not read the churn as scope creep.

### F34 — `/api/runs` re-parses `labels.jsonl` per run — NOTE for Phase 3 sizing

`load_annotations` and `load_additions` each call `read_label_events()` inside the per-run loop, so
`/api/runs` parses all 853 lines roughly fourteen times per poll. A per-run link lookup makes it
twenty-one. Measured 42 ms against a 4-second poll, so this is not urgent — but Phase 3 is where
caching the parse becomes worth one line.

---

## Threads 1-4 — CLOSED

`README.md`'s wrap-up rule: this file is live state, not an archive. Git history and the PR threads
hold the round-by-round; what was durable is in `DECISIONS.md` and `BACKLOG.md`. These tables are
the index. Collapsed 2026-08-19 — thread 5 untouched, its baton was held elsewhere.

### Thread 1 — two-surface product (`eea83b8`, PR 3) — CLOSED 2026-08-18

Fifteen findings, F1-F5 from Codex and F6-F15 from Claude Code, closed on two different bases and
the distinction matters: **F6-F11, F14-F15 (8) were fixed and then verified against the shipped
code**; **F1-F5 (5) were accepted on the implementer's evidence and never re-reviewed** — which is
why the ladder now requires a reviewer verdict.

| # | Finding | Severity | Outcome |
| --- | --- | --- | --- |
| F1 | definition of done contradicted immutable history | blocking | resolved |
| F2 | published branch instructions risked stale anchors | blocking | resolved |
| F3 | a top-level API error would prevent the degraded load | blocking | resolved |
| F4 | the repair CLI could overwrite truth by refetching | blocking | resolved |
| F5 | durable fallback semantics could not stay implicit | blocking | resolved → [[D-023]] |
| F6 | `copy timestamps` emits an invalid chapter list | blocking | resolved → [[D-027]] |
| F7 | the export fold collapses clips further apart than 2s | blocking | resolved → `TD-9`, `TD-16` |
| F8 | one shared debounce handle cancels unrelated writes | blocking | resolved → [[D-024]] |
| F9 | `labels.jsonl` records a reject as `verdict: "note"` | non-blocking | resolved forward-only → `TD-14` |
| F10 | feedback re-paint can colour the wrong row | non-blocking | resolved |
| F11 | `rowKey` is positional, so identity dissolves | non-blocking | resolved → [[D-025]], [[D-029]] |
| F12 | no fallback for focus returning from the player iframe | needs a browser | **wontfix** → [[D-026]] |
| F13 | the whole event log is re-parsed per accessor | optional | **deferred** → `TD-3` |
| F14 | `s` reverts a work/lane edit that was already saved | non-blocking | resolved |
| F15 | `blankCount` reports annotated keeps as unreviewed | non-blocking | resolved → [[D-028]] |

Two lessons outlived the thread and are rules now, not findings: **severity is measured, not
asserted** (from F7 — filed `blocking` on constructed input, never fired once on video 1), and
**say what a finding would cost** (of fifteen, three would have bitten Brian). Both in `README.md`.

### Thread 2 — video 1 store (`43c99dd`, PR 4) — CLOSED 2026-08-19

Merged. **F16** — the standing trap overstated that added markers never drift; the corrected
measurement is `README.md`'s "Shared vocabulary" section, which names the two wrong claims it
replaced so nobody restores them. **F17** — three duplicate writes leave file order and
`recordedAt` order disagreeing; no effect today because the server folds in file order, hazardous
to any reader that sorts by time. Cause is `TD-10`; the file-order rule is in
`apps/studio/README.md`. Related: `TD-4`, `TD-14`.

### Thread 3 — session write-head (`949cb7b`, PR 5) — CLOSED 2026-08-19

Superseded, never merged, **do not merge**. PR 6 closed the same way.

### Thread 4 — local video mode (`c4de36d` → `fced73f`, PR 8) — CLOSED 2026-08-19

Merged at `71b9d82`; decisions harvested as [[D-034]]-[[D-038]]. Both findings were non-blocking
because `apps/studio/media/` was empty at the time. **That is no longer true — it now holds two
symlinked Zoom exports and four downloaded lessons — so do not reuse that reasoning without
re-measuring.**

**F18 — sidecar lookup can silently ingest the adjacent recording · resolved.** Kept in full
because **thread 5's F20 is the same surface.** `local.py` used `sibling.name.startswith(stem)` as
the entire sidecar boundary, so `Lesson 1.mp4` adopts `Lesson 10.vtt` — and worse, a
`Lesson 10.info.json`, silently replacing title, description, extracted markers and video identity
with no warning, because the source is syntactically valid. A wrong caption grid is visible; a
wrong video identity is not. Fixed by requiring the remainder after the stem to begin with `.`,
admitting `Lesson 1.vtt` / `Lesson 1.en.json3` / `Lesson 1.info.json` and excluding `Lesson 10.*`
and `Lesson 1 backup.*`. Now [[D-037]]: every future stem variant owes the same boundary and its
own adversarial case.

**F19 — a non-media `HEAD` sends a body and corrupts the next HTTP/1.1 response · resolved.** Fixed
wider than filed — `HEAD` was equally wrong on `/`, `/ui/` and every `/api/` route, so one flag
reads where bodies are written rather than a parameter threaded through each branch. The flag
resets at the start of a request, not in a `finally`, so a failed `HEAD`'s 500 stays bodyless and
nothing leaks across a keep-alive connection.

**The gap this thread never closed:** playback on an actually disconnected machine. Closed by use
rather than by test — the Zoom run played in the air on intermittent service. No automated check
covers it and none is planned ([[D-005]]).

---

## Thread 5 — Zoom export ingest (`5eb55d2` → `8a47c2b`) — CLEAN

**Target.** `5eb55d2` on `zoom-export-ingest`, five product commits off `main` at `d2ad793`:
`247f7b3` (Zoom sidecar variants + late captions), `b0c4dd3` (gitignore), `4b3ee5d` (sticky
header), `cae20a2` (missing-media warning), `5eb55d2` (`k` stick). The branch head is `6ef767c`
— a duplicate session-log commit and a merge of `main`, neither of them product. Verify before
reviewing:

```bash
git merge-base --is-ancestor 5eb55d2 HEAD
git log --oneline main..zoom-export-ingest
```

**Scope.** What real use of PR 8 exposed. `docs/prs/pr-9-zoom-export-ingest.md` is the spec but
covers only the first two commits — review the diff, not the spec. Acceptance criteria and the
implementer's audit are in `CURRENT.md`. The extension is untouched ([[D-006]]).

**Read `CURRENT.md` §1 "Where to look hard" first.** It names the five places this change could
plausibly be wrong, and two of them are places the implementer's own audit records **no
receipt**: the late-caption rerun end to end, and a post-`5eb55d2` video-1 regression pass.

**What the implementer verified**, so the review need not re-derive it unless a finding depends
on it: both real Zoom exports ingesting to 688 cues each (checked, not assumed — the raw VTTs
hold 690 and the dedupe drops 2), the `Lesson 1.mp4` / `Talk_640x360.mp4` sidecar regressions,
the `k` stick reproduced and then driven directly through the poll→keypress loop, and the
header fix found from a screenshot at non-default browser zoom.

**Severity, per `README.md`.** Measure it. Two real Zoom runs and six run files now exist in
the working tree, and video 2's store carries 147 label events over 75 live added clips — so
"fires on data that exists today" is a meaningful bar here, unlike thread 4. Say plainly
whether a finding costs Brian something on his next lesson, or is latent.

**Note on process.** BugBot filed nothing on PR #9 — seven runs, seven `usage limit reached`
failures. This thread is the whole review.

### F20 — normalized Zoom base can beat an exact sidecar — non-blocking · resolved

**Finding.** `find_sidecars` adds the literal stem and then the normalized Zoom stem to one
candidate list, but subtitle candidates are finally sorted only by extension and language.
For tied `.vtt` files, the directory's lexical order decides the winner. A real title that
legitimately ends in a resolution-looking suffix therefore can ingest an unrelated sibling
instead of the media file's exact sidecar:

```
Lecture_1920x1080.mp4
Lecture.vtt                 # WRONG BASE
Lecture_1920x1080.vtt       # RIGHT EXACT
```

The disposable fixture returned `Lecture.vtt`, and `read_cue_pairs` produced `WRONG BASE`.
The current two Zoom exports do not contain both forms, so this does **not** fire on Brian's
present data and is non-blocking under the measured-severity rule. It is nonetheless one of
the adversarial cases named in the acceptance criteria: preserve the `.` boundary, but rank
an exact-stem **subtitle** sidecar ahead of every normalized-base subtitle before the generic
extension/language ranking erases which variant matched.

**Reviewer re-review — 2026-08-20 at `8a47c2b`. Resolved.** A disposable fixture with
`Lecture_1920x1080.mp4`, `Lecture.vtt` (`WRONG BASE`), and
`Lecture_1920x1080.vtt` (`RIGHT EXACT`) now orders the exact `.vtt` first and reads
`RIGHT EXACT`. A second fixture carrying both a resolution suffix and ` (1)` likewise keeps
the exact subtitle first. The change preserves the F18 `.` boundary rather than widening it.

### F21 — the player cap can leave the annotation grid with zero usable height — blocking · resolved

**Finding.** The new flex shell keeps the header reachable, but
`body.player-top .player-col { max-height: 62vh; }` sizes the player only against the viewport,
not against the space remaining after a wrapped header. On the real video-2 local run in a
760×520 browser viewport, the header consumed 170.8px and the player consumed 322.4px; after
the density control, `#gridScroll.clientHeight` was exactly **0**. The document itself stayed
at 520px and the header remained at top 0, so the original header problem is fixed while the
only annotation surface disappears.

Pressing `n` made the composer form (304.2px tall) render below the zero-height grid viewport;
it could not be used. This fires today on the actual newly ingested video and fails acceptance
criterion 5's small-viewport half, so it is blocking. Reserve a usable grid height before
giving the player its auto row; a cap expressed only in `vh` cannot account for a header that
has already claimed much of that same viewport.

**Reviewer re-review — 2026-08-20 at `8a47c2b`. Resolved.** In the browser on the real
video-2 run at 760×520, the document remains 520px tall with header top `0`, while
`#gridScroll.clientHeight` is now `162` (not `0`). `n` opens the form, focuses its label in
the visible grid viewport, and Tabs through to the visible submit button as the grid scrolls.
At 1280×800, the grid remains `241`px tall; the document still does not scroll. This restores
the annotation surface without regressing the wrapped-header repair.

### F22 — raw transcript sidecars remain neither tracked nor ignored — optional · resolved

**Finding.** PR 9 ignores the large recording media and correctly ignores `.aider*`, but the
two real `docs/reference/GMT20260712/` and `GMT20260730/` directories still appear as `??`
because their `.transcript.vtt` files are neither tracked nor ignored. The user has to notice
and exclude them manually on every broad `git add`.

**Recommendation.** Ignore `docs/reference/**/*.vtt` as well. These are raw local source
exports (full meeting transcripts), while a deliberately curated parser fixture can be tracked
elsewhere if one becomes necessary. Non-blocking by construction: the exposed files are small
text and no data is committed yet.

**Reviewer re-review — 2026-08-20 at `8a47c2b`. Resolved.**
`git check-ignore -v docs/reference/example/transcript.vtt` reports the new
`docs/reference/**/*.vtt` rule, so raw sidecars no longer appear as accidental untracked
source exports.

### F23 — the PR spec omits three of the five product commits — optional · resolved

**Finding.** `docs/prs/pr-9-zoom-export-ingest.md` describes `247f7b3` and part of `b0c4dd3`,
but not the sticky-header, missing-media warning, or duplicate-cue navigation changes
(`4b3ee5d`, `cae20a2`, `5eb55d2`). This costs a later reader the acceptance criteria and
verification intent for most of the PR, even though the current review caught them by reading
the diff. Add concise scope and browser receipts before the PR is closed.

**Reviewer re-review — 2026-08-20 at `8a47c2b`. Resolved.** The PR spec now maps all five
product commits to sections and documents the sticky header, missing-media warning, duplicate
cue navigation, and this review round with their acceptance intent.

**Baton: → implementer** — address F21 (blocking) and return with a new SHA. F20 may be batched
with it; F22–F23 are optional polish and do not hold the baton.

**Superseded by the 2026-08-20 reviewer re-review at `8a47c2b`: all four findings resolved;
the baton is now → planner.**

---

## Implementer round — 2026-08-19 (Claude Code)

All four fixed in one commit per `README.md` step 4. No diagnosis was contested; no fix touched a
decision. Every claim below was measured, not reasoned about.

**F20 — fixed.** Taken as specified: which stem variant matched now leads the subtitle ranking,
ahead of extension and language, and `variants` is ordered exact-first. The `.` boundary is
untouched. On the reviewer's own fixture — `Lecture_1920x1080.mp4` beside both `Lecture.vtt` and
`Lecture_1920x1080.vtt` — the pre-fix code at `5eb55d2` returns `Lecture.vtt` reading `WRONG BASE`
and the fixed code returns `Lecture_1920x1080.vtt` reading `RIGHT EXACT`. F18's cases still hold:
`Lesson 1.mp4` adopts nothing, `Talk_640x360.mp4` takes `Talk.transcript.vtt` and not `Talk2.vtt`.

*Fixed wider than filed, and it earns less than it looks.* The pre-SHA checklist says to look for
the same mistake elsewhere, so `.info.json` and `.description` were switched to the same ranking —
F18 recorded that a wrong `.info.json` is the worse half, since it replaces video identity
silently. **It changes nothing observable.** The normalized base is always a strict prefix of the
exact stem, so it always sorts first, and the previous last-write-wins already landed on the exact
file — verified identical before and after on the same fixture. It is hardening against a future
third variant, not a second bug, and should not be re-reviewed as one.

**F21 — fixed.** Diagnosis confirmed exactly: `62vh` sized the player against the whole viewport
while the header had already claimed part of it. The cap moved off the item and onto the grid
track as `minmax(0, 62%)`, which resolves against the grid container — the viewport *minus* the
header — so the grid is guaranteed the remainder. Measured on the real video-2 local run:

| | 760×520 | 1280×800 |
| --- | --- | --- |
| `#gridScroll.clientHeight` | **0 → 162** | 241 |
| player column | 322.4 → 157.1 | 441.3 |
| media within its wrap | yes | yes |
| `document.scrollHeight` | 520 | 800 |
| header `top` | 0 | 0 |
| run picker reachable | yes | yes |

The composer half of the finding is closed too: `n` renders the 304.2px form inside the grid
viewport, the grid scrolls, and the first field takes focus and scrolls into view.

*Two changes beyond the track cap, both forced by measurement.* At 760×520 the keyboard hint wraps
to several lines and takes the column for itself, leaving a 28px sliver of video — so under
`max-height: 640px` the hint is hidden and the player's share drops to 45%. The existing code
comment already said the hint is the right thing to lose; this makes that explicit instead of
leaving it to clipping. And `.player-wrap` now grows into the column with `min-height: 0`, so the
media has a definite parent to size against. *Dead end worth recording:* capping the media at
`max-height: 100%` of a shrink-to-fit wrap is circular and collapsed the video to 27.9px. The wrap
has to grow for that percentage to mean anything.

**F22 — fixed** as recommended. `docs/reference/**/*.vtt` ignored; both export directories stopped
showing as `??`. Curated parser fixtures can be tracked deliberately elsewhere.

**F23 — fixed.** The spec now covers all five product commits and this review round: a commit →
section table at the top, and new sections for the sticky header, the missing-media warning and
the `k` stick, each with its acceptance criterion. §4 points forward at F21, since the header fix
is what introduced it.

**Regression, and it closes a gap `CURRENT.md` flagged as having no receipt.** Video 1 loads at
`64 markers · 21 added · 24 YT` with zero console errors, which is acceptance criterion 6.

**Still unchecked, unchanged from the last handoff:** the late-caption rerun end to end
(acceptance criterion 2). It needs a video whose captions arrive between two runs, and all four
YouTube uploads still have none — re-checked against YouTube today. See `BACKLOG.md`,
"The corpus, and the one blocker". Not fixable by trying harder.

**Baton: → planner** — review clean at `8a47c2b`; scope the next task.

---

## Thread 6 — matching-label export fold (`e8d206ca9c715643764e21ded55a9d248c6cda08`, PR 10) — CLOSED

**Scope.** `mergeNearby` only folds entries inside the two-second window when they would print
the same label. The intention is to enforce [[D-033]] without changing video 1's known export.
The branch's two coordination-document edits are not product code.

**Verification.** Exact head is present on `origin/merge-only-matching-labels`; whitespace check
passes. The one-condition code change preserves the existing time-window and rank behavior, and
the changed condition is a no-op for video 1's known extracted-marker collisions. GitHub has no
CI workflow or commit-status checks configured for this repository.

### F24 — PR 10 creates a second, incompatible `D-035` — blocking · **resolved 2026-08-21**

`main` already assigns `D-035` to local playback winning over the YouTube embed. This PR adds a
different `D-035` for matching-label folding and changes `TD-16` to cite that new meaning. After
merge, `[[D-035]]` would be ambiguous and a reader following TD-16 could land on the unrelated
playback decision. That breaks the coordination records Brian and later agents use to avoid
silently relitigating decisions.

**Required repair.** Keep the `apps/studio/ui/export.js` condition in the product PR, but remove
the `BACKLOG.md` and `DECISIONS.md` changes from it. Those living records travel directly on
`main`; record the outcome there with the next free ID, `D-039`, and update TD-16's citation when
the code path is ready. The review comment is posted on PR #10.

**Baton: → implementer.**

**Implementer repair — merged `be32232`.** Taken as required. The `BACKLOG.md` and
`DECISIONS.md` changes were reverted out of the branch and `main` merged in so the diff showed
five lines rather than 106 — the stale merge base was attributing `main`'s own edits to this
branch. The outcome is recorded on `main` as `D-039`, and `TD-16` cites it. Verified: exactly
one `D-035` in `DECISIONS.md`, and `D-039` exists. **Resolved.**

---

## Thread 7 — eval scoring scripts (`e8943cdb67964a00b30a2893c1bdf83884c8244f`, PR 11) — OPEN (F25 resolved; F31 filed 2026-08-21)

**Scope.** Two offline CLIs: render a studio run as the transcript accepted by `yt-clipper`, and
score a scratch proposal file without contaminating a canonical run. No product runtime code is
changed.

**Verification.** Exact head is present on `origin/eval-scoring-scripts`; whitespace check
passes. The real video-2 transcript emits **714 lines and 26 GAP flags**, matching the run. A
scratch copy of video 1's 64 proposals reproduces the claimed 45-second results: 9/9 self-created
star recall, 65/67 region recall, and 54/64 precision. The proposal-in-`runs/` guard and current
CI absence were inspected; the guard's rejection path was already covered by the implementer's
recorded check.

### F25 — the intended zero-cue refusal raises `NameError` — optional · **resolved 2026-08-21**

At `make_transcript.py:78`, the zero-cue branch interpolates `run_id`, but `main` never defines
that name. The existing zero-cue run `Oa0wqetkNcg-20260819-0858` therefore exits 1 with a Python
traceback, not the concise `has zero cues — nothing to hand the skill` explanation. It cannot
produce a bad transcript and does not affect video 2, so this is optional; using `argv[0]` or the
resolved file name fixes it. The inline review comment is posted on PR #11.

**Resolved.** `make_transcript.py` now interpolates `path.name`. Verified 2026-08-21 by running
it against `Oa0wqetkNcg-20260819-0858`: it prints the concise `has zero cues — nothing to hand
the skill` message and exits, no traceback.

### F31 — `score_run.py` crashes instead of refusing when the ground truth has no human rows — optional · open

Found 2026-08-21 while verifying F25; never previously filed, and it is a **different file and a
different error** from F25 despite looking like the same defect.

Scoring against a run with zero human rows raises `ValueError: min() iterable argument is empty`
at `apps/studio/eval/score_run.py:84`, inside `nearest()`, because `human_all` is empty and
`min()` has nothing to pick from. Reproduce:

```bash
python3 apps/studio/eval/score_run.py /tmp/video2-proposals.json Oa0wqetkNcg-20260819-0858
```

`make_transcript.py` guards this case and explains it; `score_run.py` does not. The same
zero-cue uploads that motivated F25's guard reach this path. Cheap fix: refuse early when
`human_all` is empty, with the same tone as the `make_transcript.py` message — the ground truth
has nothing to score against, which is a corpus problem, not a skill result.

Optional: it cannot produce a wrong score, only a traceback. Same neighbourhood as the
`annotated` proxy noted in `docs/reference/EVAL.md` §4, so fix both in one pass.

**Baton: → implementer (both optional; neither holds a merge).**

---

## Thread 8 — work and lane as sections (PRs 21 + 22) — CLOSED

**Review both commits as one design.** PRs 21 and 22 are merged, but they are a single
change split in two: sections exist (21), lane joins them (22). Reading 22 alone shows lane
moving into a structure with no account of why the structure exists.

```bash
git diff 355f216~1..lane-as-section     # both, as one diff
```

PR 22 was merged as `8d57e37` after Brian's explicit 2026-08-21 authorization. PR 21 is not
being reverted to re-review it; this repo reviews by SHA, and reverting merged code for a second
reading is churn against no gain.

**Scope.** PR 21 makes `work` a section break — an event at a timestamp on the run, resolved on
read, never stored on a clip. Video 1 went from 67 stored copies to 2 events. PR 22 puts `lane`
on the same break, because on video 1 the two change at exactly the same two timestamps. On video 1 the two change at exactly
the same two timestamps, which is the tell that they are one thing — a section has a piece and a
mode. `sections` becomes `[[start, work, lane], ...]`; neither is stored on a clip.

It reverses a recommendation. Deprecating `lane` was right when it was a per-clip field costing a
keystroke per marker; as a section property it costs one entry per section.

**What the implementer verified**, so the review need not re-derive it: export byte-equal on all
three videos — same headers with their lane suffixes, 74/77/53 lines; grid renders 688 rows;
sidecar tests 15/15; the migration reused the three existing breaks rather than adding events.

**Where to look hardest**

- `persistSection` merges `{work, lane}` over the **currently resolved** values before writing,
  so editing one field must not blank the other. That is the regression this shape invites.
- `load_sections` drops a break when both fields are empty — the undo path. Confirm it cannot
  drop one that still carries the other field.
- A clip **before** the first break resolves to `""`. The header supplies the break at 0:00;
  confirm a run carrying only a later break degrades sensibly rather than printing a blank
  header.

**Context the reviewer should have.** This sits on PR 21, which exists because PR 17 shipped a
half-change — a new run-level path added on top of the old per-clip path, both live at once.
Brian found it by using the app, not by reading the diff. The same shape is the thing worth
looking for here.

### F26 — the header work writer blanks its section lane — blocking · resolved

`main.js`'s `#runWork` change handler is a second `/api/section` writer, but it
still sends only `{runId, start: 0, work}`. After PR 22, `append_section` treats
an omitted lane as `""`, so correcting a work title at 0:00 overwrites the
co-owned lane with an empty string. This is not theoretical: at
`668dff2a0266d7067d9226b39e8406cbb95a76c4`, sending the exact header payload to
the isolated video-1 store changed its first section from
`[0, "Pennies from Heaven | Stan Getz", "Transcription"]` to
`[0, "Header review work", ""]`.

**Cost.** Brian can lose the visible `Transcription` suffix from every early
video-1 grid row and the export simply by fixing the header text. The lost lane
is an append-only event, so the correct value needs to be reconstructed and
written again.

**Required repair.** Make the header use the same merge discipline as
`persistSection` (or send the resolved lane with the header write). Audit every
remaining section writer before returning a SHA; a section event must carry the
complete `{work, lane}` pair.

**Reviewer re-review — 2026-08-21 at `2b9bba5`. Resolved.** The header is now
one of the two `persistSection` callers. That function reads the currently
resolved pair at 0:00 and sends both fields, so the retained lane cannot be
blanked by a work-only edit. The server fold test preserved the sibling field
through both work-only and lane-only updates. The browser harness's text-entry
shim does not emit a native `change` event on blur, so this verdict is from the
single-writer code path plus the exercised fold rather than that harness quirk.

### F27 — in-row lane edits still write the old per-clip taxonomy — blocking · resolved

The `tbody` input handler in `main.js` still treats `data-combo="lane"` as a
clip-taxonomy field: it changes `S.liveTax.lane` and calls `queueTaxonomy()`.
PR 22's `finishComboEdit` then also writes the intended section. On an isolated
copy of video 1 at `668dff2a`, editing lane at 1:20 and pressing Enter appended
both `human-annotate` for marker index 1 (`lane: "Review lane"`) and the
intended `human-chapter` break at start 80. The existing composer path also
continues to carry inherited work/lane into `/api/miss` and `/api/annotate`.

**Cost.** The migration promises that neither value is stored on a clip, but a
normal `Tab`+`l` interaction silently creates a durable, separately folded
per-clip value. That recreates the two-live-path shape PR 21 was meant to
remove; future readers cannot tell these accidental events from the legacy
annotations they are supposed to preserve.

**Required repair.** Restrict taxonomy debounce/state writes to tags. Route
work and lane only through the merged section writer, and remove the inherited
work/lane fields from new clip writes. Re-test that one section edit produces
one `chapter` event and no `annotate` or `miss` event.

**Reviewer re-review — 2026-08-21 at `2b9bba5`. Resolved.** The tbody input
handler no longer mutates or queues clip taxonomy for work/lane, and the
composer no longer inherits either value. In an isolated video-1 store, a
keyboard-committed lane edit appended exactly one `human-chapter` event with
the inherited work and appended no `human-annotate` event.

### F28 — the section contract says an empty work deletes a lane-only section — optional · resolved

`docs/clip-schema.md` says that an empty `work` removes a break, while the
implementation correctly removes it only when **both** work and lane are empty.
That makes the documented undo rule wrong for the lane-only state that PR 22
explicitly supports. Say `both fields are empty` so the contract matches the
fold.

**Reviewer re-review — 2026-08-21 at `2b9bba5`. Resolved.** The contract now
states the complete-pair rule and that both values must be empty to remove a
break.

### Implementer response — F26, F27, F28 addressed at `2b9bba5`

Both blocking findings were correct, and both are the shape thread 8 asked the reviewer to hunt
for: a new path added on top of a live old one.

**F26 — fixed, and it was worse than filed.** The header did send `{runId, start, work}` with no
lane, so a work correction blanked the lane. It also still called `/api/run-work`, a route PR 22
deleted — so in the UI it returned `{"error": "not found"}` and did nothing at all. Reproduced
both: the dead route 404s, and the filed payload against `/api/section` turned video 1's first
section into `[0, work, ""]`. That reproduction blanked the real store and was restored by
re-appending the correct event. The header now calls `persistSection`.

**F27 — fixed.** `main.js`'s tbody input handler set `S.liveTax` and called `queueTaxonomy()` for
`lane` and `work`, so an in-row edit wrote an `annotate` event alongside the intended `chapter`
break. Removed. The composer also carried inherited `work`/`lane` into new clip writes; both now
write empty.

**F28 — fixed**, and the rule every writer must follow is now stated in the contract rather than
implied: send the complete `{work, lane}` pair.

**The audit F26 asked for.** One call site of `/api/section`; two callers of `persistSection`
(the header and `finishComboEdit`); `persistSection` merges the edited field over the currently
resolved pair before writing.

**Behavioural test, diffed against a store snapshot.** The full in-row lane interaction appended
**exactly one `chapter` event and zero `annotate` events** — before the fix it wrote both. Header
edit preserves the lane. A lane-only edit preserves the work and a work-only edit preserves the
lane. Video 1 is back to its original two sections. Sidecar tests 15/15.

**Not verified:** the `Tab`+`l` chord did not arm under synthetic keydown events in my harness,
so the write path was exercised by calling `persistSection` the way `finishComboEdit` calls it
rather than through the keyboard. Worth a real keypress before merge.

**Baton: → reviewer** — re-review at `2b9bba5`.

**Closed.** F26–F28 are resolved; PR 22 merged as `8d57e37`.

---

## Thread 9 — running the studio as an app — CLOSED 2026-08-21

PR 24 landed at `9ae0345`; F30 delivered through PR 26 at `02e0dfb`. F29 and F30 are resolved,
and review-only PR 23 was closed unmerged.

---

## Thread 11 — the launchd app surface cannot reach yt-dlp — OPEN (F35 resolved; F36, F37 open)

**Target:** the app surface as merged on `main` at `1052b5a` (PRs 24-26, thread 9, closed).
Found while resolving Codex's Phase 2 readiness review, which reported it as a *prerequisite for
the uploads cache*. It is not — it is a defect in code that already shipped, and it is filed here
rather than in `CURRENT.md` because that document is the task, not the ledger.

### F35 — the running studio cannot find `yt-dlp`, so in-app ingest is broken — blocking · **resolved 2026-08-22**

Four facts, each measured on 2026-08-21 rather than inferred:

| | |
| --- | --- |
| the live agent | pid 15513, `PATH=/usr/bin:/bin:/usr/sbin:/sbin` |
| `~/Library/LaunchAgents/com.briansze.yt-clip-studio.plist` | no `EnvironmentVariables` key at all |
| `apps/studio/ingest.py:65` | invokes the bare string `"yt-dlp"` |
| the binary | `/opt/homebrew/bin/yt-dlp` |

`launchd` gives an agent a minimal `PATH` unless the plist sets one. Homebrew's directory is not
in it, so every `subprocess.run(["yt-dlp", …])` raises `FileNotFoundError`, which `ingest.py:50`
turns into the user-facing `yt-dlp not found. Install it: pip install yt-dlp`. **Ingesting a
YouTube URL from the app has never worked.**

**Why it stayed invisible for three PRs.** Every run before the app surface was `python3
server.py` from a terminal, where Homebrew *is* on `PATH`. The regression arrived with the
launchd agent in PRs 24-26 and nothing since has ingested a URL from the app rather than a shell.
`/api/ingest` with a local *path* is unaffected — `local.py` shells out to nothing — which is why
the Zoom workflow kept working and hid the other half.

**Recommended fix.** `studio install` writes an explicit `PATH` into the plist containing the
directory of the yt-dlp it detects at install time, and the live acceptance runs through the
reinstalled agent rather than a shell. Teaching `ingest.py` a private Homebrew fallback fixes one
caller and leaves the next one to rediscover this. Missing yt-dlp must still degrade to a clear
error, never block server startup.

**Ships as its own small PR, before Phase 2.** Repairing a merged user-visible bug inside a
feature PR hides the fix in the feature's review.

**The lesson, which is the reason this is worth more than its three-line fix.** The finding is one
member of a class: *verified in a terminal, will run in a launchd agent*. `--cookies-from-browser
chrome`, which Phase 2 depends on entirely, is the second member and is still unmeasured — on
macOS it decrypts Chrome's Safe Storage key out of the login Keychain, and Keychain access is
granted per binary with a first-use prompt. Every measurement behind §3.4 was taken from a shell,
which proves nothing about the agent. `CURRENT.md` §6 gates Phase 2 on running that one refresh
through the reinstalled agent.

**Implementer response — 2026-08-21, `735ff6a` (draft PR 29).** Fixed at the process boundary.
`studio install` now writes an explicit agent `PATH` containing the detected yt-dlp directory.
It checks `command -v` first, then the standard Apple Silicon and Intel Homebrew locations so the
GUI-triggered move-healing install works even when the installer's own PATH is already minimal.
No Python caller gained a private fallback; no yt-dlp still leaves the server bootable and keeps
the existing clear ingest error.

Live receipts, not terminal inference: a normal install and
`PATH=/usr/bin:/bin:/usr/sbin:/sbin apps/studio/studio install` both generated
`/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin`; `plutil` accepted the plist; the restarted
agent process reported that PATH. A JSON `/api/ingest` request for the intentionally invalid id
`00000000000` reached yt-dlp and returned `Video unavailable`, not `yt-dlp not found`, and wrote
no run. Existing tests 24/24, `bash -n`, and diff check pass.

---

## Reviewer round — 2026-08-22 (Claude Code), PR 29 / `735ff6a`

**Verdict: no blocking findings.** 39 lines, one file, no product code, and exactly the fix F35
recommended — the launcher owns dependency discovery rather than each Python caller. Two
non-blocking findings follow, both small enough to fold into this PR rather than open another.

### F35 — verified fixed, including the branch the audit could only inspect

Checked on the live machine rather than taken from the audit:

```
pid 6138   PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin
plist      <key>EnvironmentVariables</key> → PATH set
```

The audit recorded the missing-binary case as "inspected rather than tested by uninstalling the
user's working yt-dlp", which was the right call — do not break a working tool to test a branch.
It is now tested without touching anything: `find_ytdlp` and `agent_path` were extracted and run
standalone across all three branches.

| Environment | `agent_path` output | Exit |
| --- | --- | --- |
| normal terminal | `/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin` | 0 |
| launchd's minimal PATH (the GUI-bundle case) | identical — the Homebrew fallback carries it | 0 |
| yt-dlp absent everywhere | `/usr/bin:/bin:/usr/sbin:/sbin` | 0, no abort under `set -euo pipefail` |

The third row is the one that mattered. `|| true` around `find_ytdlp` is what stops a missing
dependency aborting `write_plist` and leaving the user with no agent at all. It holds.

`plutil -lint` runs inside `write_plist` under `set -e`, so a directory containing
XML-significant characters fails the install loudly instead of writing a corrupt plist. Same
exposure `$APP_DIR` already had; covered.

### F36 — `stale_plist` sees a stale path, not a stale PATH — non-blocking · open

`stale_plist` asks exactly one question:

```bash
! grep -q "<string>$APP_DIR/server.py</string>" "$PLIST"
```

That detects a **moved checkout** and nothing else. The plist now carries a second piece of
environment state that can go stale on its own, and neither `heal_if_moved` nor `status` can see
it. Two consequences, and the first is live today:

1. **Until PR 29 merges, `main`'s own self-heal silently reverts the fix.** `studio open` calls
   `heal_if_moved`; on a moved checkout that runs `install` from whatever is checked out.
   `main`'s `write_plist` has no `EnvironmentVariables` key, so it rewrites the plist without one
   and F35 returns with no warning. The machine is currently running a configuration only the
   unmerged branch can reproduce.
2. **After merge, the PATH is frozen at install time.** Install yt-dlp *after* the studio, move
   Homebrew, or migrate between Intel and Apple Silicon, and the recorded PATH stays wrong.
   `status` says nothing, because it only checks the server.py path.

**Recommended fix, two lines in the function this PR is already next to:** make `stale_plist`
also true when the plist's recorded PATH differs from `agent_path()`. Both cases then heal
through machinery that already exists. Same "fold a few lines into the PR already editing this"
argument used for F32 and F34.

### F37 — the finder looks in Homebrew; three places tell the user pip — optional · open

`find_ytdlp` checks `command -v`, then `/opt/homebrew/bin` and `/usr/local/bin`. A pip or pipx
install lands in `~/.local/bin` or `~/Library/Python/3.x/bin`, invisible when `studio install`
runs from the app bundle with launchd's minimal PATH — the exact case the fallback list exists
for. Meanwhile:

| Where | What it says |
| --- | --- |
| `apps/studio/ingest.py:50` | `yt-dlp not found. Install it: pip install yt-dlp` |
| `README.md:16` | "on PATH (`pip install yt-dlp`)" |
| `apps/studio/README.md:50` | "Ingesting a YouTube URL needs `yt-dlp` on PATH" |

Pick one and make them agree: add `$HOME/.local/bin` to the candidate list, or change the advice
to `brew install yt-dlp`.

**The doc half is a gap this PR created.** "On PATH" now means *the agent's* PATH, baked at
install time — so **installing yt-dlp after `studio install` needs a reinstall**, and nothing says
so. `AGENTS.md` puts docs describing behaviour in the PR that changes it, so one sentence in
`apps/studio/README.md` belongs here rather than on `main` afterwards.

### Not findings, recorded so nobody re-raises them

- The yt-dlp directory is **prepended**, so every subprocess now prefers Homebrew binaries. Only
  yt-dlp is shelled out today and `ProgramArguments` pins python3 absolutely, so nothing changes.
  Worth knowing before something else gets shelled out.
- No test ships with the PR. `studio` is bash; this repo's one test file is stdlib `unittest` for
  Python, and a harness for three lines of shell is ceremony. The table above is the evidence
  instead.

**Baton at review time: Brian, for the merge call.** F36 and F37 were recommendations, not
blockers.

### Merge outcome — 2026-08-22

**PR 29 merged as-is at `255739f`.** F35 is resolved. Neither recommendation was folded in, so
both remain open against `main` — verified rather than assumed:

```
stale_plist()  still greps only for "<string>$APP_DIR/server.py</string>"     → F36 open
find_ytdlp()   still checks only /opt/homebrew/bin and /usr/local/bin         → F37 open
```

**One half of F36 is closed by the merge itself, and it was the urgent half.** Consequence (1)
was that `main`'s self-heal would rewrite the plist without `EnvironmentVariables` and silently
undo the fix. `main`'s `write_plist` now carries the key, so that path is gone. **Consequence (2)
stands:** the agent's PATH is still frozen at install time, and neither `heal_if_moved` nor
`status` can see it drift.

Re-severity: F36 drops from "fold this in" to **optional**, on the same shelf as F31 — a real
defect whose trigger requires installing yt-dlp after the studio, moving Homebrew, or changing
Mac architecture. F37 was already optional and is unchanged, **except that its doc half is now
a gap on `main`**: `studio install` bakes the PATH, so installing yt-dlp afterwards needs a
reinstall, and nothing in either README says so.

**Baton: implementer.** F36 and F37 are two small changes in one file plus one sentence of docs.
Natural home is whichever PR next opens `apps/studio/studio` — the same argument that folded F32
and F34 into Phase 3 rather than giving three lines their own PR.

---

## Thread 13 — background uploads cache (`e13e3e6`, PR 30) — CLOSED 2026-08-22

**Target.** One code commit on current `main`; verify with
`git merge-base --is-ancestor e13e3e6 HEAD`. Scope is `CURRENT.md` §3.4-§3.6 and the explicitly
carried Zoom `*newChat*.txt` ignore rule: authenticated uploads-playlist refresh, an atomic
offline-safe cache, the optional read API, and the no-run upload picker interaction. No link
event, duration match, cleanup, or title join belongs here.

**Implementer receipts.** The pre-SHA three-part audit is in `CURRENT.md`'s final handoff note.
Automated suites pass 35/35: uploads 11, sidecars 15, YouTube fallback 9. Live launchd cold start
answered immediately with the empty API shape, then cached 56 authenticated items including the
private canary. Browser acceptance showed 7 runs plus 51 no-run uploads; choosing one filled the
Add video URL, restored the current run, and did not ingest across the next poll. An isolated
server with a deliberately missing yt-dlp still loaded the real 56-item cache at normal speed,
showed its age, and produced no browser diagnostics.

**Where to look hard.** An expired Chrome login exits 0 with two public rows, so verify that a
no-canary refresh updates/adds but never removes cached ids, while a canary refresh may prune.
Verify request handlers can only read the cache and cannot start or stack yt-dlp. In the UI,
verify upload option values cannot reach `openRun`, an uploads failure preserves both runs and
the last in-memory upload list, and the four-second render never leaves an upload selected. The
cache is derived user data and must remain ignored.

**Baton: reviewer.** No merge without Brian's explicit approval.

---

## Thread 12 — eval star predictability (`d8b21f1`, PR 27) — UNREVIEWED, merged 2026-08-21

Recorded so the ledger does not imply a review that never happened. **PR 27 added
`apps/studio/eval/star_predictability.py` and merged with no review thread and no second reader
— its author was the only person who read it.** Every other code PR in this repo got a thread.

Not re-opened as a review target, because the file is 300 lines of read-only analysis: it opens
`labels.jsonl` and `runs/*.json`, writes nothing, imports nothing outside the stdlib, and no
product code imports it. The realistic failure is a wrong number in [[D-044]], not a wrong
behaviour in the studio — and a wrong number there is checkable by re-running it.

**What would justify opening it:** if [[D-044]] is ever load-bearing for a decision bigger than
"do not build rung 4" — for instance if it is cited to justify deleting collected labels — the
arithmetic deserves a second reader first. Flagged, not scheduled.

---

## Reviewer round — 2026-08-22 (Claude Code), thread 13 / PR 30 / `e13e3e6`

**Verdict: no blocking findings.** Every contract §3.4-§3.6 asks for is implemented as written,
including the four the planner added on 2026-08-21. The gate that blocked this phase was
satisfied with the right kind of measurement — a one-shot launchd job carrying the merged agent
PATH, returning 56 uploads and the canary — rather than another shell spike. That was the entire
point of the gate and it was honoured instead of worked around.

**What I verified myself, and what I took from the audit.** Verified here: 35/35 tests pass on
the branch (`test_sidecars` 15, `test_youtube_fallback` 9, `test_uploads` 11); the request path
contains no subprocess call; `/api/runs` exposes `youtubeId`, which is what the picker's run
matching depends on; upload titles reach the DOM through `escapeHtml`, so a YouTube title
containing markup cannot inject; and three edge behaviours the tests do not cover, probed
directly. Taken from the audit rather than re-run: the in-browser picker pass and the live cookie
gate — both described concretely enough to trust, and re-running them would mean driving Brian's
live Studio.

### Contract conformance

| Contract | Status |
| --- | --- |
| §3.4 one JSON object per line, no pipe delimiter | done, and a test pins a title containing a pipe |
| §3.5 5a merge, never remove; prune only on the canary | `merge_items`, exactly as specced |
| §3.5 5b reuse `ingest.SUBPROCESS_TIMEOUT` | done, asserted by a test rather than assumed |
| §3.5 8 read contract, HTTP 200 empty shape, clamped age | done; the skew clamp returns 0 on a future `fetchedAt` |
| §3.6 no-run uploads only, restore to `S.currentId` | done, via `chooseRunOrUpload` |
| §3.10 fake-executable fixtures | `test_uploads.py`, 11 cases |

Two things beyond the contract, both welcome: the `.gitignore` rule for Zoom's `*newChat*.txt`
pending since the readiness review, and a README section that explains *why* the endpoint answers
200 with nothing rather than just stating that it does.

### F38 — one malformed row discards the whole cache, and the next refresh then deletes the good rows — non-blocking · open

`_validated_cache` is all-or-nothing: it re-normalizes every item and returns `None` if any single
one fails. That is right for the API. But `refresh` decides what to merge against using the same
reader:

```python
previous = read_cache(self.path)
items, authenticated = merge_items(previous["items"] if previous else [], fetched)
```

So one bad row turns "keep the cache" into "lose the cache". Probed on the branch rather than
argued:

```
cache: 5 valid rows + 1 row with an invalid video id
  read_cache()                      -> None (whole cache discarded)
  /api/uploads items                -> 0
  then one unauthenticated refresh  -> 1 item; the 5 good rows are GONE
```

That is the outcome §3.5 5a exists to prevent, reached through validation instead of through
merging. The realistic trigger is not disk corruption — only `write_cache_atomic` writes this
file — it is a **schema change**: `_validated_cache` requires `authenticated` to be a bool, so a
cache written by a future Studio that renames or drops that key is discarded whole.

**Severity is genuinely low**, worth saying plainly rather than inflating: the cache is derived
and refetchable, so the cost is one 30-minute window with a short list, and the next authenticated
refresh heals it completely. **Fix, two lines:** drop invalid rows and keep valid ones; discard
wholesale only when the envelope — channel, `fetchedAt` — is unusable.

**Merge disposition:** deferred as TD-17. PR 30 merged without this optional repair.

### F39 — an authenticated but truncated refresh still prunes silently — non-blocking · open

`merge_items` returns `list(fetched)` whenever the canary is present. The canary proves the
*login* worked. It does not prove the *listing was complete*. Probed:

```
previous 10 rows (canary among them) → fetched 1 row (the canary) → kept 1, authenticated=True
```

Nine rows deleted, no signal. **PR 30 behaves exactly as §3.5 5a specifies**, so this is a finding
against the contract the planner wrote on 2026-08-21, not against this implementation. The canary
rule was built to stop an *unauthenticated* shrink and does that well; it says nothing about a
truncated authenticated one.

**Fix, in the same function:** prune only when the fetch is not a drastic shrink — merge and log
instead when `len(fetched)` falls below, say, half of `len(previous)`. A real deletion moves the
count by one or two; a truncated page moves it by an order of magnitude, and the two are easy to
separate.

**Noted rather than filed: canary rot.** `CANARY_ID` is the hardcoded `Oa0wqetkNcg`. Delete that
video or flip it to private and every future refresh is classified unauthenticated, pruning
switches off permanently, and nothing says so — the cache simply stops shrinking. Cheap insurance
if F39 is addressed anyway: treat any id already in the cache and known unlisted as a canary,
rather than one constant.

**Merge disposition:** deferred as TD-18. PR 30 merged without this optional repair.

### Not findings, recorded so nobody re-raises them

- `/api/uploads` re-reads and re-validates 56 items on every four-second poll. Same family as
  F34's fourteen `labels.jsonl` parses per poll, and at this size not worth a line of code.
- `fetch_uploads`'s dedup loop is convoluted — append, then index, with a `continue` in the
  middle — but correct: last occurrence wins, original order preserved.
- The refresh decrypts Chrome cookies every 30 minutes from a login-time daemon, forever. That is
  what was asked for and the README says so. If the Keychain ACL is ever reset the worker blocks
  on an invisible prompt until `SUBPROCESS_TIMEOUT`, then retains the cache and logs once — which
  is the correct failure.

**Merge outcome:** Brian explicitly approved the merge; PR 30 landed at `9622365`. The restarted
Studio retained all 56 cached uploads including the private canary, and the merged uploads suite
passed 11/11. Thread closed; F38/F39 live on as TD-17/TD-18.
