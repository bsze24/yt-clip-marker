# Current task

**Review the two-surface land — PRs 3, 4, 5.** Baton: **→ reviewer**, on `43c99dd` (PR 4) —
the only one left. Thread 1 (PR 3) closed 2026-08-18 and merged at `5af3e13`. Thread 3 (PR 5)
closed 2026-08-19 as superseded: both files it adds are older copies of files `main` already
carries, so it is closed rather than merged.

The code is written and pushed. Nothing here asks anyone to rebuild the studio, re-land
`apps/`, or re-move `content/`. The only open question is whether what sits on those three
branches is right.

---

## 0. State as of 2026-08-18

| PR | Branch | SHA | Base | Contents |
| --- | --- | --- | --- | --- |
| **3** ✅ **merged** `5af3e13` | `codex/pr-3-two-surface-product` | `eea83b8` | `main` | Studio, extension move to `apps/extension/`, two-surface PRD, `docs/clip-schema.md`, copy-timestamps ([[D-022]]), strict `extracted[]` reader + visible deprecated-key fault ([[D-023]]), review fixes F6-F11 and F14-F15 |
| **4** | `codex/pr-4-video-1-store` | `43c99dd` | PR 3 | Video 1 `runs/*.json` + `labels.jsonl`; run key migrated to `extracted[]`; non-force merge of reviewed PR 3 |
| **5** ❌ **closed, superseded** | `codex/pr-5-session-write-head` | `949cb7b` | PR 3 | Session log + folded ledger — both already on `main` in corrected vocabulary |
| **6** | `docs/coordination-write-head` | `e158710` | `main` | Coordination write-head + `AGENTS.md` |

`main` is `5af3e13` as of 2026-08-18 — PRs 1, 2 and **3** merged. The extension now lives at
`apps/extension/`; `content/` in the repo root is gone. PRs 4, 5 and 6 are still open.

PRs 3–5 are stacked, so ancestry matters. PR 4 now merges PR 3 at `eea83b8` without
rewriting its published history; PR 5 still parents at `a051667`. Video 1 now stores
`extracted[]`; a deprecated `gold[]` key is a visible fault and is never read as extracted
data ([[D-023]]). Verify any SHA before reviewing it (`README.md`, working agreement rule 2).

**Product state the review is checking against.** Video 1 (`YYW4Q1Nivg8-20260814-1248`) is
fully labelled through one careful studio pass: 64 skill markers (`g` 23 · `x` 24 · keep 14 ·
note 3 · blank 0), 21 live added markers, 4 tombstoned adds, 24 extracted markers. No unreviewed
skill markers
remain. That pass is what designed the UX now under review, and the fold of it lives in
`docs/sessions/2026-08-16-YYW4Q1Nivg8-folded-ledger.md` — read it if a grid or export
question needs ground truth without running the studio.

**Open item for Brian.** PR 6 (`e158710`) carries a copy of `docs/coordination/` from before
the PR 3 review and is ~1,000 lines stale; `docs/remove-coordination-md` exists only to delete
that copy. Both are superseded by the branch that landed this file. Close them rather than
merging either. `TD-5` covered the divergence and is now resolved for the four shared docs.

---

## 1. The task

Run the review loop from `README.md` against PR 3, then 4, then 5. PR 3 is the only one
carrying executable code — 4 is data, 5 is docs — so nearly all the weight sits on thread 1.

**Where to look hard in PR 3.** These are places this codebase has actually been wrong, not
a generic checklist:

- `apps/studio/ui/keys.js` — one dispatcher, priority chain intact, no second document-level
  listener ([[D-016]]). Focus must return after an iframe interaction; clicking a timestamp
  once stole every subsequent keystroke.
- `apps/studio/ui/grid.js` — `buildRows` aligns exact start first, then ≤2s (`MATCH` is 2).
  Selection keys on row identity, not start time ([[D-008]]) — `j` stuck on 3:19 when two
  rows shared a start. Duplicate timestamps are real data.
- `apps/studio/ui/persist.js` and `ui/api.js` — append-only writes, save failure surfaced in
  the UI, no in-place rewrite of history ([[D-002]]). Deleting an add writes an `unmiss`
  tombstone; it does not remove the original event.
- `apps/studio/ui/export.js` — the copy-timestamps fold ([[D-022]]): extracted and added
  markers never dropped, ≤2s merge, rank extracted < added < skill so an added marker steals
  both time and label from a skill marker, `x` skill markers skipped, `g` and taxonomy skill
  markers kept, `0:00` parked under the first work header, `***` for star.
- `apps/studio/server.py` — path allowlisting on the `/ui/` route. It serves from disk; check
  traversal.
- Anything that quietly grows the extension past its freeze ([[D-006]]) — a storage
  permission, a refinement hotkey, an export button.

