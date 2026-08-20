# Review

Active target: **PR 9 — Zoom export ingest** (thread 5). Threads 1, 3 and 4 are closed;
thread 2 closed when PR 4 merged. Durable outcomes from the closed threads were harvested into
`DECISIONS.md` and `BACKLOG.md` and their round-by-round is not kept here.

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
>    PRs 4 and 5 sit on top of PR 3, so `bde4ce7` is not an ancestor of PR 3's HEAD. A cited
>    SHA that is not an ancestor is stale — re-anchor instead of reviewing the wrong tree.
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
| 5 — Zoom export ingest | `5eb55d2` (PR 9) | **open** — no findings filed | → reviewer |

---

## Thread 1 — two-surface product (`eea83b8`) — CLOSED 2026-08-18

Fifteen findings, closed on two different bases — the distinction matters and the earlier
one-line version of this banner erased it.

**F6-F11 and F14-F15 — resolved (8).** Filed by the reviewer, fixed by the implementer at
`6d2ee47` and `eea83b8`, then verified by the reviewer against the shipped code. **F12 —
wontfix**, reason recorded in [[D-026]] along with what would reopen it. **F13 — deferred** to
`TD-3`.

**F1-F5 — verified, never `resolved` (5).** These were written *and* answered inside one
implementer turn reviewing Grok's cleanup plan, so no reviewer ever moved them up the ladder.
They were confirmed by an independent pass rather than taken on trust, and that evidence is
kept here because the detail it summarised is gone:

- The grep audit returns only the classified set — fault path, repair boundary, CSS paint
  tokens, historical prose. No `run.gold`, `goldCount`, `attach_gold`, `RANK.gold` or
  `source: "gold"` anywhere on the tree, and no hits under `docs/sessions/`.
- `05c1414` is a genuine merge of `bde4ce7` and `162e2f4`. No force-push, no rewritten history.
- `api.js` throws only on `data.error`, so the nonfatal `warnings` array cannot clear the run —
  the degraded load survives.
- `migrate_deprecated_key` covers old-only, equal-dual, conflicting-dual and no-key, and the
  network path is unreachable once a deprecated key is present.
- [[D-023]] exists and supersedes wording only, leaving product behaviour intact.
- Not reproducible as stated: the "semantic SHA" cited for the extracted array names no
  canonicalisation. The array is unchanged by `git diff`, so nothing is wrong — the receipt
  simply is not one.

**2026-08-18 third-party re-derivation (Grok).** F1–F5 independently CONFIRMED at the SHAs
they were filed against (`162e2f4` / `05c1414`) and still hold at PR 3/4 HEAD (`eea83b8` /
`43c99dd`). Each item below is now `resolved`. Compared after the fact with the 2026-08-18
Claude verification: no verdict disagreement. Differences of evidence, not of outcome — named
under F2/F3/F4.

Durable outcomes harvested to [[D-023]]-[[D-029]] and `TD-3`-`TD-5`.

**The round-by-round below is retained deliberately.** `README.md`'s wrap-up says to discard it
because "git history and the PR thread already hold" it. Both halves of that premise are false
here, checked on 2026-08-18: `docs/coordination/` is untracked, so the only REVIEW.md in git is
the 58-line original at `e158710` and its deletion at `10686ad` — none of F1-F15 is in any
commit. And PR 3's thread carries five Cursor Bugbot "usage limit reached" notices and zero
reviews; `gh pr checks` reports Bugbot `skipping` on both PR 3 and PR 4, so no automated review
ever ran on this code. Collapse this section when `docs/coordination/` is committed, and not
before.

Two process notes worth carrying rather than discarding:

- A hand-rolled "semantic SHA" with no stated canonicalisation is not a receipt — the next
  reader cannot recompute it. Cite `git diff`, or a named hash of a named file.
- F1-F5 were written and answered by the same turn. They held up, but the thread had no
  adversarial pass until one ran, and that pass produced F6-F15 — three blocking, two of them
  silent data loss. Self-review is a starting point, not a verdict.

---


**Scope:** https://github.com/bsze24/yt-clip-marker/pull/3 — `apps/studio/` code (not `runs/`
or `labels.jsonl`), the `content/` → `apps/extension/` move, the rewritten PRD,
`docs/clip-schema.md`, and `AGENTS.md` as of that commit, which predates this directory.

**Where to look hard:** `CURRENT.md` §1. Short version — one keyboard dispatcher with focus
returning from the player iframe, exact-start-then-≤2s alignment keyed on row identity,
append-only persistence with `unmiss` tombstones, the export fold's rank and skip rules, path
allowlisting in `server.py`, and anything growing the extension past its freeze.

**Before filing a timestamp finding:** check stored identity, not the displayed time. The
grid shows the caption a clip was aligned onto. See the vocabulary section of `README.md`.

**Verification:** implementer evidence is recorded below. No test suite. The reviewing agent can boot the server, hit
the API, and read the code; it cannot press `j`. Findings about grid behaviour, focus, or
clipboard output get filed with "not verified, needs a browser" and stay open until Brian or
a browser agent confirms. See `CURRENT.md` §1.

### F1 — definition of done contradicted immutable history — blocking · resolved

**Finding.** A repo-wide `rg gold` could not be clean while `labels.jsonl` and session logs
retain historical wording, and the repair CLI itself must name the key it migrates. Split
live structural identifiers from a case-insensitive prose audit and classify every allowed
compatibility/historical hit.

**Implementer response — addressed at `162e2f4` / `05c1414`.** Structural checks now reject
the old script name, API alias, JS property fallback, export source and run-file key. Remaining
hits are classified as migration/fault boundaries, CSS paint tokens, historical prose, or
append-only feedback.

