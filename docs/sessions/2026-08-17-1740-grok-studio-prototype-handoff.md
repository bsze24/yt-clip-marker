---
date: 2026-08-17
time: "17:40"
revised: 2026-08-22 07:10 UTC
surface: grok
project: yt-clip-marker
track: studio-workspace
work: eval dashboard prototype, two-surface named, Fable brief
branch: docs/remove-coordination-md
commit: 10686ada9324ff819346271cf36286b42e31591f
task: docs/youtube-clip-marker-prd.md
---

# Session log — 2026-08-17 17:40 (grok) — studio-prototype-handoff

## Project context
- Pointer at HEAD (`10686ad`): two-surface PRD is already in the tree. Product land is on other branches (PR 3 `a051667`). This checkout is `docs/remove-coordination-md` — unrelated coordination-doc work; do not treat its working tree as this session's product diff.
- Canonical lock-and-use log (same `track:`): `docs/sessions/2026-08-16-1507-grok-studio-fable-lock.md`. That file is the resume head. This file is composer `4a29e5bc` — Friday prototype plus the Fable-live-server tail.
- Sister: Fable lock / Sunday use is `studio-fable-lock`, not this composer.

## Summary
One Friday sitting turned a first `/yt-clipper` run into the dashboard, then named two surfaces and handed Fable a suggested path. Ended Monday by checking overlap with 1507 and logging this composer so the live-server mix-up has a home.

## What changed
- Nothing on this checkout. Friday's dashboard, row-key fix, and `docs/two-surface-handoff.md` later landed as PR 3 on `codex/pr-3-two-surface-product`. Working-tree `AGENTS.md` + untracked `docs/coordination/` + the 1507 log are other sessions.
- This composer did restart studio on `127.0.0.1:8765` (kill leftover `eval/server.py`, then `python3 apps/studio/server.py`). Not a git change.

## Decisions
- Viewing (YouTube / extension) and annotating (studio) are two clients of one clipper. They share the clip, not the screen.
- media-scraper stays a separate repo. The tie is JSON export for reels and auto-suggest, not a shared tree.
- Skill fetch belongs in the app; candidate markers can stay a model pass. Chat-runbook ingest is not the door.
- A coding agent with the studio files does not have the annotating UI. Source + `curl` of `/` and `/api/*` is not a browser tab.

## Learning arc
- 1:20 and 2:37 looked like marks in the middle of playing. The ask was not "fix the skill" first — it was "I need captions, the gap line, and the runbook on one screen." That sniff is the eval dashboard.
- Forty minutes later, still calling it eval, you said it could replace large swaths of the real tool. The instinct showed up inside the disposable stand, not after a finished prototype.
- Named the split in your own words: YouTube is the viewing surface; this dashboard is the annotating surface; they still roll up to one yt-clipper. The extension-as-IDE was the wrong host.
- "Same tree as media-scraper" was a false option from the agent. The real tie came back as export-only. Skill vs in-app scrape stayed a planning question, not a merge.
- Read "the annotation UX is still on you" as "we didn't build the product." It meant Fable cannot sit in the grid and press `j`. Files are not the tab.
- Monday: 1507 already holds this Friday. Most of that file is Fable + Sunday use. This composer is not a second product history.

## Concepts touched
- [concept] eval-harness-becomes-the-product — solidifying — 13:30 in this sitting, 42 minutes after the harness ask
- [concept] hostile-host / two-surface — solidifying — named 16:40 in your words; handoff doc asked Fable to plan, not grind
- [concept] skill as suggester not workflow — emerging — asked 16:44; ingest-in-app vs keep `/yt-clipper` left for planning
- [concept] coding-agent vs operating the UI — emerging — named after the "UX is still on you" misread; curl ≠ `j`/`k`

## Coaching hooks
- **Files are not the tab.** Same shape as expecting a coding agent to "have" studio because `server.py` exists. Next "does Fable have the app?", split source / HTTP inspect / browser operate before restarting anything.
- **Don't write a second product log from this composer.** Resume `track: studio-workspace` at 1507. This file is the live-server tail and the overlap check.

## Next / open threads
- Resume product from `docs/sessions/2026-08-16-1507-grok-studio-fable-lock.md` (land splits, video 2 ingest, export-vs-eval).
- Live studio: from repo root, `python3 apps/studio/server.py` → http://127.0.0.1:8765. If 8765 is a zombie `eval/server.py`, kill it first.
- Fable (or any coding agent): `curl` `/`, `/api/runs`, `/api/run?id=…`. HTML edits refresh; `server.py` needs a restart. Operating the grid needs a browser agent.

## Open questions / blockers
- None blocking this composer. Product questions live in 1507 (`g` on copy-timestamps, clip `end`s, suggest-markers as a studio action).

## Chronology (the record)