**Do not collapse the eval channels** while reviewing. `g`, `x`, taxonomy-without-`g`, `star`,
and blank are five distinct states; the vocabulary table in `README.md` is the reference. The
14 "keep" skill markers are keeps, not blanks — that misread has already happened once.

**Verification, split by who can actually do it.** There is no test suite.

- *The reviewing agent can check:* the studio boots on `127.0.0.1:8765`, `/api/runs` and
  `/api/run?id=…` answer, video 1's run parses, a label append lands in `labels.jsonl`, and
  the code reads correctly. Commands are in `README.md`.
- *Only Brian, or an agent driving a real browser, can check:* the annotation loop — grid
  alignment on screen, `j`/`k`, Enter, focus returning from the YouTube embed, what
  copy-timestamps actually puts on the clipboard, and the extension loading unpacked with a
  clean console.

Most of the "look hard" list above is interaction behaviour, so expect a real share of
thread 1 to end as findings the reviewer raises from the code and Brian confirms in the tab.
That is a normal outcome here, not a failed review. Record it as "not verified, needs a
browser" rather than asserting it works.

## 2. Acceptance criteria

1. Every blocking finding on PR 3 is `resolved`, or `wontfix` with a stated reason, in
   `REVIEW.md`.
2. PRs 4 and 5 each carry a recorded verdict, even if it is one line — "data only, shapes
   match `docs/clip-schema.md`, counts match the folded ledger" is a complete verdict for a
   data PR.
3. Durable outcomes harvested per the `README.md` wrap-up: dated `DECISIONS.md` entries,
   deferred items into `BACKLOG.md`. The round-by-round is not kept.
4. `REVIEW.md` reset to a clean ledger; this file replaced with the next spec.

**Out of scope.** End collection, JSON export, in-app suggest, extension→studio handoff,
removing eval chrome, changing the copy-timestamps fold, video 2 ingest. Ballpark-`g` stays an
open modeling item in `BACKLOG.md` — the export freeze resolves it, not this review.

## 3. Baton

**→ reviewer**, on `43c99dd` (PR 4) then `949cb7b` (PR 5). Thread 1 is closed; do not reopen
it to re-derive what is already in [[D-023]]-[[D-029]].

Acceptance-criteria status, corrected 2026-08-18:

- **1 — met, 2026-08-18.** Every blocking finding is `resolved` or a reasoned `wontfix`. F1-F5
  were the last gap: written and answered inside one implementer turn, then confirmed by a
  single reviewer, which is why they sat at `addressed`. A second reviewer independently
  re-derived all five and moved them to `resolved` — grep re-run at `162e2f4`, `eea83b8` and
  `43c99dd`; GitHub timeline `head_ref_force_pushed = 0` on both PRs; the two unpushed
  session-log commits named (`6075db6`, `549d667`) and shown not to be ancestors of the remote;
  `/api/run` actually hit against a disposable `gold`-key store; all four CLI migration states
  driven, with a yt-dlp timing contrast proving the fetch path is unreachable while the
  deprecated key is present.
- **3 — met for thread 1.** Durable outcomes are in [[D-023]]-[[D-029]] and `TD-3`-`TD-5`. The
  round-by-round is deliberately still in `REVIEW.md`; see the note in thread 1's banner for why
  discarding it is not yet safe.
- **2 — outstanding.** PRs 4 and 5 still need a recorded verdict. Thread 2 carries partial
  reviewer evidence, thread 3 carries a starting point.
- **4 — outstanding**, blocked on 2 and on `docs/coordination/` being committed.

Next product task once 3–5 merge is end collection ([[D-012]], `BACKLOG.md`). Do not spec it
here; the planner replaces this file first.

---

## Handoff notes

### 2026-08-18 — implementer, deprecated-key cleanup

- **Prompt audit:** Grok's cleanup prompt was reviewed before implementation. Five blocking
  plan findings and their responses are recorded inline in `REVIEW.md` thread 1.
- **PR 3:** `162e2f4`. Replaced silent fallback with a nonfatal API warning, persistent UI
  banner and console error; readers consume only `extracted[]`; renamed the CLI and made its
  migration lossless. Python compilation, JS syntax checks and `git diff --check` passed.
- **PR 4:** `05c1414`. Non-force merge of prior PR 4 (`bde4ce7`) with corrected PR 3, plus
  the video-1 key-only migration. The 24-item array kept semantic SHA-256
  `a292b9793284c464dda7c058e563b3e172f5faf9df91eee7102804c439a14b0f`;
  `labels.jsonl` remained byte-identical at
  `1ea26c91d6b046f87f4c639c41c45914661eb767b844eb32234be96f7d80acf1`.
- **Browser verification:** before migration, the real run rendered the grid with zero
  extracted rows plus the run-id warning; after migration it rendered 24 extracted rows and
  no warning. The pre-existing unloaded-player `getDuration` console error was observed and
  left out of this vocabulary-only change.