**Reviewer re-derivation — 2026-08-18 (Grok) · CONFIRMED → resolved.** Ran
`git grep -in gold` at `162e2f4` (26 hits), `eea83b8` (26 hits, identical set), and
`43c99dd` (33 hits). Every hit classified: CSS `--gold` / `--gold-text` in `styles.css`;
migration boundary `attach_extracted.py:27-36`; fault path `server.py:189,191,193` and
`ui/runs.js:13,17`; historical prose in `README.md`, `clip-schema.md`,
`two-surface-handoff.md`, `youtube-clip-marker-prd.md`; on PR 4 only, seven
`labels.jsonl` feedback/rationale strings (append-only, `source` is `human-miss` not
`gold`). Zero hits under `docs/sessions/` on any of those trees. Targeted misses:
`run.gold`, `goldCount`, `attach_gold`, `RANK.gold`, `source: "gold"` — none at
`162e2f4`, `eea83b8`, or `43c99dd`. `git ls-tree` shows `attach_gold.py` at `6ebc21a`
replaced by `attach_extracted.py` at `162e2f4`. Video-1 run keys at `43c99dd` are
`videoId,url,title,createdAt,markers,cues,descriptionText,extracted` — no `gold` key.
Workspace HEAD `af478b4` has no `apps/`; the claim is about the PR 3/4 trees.

### F2 — published branch instructions risked stale anchors and contamination — blocking · resolved

**Finding.** Updating PR 3 invalidates the `6ebc21a` review anchor, while the local PR 4
branch contains two unrelated, unpushed session-log commits. Rebase/force-push would also
rewrite published history.

**Implementer response — addressed at `162e2f4` / `05c1414`.** Brian explicitly reassigned
the work. PR 3 was re-anchored. PR 4 was built from remote `bde4ce7` in a clean worktree and
merged corrected PR 3 without force; the unrelated local session-log commits were not pushed.

**Reviewer re-derivation — 2026-08-18 (Grok) · CONFIRMED → resolved.** `git cat-file -p`
shows two parents each: `05c1414` = `bde4ce7` + `162e2f4`; `43c99dd` = `6de5aee` +
`eea83b8`; `6de5aee` itself = `05c1414` + `6d2ee47`. `git log --graph --oneline 43c99dd
^480475e` is a merge restack; `a051667`, `bde4ce7`, and `6ebc21a` remain ancestors, which
a rebase of published history would have replaced. GitHub issue timelines:
`head_ref_force_pushed` count is 0 on both PR 3 (10 events) and PR 4 (8 events); current
heads match `eea83b8` / `43c99dd`. Local `codex/pr-4-video-1-store` is ahead 2, behind 7
of origin: `6075db6` (`session-log: 2026-08-17 grok studio-eval-skilleval`) and
`549d667` (`session-log: 2026-08-16 grok studio-eval-handoff (update)`).
`git merge-base --is-ancestor` of each against `origin/codex/pr-4-video-1-store` fails;
`git log --branches --not --remotes` lists both. They were never pushed.

### F3 — a top-level API error would prevent the required degraded load — blocking · resolved

**Finding.** `ui/api.js` throws on `data.error`, so the proposed error shape would clear the
run instead of rendering captions, skill markers and additions.

**Implementer response — addressed at `162e2f4`.** `/api/run` returns a nonfatal `warnings`
array. `extractedList` is pure and strict; `openRun` emits the console fault and owns a
persistent alert separate from save status. Browser verification rendered 1,199 rows and
zero extracted cells under the fault.

**Reviewer re-derivation — 2026-08-18 (Grok) · CONFIRMED → resolved.** Read
`eea83b8:apps/studio/ui/api.js`: throws only on `!res.ok || data.error`. `warnings` is not
consulted. `openRun` assigns `S.current = await api(...)` then `showRunWarnings` and
`renderGrid`; a warning cannot take the catch path that nulls the run. `extractedList`
returns `Array.isArray(run.extracted) ? run.extracted : []` — no `gold` fallback.
Live probe (not the repo store): `git archive 43c99dd apps/studio` into
`/tmp/yt-clip-f3-*`, renamed the video-1 `extracted` key to `gold` (24 items), booted that
copy's `server.py`, `curl /api/run?id=YYW4Q1Nivg8-20260814-1248`. HTTP 200; top-level keys
`id,run,feedback,additions,edits,annotations,warnings`; **no `error` field**;
`warnings = [{code: deprecated-run-key, key: gold, …}]`; `run.cues` 1464, `run.markers`
64, `additions` 21, `gold` present, `extracted` absent so `extractedList` would be `[]`.
Stderr printed the fault line. Server killed; repo `runs/` / `labels.jsonl` untouched
(this branch has no `apps/`). **Not verified in a browser** — grid pixels and the "1,199
rows" count are implementer evidence I did not re-paint. The finding is about the API
shape that would have cleared the run; that shape is not what shipped.

### F4 — the repair CLI could overwrite truth by refetching — blocking · resolved

**Finding.** Migration needs explicit state handling: old-only exact rename, equal dual-key
cleanup, conflicting dual-key abort, and network fetch only when no old key exists.

**Implementer response — addressed at `162e2f4`.** `migrate_deprecated_key` implements those
states. The real 24-item array retained semantic SHA-256
`a292b9793284c464dda7c058e563b3e172f5faf9df91eee7102804c439a14b0f`.

**Reviewer re-derivation — 2026-08-18 (Grok) · CONFIRMED → resolved.** Read
`migrate_deprecated_key` at `eea83b8:apps/studio/attach_extracted.py:25-37`. `main`
returns after a successful migration **before** `parse_video_id` / `fetch_title_and_description`.
Imported the function and drove the CLI against files under `/tmp/yt-clip-f4-*` only.

| state | result |
| --- | --- |
| old-key-only | copies `gold` → `extracted`, pops `gold`; SHA of the array unchanged; sibling fields kept |
| equal dual keys | pops `gold`, leaves `extracted`; action `removed duplicate gold[]` |
| conflicting dual keys | `ValueError`, CLI rc 1, **file bytes identical** (SHA `594f20f9…57ca` before and after) |
| no deprecated key | function returns `None`; CLI falls through to fetch |

Network contrast with a parseable watch URL (`v=AAAAAAAAAAA`): gold present finished in
0.031s with a migrate message and no yt-dlp; no-gold ran 22.3s and failed
`This video is unavailable`, file unchanged. Same URL as an argv extra is ignored once a
deprecated key exists. Real video-1 array: gold-only copy of the `43c99dd` run migrated in
0.031s; canonical JSON of the 24 extracted items matched the original, as did `markers`,
`cues`, and `descriptionText`. Could not construct an input that dropped stored stamps —
conflict aborts rather than choosing; empty `gold: []` migrates to empty `extracted` and
skips fetch, which withholds a refill, not existing data. The cited "semantic SHA" still
names no canonicalisation, so I did not recompute it; array equality is the receipt.

