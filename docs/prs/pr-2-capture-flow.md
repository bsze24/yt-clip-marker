# PR 2 — Capture flow

Second PR. Goal: the core capture experience — `[` to mark start, `]` to mark end, type a description, see the mark appear in the panel. In-memory only. Persistence is PR 3.

**Why this PR exists alone:** Capture is the heart of the user-facing experience. Getting hotkeys, guards, two new UI surfaces, and the in-memory store working as one tested unit before adding storage means a future "marks disappeared!" bug can't simultaneously be a hotkey bug, a render bug, AND a storage bug. Isolate.

## Done criteria

1. Pressing `[` on a YouTube watch page captures `currentTime − 5s` as the pending start. A brief toast confirms (e.g. "Start at 1:23").
2. Pressing `]` while a pending start exists captures `currentTime` as end and opens a description input near the bottom of the viewport. Video does NOT pause.
3. Description input: typing + Enter saves the mark with the typed description. Empty Enter saves the mark with an empty description. Escape dismisses the input and saves the mark with an empty description (typed text discarded).
4. After save, the mark appears in the panel list, formatted as `M:SS – M:SS  Description`. Marks are sorted by start time.
5. Hotkeys do not fire while the user is typing in YouTube's search bar, comment box, or description editor — or while typing in *our own* description input.
6. Hotkeys do not fire with modifier keys (Cmd/Ctrl/Alt + `[`).
7. Hotkeys do not fire on key repeat (hold `[` down: still one mark, not 30).
8. `]` without a pending start: no-op. `[` twice without `]`: second overwrites first (no stacked pending starts).
9. Marks are wiped on full page reload. This is expected — persistence is PR 3.

## Out of scope for PR 2

- Persistence to `chrome.storage.local` (PR 3).
- SPA navigation handling (PR 3).
- Edit / delete marks (PR 4).
- Refinement hotkeys (`Shift+J`, `Shift+K`, `Tab`, `Shift+arrows`, etc.) (PR 4).
- Click-to-preview (PR 4).
- Exports (PR 4).
- Tooltips, help text, visual polish beyond functional.

## Key concepts to understand before writing code

**Multi-file content scripts.** Manifest V3's `content_scripts.js` can be an array of file paths. Files are injected in declared order and share an *isolated-world* global scope — top-level `const Foo = ...` in one file is accessible by name from later files. They cannot collide with YouTube's globals (isolated world), but they CAN collide with each other if you reuse names. Each module declares one top-level `const ModuleName = { ... }` to avoid collisions.

*Lurking trap (relevant for PR 3 SPA-nav handling, not PR 2):* if a content script ever re-runs in the same realm — e.g. via a programmatic re-injection on SPA navigation — the top-level `const` declarations will throw `SyntaxError: Identifier 'Store' has already been declared`. PR 2 doesn't trigger this (content scripts run once per page load), but the constraint is worth knowing so PR 3's re-mount design avoids it.

**The hotkey guard stack.** A document-level `keydown` listener fires for every keystroke on the page. Four guards must run *before* dispatching to handlers, each preventing a specific failure mode:

1. `e.repeat` — held-key repeat events. Without this, holding `[` fires `markStart()` ~30 times per second.
2. `e.isComposing` — IME composition events (Japanese/Chinese/Korean typing). Without this, hotkeys fire during character composition.
3. `e.ctrlKey || e.metaKey || e.altKey` — modifier keys. Without this, `Cmd+[` (browser navigate-back) also fires `markStart()`.
4. `isTypingTarget(e.composedPath()[0])` — focus on `INPUT`, `TEXTAREA`, or any element with `isContentEditable === true`. Without this, typing `[` in YouTube's search bar OR our own description input (inside a shadow root) fires `markStart()`.

**Why `e.composedPath()[0]` and not `document.activeElement`.** When focus is inside a shadow root (our description input lives in one), `document.activeElement` returns the *shadow host* — a plain `<div>` — not the actual focused input. The guard would silently fail: `isTypingTarget(host) === false`, so our handler fires even though the user is typing in our input. `e.composedPath()[0]` returns the actual originating element across shadow boundaries — the explicit API for "I know there are shadow boundaries; show me through them." Works identically for YouTube's main-DOM inputs (search bar, comment box) and our shadow-rooted inputs.

All four guards return early. None of them call `preventDefault` — we want the keystroke to keep doing its normal thing (typing into the input, browser navigation, etc.); we just want OUR handler to not fire.

