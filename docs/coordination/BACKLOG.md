# Backlog

Deferred work and the build roadmap. Git is the source of truth for code; this is the
source of truth for what's next and what's parked. (This is a roadmap, not a PRD — the
product why lives in `docs/youtube-clip-marker-prd.md`.)

Tech-debt ids (`TD-N`) stay stable so commits can say "fixes TD-3". Add new items at the
bottom of the Tech debt section; don't renumber.

## Build order (studio-first)

Shipped on GitHub (not yet merged to `main`):

- **PR 1** — extension skeleton (Shadow DOM panel on watch pages). Merged.
- **PR 2** — `[` / `]` coarse capture, in-memory. Merged.
- **PR 3** (open, `a051667`) — two-surface refactor: studio as workspace, extension
  frozen, in-app ingest, eval mode, clip contract. Includes copy-timestamps
  (`apps/studio/ui/export.js`, [[D-022]]).
- **PR 4** (open, `bde4ce7`) — video 1 run + `labels.jsonl`.
- **PR 5** (open, `949cb7b`) — session log + folded ledger.

In flight, not product: **PR 6** coordination write-head — see `CURRENT.md`.

After PRs 3–5 merge, in priority order (PRD "Next"):

1. **End collection.** Ranges (`end`) settable from the grid — required before
   reel-oriented export is useful ([[D-012]]).
2. **JSON export.** Copy as JSON (the media-scraper seam). Freeze the schema when this
   lands ([[D-015]]). Description-timestamp copy already shipped in PR 3
   (`apps/studio/ui/export.js`, [[D-022]]).
3. **Suggest-markers as a studio action.** Currently a Claude-skill invoke ([[D-011]]).
   Ingest already exists; this is the remaining skill-engineering move.

Unscheduled, unblocked:

- **Extension → studio handoff** of coarse `[` / `]` marks (clipboard JSON or localhost
  POST; decide when it hurts). Until then the extension is a capture scratchpad.

## Next studio features (detail)

- **End collection ([[D-012]]).** Markers and adds are start-only today. The grid should
  set `end` without turning YouTube back into an IDE — likely a keyboard nudge + an
  explicit range on the selected row. Don't block JSON export on perfect ranges if
  media-scraper can take start-only, but reels want ends.
- **JSON export ([[D-015]]).** Array of clip objects as in `docs/clip-schema.md` plus
  `videoUrl` / `videoTitle`. Decide the fold (which of marker / add / gold survive) against
  the open modeling item below, not by silently changing copy-timestamps.
- **Suggest-markers in-app ([[D-011]]).** Studio action that writes `markers[]` onto an
  ingested run. The skill file remains the prompt/rules source. Don't pull LLM calls into
  the stdlib server until the shape is obvious — a local invoke that the page polls is
  enough.

## Deferred design detail

- **Eval chrome removal.** [[D-010]] keeps check/note/rationale behind a toggle until
  ~5 labeled videos. Video 1 is labeled; don't remove yet.
- **`kind` on old events.** [[D-009]] — readable forever; no migration pass unless a
  consumer chokes.
- **attach_cues.py / attach_gold.py.** Still useful for skill-written runs. In-app ingest
  covers the human-only door. Don't delete the CLIs until suggest-markers is in-app and
  the skill writes through the same ingest path.
- **Formal YouTube chapter-rule validation.** If marks happen to satisfy the rules,
  chapter use works as a side effect. Not a feature.

## Tech debt (stable `TD-N`)

Moved from `docs/tech-debt.md` (that file is now a pointer).

### TD-1 — Double-injection guard may block legitimate re-mounts

**Where:** `apps/extension/content/panel.js`, top of `mount()` —
`if (document.getElementById(this.HOST_ID)) return false;`

**Issue:** Prevents stacked panels on double injection (correct for PR 1). Also silently
no-ops a legitimate tear-down/rebuild.

**Trigger:** First PR that adds dynamic re-mount logic. The two-surface freeze ([[D-006]])
took SPA remount off the table; revisit only if the extension grows again.

### TD-2 — Match pattern doesn't cover `youtube.com` without `www.`

**Where:** `apps/extension/manifest.json` —
`"matches": ["https://www.youtube.com/watch*"]`

**Issue:** Bare `https://youtube.com/watch?v=…` does not load the extension. YouTube
auto-redirects most entry paths through `www.`; real-world hit rate likely near zero.

**Trigger:** First time it fails for a user, or before public release. Don't use
`https://*.youtube.com/watch*` without a decision — that also matches `m.youtube.com`,
and V1 is desktop-only.

## Parking lot

- Voice input; YouTube Data API write-back; sync; mobile / in-car; Shorts / playlists /
  embedded players; multi-user.
- Live-video annotation (in-flight calls/streams) — a different product.
- A framework / database / deploy story for the studio.
- PKM ingest of the clip JSON (keep the export generic; don't over-fit to YouTube).

## Open modeling decisions

Each item is bound to the step that forces it. When the planner specs that step in
`CURRENT.md`, resolving its bound decisions is part of that task, and the resolution
becomes a dated entry in `DECISIONS.md`.

- **Ballpark-`g` in copy-timestamps — Decide at: JSON-export / copy-timestamps freeze.**
  Today `g` still exports ([[D-022]]): 20:46 (`g`, Double-note…) and 21:18 (added, same
  lick, better place) both copy. Eval wants the few-shot positive kept; publishable
  timestamps may not want the early hunt. Don't collapse this into "exclude all `g`" —
  taxonomy-without-`g` is an ordinary keep. Options: (a) keep current, (b) exclude `g`
  when a nearby add exists, (c) eval-only `g` never copies. Bound to the export freeze
  so copy-timestamps and JSON don't diverge.

- **Extension→studio handoff transport — Decide at: when capture-scratchpad friction hurts.**
  Clipboard JSON vs localhost POST vs something else. The studio store stays canonical
  ([[D-007]]); the extension must not grow a second store to make the handoff easier.

- **media-scraper JSON freeze — Decide at: JSON export button ([[D-015]]).** Draft lives
  in `docs/clip-schema.md`. Don't freeze from a conversation.

- **Suggest-markers runtime — Decide at: in-app suggest ([[D-011]]).** Skill-invoke in
  chat vs a studio button that shells out vs something hosted. Constraint: stay stdlib
  until it hurts ([[D-005]]); don't add a model provider to `server.py` as a side effect.