### F5 — durable fallback semantics could not remain implicit — blocking · resolved

**Finding.** Existing decisions still used the old storage vocabulary and fallback semantics;
accepted entries must not be silently rewritten.

**Implementer response — addressed in [[D-023]].** A new dated decision supersedes only the
old key/fallback wording while preserving the extracted lane and copy-timestamps behavior.

**Reviewer re-derivation — 2026-08-18 (Grok) · CONFIRMED → resolved.** Read working-tree
`docs/coordination/DECISIONS.md` (D-023 is **not** on `eea83b8` / `43c99dd`; those trees
have no `docs/coordination/`. It also is not in `e158710`. The supersession lives in this
untracked file, which is the decisions ledger the finding asked for). D-023 names the
extracted lane, the visible non-alias fault, lossless repair, and "supersedes only the old
storage vocabulary and fallback wording in D-011, D-013, D-020 and D-022". Those four
entries still say `gold` in their original text — not silently rewritten. Code at
`6ebc21a..162e2f4` matches that scope: `extractedList` / `extracted_markers` drop the
`gold` fallback (the documented semantic change); `RANK.gold` deleted while
`RANK = { extracted: 0, miss: 1, skill: 2 }` keeps extracted winning a cluster;
`goldCount` removed from the ingest JSON; `attach_gold.py` renamed. Product behaviour
checked in source, not in a browser: `grid.js` still builds an extracted column from
`extractedList`; `export.js` still pushes every extracted and every added marker and only
gates **skill** markers through `keepSkill` (`isCheck` / taxonomy keep / skip `isWrong`);
`evalMark` still maps `check` → `g`. No smuggled change to the extracted lane, the
never-drop rule, or the eval `g` channel. Clipboard output itself: not verified, needs a
browser.

### Reviewer verification — 2026-08-18

Independent re-check of the cleanup before reviewing the rest of the tree. F1–F5 were written
and answered by the same turn; a reviewer confirming them is not redundant.

- **F1 grep.** `git grep -in gold 162e2f4` returns exactly the classified set: fault path
  (`server.py:189,191,193`, `runs.js:13,17`), repair boundary (`attach_extracted.py:27-36`),
  CSS tokens (`styles.css:12,13,161,219,225,293`), and prose (`README.md:46`,
  `clip-schema.md:35`, `two-surface-handoff.md`, `youtube-clip-marker-prd.md:107`). No
  `run.gold`, `goldCount`, `attach_gold`, `RANK.gold`, or `source: "gold"`. Zero hits under
  `docs/sessions/` on this tree. Confirmed.
- **F2 branch state.** `05c1414` is a real merge of `bde4ce7` and `162e2f4`. No force-push,
  no rebase of published history. Confirmed.
- **F3 nonfatal load.** `api.js` throws only on `data.error`; `warnings` is a separate array,
  so the degraded load survives. Confirmed by reading; browser evidence accepted per Brian.
- **F4 CLI states.** `migrate_deprecated_key` covers old-only, equal-dual, conflicting-dual,
  and no-key. The fetch path is unreachable once a deprecated key exists. Confirmed.
- **F5 supersession.** [[D-023]] exists and supersedes wording only. Confirmed.
- **Data.** Video 1 at `05c1414`: one changed line, 24 `extracted[]` entries, 64 markers,
  1464 cues. `labels.jsonl` SHA-256 matches `bde4ce7` byte-for-byte. Confirmed.
- **Not reproducible as stated.** The "semantic SHA `a292b979…14b0f`" for the extracted array
  cites no canonicalisation, so it cannot be recomputed. The array itself is unchanged by
  diff, so nothing is wrong — the receipt is just not a receipt. Prefer `git diff` over
  hand-rolled hashes.

The cleanup is clean. The findings below are the rest of the PR 3 tree, which had not been
reviewed.

### F6 — `copy timestamps` emits an invalid chapter list when the first clip has no work — blocking · resolved

**Finding.** `export.js:142-147` injects the required `0:00` stamp after the first
non-timestamp line. When the earliest clip carries no `work` but a later one does, that line
is a *later* section header, so `0:00 Start` lands mid-list and out of order.

Reproduced by running the real `mergeNearby` / `descriptionTimestampText` logic on two clips
(`0:30` with no work, `1:40` work `Eb Blues`):

```
0:30 intro chat

Eb Blues
0:00 Start
1:40 blues head
```

YouTube requires the first chapter at `0:00` and ascending stamps; this output satisfies
neither, so the whole description silently stops being chapters. With `work` on the first
clip the output is correct, which is why it survives a happy-path check. Taxonomy is
optional, so the broken shape is the ordinary case for a lightly-annotated run.

**Implementer response — addressed at `6d2ee47`.** `descriptionTimestampText` now inserts
`0:00 Start` after a header only when the first clip owns that header; otherwise it prepends
the stamp. The two-clip no-work-first reproduction now starts `0:00`, `0:30`, then the later
`Eb Blues` header. The existing first-work case still parks `0:00` under that header.

**Reviewer verdict — resolved at `6d2ee47`.** Re-ran the original reproduction against the
shipped `descriptionTimestampText`. No-work-first now emits `0:00 Start`, `0:30 intro chat`,
then the `Eb Blues` header. Work-first still parks `0:00` under the header. A first clip
already at `0:00` correctly gets no injected stamp. The fix keys on `clips[0].work` rather
than searching the rendered lines, which removes the class of bug rather than the instance.

### F7 — the export fold collapses clips further apart than the 2s window — blocking · resolved

**Finding.** `export.js:92-106` compares each item to `out[out.length-1]`, and `mergePair`
adopts the *kept* item's start. When a lower-rank item wins, the cluster anchor moves forward
up to 2s, and the next comparison is against the new anchor. Merging is transitive, so a chain
folds items arbitrarily far apart.

Reproduced with three real-shaped items at `10.0` (skill), `11.5` (extracted), `13.0` (skill):
all three collapse to one line at `11.5`. The first and last are 3s apart — outside `MATCH`.

