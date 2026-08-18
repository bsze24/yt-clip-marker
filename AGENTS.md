# AGENTS.md

Shared guidance for coding agents working in this repo.

Claude Code loads these instructions through the `@AGENTS.md` import in
`CLAUDE.md`. Keep shared project guidance here to prevent the two files from
drifting.

## Project context

**One clipper, two surfaces.** This repo is a clip-marking tool for long-form YouTube video (music lessons), split into two clients of one clip record:

- **Studio (`apps/studio/`) — the workspace.** A local Python-stdlib web app: time-aligned grid of captions, markers, and published description timestamps; keyboard-first clip creation; taxonomy (work / lane / tags); in-app ingest (URL → transcript + gaps + extracted). This is where annotation, refinement, and (future) export happen. It began life as an eval dashboard for the suggester skill — do NOT treat it as disposable eval tooling; it is the product.
- **Extension (`apps/extension/`) — the viewing surface, frozen thin.** Manifest V3 Chrome extension loaded unpacked from `apps/extension`. Coarse `[` / `]` capture on the watch page, in-memory only. It is not a store, not an editor, and does not grow taxonomy/transcript/export features. Do not rebuild the on-YouTube IDE.

The surfaces share the clip contract (`docs/clip-schema.md`), never code. Side project to media-scraper, which will consume clips via the studio's JSON export only — media-scraper never lives in this tree.

Tech stack:
- Studio: Python 3 stdlib server (`http.server`) + one vanilla-JS HTML page. `yt-dlp` on PATH for ingest. Store is `runs/*.json` + append-only `labels.jsonl`. No framework, no database, no npm, no build step.
- Extension: Manifest V3, vanilla JS, Shadow DOM panel. No storage permissions.

## Context files — read before starting any task

- `AGENTS.md`
- `docs/youtube-clip-marker-prd.md` — two-surface product requirements
- `docs/clip-schema.md` — the shared clip contract and store shapes
- `docs/two-surface-handoff.md` — how the product model got here
- The current PR spec under `docs/prs/` if one exists for the task

## Session logs

See `docs/sessions/` for prior-session context; resume related work by matching the frontmatter `track:` value.

## Architecture rules — studio

- **The studio is the workspace; the store is the source of truth.** `runs/{id}.json` is immutable ingest/model output; `labels.jsonl` is append-only human events. Latest event per row identity wins; deletes are tombstones (`unmiss`). Never rewrite history in place.
- **Row identity, not start time.** Duplicate timestamps are real (two markers at 3:19). Selection and event keys use row identity (`(runId, markerIndex)` or `(runId, start)` for additions) — never assume start times are unique.
- **`kind` (TAKE/CONCEPT) is legacy.** Readable on old data, never required on new writes. Taxonomy is work / lane / tags.
- **Eval chrome stays behind eval mode.** Check/note feedback, rationales, and their stats are skill-eval tooling, not the annotation loop. Default off.
- **Keyboard-first; keep keys on the page.** The grid owns `j`/`k`/`Enter`/etc. The YouTube IFrame steals focus after interactions — re-blur it (`keepKeysOnPage`) so hotkeys keep working.
- **One keyboard dispatcher.** All global hotkeys route through the priority chain of named contexts in `ui/keys.js` (combo → composer form → desc inputs → typing guard → tab prefix → grid → player). Never add a second document-level keydown listener; add or change behavior by editing the owning context.
- **Shared UI state lives on `S`.** Cross-module mutable state is the `S` object in `ui/state.js`; state owned by one module (player handle, suggest highlight, tab-prefix timer) stays module-local. No new top-level `let` globals.
- **Stay stdlib.** No pip dependencies for the server, no framework for the page, until it actually hurts. `yt-dlp` is the one external tool (subprocess).

## Architecture rules — extension

