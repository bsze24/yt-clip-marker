# Agent coordination

Durable async-handoff surface for Brian and the agents on this repo. Git commits remain
the source of truth for code; these files are the source of truth for intent and
coordination.

Name the **role** in the baton, the **surface** in the handoff note — which model sits
in a role changes turn to turn. Learning state stays in session logs, never here.

## Files
- `CURRENT.md` — the one active task: owner, scope, acceptance criteria, baton.
- `DECISIONS.md` — accepted architecture/product decisions that outlive a task (D-001…).
- `REVIEW.md` — the active review target; findings as per-item threads with a status.
- `BACKLOG.md` — deferred work + roadmap, explicitly outside the active task.

## Roles

Roles are stable; which product sits in a role can change per turn. Baton is a role
(`→ implementer`). The handoff note names the surface Brian invoked (`Cursor Grok`,
`Claude Code`, `Codex`).

| Role | Usual surface | Owns |
| --- | --- | --- |
| Planner | Claude Code | Design, `DECISIONS.md`, the `CURRENT.md` spec |
| Implementer | Cursor or Codex | Code for the active task; commit SHA + verification |
| Reviewer | Claude Code | `REVIEW.md` findings; may implement when assigned |
| Brian | Owner | Resolves product/scope; invokes each turn; breaks ties |

## Working agreement
1. Reference an exact commit SHA when requesting or recording a review.
2. Keep `CURRENT.md` to one active task.
3. Record contract/architecture changes in `DECISIONS.md`; never revise them silently.
4. Label review findings **blocking** vs **optional**.
5. Thread each finding's finding → response → re-review inline in one `REVIEW.md` item
   with a status; collapse to a one-line resolution once resolved. Don't split responses
   into a separate section or let threads sprawl.
6. Graduate to repo issues if the workflow outgrows these files.
7. **Never `git add -A`.** Data (`runs/`, `labels.jsonl`) and session logs are not the
   product PR. Coordination docs travel with the product docs, not with a video's labels.

## Handoff cycle
1. **Planner** specs (or re-plans) the task in `CURRENT.md`.
2. **Brian** resolves any product/scope choices.
3. **Implementer** implements the task; records the commit SHA + verification in `CURRENT.md`.
4. **Review loop (implementer ↔ reviewer)** — iterates until it settles (expanded below).
5. **Planner** scopes the next task once the review lands clean.

Agents do not run continuously; **Brian invokes each turn; Brian or the planner break ties.**

### Before recording a SHA (step 3, expanded)
The implementer's obligations before passing the baton to review. All cheap, and they're
what keeps the review loop to one or two rounds instead of five.

**1. Audit the work against `CURRENT.md`** — don't record a SHA until you've written, in the
handoff note, all three of:
- **Acceptance criteria, item by item.** For each one, cite the evidence (function, file, line)
  or state plainly what is missing or different. "Done" with no pointer isn't verifiable.
- **Assumptions.** Choices the spec didn't decide — places where two reasonable implementations
  were possible and you picked one — and why you picked it. A reviewer cannot tell a deliberate
  interpretation from an oversight; this is the difference between the two.
- **Skips & divergences.** Anything intentionally not built, or built differently, and why.
  Scaling scope down is Brian's call, not the implementer's — so surface it rather than absorb it.

If the session was driven by a session prompt (`.md` file), the same three-part audit applies
before commit — that's the "session prompt audit" in `AGENTS.md`.

**2. Run the checks that exist.** There is no test suite and no typecheck yet. Minimum:
- Studio: `python3 apps/studio/server.py` boots; an existing run loads; a label save round-trips.
- Extension: still loads unpacked from `apps/extension` — `chrome://extensions` shows no
  warnings, console clean on a watch page.
Paste what you actually did into `CURRENT.md` under verification — "it works" without a
pointer isn't evidence.

**3. Scan the diff for:**
- Missing try/catch around async operations (fetch in the studio page, `chrome.*` APIs)
- Missing error/empty states in UI (no runs, ingest failure, missing video element)
- Edge cases: empty marks/markers array, null `videoId`, null `end`, duplicate start times,
  no pending start
- Unguarded keyboard listeners (input-focus guard, modifier-key guard, repeat guard; in
  the extension, `e.composedPath()[0]` because `document.activeElement` can't see through
  shadow roots)
- When you fix a bug, check the same file for the same mistake elsewhere
- No API keys, tokens, or secrets in committed code

**4. Batch related fixes** in one commit, not a chain of one-line follow-ups. Don't push new
commits while BugBot is mid-review (the review restarts).

**5. Don't silently revise a decision.** If the task can't be built as specified without
contradicting `DECISIONS.md`, say so in `CURRENT.md` and let the planner rule (design/contract)
or Brian (product/scope). The reviewer is held to the same rule.

### The review loop (step 4, expanded)
Review is a short back-and-forth that repeats until no blocking findings remain:
1. **Reviewer** reviews the referenced commit and writes each finding as its own item in
   `REVIEW.md` — severity (blocking/optional) + status `open`.
2. **Implementer** responds **inline under each finding** (fixed / `wontfix` + why) with the
   new SHA and flips that item's status to `addressed`.
3. **Reviewer** re-reviews at the new SHA, writing its verdict inline under the item and
   setting status to `resolved` (or back to `open`).
4. Repeat 2–3 until zero blocking findings are open. Optional suggestions get `deferred` to
   `BACKLOG.md` rather than holding up the handoff.
5. **Brian or the planner** breaks any implementer ↔ reviewer stalemate — Brian on
   product/scope, the planner on design/contract (recorded in `DECISIONS.md`, since neither
   implementer nor reviewer may silently revise it).

`REVIEW.md` is a **per-item todo list**: each finding is one item carrying its full thread
inline (finding → response → re-review) and a status (`open → addressed → resolved`, or
`deferred`/`wontfix`). All context for a finding stays in its item. Resolved items remain
as checked-off entries until wrap-up. Every round references the exact commit SHA under review.

If several review targets are in flight at once, use one `## Thread` per SHA and edit only
the thread whose baton you hold — see the concurrency note at the top of `REVIEW.md`.

### Wrap-up (when the review lands clean)
`REVIEW.md` is live state for the *current* review, not an archive — git history (of
`REVIEW.md` and the commits) plus the PR thread already preserve the play-by-play. So at
the end of a review:
1. **Harvest durable outcomes.** Anything that outlives the task → a new dated entry in
   `DECISIONS.md`, or deferred work → `BACKLOG.md`. The round-by-round discussion does not
   get kept.
2. **Reset `REVIEW.md`** to a clean template pointing at the next target (or "no active review").
3. **Planner** replaces `CURRENT.md` with the next task spec.

No per-PR archive files: git is the archive. `docs/prs/pr-*.md` are the *task specs* that
became PRs — useful provenance, not a second `CURRENT.md`.

## Where things go

| Kind | Home |
| --- | --- |
| Active task, baton, acceptance | `CURRENT.md` |
| Durable architecture / product calls | `DECISIONS.md` |
| Review findings | `REVIEW.md` |
| Roadmap, deferred work, tech-debt ids | `BACKLOG.md` |
| Product requirements (the why) | `docs/youtube-clip-marker-prd.md` |
| Clip contract | `docs/clip-schema.md` |
| Session / learning state | `docs/sessions/` |
| Provenance of the two-surface pivot | `docs/two-surface-handoff.md` (historical; don't treat as live) |

A real project finding surfaced *while* learning (a bug, a contract gap) is project state —
route it here. The test is what the artifact is, not how it surfaced.