This drops added and skill markers from the only export path, which is the one thing
`export.js:2` promises it never does. Anchor the window to the cluster's first start, or to
the kept item's start fixed at cluster open.

**Implementer response — addressed at `6d2ee47`.** `mergeNearby` now keeps an immutable
`firstStart` per cluster and compares every candidate to it. The reported `10.0`, `11.5`,
`13.0` chain produces two clips: the extracted clip at `11.5` and the skill clip at `13.0`.

**Reviewer verdict — resolved at `6d2ee47`.** Re-ran the `10.0 / 11.5 / 13.0` chain: two
clips out, `11.5` and `13.0`, as claimed. `firstStart` is set once at cluster open and never
reassigned, so the window cannot walk. Checked the boundary too — `10.0 / 12.0 / 12.5` now
splits after `12.0` instead of chaining. Sorted input makes the dropped `Math.abs` safe.

### F8 — one shared debounce handle cancels writes across unrelated fields — blocking · resolved

**Finding.** `S.saveTimer` (`state.js:40`) is cleared by every input path: feedback
(`persist.js:60`), reject reason (`:69`), relabel (`:104`), miss description
(`main.js:144`), and combo lane/work (`main.js:154,159`). `state.js:38-40` documents this as
deliberate — "only the latest edit lands" — which is right for repeated keystrokes in one
field and wrong across targets.

Type a note on marker A, then within 400ms touch the lane on row B: A's write is cancelled
and never retried. `queueSave` and `queueWrongReason` have already written
`S.current.feedback` optimistically, so the grid keeps showing A as saved, the status line
never leaves "saved", and the value is gone on reload. `queueRelabel` loses it more quietly
still — the DOM holds the typed text while `S.edits` never changes.

Key one timer per target (`Map` keyed by field+id), or flush the pending write before
starting a new one.

**Implementer response — addressed at `6d2ee47`.** Debounces are keyed by run, record and
event stream. Added-marker description and taxonomy deliberately share one key and one full
record snapshot, while unrelated rows and feedback/relabel/annotation streams do not cancel
one another. Browser verification wrote feedback on marker 4 and taxonomy on marker 1 within
400 ms and observed both append-only events; editing description and lane on one added marker
produced one event containing both values.

**Reviewer verdict — resolved at `6d2ee47`.** Keys are `runId:stream:id`, so two rows and two
event streams no longer share a handle. Three things beyond the finding are right and worth
recording: every queued write captures `runId` and its own payload snapshot, so a run switch
mid-debounce still lands the write against the correct run instead of dropping it;
`isCurrentRun` gates only the UI mutations, not the append; and `submitComposer` /
`persistUnmiss` cancel the matching pending write before issuing their authoritative one.
Added-marker description and taxonomy sharing one key is correct — both mutate the same
`S.additions` entry before snapshotting, so whichever fires last carries both values.

### F9 — `labels.jsonl` records a reject as `verdict: "note"` — non-blocking · resolved

**Finding.** `server.py:200-207` knows three verdicts: `check`, `note`, `blank`. The UI knows
five channels, and `README.md` says they "must not be collapsed". `x` has no server-side
verdict, so every reject is written as `note`.

Measured on the PR 4 log: of 193 `note` events, **121** carry feedback that is `wrong` or
`wrong: …`. The first is `markerIndex 1`. The folded ledger's `x 24` is reconstructible only
by re-parsing `feedback` text; the durable `verdict` field cannot produce it.

`list_runs` inherits this — `noteCount` counts rejects as notes. Nothing is lost, because the
text survives, but the field that names the channel does not name it. Add a `wrong` verdict
and leave existing lines alone; the folder already reads text.

**Implementer response — addressed at `6d2ee47`.** New `wrong` and `wrong: …` writes receive
`verdict: "wrong"`; `list_runs` reports `wrongCount` separately and excludes it from notes and
blanks. Existing history is untouched. A real API append with `wrong: review-f9` returned and
stored the `wrong` verdict.

**Reviewer verdict — resolved at `6d2ee47`.** Verified against a throwaway copy of the PR 4
store, not the repo's. A real `PUT /api/feedback` with `wrong: reviewer probe` stored
`verdict: "wrong"` and moved `wrongCount` 24 → 25 and `blankCount` 14 → 13. `list_runs` on
untouched history reports `check 23 · wrong 24 · note 3`, which matches the folded ledger's
`g 23 · x 24 · note 3` exactly — the count the old schema could not produce.
`current_feedback_map`'s skip list was correctly left alone; adding `wrong` to it would have
emptied the feedback map, and it wasn't.

### F10 — feedback re-paint can colour the wrong row — non-blocking · resolved

**Finding.** `persist.js:50` selects `tr[data-markers*="${index}"]`. `data-markers` is a
comma-joined id list (`grid.js:386`), and `*=` is a substring match, so index `1` also matches
a row whose list contains `12`, `10`, or `21`. `querySelector` returns the first such row in
document order, which colours a marker the user did not grade until the next `renderGrid`.

`composer.js:169` and `:199` parse the same attribute correctly with `.split(",")`. Use that
here, or match on the `[data-marker]` block id.

**Implementer response — addressed at `6d2ee47`.** Repaint now selects the exact
`[data-marker="<index>"]` block and walks to its owning row. Browser verification of marker 4
found that exact block's row carrying the expected `note` class.

**Reviewer verdict — resolved at `6d2ee47`.** `[data-marker="…"]` is an exact match on a
unique block, and `.closest("tr")` reaches the owning row. `CSS.escape` output is still fine
here — inside a quoted attribute value, `\34 ` and `miss\:280` are valid escapes for `4` and
`miss:280` — though the escape is now decorative rather than load-bearing.

### F11 — `rowKey` is positional, so row identity dissolves on any list change — non-blocking · resolved

**Finding.** `grid.js:192-196` prefixes the key with `i`, the index in the *filtered* row
array. Adding a clip, toggling `all captions`, or toggling `hide filler` renumbers every later
row, so the stored key stops matching and `restoreSelection` (`:30-32`) falls back to start
time — the exact thing `grid.js:2-3` says must never decide selection. The persisted cursor
(`state.js:84`) has the same problem across reloads.

Not a live bug today, because the fallback usually lands somewhere sensible; it does become
one wherever duplicate starts are real, which is the case the design exists for. Drop `i` from
the key, or add a stable per-row id at build time.

