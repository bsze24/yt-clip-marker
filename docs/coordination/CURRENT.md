# Current task

**Review loop on the two-surface land — PRs 3, 4, 5.** Baton: **→ reviewer** on
`a051667` (PR 3 first; 4 and 5 are stacked behind it).

The product is written and pushed. Nothing here asks anyone to rebuild the studio,
re-land `apps/`, or re-move `content/`. The open question is whether what's on those
three branches is right.

---

## 0. State as of 2026-08-16

| PR | SHA | Base | Contents |
| --- | --- | --- | --- |
| **3** (open) | `a051667` | `main` | Studio + extension move, PRD, clip-schema, copy-timestamps ([[D-022]]) |
| **4** (open) | `bde4ce7` | PR 3 | Video 1 `runs/` + `labels.jsonl` — data only |
| **5** (open) | `949cb7b` | PR 3 | Session log + folded ledger |

Stacked, so SHA ancestry matters: PR 4's SHA is not on PR 3's branch. Verify before
reviewing (`REVIEW.md` rule 3).

---

## 1. The task

Run the review loop in `README.md` §"The review loop" against PR 3, then 4, then 5.
PR 3 is the only one carrying real code; 4 is data and 5 is docs, so expect the weight
to sit almost entirely on thread 1.

**Where to look hard in PR 3** — the places this codebase has actually been wrong before:

- `apps/studio/ui/keys.js` — one dispatcher, priority chain intact, no second
  document-level listener ([[D-016]]). Focus returns after IFrame interaction.
- `apps/studio/ui/grid.js` — row identity, not start time ([[D-008]]). Exact-start
  align first, then ≤2s. Duplicate timestamps are real.
- `apps/studio/ui/persist.js` / `api.js` — append-only writes, save-failure surfaced,
  no in-place history rewrite ([[D-002]]).
- `apps/studio/ui/export.js` — the fold ([[D-022]]): gold and adds never dropped, add
  beats marker at 2s, `0:00` parked under the first work header.
- `apps/studio/server.py` — path allowlisting on the `/ui/` route; no traversal.
- Anything that quietly grows the extension past [[D-006]].

## 2. Acceptance

1. Every blocking finding on PR 3 is `resolved` or `wontfix`-with-reason in `REVIEW.md`.
2. PRs 4 and 5 each have a recorded verdict, even if it's one line ("data only, shape
   matches `docs/clip-schema.md`").
3. Durable outcomes harvested per `README.md` wrap-up — new dated `DECISIONS.md`
   entries, deferred items into `BACKLOG.md`. Round-by-round discussion is not kept.
4. `REVIEW.md` reset to a clean template; this file replaced with the next task.

Out of scope: end collection, JSON export, in-app suggest, extension→studio handoff,
removing eval chrome, changing the copy-timestamps fold. Ballpark-`g` stays an open
modeling item in `BACKLOG.md` — do not resolve it here.

## 3. Baton

**→ reviewer** on `a051667`. Write findings into `REVIEW.md` thread 1.

Next *product* task once 3–5 merge: end collection ([[D-012]], `BACKLOG.md` §1). Don't
spec it here until the planner replaces this file.

---

## Appendix — how this file got committed (PR 6, docs only)

Kept as provenance; not an active task. The coordination write-head landed as one
docs-only commit, `PR 6: add agent coordination write-head`:

**In:** `docs/coordination/*`, `AGENTS.md`, `README.md`, `docs/tech-debt.md` (pointer),
`docs/two-surface-handoff.md` (historical banner), `docs/youtube-clip-marker-prd.md`
(pointers to BACKLOG / DECISIONS).

**Out:** `apps/` (PRs 3/4), `docs/sessions/` (PR 5). Never `git add -A` — data and
session logs are not the product PR.

Housekeeping this left behind: `docs/sessions/` still holds two duplicate copies of the
1507 log (`NEW - …`, `grok-claude-…`). Delete them rather than carrying a standing
instruction not to commit them.
