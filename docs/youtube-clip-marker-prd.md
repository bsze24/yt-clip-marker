# YouTube Clip Marker — V1 PRD

Working name TBD. Side project to media-scraper. Supersedes prior PRD versions.

## Problem

BZ creates long-form video content (music lessons, sales calls) and needs to annotate highlights for sharing and future consumption. Two pain points compound:

1. **Capture friction.** Watching → catching a moment → switching tabs → editing the description → manually typing timestamps → returning. Friction high enough to make annotation inconsistent.
2. **Refinement friction.** Nailing the "perfect clip" boundaries requires rewatching the same range three to five times. Waste compounds across marks.

Net effect: videos end up under-annotated, and there's no source of structured highlight ranges to seed eventual auto-suggest in media-scraper.

## Reframe

This is a **clip-marking tool for long-form video**, not a YouTube chapter helper. The data model centers on `{start, end, description}` ranges.

Three downstream uses, in priority order:

1. **Navigable timestamps in YouTube descriptions** — pasted as `M:SS Title` lines, which YouTube auto-links to seek times. Works for any video; no chapter-rule validation needed. This is the primary near-term use case.
2. **JSON export for media-scraper** — full range data for the eventual reel and auto-suggest features.
3. **Formal YouTube chapters** — same `M:SS` output but requires meeting YouTube's stricter rules (first = `0:00`, min 3, min 10s gap). Out of V1 scope; if a user's marks happen to satisfy the rules, the chapter export works as a side effect.

## Design principle: "watch once"

The tool exists to make a *single careful watch* sufficient for annotation. Capture happens during watching with minimum disruption. Refinement happens afterward in the marks panel, **without re-watching the full video**. If a user has to rewatch to find boundaries, the tool has failed.

Concrete decisions this drives:

- `]` does not pause the video — capture must not interrupt the watching flow.
- Description is optional at capture time. Hit `]` then Enter to save with no description; add it later.
- Mark refinement uses the video itself as the editing interface — preview ranges with one click, nudge boundaries with keyboard.

## Users

Just BZ. Single user, single machine, no auth, no sync. Multi-user is V2.

## V1 scope

### Capture hotkeys

Active on YouTube watch pages when the user is not typing in an input / textarea / contenteditable.

| Key | Action |
|---|---|
| `[` | Mark range start. Captures `currentTime − 5s` (backdate for reaction lag). Stores as pending. Brief toast confirms capture. If `[` fires again before `]`, second overwrites first. |
| `]` | Mark range end. Requires pending start; otherwise no-op. Captures `currentTime`. **Does not pause the video.** Opens inline description input near the bottom of the player. Enter saves with description; empty Enter saves with no description; Esc dismisses (mark still saved with empty description). |

### Refinement hotkeys

When the marks panel has a selected mark (via click or `Shift+J` / `Shift+K`):

| Key | Action |
|---|---|
| `Shift+J` | Next mark (select + seek to start) |
| `Shift+K` | Previous mark (select + seek to start) |
| `Tab` | Cycle focused boundary (start ↔ end) within selected mark |
| `Shift+←` | Nudge focused boundary −1s |
| `Shift+→` | Nudge focused boundary +1s |
| `Shift+T` | Edit description of selected mark |
| `x` | Delete selected mark (with confirm) |
| `Esc` | Cancel input / clear selection |

**"Focused boundary" defined.** A mark has two boundaries: start time and end time. When a mark is selected, exactly one boundary is *focused* — the target of nudge operations. Default on selection is **start** (most common case after the -5s backdate). `Tab` cycles to end. A visual indicator on the selected mark row shows which boundary is focused (highlighted timestamp or cursor underline — exact treatment is an open UI question).

### Refinement via re-capture

Click a mark to select it and seek to its start. While selected, pressing `[` at the current playhead overwrites the start; `]` overwrites the end. Same muscle memory as initial capture, used for *coarse* re-capture. For ±1s tweaks, use `Shift+arrow` nudges.

### Marks panel UI

A panel anchored to the right of the YouTube player. Three properties:

- **Floating** — positioned over the page, not embedded in YouTube's layout. Doesn't push YouTube content around. Survives YouTube layout updates.
- **Default-expanded** — visible by default on every watch page. No friction to see marks.
- **Collapsible** — can be tucked away (hotkey or small button) when full video attention is wanted.

Each row:

```
M:SS – M:SS   Description text
```

**Click anywhere on the row** → seek to start, play, **auto-pause at end**. Preview is the default click behavior because it's the most common action.

**Click the timestamp text specifically** → just seek to start, don't play (opt-in for the edge case where preview isn't wanted).

Hover or selected state reveals edit / delete affordances. Panel collapsed/expanded state persists across pages.

### Storage

`chrome.storage.local`, keyed by `videoId`. Schema:

