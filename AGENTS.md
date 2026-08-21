# AGENTS.md

Shared guidance for coding agents working in this repo. Process detail is not here — it is
in `docs/coordination/README.md`, and duplicating it into this file is how the two drift.

## Read first, in order

1. `docs/coordination/README.md` — roles, vocabulary, handoff cycle, review loop, and the
   audit every implementer owes before recording a SHA.
2. `docs/coordination/CURRENT.md` — the one active task and where the baton is.
3. `docs/coordination/REVIEW.md` — active review targets and findings.
4. `docs/coordination/BACKLOG.md` — roadmap, deferred work, tech debt, open modeling decisions.
5. `docs/coordination/DECISIONS.md` — durable calls (`D-001`…). Do not relitigate a decision
   silently; supersede it with a new dated entry.
6. The current PR spec under `docs/prs/`, if one exists for the task.

Git history is the source of truth for code; those files are the source of truth for intent.
The product why is `docs/youtube-clip-marker-prd.md`.

## Repo state

`main` is `5af3e13` (2026-08-18). The two-surface layout is merged: the extension lives at
`apps/extension/`, the studio at `apps/studio/`, and the clip contract at
`docs/clip-schema.md`. The old `content/` directory in the repo root is gone.

Older branches and session logs still describe the pre-merge layout, so confirm which tree you
are standing in before quoting a path from one of them. `docs/coordination/CURRENT.md` §0
carries the live PR table.

## Mission — two goals, both first-class

1. Ship the clipper.
2. **Grow Brian's understanding** of skills, agents, and web-app engineering. This is a
   primary goal, not a side effect.

Every agent is a mentor. Explain the why and the tradeoffs, teach while you work, flag gaps
worth drilling, and steer toward the answer rather than silently producing it. Brian learns by
building — operator background, not a career engineer — and works hands-on.