**Implementer response — addressed at `6d2ee47`.** Rows now receive stable ids at build time:
cue array identity, extracted identity, or marker identity. The filtered-list index and
mutable row content are absent from `rowKey`. Browser verification kept selection on
`cue:308` across both `hide filler` and `all captions` changes.

**Reviewer verdict — resolved at `6d2ee47`.** Row ids are assigned at build time from the
source collection (`cue:N`, `extracted:eN`, `marker:<index>`), all namespaced, so no
collisions. Neither the filtered index nor mutable row content survives in the key. Stale
keys persisted in `localStorage` from the old scheme simply miss and fall back to start time
once, which is the intended degradation.

### F12 — no fallback path for focus returning from the player iframe — not verified, needs a browser · wontfix

**Finding.** `player.js:92-105` is only reached from explicit actions and from
`onStateChange`. An iframe interaction that changes focus without changing player state —
scrubbing the embed's progress bar while paused, clicking its chrome — leaves focus inside the
iframe with no event in the parent document, so the dispatcher goes deaf until the next state
change.

Filed per the thread's verification rule: reasoned from the code, not observed. A
`window.blur` listener or a low-rate focus poll would close it if it reproduces.

**Implementer response — wontfix, not reproducible in the browser at `6d2ee47`.** The
absolute `.player-catcher` covers the full iframe (`1233×378` versus the iframe's
`1233×374`) with `pointer-events: auto`, so the paused-control interaction described in the
finding cannot reach the iframe. Clicking the player surface focused `#gridWrap`. A blur
poll would therefore add timing behavior for an unreachable path; reopen with a concrete
interaction that bypasses the catcher if one appears.

**Reviewer verdict — wontfix accepted.** `.player-catcher` is `position: absolute; inset: 0;
z-index: 1` over the iframe, so pointer events cannot reach the embed, and `keys.js`
`preventDefault`s every `Tab`, so focus cannot walk into it either. Both routes into the
finding are closed by construction. Worth stating the trade the catcher makes, since it is
not written down anywhere: the embed's own controls — scrub bar, captions button,
fullscreen — are unreachable by design, and all transport is the page's keyboard.

### F13 — the whole event log is re-parsed per accessor — optional · deferred

**Finding.** `read_label_events` reads and parses `labels.jsonl` end to end on every call.
`/api/run` does it five times (feedback, additions, edits, annotations, and again inside
`append_*`); `/api/runs` does it once per run in the `list_runs` loop, and `main.js:180` polls
that endpoint every 4s. Cost is O(runs × events) per poll.

553 lines makes this free today. It is the kind of thing that stops being free without
announcing itself. One cached parse keyed on file mtime would do.

**Implementer response — deferred to TD-3.** Correctness and append-only behavior are more
valuable than a cache at the current 553-event scale. `BACKLOG.md` now names a measurable
trigger and the mtime-keyed direction so the issue is not lost.

**Reviewer verdict — deferral accepted.** TD-3 records the location, the mechanism and the
trigger. Correct call at 553 events.

### F14 — `s` reverts a work/lane edit that was already saved — non-blocking · resolved

**Finding.** `toggleStar` (`persist.js:246-259`) rebuilds `S.liveTax` from the row's
`data-tax-*` attributes. Those attributes are written at render time and nothing re-renders
the grid after a taxonomy save — `persistTaxonomy` updates `S.annotations` and the save
status, never the DOM.

So: select a row, edit `lane` to `abc`, leave the field. `finishComboEdit`
(`suggest.js:208-219`) reads the live input, sets `S.liveTax.lane = "abc"` and persists it —
correctly. Now press `s`. `s` only reaches `toggleStar` once focus is out of the combo, so
this is the ordinary annotate-then-star order, not a race. `toggleStar` overwrites
`S.liveTax` from the stale dataset, which still says the pre-edit lane, and persists that.
The `abc` write is undone by the next append, and `renderGrid` at the end of `toggleStar`
shows the old value.

Pre-existing, not introduced by `6d2ee47` — I missed it in the first pass. It is the same
shape as F8 (a write cancelled by an unrelated action) with the DOM as the stale source
instead of a shared timer, which is why the F8 fix does not reach it. Merge the star into the
live `S.liveTax` instead of rebuilding from `dataset`, or re-render the row after a taxonomy
save so the dataset stops lying.

**Implementer response — addressed at `eea83b8`.** `toggleStar` now reuses `S.liveTax` when
it belongs to the selected taxonomy record, changing only the `star` tag; render-time row
attributes remain a fallback for a genuinely different selection. Browser verification
reproduced the stale DOM (`lane` input `review-f14-lane`, dataset still `Transcription`),
then pressed `s`. Both appended annotation events retained `review-f14-lane`, and the second
added `star`.

**Reviewer verdict — resolved at `eea83b8`.** The `sameLiveTax` guard is the right shape:
`S.liveTax` is reused only when its type and id match the selected row, and it is genuinely
fresher than the dataset — `suggest.js` maintains `tags` through `addTag` / `removeTag` /
`pickSuggest` and `lane` / `work` through `finishComboEdit`, while `syncLiveTax` resets it
from the DOM on every render. The guard also covers the case that motivated keeping the
fallback: `followPlayhead` moves the selection without re-rendering, so `S.liveTax` can point
at the previous row; type and id then differ and the new row's attributes win. Ids are unique
per record, so the guard cannot match the wrong row.

### F15 — `blankCount` still reports annotated keeps as unreviewed — non-blocking · resolved

**Finding.** F9 fixed the reject channel. The keep channel has the same collapse and is still
live. `list_runs` (`server.py:401-425`) derives `blankCount` from feedback text alone and
never reads annotations, so `README.md`'s "taxonomy with no `g` — an ordinary keep, not a
blank" and "blank feedback and no taxonomy — genuinely unreviewed" land in the same bucket.

Measured on the PR 4 store: the API reports `blankCount: 14` for video 1. The folded ledger
for the same run says `keep 14 · blank 0`. Every one of those 14 is an annotated keep; none
is unreviewed. Anything reading the API — a future dashboard, a coverage check, an agent
deciding what still needs a pass — concludes 14 markers are untouched when zero are.

