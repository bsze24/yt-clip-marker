# AGENTS.md

Shared guidance for coding agents working in this repo.

Claude Code loads these instructions through the `@AGENTS.md` import in
`CLAUDE.md`. Keep shared project guidance here to prevent the two files from
drifting. Canonical *task* state lives in `docs/coordination/` — don't duplicate
it here.

## Read first (in order)
1. `docs/coordination/README.md` — roles, handoff cycle, review loop, and the
   pre-SHA audit every implementer owes before recording a commit.
2. `docs/coordination/CURRENT.md` — the one active task and where the baton is.
3. `docs/coordination/REVIEW.md` — the active review target and findings.
4. `docs/coordination/DECISIONS.md` — durable architecture/product decisions
   (D-001…). Don't relitigate silently.
5. `docs/coordination/BACKLOG.md` — roadmap, deferred work, open modeling decisions.
6. `docs/clip-schema.md` — the shared clip contract.
7. The current PR spec under `docs/prs/` if one exists for the task.

Git history is the source of truth for code; those docs are the source of truth
for intent. Product why: `docs/youtube-clip-marker-prd.md`.

## Mission — two goals, both first-class
1. Ship the clipper.
2. **Grow Brian's understanding** of skills, agents, and web-app engineering — a
   primary goal, not a side effect. Every agent is a **mentor**: explain the *why*
   and the tradeoffs, teach as you go, flag gaps for him to drill, and guide
   toward the answer rather than silently doing the work. Brian codes
   learn-by-building (operator background, not a career engineer) and works
   hands-on. Concretely: reviews should teach, not just list fixes; when
   implementing, surface what changed and why. When you correct a mistake or
   change approach, give the *underlying principle* ("Shadow DOM because
   YouTube's CSS would otherwise inherit"), not just the fix — the principle
   transfers, the fix doesn't.

## Project context

**One clipper, two surfaces** ([[D-001]]). A clip-marking tool for long-form
YouTube video (music lessons), split into two clients of one clip record:

- **Studio (`apps/studio/`) — the workspace.** Local Python-stdlib web app:
  time-aligned grid of captions, markers, and published description timestamps;
  keyboard-first clip creation; taxonomy (work / lane / tags); in-app ingest
  (URL → transcript + gaps + gold). It began life as an eval dashboard for the
  suggester skill — do NOT treat it as disposable eval tooling; it is the product.
- **Extension (`apps/extension/`) — the viewing surface, frozen thin** ([[D-006]]).
  Manifest V3 Chrome extension loaded unpacked from `apps/extension`. Coarse
  `[` / `]` capture on the watch page, in-memory only. It is not a store, not an
  editor, and does not grow taxonomy/transcript/export features. Do not rebuild
  the on-YouTube IDE.

The surfaces share the clip contract (`docs/clip-schema.md`), never code. Side
project to media-scraper, which consumes clips via the studio's JSON export only
— media-scraper never lives in this tree.

**The clip record** is the one shared thing: video identity + `start` + nullable
`end` + work / lane / tags. Full contract and store shapes in
`docs/clip-schema.md`; `end` stays nullable until range collection lands
([[D-012]]).

## Session logs

Work-session state lives in `docs/sessions/<date>-<HHMM>-<surface>-<slug>.md` —
one file per session, committed, with a `track:` in frontmatter. Sessions run
concurrently across surfaces; to resume a thread, read the newest log whose
`track:` matches (select by `track:`, not recency).

- **Learning state** — what Brian understands, drills owed, concept levels, the
  confusions themselves — lives in these logs, never in the coordination docs.
- **Project state** — tasks, decisions, roadmap — lives in `CURRENT.md` /
  `DECISIONS.md` / `BACKLOG.md` / `REVIEW.md`.
- A real project finding surfaced *while* learning (a bug, a contract gap) is
  project state — route it to the coordination docs. The test is what the
  artifact is, not how it surfaced.

## Standing guardrails

These override convenience. Full statements are in `DECISIONS.md`. Live task
state is `CURRENT.md` — do not copy it here.

- **Studio store is canonical** ([[D-002]], [[D-007]]). `runs/{id}.json` is
  immutable ingest/model output; `labels.jsonl` is append-only. Latest event per
  **row identity** wins ([[D-008]]); deletes are tombstones (`unmiss`). Never
  rewrite history in place. The extension stays storeless.
- **Extension stays frozen** ([[D-006]]). No `chrome.storage` canonical store, no
  refinement hotkeys, no panel export, no SPA remount for an on-page editor.
- **Stay stdlib** ([[D-005]]). No pip dependencies for the server, no framework
  for the page, until it actually hurts. `yt-dlp` is the one external tool.
- **Eval chrome stays behind eval mode** ([[D-010]]). Check/note/rationale are
  not the annotation loop. Default off. Don't collapse eval channels ([[D-021]]).

## Stack

- Studio: Python 3 stdlib server (`http.server`) + one vanilla-JS HTML page.
  Store is `runs/*.json` + append-only `labels.jsonl`. No framework, no database,
  no npm, no build step. UI modules live in `apps/studio/ui/` — `keys.js` is the
  one keyboard dispatcher ([[D-016]]); shared UI state lives on `S` ([[D-017]]).
- Extension: Manifest V3, vanilla JS, Shadow DOM panel ([[D-018]]). No storage
  permissions. Input-focus guard uses `e.composedPath()[0]`.

The suggester skill lives outside the repo at `~/.claude/skills/yt-clipper/` and
writes runs into `apps/studio/runs/`. In-app ingest is the other door (empty
markers). Suggest-as-studio-action is backlog ([[D-011]]).

Layout: `apps/extension/`, `apps/studio/`, `docs/coordination/`, `docs/sessions/`,
`docs/clip-schema.md`, `docs/youtube-clip-marker-prd.md`.
`docs/two-surface-handoff.md` is historical; live decisions are D-001….
`docs/prs/` are task-spec provenance, not a second `CURRENT.md`.

## Code style

- Vanilla JS, modern (ES2022+) fine — runs in current Chrome only. Functional
  over class-based. Self-contained modules over scattered side effects. No sloppy
  code that wouldn't pass strict mode.
- Python: stdlib style, small pure functions, no dependencies.

## Git workflow

- Never commit to `main`. Always pull latest `main` before creating a new branch.
- Always create a NEW branch for each change (never reuse old names).
- One PR per change, even small ones.
- Never `git add -A` — data and session logs are not the product PR.
- Don't push new commits while BugBot is mid-review (wait or the review restarts).
- Commit messages: concise single-line title with PR number prefix (e.g. `PR 1:
  skeleton extension with shadow-DOM panel`), plus an optional body. Title stays
  single-line; body is free-form.

## Session prompt audit

If this session was driven by a session prompt (`.md` file), do NOT commit until
completing the three-part audit in `docs/coordination/README.md` (acceptance
criteria with evidence, assumptions, skips & divergences). Same audit before
recording a SHA on any `CURRENT.md` task.

## Before committing

Follow the pre-SHA checklist in `docs/coordination/README.md`. Short form:

- Scan for unguarded async, missing empty/error UI, edge cases (empty arrays,
  null `end`/`videoId`, duplicate starts, no pending start), unguarded keyboard
  listeners.
- When fixing a bug, check the same issue elsewhere in the file.
- Batch related fixes in one commit.
- No secrets. Studio boots and a label save round-trips. Extension still loads
  unpacked from `apps/extension`.