```json
{
  "videoId": "abc123",
  "videoTitle": "Customer call — Acme Corp 2026-04-15",
  "videoUrl": "https://youtube.com/watch?v=abc123",
  "lastUpdated": "2026-05-17T10:23:00Z",
  "marks": [
    { "start": 12.5, "end": 47.2, "description": "Customer pain: data silos across CRM and email" }
  ]
}
```

Persists across reloads, browser restarts, and SPA navigation between videos.

Storage writes are debounced (~500ms): in-memory state mutates immediately for UI responsiveness; persistence happens after the user pauses input. Worst-case data loss on crash is ~500ms of work. Important for the rapid-tap nudge case — `Shift+→` ten times in a row should not fire ten storage writes.

### Exports

Two buttons in the marks panel; both copy to clipboard.

**Copy as timestamped links** — `M:SS Title` format, end times dropped:

```
0:00 Intro
2:15 Customer pain: data silos
8:42 Pricing objection
```

YouTube auto-links any `M:SS` line in a video description to a seek time. Works for any video regardless of count or spacing. No validation against formal-chapter rules.

**Copy as JSON** — full structured data with start/end ranges. Primary export for media-scraper.

## Hotkey choice rationale

YouTube watch pages bind a lot of keys natively (`j` `k` `space` `m` `,` `.` `<` `>` `/` `1-9` `t` `Esc` and more). Overriding them breaks host-page behavior, which is worse than mild inconsistency with media-scraper.

The principle: **match media-scraper semantically where YouTube doesn't conflict; use `Shift+` versions where it does; choose freely where neither binds.** That's why `Shift+J` / `Shift+K` instead of plain `j` / `k`, and why `[` `]` `Shift+arrows` `x` are used directly — YouTube doesn't bind them.

`x` for delete and `Shift+T` for edit need verification in implementation; ~80% confident YouTube doesn't bind them on the watch page.

## Adjacent projects (architectural hints, not V1 scope)

Two adjacent projects influence design without expanding V1 scope:

- **Memory / PKM project.** BZ is considering a broader system that captures interesting content across articles, tweets, and (eventually) video clips. Implication: keep the JSON export schema generic enough that a future PKM could ingest these marks alongside other annotated content. Don't over-fit to YouTube specifics. Eventually the underlying transcript may want to be accessible alongside the marks.
- **Superbrowser extension.** BZ is considering a broader keyboard-shortcut extension that augments arbitrary web apps. Implication: implement the hotkey listener as a self-contained module (one place to register/route hotkeys), not scattered `addEventListener` calls. Easy to extract later if the superbrowser happens.

Neither changes V1 scope. They're flags to keep the design honest.

## Explicit non-goals

- Voice input. V2.
- YouTube Data API write-back. V2 at earliest; probably never given human-review-before-publishing requirement for customer-facing content.
- Sync across devices.
- Mobile / in-car case. Different product.
- YouTube Shorts, playlists, embedded players. Only `/watch?v=` URLs.
- Formal YouTube chapter rule validation. V2.
- Indexed mark hotkeys (`1-9`). YouTube binds those; doesn't scale past 9 marks anyway.
- Multi-user / sharing.
- Underlying transcript capture or display. Likely V2+ when media-scraper integration arrives.

## Done criteria

1. Loads as unpacked Chrome extension.
2. On a YouTube watch page, marks panel renders without breaking YouTube's UI.
3. `[` and `]` produce a mark with optional description, never interrupting playback.
4. Marks list shows ranges; click-to-preview works (seek + play + auto-pause at end); Tab cycles boundary focus; Shift+arrows nudge by 1s; re-hotkey overwrites; delete works.
5. Reload → marks persist for that video.
6. SPA navigation to a different video → panel re-mounts with marks for the new video.
7. Both export buttons produce correct clipboard content.
8. No hotkey fires while typing in YouTube inputs (search, comments, description editor).

## Open implementation questions

Resolved in the impl spec, not here:

- Shadow DOM for the panel — almost certainly yes; YouTube's CSS will eat anything not isolated.
- Build tooling — lean vanilla JS for V1, no bundler.
- SPA navigation detection: `yt-navigate-finish` (cleanest, depends on undocumented YouTube behavior) vs. `MutationObserver` (robust, more complex) vs. polling `location.href` (hacky, simple).
- Verifying `x` and `Shift+T` don't conflict on the watch page.
- Hotkey listener architecture (self-contained module per superbrowser hint).
- Debounce implementation for storage writes.
- Exact visual treatment of focused boundary (highlight, underline, etc.).

## Next step

Implementation spec covering manifest structure, content script lifecycle (SPA navigation as a core concern), shadow DOM setup, hotkey listeners with input-focus guards, `chrome.storage.local` access with debounced writes, and clipboard API usage.