`load_annotations(run_id)` already returns what is needed. Split them: `keepCount` for
markers with taxonomy and no `g`, `blankCount` for the genuinely untouched.

**Implementer response — addressed at `eea83b8`.** `list_runs` now applies the channel
precedence `check → wrong → note → annotated keep → blank`, exposes `keepCount`, and subtracts
keeps from `blankCount`. The same collapse existed in the live grid header and was fixed in
the same pass. Against an untouched copy of PR 4, both API and browser report
`23 check · 24 wrong · 14 keep · 3 notes · 0 blank`.

**Reviewer verdict — resolved at `eea83b8`.** Confirmed independently: `/api/runs` against an
untouched copy of the PR 4 store returns `check 23 · wrong 24 · keep 14 · note 3 · blank 0`,
summing to all 64 markers, against a ledger that reads `g 23 · x 24 · keep 14 · note 3 ·
blank 0`. The five channels now reconcile exactly. Catching the same collapse in the grid
header was not asked for and is the right call — the API and the header would otherwise have
disagreed about the same run.

One consequence to record rather than file: `list_runs` now folds the event log a third time
per run (`load_annotations` joins `load_additions` and `current_feedback_map`), polled every
four seconds. That does not change the shape of TD-3, but it moves its trigger closer.

---

## Thread 2 — video 1 store (`43c99dd`)

**Scope:** https://github.com/bsze24/yt-clip-marker/pull/4 —
`apps/studio/runs/YYW4Q1Nivg8-20260814-1248.json` and `apps/studio/labels.jsonl`. Data only.

Three questions: do the shapes match `docs/clip-schema.md`; does the event log honour row
identity ([[D-008]]) and tombstones rather than rewriting history ([[D-002]]); and does the
data reconcile with the folded ledger in
`docs/sessions/2026-08-16-YYW4Q1Nivg8-folded-ledger.md` — 64 markers (`g` 23 · `x` 24 ·
keep 14 · note 3 · blank 0), 21 live added markers, 4 tombstoned adds, 24 extracted.

A mismatch in those counts is a real finding. So is a "blank" count above zero, which would
mean taxonomy-without-`g` keeps were misclassified as unreviewed.

**Verification:** implementer confirmed 64 skill markers, 24 extracted markers and no
deprecated run key. `labels.jsonl` remains 553 lines and byte-identical to `bde4ce7` at
SHA-256 `1ea26c91d6b046f87f4c639c41c45914661eb767b844eb32234be96f7d80acf1`.

**Reviewer evidence carried over from thread 1 — 2026-08-18.** Checked while reviewing PR 3,
independently of the implementer's claims. Not a verdict; it is the part of the third question
that is already answered.

- Run file keys are `videoId`, `url`, `title`, `createdAt`, `markers`, `cues`,
  `descriptionText`, `extracted` — no deprecated key. 64 markers, 1464 cues, 24 extracted.
- `labels.jsonl` is 553 lines and byte-identical to `bde4ce7` at every restack: `05c1414`,
  `6de5aee` and `43c99dd` all hash to `1ea26c…acf1`. No review round rewrote the append-only
  store, and the test appends made during the review went to a disposable copy.
- `git diff eea83b8 43c99dd` is those two data files and nothing else.
- The five-channel fold reconciles exactly. `/api/runs`, served by the real server against a
  disposable copy of this store, returns `check 23 · wrong 24 · keep 14 · note 3 · blank 0`,
  summing to all 64 markers, against a folded ledger reading `g 23 · x 24 · keep 14 · note 3 ·
  blank 0`. The "blank above zero" trap named above is closed — it read 14 before [[D-028]].
- Tombstones are honoured: 5 `unmiss` events fold out of `load_additions` rather than deleting
  anything.

**Verdict — 2026-08-19: clean. Merge.** All three scope questions answered.

**Shapes match `docs/clip-schema.md`.** Run file: all 8 documented keys, no extras, no `gold`,
11-char `videoId`, ISO-8601 `createdAt`, every array ascending. `labels.jsonl`: 553/553 lines
parse; every event carries all 7 required fields; every `verdict` is in the contract's set;
`markerIndex` in range on marker events and `null` on every `miss`/`unmiss`; all tags lowercase
and deduped; one `runId` and one `videoId`, both matching the run file. `end` is null on all 553
events and all 64 markers, per [[D-012]]. Legacy `kind` present and readable per [[D-009]].

**Row identity and tombstones hold** ([[D-007]], [[D-002]]). Nothing is rewritten in place. 5
`unmiss` events fold to 4 tombstones because `200.0` was deleted twice; nothing was re-added.

**Counts reconcile with the folded ledger exactly** — 64 markers as `g` 23 · `x` 24 · keep 14 ·
note 3 · blank 0, 21 live added markers, 4 tombstoned, 24 extracted.

### F16 — the standing trap overstates that added markers never drift — non-blocking · fixed

**Finding.** `README.md`'s standing trap claimed added markers inherit a caption time "by
construction". Three of video 1's 21 do not: `1:19:27`, `1:19:54`, `1:23:04`, all sitting exactly
on extracted stamps with an empty `cueText`. They were created by pressing Enter on a
description-only row — the "YT overview / not a caption" rows the grid builds for a stamp with no
caption within 2s.

Not a defect in PR 4. PR 4's data is correct and is what exposed it; the wrong claim was written
into `main` on 2026-08-18 by the reviewer. Fixed in the same commit as this verdict.

### F17 — three duplicate writes leave file order and timestamp order disagreeing — non-blocking · open

**Finding.** Lines 75/76, 131/132 and 160/161 are byte-identical except `recordedAt`, written
1.7-2.5 ms apart, and in each pair the earlier timestamp is written second. `append_label` and
friends stamp `datetime.now()` while building the event, then `append_event` acquires
`LABELS_LOCK` — so two rapid writes can stamp in one order and land in the other.

Measured severity: none today. The server folds in file order everywhere
(`read_label_events` → last wins), so its answer is deterministic, and the pairs are identical,
so both orderings agree. The hazard is a reader that sorts by `recordedAt` — the obvious thing to
do, and what a skill-scoring pass would do — meeting a future pair that *does* differ. Pairs with
different content are the case to worry about; there are none in this store.

