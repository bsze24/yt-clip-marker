# Tech debt

Items deliberately deferred during development. Each has a stable index (`TD-N`) so PRs and commits can reference them (e.g. "fixes TD-3"). Add new items at the bottom; don't renumber.

## Index

- **TD-1** — Double-injection guard may block legitimate re-mounts
- **TD-2** — Match pattern doesn't cover `youtube.com` without `www.`

---

## TD-1: Double-injection guard may block legitimate re-mounts

**Where:** `content.js`, top of file — `if (document.getElementById(HOST_ID)) return;`

**Issue:** The guard prevents stacked panels if the content script runs twice against the same DOM (extension reload, accidental re-injection). For PR 1 this is correct behavior. But the guard *also* silently no-ops legitimate re-mounts — e.g., if PR 3's SPA navigation logic ever needs to tear down and rebuild the panel, calling the mount function again will short-circuit at the guard with no error and no rebuild.

**Failure mode:** "I'm sure I'm re-mounting, but nothing changes." Silent. Hard to diagnose.

**Fix when needed:** Change the guard to remove the existing host before mounting:
```js
const existing = document.getElementById(HOST_ID);
if (existing) existing.remove();
// proceed with mount
```
Or expose an explicit `unmount()` function that callers invoke before re-mounting.

**Trigger to revisit:** First PR that adds dynamic re-mount logic. Likely PR 3 (SPA navigation), though may not be needed if PR 3 only updates panel contents rather than re-mounting the panel itself.

---

## TD-2: Match pattern doesn't cover `youtube.com` without `www.`

**Where:** `manifest.json` — `"matches": ["https://www.youtube.com/watch*"]`

**Issue:** Chrome match patterns require exact host matching unless wildcards are used. The current pattern matches `https://www.youtube.com/watch?v=...` but not `https://youtube.com/watch?v=...`. Users who paste or type the bare-domain form land on a YouTube page without the extension loaded.

**User impact:** Almost nobody types `youtube.com/watch` without `www`; YouTube auto-redirects most entry paths through `www.`. Real-world hit rate likely near zero.

**Fix when needed:** Add a second match pattern, or use a wildcard:
```json
"matches": [
  "https://www.youtube.com/watch*",
  "https://youtube.com/watch*"
]
```
Or:
```json
"matches": ["https://*.youtube.com/watch*"]
```
The wildcard form also covers `m.youtube.com` (mobile web), which is a separate decision — V1 is desktop-only per PRD, so probably don't want the broad wildcard.

**Trigger to revisit:** First time the extension visibly fails for a user / for you on a non-www URL. Or before public release.