- **Frozen at thin client.** Load on watch pages, coarse capture, in-memory marks. The original PR 3/4 plans (chrome.storage as canonical store, refinement hotkeys, panel export, SPA remount work for the on-YouTube IDE) are superseded — see `docs/prs/pr-3-two-surface-refactor.md`.
- **All panel UI lives inside Shadow DOM.** YouTube's CSS will override anything mounted directly into the document.
- **Input-focus guard on every keyboard listener.** Check `e.composedPath()[0]` for `INPUT`, `TEXTAREA`, or `isContentEditable === true` (`document.activeElement` can't see through shadow roots). Also guard modifiers (Cmd/Ctrl/Alt), key repeat (`e.repeat`), and IME composition (`e.isComposing`).
- **Hotkey listener as a self-contained module.** One place to register/route hotkeys.
- **No broad permissions or `host_permissions` unless required.**

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
│       ├── index.html        markup only; loads /ui/ assets
│       ├── ui/               ES modules (served via allowlisted /ui/ route)
│       │   ├── main.js       entry: event wiring + boot
│       │   ├── keys.js       global keydown dispatcher (priority contexts)
│       │   ├── state.js      the one shared mutable state object (S)
│       │   ├── grid.js       row building, alignment, selection, rendering
│       │   ├── suggest.js    taxonomy vocab, dropdown, tag chips
│       │   ├── composer.js   add-clip form logic
│       │   ├── persist.js    all server writes + debounces
│       │   ├── player.js     YouTube IFrame wrapper, focus management
│       │   ├── runs.js       run list polling + switching
│       │   ├── api.js        fetch wrapper + save-failure surface
│       │   ├── util.js       pure helpers, constants
│       │   └── styles.css
│       ├── attach_cues.py    CLI: merge a transcript dump into a run
│       ├── attach_extracted.py CLI: attach or migrate description timestamps
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

- Vanilla JS, modern (ES2022+) fine — runs in current Chrome only. Functional over class-based. Self-contained modules over scattered side effects. No sloppy code that wouldn't pass strict mode.
- Python: stdlib style, small pure functions, no dependencies.

## Git workflow

- Never commit to `main`.
- Always pull latest `main` before creating a new branch.
- Always create a NEW branch for each change (never reuse old names).
- One PR per change, even small ones.
- Don't push new commits while BugBot is mid-review (wait or the review restarts).
- Commit messages: concise single-line title with PR number prefix (e.g. `PR 1: skeleton extension with shadow-DOM panel`), plus an optional body for context, bullet points, or rationale. Title stays single-line; body is free-form.

## Session prompt audit

If this session was driven by a session prompt (`.md` file), do NOT commit until completing this audit:

1. **Task verification.** Compare every task in the prompt against what was built. For each task, confirm it was done with specific evidence (function name, file, line) or flag what's missing/different.
2. **Assumptions.** List any assumptions made that weren't explicit in the prompt — places where two reasonable implementations were possible and you picked one. Explain why.
3. **Skips & divergences.** List anything from the prompt you intentionally skipped or interpreted differently, and why.

## Before committing

- Scan changed files for:
  - Missing try/catch around async operations (fetch in the studio page, `chrome.*` APIs)
  - Missing error/empty states in UI (no runs, ingest failure, missing video element)
  - Edge cases (empty marks/markers array, null `videoId`, null `end`, duplicate start times, no pending start)
  - Unguarded keyboard listeners (input-focus guard, modifier-key guard, repeat guard)
- When fixing a bug, check for similar issues elsewhere in the file.
- Batch related fixes in one commit (reduces BugBot round-trips).
- Verify no API keys, tokens, or secrets in committed code.
- Studio: `python3 apps/studio/server.py` boots, existing runs load, a label save round-trips.
- Extension: still loads unpacked from `apps/extension` — `chrome://extensions` shows no warnings, console clean on a watch page.

## Communication style

When correcting a mistake or changing approach, briefly explain *why* (e.g. "Shadow DOM because YouTube's CSS would otherwise inherit"). I'm using this project to learn — explain the underlying principle, not just the fix.
