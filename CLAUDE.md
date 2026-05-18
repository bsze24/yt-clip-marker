# CLAUDE.md

Guidance for Claude Code when working in this repo.

## Project context

Chrome extension for marking and exporting clip ranges from YouTube videos. Side project to media-scraper; downstream goal is feeding annotated clip ranges into media-scraper's reel and auto-suggest features.

Tech stack:
- Manifest V3 Chrome extension
- Vanilla JavaScript (no TypeScript, no bundler for V1)
- `chrome.storage.local` for persistence
- Shadow DOM for panel UI isolation

There is no server, no database, no build step, no npm dependencies, no deployment. The extension is a folder of files loaded directly into Chrome via `chrome://extensions` → "Load unpacked".

## Context files — read before starting any task

- `CLAUDE.md`
- `docs/youtube-clip-marker-prd.md` — full product requirements
- The current PR spec (e.g., `docs/prs/pr-1-skeleton.md`)

## Architecture rules

- **All panel UI lives inside Shadow DOM.** YouTube's CSS will override anything mounted directly into the document. Every visible UI element gets a host div + open-mode shadow root + styles scoped inside.
- **`chrome.storage.local` for persistence, never page `localStorage`.** Extension-scoped, survives YouTube's storage management, accessible from a popup later if added.
- **Debounce storage writes (~500ms).** Mutate in-memory immediately for UI responsiveness; persist after the user pauses input. Rapid-tap nudge (`Shift+→` ten times) must fire one storage write, not ten.
- **Hotkey listener as a self-contained module.** One place to register/route hotkeys, not `addEventListener` calls scattered through the codebase. Easier to debug; easier to extract later if the broader keyboard-extension project happens.
- **Input-focus guard on every keyboard listener.** Check `document.activeElement` for `INPUT`, `TEXTAREA`, or `isContentEditable === true` before acting. Also guard against modifier keys (Cmd/Ctrl/Alt), key repeat (`e.repeat`), and IME composition (`e.isComposing`).
- **No broad permissions or `host_permissions` unless required.** Permission requests trigger Chrome warnings on install; only ask for what we need.
- **SPA navigation handling via `yt-navigate-finish`.** YouTube swaps video content without full page reloads; content scripts do NOT re-fire on SPA navigation. Listen for `yt-navigate-finish` on the document and re-mount / re-load marks on each navigation. (PR 3+.)

## File structure (current)

```
yt-clip-marker/
├── manifest.json
├── content.js
├── README.md
├── CLAUDE.md
├── docs/
│   ├── youtube-clip-marker-prd.md
│   └── prs/
│       └── pr-*.md
└── .gitignore
```

Modular split (`content/index.js`, `content/panel.js`, `content/hotkeys.js`, etc.) happens when complexity demands it — likely PR 2.

## Code style

- Vanilla JS, modern (ES2022+) features fine — extension runs in current Chrome only.
- Functional, not class-based, where possible.
- Named exports if/when modules are introduced.
- Self-contained modules over scattered side effects.
- No shortcuts or sloppy types — even without TypeScript, write code that would pass strict mode.

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
  - Missing try/catch around async operations (`chrome.storage.local` APIs are async)
  - Missing error/empty states in UI
  - Edge cases (empty marks array, null `videoId`, missing video element, no pending start)
  - Unguarded keyboard listeners (input-focus guard, modifier-key guard, repeat guard)
- When fixing a bug, check for similar issues elsewhere in the file.
- Batch related fixes in one commit (reduces BugBot round-trips).
- Verify no API keys, tokens, or secrets in committed code.
- Verify the extension still loads in Chrome without errors after changes — `chrome://extensions` shows no warnings, console clean on a watch page.

## Communication style

When correcting a mistake or changing approach, briefly explain *why* (e.g. "Shadow DOM because YouTube's CSS would otherwise inherit"). I'm using this project to learn — explain the underlying principle, not just the fix.
