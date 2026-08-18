# Two-surface clipper — handoff

Context for planning and execution in Claude. This is a **suggested path**, not a locked plan. The product decision is the load-bearing part; repo layout, rename, and sequencing are open to a better plan.

**Date:** 2026-08-14
**Repo:** `yt-clip-marker`
**Related:** `docs/youtube-clip-marker-prd.md` (still the old one-surface PRD), `eval/` (dashboard), `content/` (Chrome extension), `~/.claude/skills/yt-clipper/SKILL.md` (candidate-marker skill)

---

## Chronology — how we got here

1. **Clipper as a YouTube extension.** V1 PRD: mark `{start, end, description}` ranges *on the watch page* (`[` / `]`), refine in a Shadow DOM panel, persist in `chrome.storage.local`, export timestamps + JSON. Built as a learning project (PR 1 skeleton, PR 2 capture). Refinement, persistence, SPA nav, and export were still ahead (PR 3 / 4).

2. **media-scraper is downstream, not this repo.** Long-term, clipper’s JSON ranges feed media-scraper’s **reels** and **auto-suggest**. Separate project. Shared *export contract*, not shared code. (Earlier chat noise about “same tree” was a false option — do not merge repos.)

3. **Skill as the linear-watch replacement.** `yt-clipper` skill fetches the caption track (`yt-dlp`), flags silence gaps, and proposes a copious TAKE/CONCEPT candidate list. Approximate neighborhoods only; nailing boundaries was supposed to be the extension’s job.

4. **Eval dashboard to judge the skill.** Local `eval/server.py` + `eval/index.html`: time-aligned grid of captions, skill markers, and YouTube-description timestamps (then called `gold`; now **extracted**). Judgments append to `eval/labels.jsonl`. First run: `eval/runs/YYW4Q1Nivg8-20260814-1248.json`.

5. **The dashboard ate the product.** In practice we built the annotation IDE here, not on youtube.com: `j`/`k` row nav, Enter to add/edit, work / lane / tags (replacing exclusive TAKE/CONCEPT), human-added clips, layout toggle, YouTube embed. Duplicate timestamps (`j` stuck on 3:19) forced selection by **row identity**, not start time alone.

6. **Product breakthrough (this conversation).** Viewing surface (YouTube) and annotating surface (this dashboard) are **two clients of one clipper**, not two features of the YouTube panel. The dashboard may be the better home for what the PRD imagined as “the extension.” Extension shrinks toward ingest / optional coarse capture / handoff. Studio (today’s `eval/`) is the workspace.

---

## Findings

- **YouTube is a hostile editor.** It owns `j`/`k`/`space`, CSS fights injected UI, SPA nav remounts content scripts. A dense taxonomy + transcript grid does not belong there. An embed still uses YouTube as *player*, not as *IDE*.
- **Share the clip, not the screen.** Contract is `{ videoId, start, end, description, work, lane, tags }`. Do not share panel/hotkey/grid code between extension and studio.
- **The skill bundled three jobs.** (1) Fetch transcript — engineering, belongs in the app. (2) Propose candidates — still an LLM pass; keep `SKILL.md` as rules/prompt. (3) Write eval JSON + extracted timestamps (then called gold) + `check`/`note` — harness, not the product loop.
- **You still want a first-pass scrape.** An empty 90-minute grid is the old linear watch. Ingest can happen without the skill; suggest-markers should not stay a chat-only runbook (write JSON path → attach cues → attach extracted markers → boot server).
- **Eval chrome is leftover product-shape.** Extracted markers (then called gold) as a skill-eval target, `kind: TAKE|CONCEPT`, rationales as the main loop — useful while scoring the suggester; they should not define the studio UX.
- **Canonical store has not been chosen.** Extension PRD says `chrome.storage.local`. Studio already uses `labels.jsonl` + `runs/`. If studio is the workspace, JSONL (or whatever replaces it) is the source of truth; the extension should not become a second store.

---

## Outstanding questions

Worth deciding in planning, not assumed:

- **How thin is the extension in V1 of the split?** Handoff-only (`videoId` → studio) vs keep `[` `]` coarse capture on the watch page?
- **When does “Suggest markers” become a studio action** vs staying a Claude skill invoke? Ingest-in-app can land first either way.
- **Eval mode:** hide check/note/rationale now, or keep visible until ~5 labeled videos exist?
- **`end` on clips:** skill markers are often start-only; PRD wanted ranges. Does studio collect ends now or later?
- **Extracted-marker column (then called gold):** keep as published YT description timestamps (useful) — any other role?
- **Rename `eval/` → `studio/` (or `apps/studio`)** now vs after a layout plan? Naming in AGENTS.md matters so the next agent doesn’t treat the dashboard as disposable eval.
- **media-scraper JSON:** freeze a schema soon, or wait until studio export exists? Don’t block the split on it.
- **Uncommitted eval work** is the real studio. Don’t plan as if `eval/` weren’t the product.

---

## Current state

**Extension (`content/`, `manifest.json`)**
Loads on `youtube.com/watch`. Shadow DOM panel + `[` `]` capture (PR 2). In-memory marks; no persistence, no SPA remount, no refinement, no export. PR 3/4 as originally written (storage + IDE-on-YouTube) are **misaligned** with the two-surface model.

**Studio (still named `eval/`)**
Working local app: `python3 eval/server.py` → http://127.0.0.1:8765. Keyboard grid, taxonomy, additions, YouTube IFrame, row-key selection fix. Data: `eval/runs/*.json`, `eval/labels.jsonl`. README still says “dev-only annotation set for the clipper skill. Not part of the Chrome extension runtime.”

**Skill**
Still the ingest path: fetch transcript, write a run file under `eval/runs/`, `attach_cues.py` / `attach_extracted.py`, then open the dashboard.

**Docs**
PRD + `AGENTS.md` still describe a Chrome-only product: no server, `chrome.storage`, annotation on the watch page. They will fight any agent that doesn’t get this handoff.

**Out of scope for this repo**
media-scraper. Consume clips later via export.

---

## Suggested path

For Claude to **plan**, then execute in whatever order planning prefers. Treat as a direction, not a checklist to grind in one pass.

**A. Lock the story in docs first**
So the next session doesn’t rebuild the YouTube-panel IDE. Rewrite the PRD around two surfaces / one clip. Point `AGENTS.md` and the README at studio as the workspace and the extension as the viewing/capture client. Note the media-scraper tie as export-only. A short clip schema note is enough; don’t over-specify the store.

**B. Make the tree match the story**
Something like `apps/extension`, `apps/studio` (today’s `eval/`), and a small `schema/` — or a lighter rename. Planning should pick a layout that’s Fable-readable without a premature monorepo/npm extraction.

**C. Freeze the extension at “thin client”**
Keep load-on-watch and optional capture. Do not implement original PR 3/4 (canonical `chrome.storage`, refinement hotkeys, click-to-preview as editor, export from the panel). Supersede those PR specs or rewrite them as handoff-to-studio.

**D. Promote studio from eval harness to workspace**
Rename in the UI. Keep `labels.jsonl` / `runs/` as the first store. In-app ingest (URL → transcript/cues → run) so the skill runbook is no longer the only door. Fold attach-cues / attach-extracted / fetch-transcript into that ingest path when it pays off. Extracted-marker column can stay (then called gold); TAKE/CONCEPT as required `kind` can stop for new writes. Check/note/rationale → eval mode or later.

**E. Keep the skill as suggester, not as workflow**
Move fetch into the app. Keep rule IDs and “over-include” as the prompt. “Suggest markers” can remain a skill invoke until ingest exists; then it’s an obvious studio action. You should be able to open a video with an empty skill column and only human clips.

**Leave alone until planning says otherwise**
Keyboard/grid/taxonomy (that is the product). Append-only labels. YouTube embed. JSON export as a *future* studio button (media-scraper seam). Don’t Next/Vercel the store just to look like an app. Don’t put media-scraper in this tree.

---

## How to use this in Claude

1. Read this file + current PRD + `eval/README.md` + `AGENTS.md`.
2. Plan the split (questions above are real; don’t silently pick).
3. Execute in small steps; docs-first is the suggestion so later agents don’t revert the product model.
4. The dashboard in `eval/` is the annotating surface. The extension is not the place to grow taxonomy/transcript/export.