Use `isContentEditable`, not `getAttribute('contenteditable')` — the former walks up the DOM tree for inherited editability (YouTube's comment box uses this pattern), the latter checks only the element's own attribute.

**Accessing YouTube's video element.** YouTube uses a single `<video>` element on watch pages. `document.querySelector('video')` returns it. `video.currentTime` is the current playback position in seconds (float). Read it at the moment a hotkey fires — don't cache it. The video element may not exist briefly during SPA navigation; handle null defensively.

## File structure

```
yt-clip-marker/
├── manifest.json                  ← updated: content_scripts.js now an array
├── content/
│   ├── store.js                   ← in-memory data + formatTime helper
│   ├── panel.js                   ← panel UI: marks list, description input, toast
│   ├── hotkeys.js                 ← keyboard listener + command handlers
│   └── index.js                   ← orchestrator: mount panel, init hotkeys
├── content.js                     ← DELETED
├── README.md
├── CLAUDE.md
├── docs/
│   ├── youtube-clip-marker-prd.md
│   ├── tech-debt.md
│   └── prs/
│       ├── pr-1-skeleton.md
│       └── pr-2-capture-flow.md   ← this file
└── .gitignore
```

Manifest must declare files in dependency order: `store.js` (no deps) → `panel.js` (uses Store, formatTime) → `hotkeys.js` (uses Store, Panel) → `index.js` (uses all).

## Manifest changes

Replace the `content_scripts` entry:

```json
"content_scripts": [
  {
    "matches": ["https://www.youtube.com/watch*"],
    "js": [
      "content/store.js",
      "content/panel.js",
      "content/hotkeys.js",
      "content/index.js"
    ],
    "run_at": "document_idle"
  }
]
```

## Module specs

### `content/store.js`

Declares two top-level things:

**`formatTime(seconds)`** — utility. Takes a number of seconds (float), returns a display string. `<3600` → `M:SS` (e.g. `1:23`). `>=3600` → `H:MM:SS` (e.g. `1:05:09`). Floor seconds, pad with leading zeros. Clamp negative to 0. Used by Panel and Hotkeys.

**`const Store = { ... }`** — in-memory mark store. State and methods:

- `marks: []` — array of `{ start: number, end: number, description: string }`. Kept sorted by start ascending.
- `pendingStart: number | null` — pending start timestamp, or null if none.
- `setPendingStart(time)` — sets pending. Clamps to 0 (can't go negative).
- `hasPendingStart()` — boolean. (Optional convenience; callers can also check `Store.pendingStart !== null` directly.)
- `clearPendingStart()` — sets to null.
- `finalizeMark(start, end, description)` — pushes `{ start: max(0, start), end: max(start, end), description: description ?? '' }` to `marks`, re-sorts by start ascending, returns the new mark. **Takes `start` as an explicit argument** rather than reading from `Store.pendingStart`. Reason: avoids a real bug where double-`]` (two end-marks without an intervening start) silently loses the second mark because `pendingStart` is hidden shared state across two in-flight description inputs. Callers (specifically `markEnd`) are responsible for capturing `pendingStart` upfront and passing it through.
- `list()` — returns a copy of `marks` (defensive — callers shouldn't mutate the internal array).

The "end is at least start" clamp prevents edge-case inversions (user manages to hit `]` with a stale `currentTime` somehow — rare but cheap to guard against).

Note that `finalizeMark` no longer clears `pendingStart` — that's the caller's job (`markEnd` clears it before opening the description input, see hotkeys.js).

### `content/panel.js`

Declares `const Panel = { ... }`. Owns all DOM under the shadow root. Internal state: `host`, `shadowRoot`, `marksListEl`, `emptyStateEl`, `descriptionInputEl`, `toastEl`.

**`mount()`** — replaces PR 1's mount logic. Returns `true` on successful mount, `false` if the double-injection guard fires (host already exists in DOM). The boolean lets `index.js` gate `Panel.render()` and `Hotkeys.init()` — see `index.js` section.

On successful mount: creates the host div, attaches open-mode shadow root, builds the full UI structure inside the shadow root:

- Single `<style>` element with all panel + input + toast CSS.
- Panel container (top-right, the box from PR 1, ~280px wide).
  - Header: `Clip Marker` when 0 marks; `Clip Marker · 1 mark` when 1; `Clip Marker · N marks` when N>1. Pluralization matters — "1 marks" reads sloppy.
  - Marks list (`<ul>` or `<div>`, scrollable if it grows).
  - Empty state element shown when no marks: `No marks yet. Hit [ to mark a start, ] to mark an end.`
- Description input container (bottom-center, hidden by default). Contains:
  - Range label: `1:23 – 1:47` (the captured range).
  - Text `<input>` (the actual focus target).
  - Hint text: `Enter to save · Escape to skip`.
- Toast element (**top-center of viewport, fixed position**, hidden by default). Top-center avoids visual conflict with the description input (which lives at the bottom of the viewport) and stays clear of YouTube's player controls.

Note on spec rendering vs UI rendering: backticks and code formatting in this spec are markdown for the spec document itself. The actual UI text uses plain characters — the empty state literally reads `No marks yet. Hit [ to mark a start, ] to mark an end.` with plain `[` and `]`, not `<code>[</code>` styling. Same for the header (`Clip Marker · 3 marks`, plain text, not code-styled).

**`render()`** — re-renders the marks list from `Store.list()`. Show/hide the empty state. Update the mark-count header. Each mark row: `<div>` with `formatTime(start) – formatTime(end)  description`. Read-only in PR 2 (no click handlers, no edit/delete affordances).

**`showToast(text)`** — sets toast text, shows it (e.g. add a `visible` class), schedules removal after ~1500ms via `setTimeout`. **If a toast is already showing, explicitly `clearTimeout` the prior timer ID before scheduling the new one**, otherwise the old timer can fire mid-display and prematurely hide the new toast. Pattern: `this.toastTimerId = setTimeout(...)`; on each call, `clearTimeout(this.toastTimerId)` first, then assign anew.

**`showDescriptionInput(start, end, onSubmit)`** — shows the description input.

**On entry, check for an in-flight prior input.** If `this.currentOnSubmit` is already set, save the prior mark with empty description before overwriting:

```js
showDescriptionInput(start, end, onSubmit) {
  // Reachable via [ ] [ ] sequence: user marks a range, clicks out of the input
  // (input no longer focused, so hotkey guard doesn't block), marks a new range
  // before dismissing the first input. Save the prior mark before taking over.
  if (this.currentOnSubmit) {
    const priorSubmit = this.currentOnSubmit;
    this.currentOnSubmit = null;
    priorSubmit('');
  }
  this.currentOnSubmit = onSubmit;
  // ... set range label to `${formatTime(start)} – ${formatTime(end)}`
  // ... clear input value, focus input, show the UI
}
```

This restores cleanly what would otherwise be silent data loss: without the check, the second `]` overwrites `currentOnSubmit` and the first mark's closure has no path to ever fire.

**Critical: how the keydown listener is attached.** Do NOT attach a fresh `addEventListener('keydown', ...)` on each `showDescriptionInput` call — that accumulates one listener per invocation, and on a future keystroke ALL of them fire in order, saving every prior mark again with each new Enter press.

Correct pattern: attach ONE persistent keydown listener inside `mount()`, on the description `<input>` element. The listener reads `this.currentOnSubmit` at fire time:

```js
// in mount():
this.descriptionInputEl.addEventListener('keydown', (e) => {
  if (!this.currentOnSubmit) return;  // input not active
  if (e.key === 'Enter') {
    const submit = this.currentOnSubmit;
    this.hideDescriptionInput();  // clears currentOnSubmit
    submit(this.descriptionInputEl.value);
  } else if (e.key === 'Escape') {
    const submit = this.currentOnSubmit;
    this.hideDescriptionInput();  // clears currentOnSubmit
    submit('');
  }
});
```

Capture `submit` in a local *before* `hideDescriptionInput()` runs, since hideDescriptionInput clears `this.currentOnSubmit`. The local reference survives. This pattern guards against `submit` firing twice if a rapid second keystroke arrives mid-handler — the second keystroke reads `currentOnSubmit === null` and early-returns at the top.

`hideDescriptionInput()` clears `this.currentOnSubmit` and hides the UI element.

Use `'Escape'` exactly (modern standard). `'Esc'` is non-standard / legacy and will silently never match — easy bug to ship.

**Click-outside does NOT dismiss in PR 2.** Input stays open until Enter or Escape. Click-outside-dismisses-with-save is PR 4 polish.

`onSubmit` always fires (Enter or Escape) — the mark always gets saved per PRD. The caller's callback is responsible for storing the mark and re-rendering. The caller is also responsible for `.trim()`-ing the description before storing (handled in `markEnd`).

**On the `]` `]` vs `[` `]` `[` `]` distinction.** A second `]` *without an intervening `[`* finds `pendingStart === null` (cleared by the first `markEnd`) and `markEnd` no-ops at the top — `showDescriptionInput` is not called again. But a `[` `]` `[` `]` sequence with focus drift off the input *can* trigger a second `showDescriptionInput` call — the new `[` re-sets `pendingStart`, the new `]` clears it and opens a fresh input. The close-on-overwrite logic at the top of `showDescriptionInput` handles this case, saving the prior mark with empty description so nothing is silently dropped.

### `content/hotkeys.js`

Declares one top-level constant and `const Hotkeys = { ... }`. Wires keyboard input to commands.

**Constants at top of file:**

```js
const BACKDATE_SECONDS = 5;
```

Captures the assumption that pressing `[` should mark the start 5 seconds before `currentTime` (to absorb reaction lag). Parameterized as a constant so tuning is a one-line change, not a search-and-replace. Not a user-facing setting in V1 — see PRD non-goals for the rationale (add user controls in response to evidence, not anticipation).

**`init()`** — attaches a single document-level `keydown` listener. Capture phase? Use bubbling (the default) — capture is only needed if we want to intercept before YouTube's handlers, which we don't.

**`handle(e)`** — main listener:
1. Run the guard stack: `e.repeat`, `e.isComposing`, modifier keys, then `isTypingTarget(e.composedPath()[0])`. Return early on any. Pass the *event* to the typing-target check, not `document.activeElement` — see Key Concepts on why composedPath is required for shadow-DOM-rooted inputs.
2. Switch on `e.key`. `[` → `markStart()`. `]` → `markEnd()`. Default: no-op.

**`isTypingTarget(el)`** — returns true if `el` is `INPUT`, `TEXTAREA`, or has `isContentEditable === true`. Returns false if `el` is null or none of the above.

**`markStart()`** — gets `currentTime` from the video element. If video missing, no-op. Compute `Math.max(0, currentTime - BACKDATE_SECONDS)` (clamp to 0 so we never store negative timestamps for marks near the start of a video). Set as pending start. Show toast `Start at ${formatTime(backdated)}`.

**`markEnd()`** — sequence matters; bugs hide between the steps.

1. `const start = Store.pendingStart;` — capture pending start as a local variable.
2. `if (start === null) return;` — no pending start, nothing to do.
3. `const end = this.getCurrentTime();` — read current playback time.
4. `if (end === null) return;` — video element missing; do nothing (note: `pendingStart` is NOT cleared in this case, so the user can re-attempt with another `]`).
5. `Store.clearPendingStart();` — clear pending state NOW, before opening the input. This prevents the double-`]` bug: a second `]` while the description input is still open would otherwise re-read `pendingStart` and create a phantom second mark sharing the original start. Clearing here makes the second `]` correctly a no-op.
6. `Panel.showDescriptionInput(start, end, (description) => { Store.finalizeMark(start, end, description.trim()); Panel.render(); })` — note `start` and `end` are captured in the closure as locals, not read from `Store`. Each invocation of `markEnd` produces its own closure with its own captured values; overlapping description inputs (if user dismisses one and starts a new one) cannot interfere with each other's data.

The `.trim()` ensures whitespace-only descriptions save as empty string, not literal whitespace.

**`getCurrentTime()`** — `const v = document.querySelector('video'); return v ? v.currentTime : null;`. Called fresh on each hotkey — don't cache the element across calls (YouTube may swap it during SPA nav, even though PR 2 doesn't handle SPA explicitly).

### `content/index.js`

Tiny orchestrator. One IIFE that gates the cascade on `Panel.mount()`'s return value:

```js
(() => {
  if (!Panel.mount()) return;
  Panel.render();
  Hotkeys.init();
})();
```

`Panel.mount()` must return `true` on successful first mount, `false` if it short-circuited (host already exists). The gating prevents two real downstream problems: `Panel.render()` would crash trying to read panel refs that were never assigned (e.g. `this.marksListEl.innerHTML = ...` with `marksListEl === undefined`), and `Hotkeys.init()` called twice would attach two `keydown` listeners on `document`, firing every command twice with no easy cleanup until the page reloads.

PR 2 doesn't realistically trigger this (content scripts only run once per page load), but the gate is forward-looking for PR 3, which may need re-mount semantics on SPA navigation. Cheap to add now; saves a real footgun later.

## UI specifications

### Panel (already exists from PR 1, now extended)

- Top-right position, ~280px wide. Existing.
- Add: header. See panel.js mount section for exact pluralization rules (`Clip Marker` / `Clip Marker · 1 mark` / `Clip Marker · N marks`).
- Add: marks list area. Each row roughly:
  ```
  1:23 – 1:47   Customer pain: data silos
  ```
  - Timestamps in a slightly de-emphasized color or smaller size.
  - Description text wraps if long.
  - Subtle row separator (1px line, low contrast).
- Add: empty state. Centered, slightly de-emphasized.

### Description input

- Position: `position: fixed`, anchored bottom-center of viewport. `bottom: 120px` (clears YouTube's player controls). `left: 50%; transform: translateX(-50%)`.
- Width: ~480px. Padding generous. Background, border-radius, drop shadow.
- Layout (top to bottom): range label, text input, hint text.
- Text input: full width of container minus padding, decent font size (15-16px), no native browser styling.
- Hidden by default (`display: none` or a `hidden` class).
- z-index above the panel, above YouTube's UI.

### Toast

- Position: `position: fixed`, anchored **top-center**. Pinned: top-center avoids visual conflict with the bottom-center description input and stays clear of YouTube's player controls.
- Width: auto, padding generous.
- Background distinct from panel (e.g. darker or accent color).
- Fade in/out via CSS transition. Auto-dismiss after 1500ms.
- z-index above everything else in our shadow root.

All three (panel, input, toast) live inside the same shadow root attached to the same host element. The host is positioned `position: fixed` at the top-left with `width: 0; height: 0`; its children all use their own `position: fixed` to anchor wherever they want. (This keeps the host element from interfering with page layout while letting children position freely.)

## Pre-coding verification (BZ runs this, NOT Claude Code)

Claude Code can't open YouTube in a real browser to verify keyboard bindings — this is a BZ-only check before kicking off CC.

**Does YouTube bind `[` or `]` on watch pages?** Open a YouTube watch page with NO extensions installed, press `[` and `]` while the video has focus. If nothing happens visibly (no chapter skip, no playback rate change, no UI response), we're clear — our handlers run in bubble phase, YouTube does nothing, no conflict. If YouTube *does* respond, we'll need to revisit the "never call `preventDefault`" rule for these specific keys when no input is focused.

Prior: ~80% confident YouTube doesn't bind them. Worth 30 seconds to confirm before assuming.

If Claude Code starts before BZ verifies: CC may proceed assuming no binding, but MUST flag this assumption in its self-audit output for BZ to verify post-implementation.

## Self-audit (run before committing)

Before pushing, verify each:

1. Each of the four content files contains exactly one top-level `const ModuleName` (or `function` for `formatTime`). No accidental top-level variables that leak.
2. Hotkey guard stack is in the right order: cheap checks first (repeat, isComposing, modifiers), then `isTypingTarget(e.composedPath()[0])` last.
3. Guard uses `e.composedPath()[0]`, NOT `document.activeElement`. Test specifically: typing `[` into the description input must not fire `markStart()`. (`document.activeElement` would return the shadow host in this case and silently fail.)
4. `markStart` and `markEnd` both call `getCurrentTime()` fresh; no cached video element.
5. `markStart` clamps backdated time to 0: `Math.max(0, currentTime - BACKDATE_SECONDS)`. Test: video at 2s, hit `[`, pending start is 0 (not -3).
6. `formatTime(0)` returns `"0:00"`. `formatTime(59.9)` returns `"0:59"` (floor). `formatTime(3661.5)` returns `"1:01:01"`.
7. `Store.list()` returns a new array each call (defensive copy), not the internal reference.
8. `Panel.mount()` returns a boolean. `index.js` gates `render()` and `init()` on the return value (`if (!Panel.mount()) return;`).
9. Description input has exactly ONE persistent `keydown` listener, attached during `mount()`. `showDescriptionInput` sets `this.currentOnSubmit = onSubmit` — it does NOT call `addEventListener` on every invocation. Test: open description input ten times in a row (with valid `[`/`]` flows); after the tenth Enter, only ONE mark gets added by that Enter, not ten. Listener-accumulation would cause N marks per keystroke after N inputs.
10. Description input handler uses `e.key === 'Enter'` and `e.key === 'Escape'` (NOT `'Esc'`). `'Esc'` is non-standard and silently never matches.
11. Description input does NOT call `preventDefault` on `[` or `]` keys — typing those characters into the description must work.
12. `Store.finalizeMark` takes `(start, end, description)` and does NOT read `Store.pendingStart` internally. The start value flows in from the caller.
13. `markEnd` clears `Store.pendingStart` BEFORE calling `Panel.showDescriptionInput`. Sequence: capture start as local, validate, get end, validate, clear pendingStart, open input. (Critical for the double-`]` bug fix.)
14. `markEnd`'s closure captures `start` and `end` as locals, not as `Store.pendingStart` reads. Test: press `[`, press `]`, click out of input, press `]` again — the second `]` is a no-op (pendingStart was cleared); user must press `[` again first.
15. Description trim on save: `description.trim()` before storing. Empty/whitespace-only saves as empty string.
16. Mark count header pluralizes correctly: `Clip Marker` (0), `Clip Marker · 1 mark` (1), `Clip Marker · 3 marks` (3+).
17. Toast `showToast` uses `clearTimeout(this.toastTimerId)` before scheduling a new `setTimeout`. Test: trigger two toasts in quick succession (e.g. press `[` twice fast); the second toast should display for the full ~1500ms, not get cut short by the first toast's timer firing.
18. No `console.log` left in production code (except actually-needed warnings).
19. Manifest lists files in dependency order: store, panel, hotkeys, index.
20. `markStart` uses the `BACKDATE_SECONDS` constant, not a hardcoded `5`. The constant lives at the top of `hotkeys.js`, not inlined.
21. YouTube `[`/`]` binding verified per pre-coding section. If unverified at CC time: flag explicitly in self-audit output and STOP — ask BZ before committing. Do not proceed and commit assuming "probably fine."
22. `showDescriptionInput` checks `this.currentOnSubmit` on entry; if set, captures it, nulls it, fires it with `''` BEFORE assigning the new `onSubmit`. Test: press `[`, `]`, click outside the input (focus drifts away), press `[`, `]`. Two marks should appear in the panel: the first with empty description (auto-saved when the second invocation took over), the second from the new flow.

## Verification (for BZ to run after Claude Code finishes)

1. `git diff` — read every line of every changed file. This PR has real surface area.
2. Load unpacked in Chrome. Visit a YouTube watch page.
3. Done criteria walkthrough — every one, one at a time:
   - Press `[`. Toast should appear briefly with timestamp.
   - Press `]`. Description input should appear at the bottom. Video should keep playing.
   - Type something, press Enter. Input should dismiss. Mark should appear in the panel.
   - Press `[` again. Press `]`. Press Escape. Mark should appear in panel with empty description.
   - Type spaces only into description and Enter. Mark saved with empty description (trim applied).
   - **Type `[` and `]` directly into our description input.** Both characters should appear in the input. NO new mark should be created from these keystrokes. (Shadow-DOM-guard test — easy to silently break.)
   - **Double-`]` sequence:** press `[`, press `]` (input opens), click somewhere outside the input, press `]` again. Second `]` should be a no-op (no second input opens, no phantom mark). User must press `[` again to start a new mark. (Hidden-state-coupling test — protects the double-mark fix.)
   - **Re-mark sequence:** press `[`, press `]` (input opens), click outside the input, press `[`, press `]`. Two marks should appear in the panel: first with empty description (auto-saved when overwritten), second with whatever description you type. (Tests `showDescriptionInput` re-entry — protects against silent loss of in-flight marks.)
   - Type something in YouTube's search bar — `[` should NOT fire (search receives the character).
   - Hold `[` for 1 second — should fire exactly once, not 30 times.
   - Press `Cmd+[` — browser should navigate back, no mark should be created.
   - Press `]` without `[` first — nothing should happen.
4. Reload page. All marks should be gone (expected — no persistence yet).
5. DevTools → Elements panel. Verify all UI is inside the shadow root, not in the main document.
6. DevTools → Console. No errors during normal use.

If anything fails, capture the failure (specific repro steps, screenshot if visual) before iterating with Claude Code.

## Commit message

```
PR 2: capture flow with hotkeys, description input, in-memory mark store

- Split content/ into store/panel/hotkeys/index modules
- Hotkey listener with input-focus, modifier, repeat, composition guards
- `[` captures start with -5s backdate + toast confirmation
- `]` captures end, opens description input, saves on Enter/Escape
- Panel renders marks list with M:SS – M:SS format
- In-memory only; persistence deferred to PR 3
```