**Actions taken 2026-08-19.** The file-order rule is now stated in `apps/studio/README.md`, which
protects the reader actually at risk. The cause — a duplicate write — is `TD-10`: the add-clip
form's guard is a check that a form is open, and the form does not close until after the server
replies, so a second submit inside that window passes. The taxonomy half of this was already
fixed by [[D-024]]. Stamping inside the lock was considered and rejected: it would make the
duplicate pair look correctly ordered, hiding the only visible symptom. Related to `TD-4`, the
other reason an external reader of this log can go wrong.

---

## Thread 3 — session write-head (`949cb7b`)

**Scope:** https://github.com/bsze24/yt-clip-marker/pull/5 — the curated session log and the
folded ledger under `docs/sessions/`.

Check what the commit contains, not what it claims. Session logs have duplicated before, and
a duplicate should be deleted rather than committed and then explained. The log's chronology
starts at the first `/yt-clipper` run on 2026-08-14, not at the last thing that happened —
if a later log starts at the leftovers, that is a real finding.

**Where to look first — carried from the PR 3 review.** PR 5 parents at `a051667`, PR 3's
*first* commit, which predates the `gold[]` → `extracted[]` rename ([[D-023]]). Both files it
adds are written in the retired vocabulary: `2026-08-16-YYW4Q1Nivg8-folded-ledger.md` has a
literal `gold` source column with `| gold | gold |` rows throughout, and the eval-handoff log
describes ingest as producing "gold".

That is not the historical prose [[D-023]] grandfathers. Thread 2's scope cites that folded
ledger as the ground truth its counts must reconcile against, so it is a live reference landing
after the rename in the dead words. Decide which it is — rewrite the source column to
`extracted`, or date both files as pre-rename artifacts in their own opening lines — and record
the choice. The ledger's numbers are correct either way; only its vocabulary is stale.

**Verdict — 2026-08-19: superseded. Close PR 5 rather than merging it.**

Both files it adds are older copies of files `main` already carries under different names, so a
merge would not conflict — it would silently duplicate.

- `docs/sessions/2026-08-16-1507-claude-studio-eval-handoff.md` is the **same session log** as
  `main`'s `docs/sessions/2026-08-16-1507-grok-studio-fable-lock.md`: same date, same `15:07`,
  same `surface: grok`, same `commit: 56fac83`, same `track`, same 101 chronology beats. The
  only differences are `revised:` — PR 5 has `2026-08-16 16:34`, `main` has `2026-08-17 17:45` —
  and the vocabulary. `main` carries the later revision.
- `docs/sessions/2026-08-16-YYW4Q1Nivg8-folded-ledger.md` is the pre-rename folded ledger, 40
  hits on the retired word across 238 differing lines: a `gold` source column, `| marker |` for
  what is now `| skill |`, and "Reject this **marker**" for "Reject this **skill marker**".
  `main` carries the corrected copy at `docs/reference/`, with zero hits.

Checked what a merge would actually apply, not what `git diff main..branch` shows — PR 5's
merge-base is `a051667`, so the branch's apparent reversion of `apps/studio/` (re-adding
`attach_gold.py`, undoing every F6-F15 fix) is an artifact of the base, not something a merge
would do. It would apply exactly the two files above.

The thread's own scope note anticipated this: "session logs have duplicated before, and a
duplicate should be deleted rather than committed and then explained." That is what happened.

_No findings — the branch is obsolete rather than wrong._


---

## Thread 4 — local video mode (`c4de36d`) — CLOSED 2026-08-19

**Closed on merge.** Two findings, both non-blocking, both fixed at `fced73f` and verified by
the reviewer; PR 8 merged to `main` at `71b9d82`. F18 (sidecar lookup adopting the adjacent
recording) and F19 (a non-media `HEAD` sending a body) are `resolved`. The round-by-round below
is kept because thread 5 widens F18's matching surface and a reviewer will want the original
reasoning to hand.

Durable outcomes harvested as [[D-034]]–[[D-038]]. The one gap this thread never closed —
playback on an actually disconnected machine — was closed by use rather than by test: the Zoom
run played in the air on intermittent service during the session that produced PR 9. No
automated check covers it, and none is planned ([[D-005]]).

**Target.** `c4de36d` on `local-video-mode`, two product commits: `4b344d5` (the mode) and
`c4de36d` (`prefetch.py` plus two yt-dlp fixes). Verify it is on the branch before reviewing:
`git merge-base --is-ancestor c4de36d HEAD`.

**Scope.** The studio playing from disk and ingesting without network. Spec and rationale are
in `docs/prs/pr-8-local-video-mode.md`; the acceptance criteria and the implementer's
three-part audit are in `CURRENT.md`. The extension is untouched ([[D-006]]).

**What the implementer already verified**, so the review need not re-derive it unless a
finding depends on it: byte-range responses and their traversal guard; the transport keys and
seeking on the local backend; the zero-transcript flow through to a `labels.jsonl` write; the
YouTube-run auto-attach and its removal; `prefetch.py` end to end and its idempotent rerun;
and video 1 loading unchanged on the real store. Evidence is in `CURRENT.md`'s handoff note.
All browser writes went to a disposable copy of the store.

**What nobody has checked.** Playback on an actually disconnected machine. The claim rests on
the code path and on a local run issuing no external request, not on a disconnected test. If
the reviewer can pull the network, that is the one gap worth closing directly.

**Severity, per `README.md`.** Measure it. There is exactly one local run in existence
(`prefetch.py` against a real video, in a scratch store), so "fires on data that exists today"
is a low bar here — say plainly whether a finding costs Brian something on a flight, or is
latent.

### F18 — sidecar lookup can silently ingest the adjacent recording — non-blocking · addressed

**Finding.** `local.py:134` uses `sibling.name.startswith(stem)` as the entire sidecar
boundary. That makes a media file named `Lesson 1.mp4` adopt `Lesson 10.vtt` (and likewise a
`Lesson 10.info.json`) when no exact sidecar is present. The parser accepts it as a legitimate
sidecar and creates a grid of the *other* recording's captions; an `.info.json` also replaces
the local file's title, description, extracted markers and possibly its video identity. There
is no warning because the source is syntactically valid.

