# PR 1 — Skeleton extension

First PR. Goal: prove the wiring. A Chrome extension that loads on YouTube watch pages and injects a visible placeholder panel. No hotkeys, no storage, no real functionality.

**Why this PR exists alone:** BZ has never written a Chrome extension. Getting "load, match the right URL, inject a styled panel, isolate from YouTube's CSS" working as a single unit means later PRs (hotkeys, storage, refinement) don't have to debug "why isn't anything showing up" on top of their own complexity.

## Done criteria

1. `chrome://extensions` shows the extension loaded with no errors.
2. Visit any `https://www.youtube.com/watch?v=*` page → panel appears in the top-right, displaying "Clip Marker".
3. Visit `https://www.youtube.com/` (homepage) → no panel.
4. Visit `https://google.com` → no panel.
5. Panel's styles are not visually broken by YouTube's CSS (rounded corners intact, padding consistent, font matches what we set, not what YouTube uses).
6. DevTools → Elements panel: the panel's CSS lives inside a shadow root, not in the main document head.

## Out of scope for PR 1

- Hotkeys (PR 2)
- Description input (PR 2)
- Storage / persistence (PR 3)
- SPA navigation handling (PR 3) — for now, manually refresh after navigating between videos. The panel will persist from the previous video, but that's fine because it doesn't do anything yet.
- Marks list, edits, exports (PR 4)
- Build tooling, TypeScript, npm

## Key concepts to understand before writing code

**Manifest V3.** A Chrome extension is described by `manifest.json` at the root. It declares metadata and which pages the extension should run on. We need three fields: top-level metadata (`manifest_version`, `name`, `version`, `description`), and `content_scripts` — an array describing what JS/CSS gets injected into which pages.

**Content scripts.** JS files declared in `content_scripts` get injected into pages whose URL matches the declared `matches` patterns. They run in an *isolated world* — same DOM as the host page, but separate JS scope. The host page's globals don't collide with yours. URL matching uses Chrome's match pattern syntax, not regex.

Important limitation: content scripts run on page load. They do NOT re-fire when YouTube SPA-navigates (clicking a thumbnail to swap videos without a full reload). Ignored in PR 1; PR 3 handles it.

**Shadow DOM.** A DOM API for isolating a subtree from the rest of the page's CSS. Why we need it: YouTube has thousands of CSS rules with broad selectors. A plain injected `<div>` would inherit and conflict. Shadow DOM creates a boundary — outside CSS doesn't reach inside, inside CSS doesn't leak out.

Usage pattern:
1. Create a host element and append to `document.body`.
2. Call `host.attachShadow({ mode: 'open' })` → returns a shadow root.
3. Append your content and a `<style>` element *inside* the shadow root.

The `<style>` element must be inside the shadow root, not in the main document head. That's the whole point.

## File structure

```
yt-clip-marker/
├── manifest.json
├── content.js
├── README.md
└── .gitignore
```

Single content script file for now. Modular split happens when complexity demands it (PR 2+).

`CLAUDE.md` is a separate manual task — adapt from media-scraper's, strip the pipeline-specific stuff. Not part of this PR.

## Implementation

### `manifest.json`

Exact contents:

```json
{
  "manifest_version": 3,
  "name": "YouTube Clip Marker",
  "version": "0.0.1",
  "description": "Mark and export clip ranges from YouTube videos.",
  "content_scripts": [
    {
      "matches": ["https://www.youtube.com/watch*"],
      "js": ["content.js"],
      "run_at": "document_idle"
    }
  ]
}
```

`run_at: document_idle` is the default; included explicitly for clarity. No `permissions`, `host_permissions`, `action`, or `background` needed for PR 1.

### `content.js`

Structure (you, Claude Code, write the implementation):

1. A top-level IIFE or top-level statement that runs on script load. No DOM-ready event needed; `document_idle` already guarantees parse is complete.
2. Create a host `<div>` and append to `document.body`. Give it an `id` like `yt-clip-marker-host` so it's findable in DevTools.
3. Attach an open-mode shadow root.
4. Build the shadow root's content:
   - A `<style>` element containing the panel CSS (inline as a template literal — no separate CSS file in PR 1).
   - A content `<div>` containing the text "Clip Marker".

Panel CSS requirements:
- `position: fixed`, anchored top-right, clear of YouTube's header (e.g. `top: 80px; right: 20px`).
- Width around 280px.
- Visible background (light or dark — pick one that looks decent on YouTube), padding, border-radius.
- `z-index: 999999` — must sit above YouTube's UI.
- System font stack: `-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`.
- Text color and font-size that look intentional, not default.

Keep all code in `content.js` for this PR. Splitting into modules is PR 2 work.

### `README.md`

Short. Contains:
- One-sentence project description.
- "How to install for development" — clone, visit `chrome://extensions`, enable Developer mode, click "Load unpacked", select the project folder, visit a YouTube watch page.
- A line saying V1 is in active development; status link to PRs.

### `.gitignore`

Standard hygiene:

```
.DS_Store
node_modules/
*.log
.env
```

## Self-audit (run before committing)

Before pushing, verify each:

1. Panel appears on a YouTube watch page in the top-right corner.
2. Panel does NOT appear on the YouTube homepage or other sites.
3. DevTools → Elements panel: find `#yt-clip-marker-host`. It has a `#shadow-root (open)` child. The `<style>` element is inside that shadow root, not in the document `<head>`.
4. Right-click the panel → Inspect. Walk the inheritance — no YouTube CSS is bleeding in (the font in your panel matches the system font you set, not whatever YouTube uses).
5. Refresh the page. Panel re-appears (content scripts re-fire on full reload).
6. Manifest has no warnings or errors in `chrome://extensions` (Chrome will surface validation issues there).

If any of these fails, debug before opening the PR.

## Verification (for BZ to run after Claude Code finishes)

1. `git status` and `git diff` — confirm only the expected files changed. Read each file. Understand what was written.
2. Load unpacked in Chrome (`chrome://extensions` → "Load unpacked" → select project folder).
3. Walk through the done criteria above.
4. Open DevTools on a watch page. Find the host element. Confirm the shadow root structure matches what the spec describes.
5. Ask Claude Code to explain any line you don't understand. Specifically: any usage of `attachShadow`, how the CSS got into the shadow root, why `document_idle` was chosen.

If anything fails, capture the specific failure (DevTools console errors, screenshots) before iterating with Claude Code.

## Commit

One commit per PR. Suggested commit message:

```
PR 1: skeleton extension with shadow-DOM-isolated panel on YouTube watch pages

- Manifest V3, content script targeting /watch* URLs
- Open shadow root, scoped panel CSS
- Placeholder panel with "Clip Marker" text
- No hotkeys, storage, or video integration yet (PR 2/3/4)
```