- **Assumptions:** Brian's explicit instruction reassigned the implementer baton for this
  out-of-cycle cleanup. A dedicated warning banner was chosen so ordinary save status cannot
  erase a store fault. Published branch history was preserved with a merge, not a rebase.
- **Skips/divergences:** immutable `labels.jsonl` feedback and session-history prose were not
  rewritten, so the audit classifies those separately from prohibited live identifiers.

### 2026-08-18 — implementer, PR 3 review findings F6-F13

- **Acceptance criteria and evidence:** F6 is fixed in `descriptionTimestampText` with both
  no-work-first and first-work output checked; F7 is fixed by `mergeNearby`'s immutable
  cluster anchor and the reported three-item chain now yields two clips; F8 uses keyed
  debounces in `persist.js`, browser-verified across two independent records and a combined
  added-marker record; F9 gives `wrong` its own server verdict and count, verified by a real
  API append; F10 repaints through an exact marker block; F11 uses stable build-time row ids,
  browser-verified across filter changes. Python compilation, JS syntax checks and
  `git diff --check` passed. PR 3 is `6d2ee47`; PR 4 was restacked without force at
  `6de5aee`, and its diff against PR 3 remains the two data files only.
- **Assumptions:** added-marker description and taxonomy are fields of one append-only record,
  so they share a debounce key and persist one complete snapshot; separate event streams on
  model markers keep separate keys. Pending writes retain their captured run id so switching
  runs does not silently drop typed data.
- **Skips/divergences:** F12 was not changed because browser inspection showed the player
  catcher fully intercepts the proposed iframe-control path and restores grid focus. F13 is
  deferred as TD-3 until polling cost becomes measurable. The append-only test writes were
  made only in a disposable copy of PR 4's store, never in either PR.

### 2026-08-18 — implementer, PR 3 review findings F14-F15

- **Acceptance criteria and evidence:** F14 keeps the selected record's live work/lane/tags
  when toggling `star`; browser verification observed the intentionally stale dataset, then
  confirmed both appended events retained the edited lane. F15 adds `keepCount`, removes
  annotated keeps from `blankCount`, and fixes the same classification in the grid header.
  The real video-1 fold is `23 check · 24 wrong · 14 keep · 3 notes · 0 blank` in both API
  and browser. Python compilation, JS syntax checks and `git diff --check` passed. PR 3 is
  `eea83b8`; PR 4 is restacked without force at `43c99dd` and remains data-only relative to
  PR 3.
- **Assumptions:** eval channels are mutually exclusive for coverage reporting, with
  precedence `check`, `wrong`, freeform note, taxonomy keep, then genuinely blank. An
  annotation whose tags, lane and work are all empty is not a keep.
- **Skips/divergences:** neither finding was deferred because both are current correctness
  bugs with narrow fixes. Browser writes landed only in a disposable copy of PR 4's store.

### 2026-08-18 — reviewer, PR 3 close-out and harvest

- **Reviewed:** PR 3 across three implementation rounds, `162e2f4` → `6d2ee47` → `eea83b8`.
  Filed F6-F15; verdicts recorded before the thread was collapsed. Verification was mine, not
  taken from the implementer: re-ran the F6 and F7 reproductions against the shipped
  `export.js`; booted `server.py` against a disposable copy of PR 4's store and confirmed the
  five-channel fold reconciles at `check 23 · wrong 24 · keep 14 · note 3 · blank 0`; appended a
  real `wrong` event and watched `wrongCount` move; re-checked the deprecated-key fault and the
  `attach_extracted.py` repair on the final tree; `py_compile`, `node --check` and
  `git diff --check` all clean.
- **Harvested:** [[D-024]]-[[D-029]] carry the durable contracts the fixes established, each
  naming the finding it came from. `TD-4` (frozen `schemaVersion` across a verdict-vocabulary
  change) and `TD-5` (four shared docs in divergent copies across the open PRs) are new. `TD-3`
  gained a note that the keep/blank split added a third fold per run to `list_runs`.
- **Assumptions:** the wrap-up in `README.md` fires per thread, not per file — thread 1 was
  collapsed and harvested while threads 2 and 3 stayed intact, because a full `REVIEW.md` reset
  would have discarded two live threads. New decision entries went to the section matching their
  type rather than in id order, per this file's own "the section is the decision's type".
- **Skips/divergences:** F10's implementation detail (parse `data-markers` as a comma list, do
  not substring-match it) was deliberately not harvested — the code is correct and the rule is
  too narrow for a decision entry. I did not review PRs 4 or 5; thread 2's reviewer evidence is
  a by-product of the PR 3 work, not a verdict. `docs/coordination/` remains untracked in the
  working tree, so all of the above is uncommitted.

Each turn appends here: role, surface, SHA, what was verified, assumptions made, anything
skipped. See `README.md`, "Before recording a SHA".