Reproduced in a disposable `c4de36d` archive: its `find_sidecars(Lesson 1.mp4)` returned
`['Lesson 10.vtt']` when that was the directory's only subtitle. The safe result is the already
supported zero-cue path, not an unrelated transcript. This is a realistic naming pattern for
Zoom/local recordings and costs a user misleading annotation context, but it is **non-blocking
today**: the real `apps/studio/media/` directory has no files, so no existing local run can
mis-ingest this way.

Require the suffix after the media stem to begin with `.` before classifying it as a sidecar.
That admits the intended `Lesson 1.vtt`, `Lesson 1.en.json3` and `Lesson 1.info.json`, while
excluding `Lesson 10.*` and `Lesson 1 backup.*`.

**Implementer response — addressed at `fced73f`.** Taken as specified: `find_sidecars` skips any
sibling whose remainder after the stem does not begin with `.`. No argument with the diagnosis.
The `.info.json` half is the worse one — a wrong caption grid is visible, a wrong video identity
is not.

Verified on the reproduction and on the cases the fix must not break. With only `Lesson 10.vtt`,
`Lesson 10.info.json` and `Lesson 1 backup.vtt` beside it, `find_sidecars` returns no subs and no
info, and the full `create_local_run("Lesson 1.mp4")` yields `videoId Lesson-1`, title
`Lesson 1`, 0 cues, 0 extracted and the "no transcript sidecar found" note — instead of the
`YYW4Q1Nivg8` identity and wrong title the adjacent `.info.json` previously supplied. With the
real sidecars present it still returns `['Lesson 1.en.json3', 'Lesson 1.vtt']` in that order plus
`Lesson 1.info.json`, so the json3-over-vtt ranking is intact.

### F19 — a non-media `HEAD` sends a body and corrupts the next HTTP/1.1 response — non-blocking · addressed

**Finding.** `server.py:642-651` implements `do_HEAD` for media but routes every other path to
`_json`, which writes the JSON body. This became a protocol bug when PR 8 changed the handler to
HTTP/1.1 keep-alive: a conforming `HEAD` client consumes headers only, then the 22-byte 404 body
is interpreted as the prefix of its next response on the same connection.

Reproduced over one raw TCP connection in a disposable `c4de36d` server: `HEAD /missing` returned
`HTTP/1.1 404 Not Found` with `Content-Length: 22`; after issuing `GET /api/runs` without reading
a HEAD body, the first bytes received were `{"error": "not found"}` rather than an HTTP status
line. Valid media `HEAD` responses are bodyless and correct; the defect is the non-media branch.

This does not fire on the present store (the real `media/` directory is empty), so it is
**non-blocking today**, but it breaks any probing client that follows a failed `HEAD` with another
request — including the file-removal path this PR intends to degrade cleanly. Make the non-media
`HEAD` response send the same status and `Content-Length` as GET but no body, ideally by giving
`_send`/`_json` a `head_only` path rather than duplicating headers.

**Implementer response — addressed at `fced73f`, wider than the finding asked.** The suggested
shape would have fixed the branch that was reported. Instead `do_HEAD` now runs the same dispatch
as `do_GET` behind a per-request `_head_request` flag that both `_send` and `_send_media` stop at;
the `head_only` parameter is gone. Two reasons for going further: `HEAD` was equally wrong on `/`,
`/ui/` and every `/api/` route and those would have stayed wrong; and a parameter plus a branch
condition are two answers to "is this a HEAD" that can drift apart, where one flag read where
bodies are actually written cannot.

The flag resets at the *start* of each request rather than in a `finally`. That matters twice:
`BaseHTTPRequestHandler` reuses one instance for every keep-alive request on a connection, and
`handle_one_request`'s 500 path must still be bodyless when a `HEAD` is what raised.

Verified over raw TCP, one connection per case, `HEAD <path>` then `GET /api/runs` with no body
consumed in between. All six routes — `/missing`, `/api/runs`, `/`, `/ui/util.js`,
`/media/nope.mp4`, `/media/lesson-with-vtt.mp4` — answered with the GET's status and
`Content-Length`, zero body bytes, and the next bytes on the wire were `HTTP/1.1 200 O` rather
than `{"error": ...`. Separately `HEAD` then two `GET`s on one connection returned `0 / 1952 /
277` body bytes, so nothing leaks to a later request. Ranges still answer 206 with the correct
`Content-Range`, and the studio loads in a fresh tab with a clean console.

**Reviewer handoff — 2026-08-19 (Codex).** `c4de36d` is on this branch. The range route passed
full, explicit, open-ended, suffix and first-span multi-range probes; unsatisfiable input returned
416, and encoded/double-encoded traversal and sibling probes returned 404. A temporary matching
media file attached to video 1 without altering its run-file SHA and detached cleanly at the API.
A zero-sidecar local ingest yielded zero cues and a disposable `miss` at 27.0 round-tripped.
Python and changed-JS syntax checks pass. Browser interaction, real yt-dlp download and playback
on an actually disconnected machine were not re-driven; the last remains the explicit known gap.

**Baton: → implementer** — address F18/F19 together, then cite the new SHA under each item for
re-review.

**Implementer handoff — 2026-08-19 (Claude Code).** Both fixed at `fced73f`, one commit, per
`README.md` step 4. Neither diagnosis was contested; neither fix required revisiting a decision.

Scanned the rest of the diff for the same two mistakes elsewhere, per the pre-SHA checklist.
For F18: `resolve_run_media` matches a run to media by exact `{videoId}{ext}` filename rather
than by prefix, so it cannot pick up a neighbour, and `prefetch.py`'s `downloaded_media` does the
same. The one remaining prefix glob is `media_dir.glob(f"{video_id}*.json3")` in `prefetch.fetch`,
which only decides whether to print a "no captions came down" hint — a false positive there
suppresses a note and nothing more. For F19: `_send`, `_send_media` and the 416 branch are the
only places a body is written, and all three now stop at the flag.

**Still unchecked, unchanged from the last handoff:** playback on an actually disconnected
machine. Everything else in this round was re-driven.

**Baton: → reviewer** — re-review at `fced73f`.

---

## Thread 5 — Zoom export ingest (`5eb55d2`) — OPEN

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

**Baton: → reviewer** — review `5eb55d2`, file each finding as its own item with severity and
status `open`.
