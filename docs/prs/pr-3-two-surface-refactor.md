# PR 3 — Two-surface refactor

Third PR, and a product-model pivot. The original plans for PR 3 (storage + SPA navigation) and PR 4 (refinement hotkeys, click-to-preview, exports in the panel) built toward an annotation IDE *on the YouTube watch page*. Building the eval dashboard falsified that model — the dashboard became the annotation IDE (`docs/two-surface-handoff.md`). **The original PR 3 / PR 4 are superseded and will not be implemented.** This PR locks in the replacement.

## What this PR does

**Docs first (so no future session rebuilds the on-YouTube IDE):**

- Rewrite `docs/youtube-clip-marker-prd.md` around two surfaces / one clip, with a decisions log for the handoff's open questions.
- Add `docs/clip-schema.md` — the shared clip contract; the extension and studio share the clip, never code.
- Point `AGENTS.md` and `README.md` at the studio as the workspace and the extension as the frozen viewing/capture client.

**Tree matches the story:**

- `content/` + `manifest.json` → `apps/extension/` (load unpacked from `apps/extension` now).
- `eval/` → `apps/studio/` (server, page, attach scripts, `runs/`, `labels.jsonl`).

**Extension frozen at thin client (this supersedes old PR 3/4):**

- Keeps: load on watch pages, `[` / `]` coarse capture, Shadow-DOM panel, in-memory marks. No code changes.
- Never builds: `chrome.storage` canonical store, refinement hotkeys, panel exports, taxonomy/transcript UI, SPA remount work for an on-page editor.
- Future seam (unscheduled): "send to studio" handoff of coarse marks.

**Studio promoted from eval harness to workspace:**

- UI renamed to Clip Studio.
- In-app ingest: paste a URL → server fetches captions + description via `yt-dlp`, flags silence gaps, parses extracted timestamps, writes a run with an empty `markers` array, opens it. (`apps/studio/ingest.py`, `POST /api/ingest`.)
- Eval chrome (check/note feedback, rationales, check stats) behind an eval-mode toggle, default off.
- `kind` (TAKE/CONCEPT) never required on new writes; taxonomy is work / lane / tags.
- Store unchanged: `runs/` + append-only `labels.jsonl`.

**Skill (`~/.claude/skills/yt-clipper/`):** paths updated for the rename. It remains the suggester (rules + prompt); its fetch/attach engineering now exists in-app. Full "suggest markers as a studio action" is future work.

## Done criteria

1. Extension loads unpacked from `apps/extension`; no manifest warnings; capture still works on a watch page.
2. `python3 apps/studio/server.py` boots; the existing run and labels load unchanged.
3. Header shows Clip Studio + eval-mode toggle; check/note inputs and rationales appear only with it on.
4. URL ingest produces a run with cues, `gapBefore` flags, extracted markers, empty `markers[]` — and opens it.
5. New label events carry no required `kind`.
6. A fresh agent reading AGENTS.md + PRD lands on the two-surface model.

## Out of scope

- End (range) collection in the studio grid.
- Export buttons (description timestamps, media-scraper JSON) — schema freezes when those land.
- "Suggest markers" as a studio action; extension→studio handoff.
