# Review

Active target: **PR 3 (`a051667`)**. Threads 2 and 3 are stacked behind it and open
once thread 1 lands. No findings recorded yet — the first review has not run.

> ## Concurrency protocol
> 1. **One thread per target SHA.** Each thread is self-contained. Never move a finding
>    between threads or renumber another thread's items.
> 2. **Edit only the thread whose baton you hold.** The ledger's `Baton` column is
>    authoritative; leave other threads byte-for-byte alone.
> 3. **Verify the SHA is on the branch first:** `git merge-base --is-ancestor <sha> HEAD`.
>    These PRs are stacked — PR 4's SHA is not on PR 3's branch. A cited SHA that isn't an
>    ancestor of HEAD is stale; re-anchor before reviewing.
> 4. **Findings are append-only.** Add responses and verdicts *under* a finding; don't
>    rewrite its text. Ladder: `open → addressed → resolved` (or `deferred` / `wontfix`).
>    Optional findings never hold a baton. When a thread goes clean, collapse it to a
>    one-line CLOSED banner and harvest per the `README.md` wrap-up.

### Ledger
| Thread | Target | Status | Baton |
| --- | --- | --- | --- |
| 1 | `a051667` — PR 3, two-surface product | first review not started | → reviewer |
| 2 | `bde4ce7` — PR 4, video 1 store | blocked on thread 1 | — |
| 3 | `949cb7b` — PR 5, session write-head | blocked on thread 1 | — |

---

## Thread 1 — two-surface product (`a051667`)

**Scope:** https://github.com/bsze24/yt-clip-marker/pull/3 — `apps/studio/` (no `runs/`
or `labels.jsonl`), the `apps/extension/` move, PRD, `docs/clip-schema.md`, and AGENTS as
of that commit (pre-coordination). Where to look hard: `CURRENT.md` §1.
**Verification:** none recorded.

_No findings yet._

---

## Thread 2 — video 1 store (`bde4ce7`)

**Scope:** https://github.com/bsze24/yt-clip-marker/pull/4 —
`apps/studio/runs/YYW4Q1Nivg8-20260814-1248.json` + `apps/studio/labels.jsonl`. Data
only; the review question is whether the shapes match `docs/clip-schema.md` and whether
the event log honors row identity ([[D-008]]) and tombstones ([[D-002]]).
**Verification:** none recorded.

_No findings yet._

---

## Thread 3 — session write-head (`949cb7b`)

**Scope:** https://github.com/bsze24/yt-clip-marker/pull/5 — curated session log + folded
ledger. Excludes `docs/sessions/2026-08-16-session-log-skill-critique.md` and the
duplicate `NEW -` / `grok-claude` copies (those should be deleted, not committed).
**Verification:** none recorded.

_No findings yet._