Concretely: reviews teach rather than just listing fixes; when implementing, say what changed
and why. When you correct a mistake, give the underlying principle ("Shadow DOM, because
YouTube's CSS would otherwise inherit into the panel"), not just the fix. The principle
transfers; the fix does not.

## Project context

**One clipper, two surfaces** ([[D-001]]). A tool for marking clips in long-form YouTube music
lessons, split into two clients of one clip record:

- **Studio — the workspace.** A local Python-stdlib web app: a time-aligned grid of captions,
  skill markers, added markers, and extracted markers; keyboard-first clip creation; taxonomy of
  work, lane and tags; in-app ingest from a URL. It began as an eval dashboard for the
  `yt-clipper` skill and stayed in daily use until it *was* the product. It is not disposable
  eval tooling.
- **Extension — the viewing surface, frozen thin** ([[D-006]]). Manifest V3, loaded unpacked.
  Coarse `[` / `]` capture on the watch page, in memory only. Not a store, not an editor. It
  does not grow taxonomy, transcript, or export features. Do not rebuild the on-YouTube IDE.

The two share the clip contract (`docs/clip-schema.md`), never code. media-scraper is a
separate repo downstream and consumes clips through the studio's JSON export only; it never
lives in this tree.

The clip record is video identity, `start`, a nullable `end`, and work / lane / tags. `end`
stays nullable until range collection lands ([[D-012]]).

**Vocabulary matters here.** Three kinds of marker: *skill marker* (skill proposal),
*added marker* (human, after ingest), *extracted marker* (published description stamps).
Do not say gold — that word collides with the `g` few-shot grade. The eval verdicts —
`g`, `x`, taxonomy-without-`g`, `star`, blank — are five distinct channels and collapsing
them has caused real errors. Full table in `docs/coordination/README.md`.

## Session logs

Work-session state lives in `docs/sessions/<date>-<HHMM>-<surface>-<slug>.md` — one committed
file per session, with a `track:` in frontmatter grouping the logs that belong to one
workstream.

To resume a thread: filter by `track:`, then open the candidates and read their "Project
context" blocks, which name the resume head. **Do not just take the newest match** — the
filename carries the date the log was written, not the dates it covers, and a log written
after the fact sorts newest while pointing backwards. On `track: studio-workspace` today the
head is `2026-08-16-1507-grok-studio-fable-lock.md`, and the newer `2026-08-17-1740-…` file
says so itself. The folded ledger shares the track but is a data artifact, not a resume point.

- **Learning state** — what Brian understands, drills owed, the confusions themselves — lives
  in these logs, never in the coordination docs.
- **Project state** — tasks, decisions, roadmap, findings — lives in the coordination docs.
- A real project finding that surfaces during a learning session is project state. What the
  artifact is decides its home, not how it came up.

## Standing guardrails

These override convenience. Full statements are in `DECISIONS.md`; live task state is
`CURRENT.md` and is not copied here.

- **The studio store is canonical** ([[D-002]], [[D-007]]). `runs/{id}.json` is immutable
  ingest and model output; `labels.jsonl` is append-only. Latest event per row identity wins
  ([[D-008]]); deletes are `unmiss` tombstones. Never rewrite history in place. The extension
  stays storeless.
- **The extension stays frozen** ([[D-006]]). No `chrome.storage` canonical store, no
  refinement hotkeys, no panel export, no SPA remount for an on-page editor.
- **Stay stdlib** ([[D-005]]). No pip dependencies for the server, no framework for the page,
  until it actually hurts. `yt-dlp` is the one external tool.
- **Eval chrome stays behind eval mode** ([[D-010]]). Check, note and rationale are not the
  annotation loop. Default off, and do not collapse the eval channels ([[D-021]]).

## Stack

- **Studio:** Python 3 stdlib (`http.server`) plus one vanilla-JS page, served on
  `127.0.0.1:8765`. Store is `runs/*.json` and append-only `labels.jsonl`. No framework, no
  database, no npm, no build step. UI modules live in `apps/studio/ui/`; `keys.js` is the one
  keyboard dispatcher ([[D-016]]) and shared UI state lives on `S` ([[D-017]]).
- **Extension:** Manifest V3, vanilla JS, Shadow DOM panel ([[D-018]]). No storage permission.
  The input-focus guard reads `e.composedPath()[0]`, because `document.activeElement` cannot
  see through a shadow root.
- **The suggester skill** lives outside the repo at `~/.claude/skills/yt-clipper/` and writes
  runs into `apps/studio/runs/`. In-app ingest is the other door and produces empty
  `markers[]`. Suggest-as-studio-action is backlog ([[D-011]]).

`docs/two-surface-handoff.md` is historical provenance; the live decisions are `D-001`…
`docs/prs/` holds task specs that became PRs — provenance, not a second `CURRENT.md`.

## File structure (current)

```
yt-clip-marker/
├── apps/
│   ├── extension/
│   │   ├── manifest.json
│   │   └── content/          store.js, panel.js, hotkeys.js, index.js
│   └── studio/
│       ├── server.py         stdlib HTTP server + label-event store
│       ├── ingest.py         yt-dlp fetch: captions, gaps, description, extracted
│       ├── local.py          offline ingest: media file + sidecar subs/info.json
│       ├── prefetch.py       CLI: yt-dlp video + captions + run, for offline use
│       ├── index.html        markup only; loads /ui/ assets
│       ├── ui/               ES modules (served via allowlisted /ui/ route)
│       │   ├── main.js       entry: event wiring + boot
│       │   ├── keys.js       global keydown dispatcher (priority contexts)
│       │   ├── state.js      the one shared mutable state object (S)
│       │   ├── grid.js       row building, alignment, selection, rendering
│       │   ├── suggest.js    taxonomy vocab, dropdown, tag chips
│       │   ├── composer.js   add-clip form logic
│       │   ├── persist.js    all server writes + debounces
│       │   ├── player.js     YouTube embed + local <video> behind one interface
│       │   ├── runs.js       run list polling + switching
│       │   ├── api.js        fetch wrapper + save-failure surface
│       │   ├── util.js       pure helpers, constants
│       │   └── styles.css
│       ├── attach_cues.py    CLI: merge a transcript dump into a run
│       ├── attach_extracted.py CLI: attach or migrate description timestamps
│       ├── media/            local video/audio for offline playback (gitignored)
│       ├── runs/             {videoId}-{stamp}.json
│       ├── labels.jsonl      append-only human judgments
│       └── README.md         store/event schema details
├── docs/
│   ├── youtube-clip-marker-prd.md
│   ├── clip-schema.md
│   ├── two-surface-handoff.md
│   ├── tech-debt.md
│   └── prs/pr-*.md
├── README.md · AGENTS.md · CLAUDE.md · .gitignore
```

The suggester skill lives outside the repo at `~/.claude/skills/yt-clipper/` and writes runs into `apps/studio/runs/`.

## Code style

- Vanilla JS, ES2022+ is fine — this runs in current Chrome only. Functional over
  class-based. Self-contained modules over scattered side effects. Nothing that would fail
  strict mode.
- Python: stdlib style, small pure functions, no dependencies.

## Git workflow

- Never commit **code** to `main`. Pull latest `main` before creating a branch.
- **Living records go straight to `main`**: `docs/coordination/`, `docs/sessions/`,
  `docs/reference/`. They are appended to continuously, so a PR holds only a stale snapshot —
  PRs 5 and 6 both died that way, and the review record sat outside git for three days. Docs
  that *describe code* — `docs/clip-schema.md`, field tables, the file tree below — ride in the
  PR that changes the behaviour, or `main` documents software that does not exist yet. Test:
  would this doc be wrong once some open PR merges? Yes → it belongs in that PR. The cost of
  going straight to `main` is that nobody else reads it, so re-read before you push.
- A new branch per change; never reuse a branch name. One PR per change, even a small one.
- **Default to opening a PR. Merge only when Brian explicitly says to.** Standing instruction,
  2026-08-21. "Execute and PR", "do it", "ship it" authorise the *work*, not the merge — say the
  PR is open and stop. Permission is per-PR and never carries to the next one. The exception is
  the rule above: living records go straight to `main` and never wait for a PR.
  This exists because ten PRs reached `main` unreviewed in two days, and the one bug among them
  — PR 17 shipping a new code path on top of a live old one — was found by Brian using the app,
  not by the author who wrote and merged it.
- **Never `git add -A`.** Run data and session logs are not the product PR.
- Do not push while BugBot is mid-review — the review restarts.
- Commit messages: a single-line title prefixed with the PR number (`PR 1: skeleton extension
  with shadow-DOM panel`), plus an optional free-form body.

## Before committing

Run the pre-SHA checklist in `docs/coordination/README.md` — it is the one copy. If the
session was driven by a prompt file, the same three-part audit (acceptance criteria with
evidence, assumptions, skips and divergences) applies before you commit.

There is one test file, `apps/studio/tests/test_sidecars.py` — stdlib `unittest`, no
dependencies, covering the sidecar matching that F18 and F20 were both filed against. Run it:

```bash
python3 apps/studio/tests/test_sidecars.py
```

Everything else is unverified by machine. The floor is: that file passes, the studio boots and a
label save round-trips, and the extension still loads unpacked with a clean console on a watch
page.