> **Chronology timestamp key:** All times are UTC. An unmarked minute is anchored to a recovered source event; `≈` marks a source-supported window or rounded prose boundary; `reconstructed` marks preserved ordering where the original source clock is unreliable.
- **2026-08-14 04:09 UTC** — captions have start not end?
- **≈2026-08-14 04:17–04:30 UTC** — `yt-dlp` install — pip/`--user` vs Homebrew Python vs `brew install yt-dlp`.
- **2026-08-14 04:35 UTC** — first `/yt-clipper` on `YYW4Q1Nivg8`. Run `YYW4Q1Nivg8-20260814-1248`.
- **2026-08-14 04:42 UTC** — 1:20 and 2:37 look arbitrary mid-playing. "Sniffing like an eval surface."
- **2026-08-14 04:44 UTC** — where is the runbook?
- **2026-08-14 04:48 UTC** — spin up a quick eval dashboard; rationale near the rule; `check` = good marker; 5 videos in a few hours.
- **2026-08-14 04:51 UTC** — store feedback durably "in case we want this in the product" → `labels.jsonl`.
- **≈2026-08-14 05:03–05:05 UTC** — `>>> GAP` is the fetch script, not a caption. Put caption rows on the grid.
- **≈2026-08-14 05:09–05:11 UTC** — formatting; keep YouTube native ←/→.
- **≈2026-08-14 05:12–05:24 UTC** — how to mark a missed clip; Enter on caption to add.
- **2026-08-14 05:30 UTC** — could replace large swaths of the actual tool. Editable description; keep the skill's original label.
- **2026-08-14 05:32 UTC** — is edit auto-saved?
- **2026-08-14 05:36 UTC** — extracted-marker / description column; 3-way time-aligned grid.
- **2026-08-14 05:48 UTC** — video on top; `j`/`k`/Enter; want YouTube expand back.
- **2026-08-14 05:54 UTC** — `f` toggles video-top vs video-left.
- **≈2026-08-14 06:02–06:08 UTC** — Enter to apply a clip; delete for adds; extracted-inserted rows vs overlap-with-caption.
- **≈2026-08-14 06:15–06:16 UTC** — kill the checkbox; freeform feedback; positive feedback on generated markers too.
- **2026-08-14 06:20 UTC** — click timestamp steals keys; Esc doesn't return them.
- **≈2026-08-14 06:29–06:53 UTC** — TAKE/CONCEPT independent of the clip. Tags + work (song|rendition) + lane. Autocomplete; Tab+t/w/l; field order Work, Lane, Tags; Enter on existing → edit label.
- **2026-08-14 06:58 UTC** — `j` stuck on 3:19 — two rows share a start. Selection must be row identity.
- **2026-08-14 07:43 UTC** — easiest path for Fable to audit/refactor. Dashboard is the app; don't wrap in Next or fold into the extension.
- **2026-08-14 08:40 UTC** — product breakthrough in your words — viewing (YouTube) vs annotating (dashboard), same yt-clipper.
- **2026-08-14 08:44 UTC** — media-scraper is a separate project; remind the long-term JSON-export tie. Skill vs wrap scrape into the app. Ask for a split to-do.
- **2026-08-14 08:50 UTC** — wrap chronology + findings as a **suggested path** for Claude → `docs/two-surface-handoff.md`.
- **2026-08-14 09:03 UTC** — Fable is going; does it have `python3 apps/studio/server.py` → 8765?
- **2026-08-14 09:12 UTC** — "annotation UX still on you" read as the product isn't built. Clarified: Fable has source, not a browser tab.
- **2026-08-14 09:13 UTC** — kill PID 56490 (zombie `eval/server.py`, empty `curl`); start `apps/studio/server.py`; paste-block for Fable (URL, curl, HTML-from-disk, restart Python on server edits).
- **≈2026-08-14 09:14–09:48 UTC** — 143s as that process (and the next) get SIGTERM. Port empty → restart studio again. Fable bouncing `server.py`.
- **2026-08-17 09:39 UTC** — audit 1507 vs this composer. ~25–30% is this Friday afternoon; most of 1507 is Fable + Sunday. Unique here: zombie 8765 / files-not-the-tab.
- **2026-08-17 09:40 UTC** — `/session-log` this composer. New file; do not edit 1507.

## Banked artifacts

Fable live-studio paste (Fri 17:13):

Live studio is running. Do not start another copy, and do not use `eval/` — that folder is a husk.

- App (browser): http://127.0.0.1:8765
- Code: `apps/studio/index.html` (UI, served from disk on every GET `/` — HTML edits show on refresh, no restart)
- Server: `apps/studio/server.py` (API; restart this process if you change the Python)
- Data: `apps/studio/runs/`, `apps/studio/labels.jsonl`

```bash
curl -s http://127.0.0.1:8765/ | head
curl -s http://127.0.0.1:8765/api/runs
curl -s "http://127.0.0.1:8765/api/run?id=YYW4Q1Nivg8-20260814-1248" | head -c 500
```

That is source + HTTP. The annotation UX (grid, `j`/`k`, YouTube embed) only exists in a real browser at that URL. If port 8765 is dead or still serving empty replies, from repo root:

```bash
lsof -nP -iTCP:8765 -sTCP:LISTEN
# kill that PID if it is not `python3 apps/studio/server.py`
python3 apps/studio/server.py
```
