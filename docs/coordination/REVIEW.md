# Review

Active targets: **PR 10** at `e8d206ca9c715643764e21ded55a9d248c6cda08` and **PR 11** at
`e8943cdb67964a00b30a2893c1bdf83884c8244f`. PR 10 has one blocking record conflict;
PR 11 has one optional error-path fix. PR 9's F20-F23 are resolved at `8a47c2b`.
Threads 1-4 are closed and collapsed to an index; durable outcomes live in `DECISIONS.md` and
`BACKLOG.md`.

Roles stay reversed on thread 5, same as thread 4 and at Brian's instruction: Claude Code
implemented, **Codex reviews**. BugBot is not a second pair of eyes on this one — it failed
seven times on PR #9 against the Cursor usage cap and filed nothing.

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
| 7 — eval scoring scripts | `e8943cd` (PR 11) | **CLOSED** — F25 fixed at `ea698a3`, merged `70b343d` | — |
| 8 — lane as a section break | PR 22, `lane-as-section` | **open** — unmerged, awaiting review | → reviewer |

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

## Thread 6 — matching-label export fold (`e8d206ca9c715643764e21ded55a9d248c6cda08`, PR 10) — OPEN

**Scope.** `mergeNearby` only folds entries inside the two-second window when they would print
the same label. The intention is to enforce [[D-033]] without changing video 1's known export.
The branch's two coordination-document edits are not product code.

**Verification.** Exact head is present on `origin/merge-only-matching-labels`; whitespace check
passes. The one-condition code change preserves the existing time-window and rank behavior, and
the changed condition is a no-op for video 1's known extracted-marker collisions. GitHub has no
CI workflow or commit-status checks configured for this repository.

### F24 — PR 10 creates a second, incompatible `D-035` — blocking · open

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

## Thread 7 — eval scoring scripts (`e8943cdb67964a00b30a2893c1bdf83884c8244f`, PR 11) — OPEN

**Scope.** Two offline CLIs: render a studio run as the transcript accepted by `yt-clipper`, and
score a scratch proposal file without contaminating a canonical run. No product runtime code is
changed.

**Verification.** Exact head is present on `origin/eval-scoring-scripts`; whitespace check
passes. The real video-2 transcript emits **714 lines and 26 GAP flags**, matching the run. A
scratch copy of video 1's 64 proposals reproduces the claimed 45-second results: 9/9 self-created
star recall, 65/67 region recall, and 54/64 precision. The proposal-in-`runs/` guard and current
CI absence were inspected; the guard's rejection path was already covered by the implementer's
recorded check.

### F25 — the intended zero-cue refusal raises `NameError` — optional · open

At `make_transcript.py:78`, the zero-cue branch interpolates `run_id`, but `main` never defines
that name. The existing zero-cue run `Oa0wqetkNcg-20260819-0858` therefore exits 1 with a Python
traceback, not the concise `has zero cues — nothing to hand the skill` explanation. It cannot
produce a bad transcript and does not affect video 2, so this is optional; using `argv[0]` or the
resolved file name fixes it. The inline review comment is posted on PR #11.

**Baton: → implementer (optional; does not hold a merge).**

---

## Thread 8 — lane as a section break (PR 22, `lane-as-section`) — OPEN

**Unmerged, deliberately.** Brian's standing instruction from 2026-08-21: nothing merges without
him saying so. This is the first PR held for that.

**Scope.** `lane` joins `work` on the same `chapter` event. On video 1 the two change at exactly
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

**Baton: → reviewer.**
