---
date: 2026-08-16
time: "15:07"
revised: 2026-08-16 16:34
surface: grok
project: yt-clip-marker
track: studio-workspace
branch: two-surface-refactor
commit: 56fac8380824bef232850cd4813c944218823c0c
task: docs/youtube-clip-marker-prd.md
---

# Session log — 2026-08-16 15:07 (grok) — studio-eval-handoff

## Project context
- Pointer at HEAD (`56fac83`): `docs/youtube-clip-marker-prd.md` is still the **V1 one-surface** PRD. Working tree (uncommitted) already has the two-surface PRD, `docs/two-surface-handoff.md`, `docs/clip-schema.md`, `AGENTS.md`, and `apps/studio/`. Resume from the working-tree docs, not `git show HEAD:…`.
- Companion fold (uncommitted): `docs/sessions/2026-08-16-YYW4Q1Nivg8-folded-ledger.md`.
- Authored in **Cursor Grok**. Filename keeps `claude` from the first write. Skill `surface` allowlist has no grok bucket; yaml `surface: grok` is the agent that wrote this file. The *session* spanned Grok (Fri prototype) → Fable (Fri–Sat lock) → Grok (Sun use). Resume by `track: studio-workspace`.
- Sister Friday chat (prototype): `4a29e5bc-ab92-4039-b509-2181e3df77e5`. This composer (`59a62acc`) opened Fri 16:54 as Fable executing the handoff, then flipped to Grok Sunday.
- Live studio: `http://127.0.0.1:8765`. Run in play: `YYW4Q1Nivg8-20260814-1248`.

## Summary
Started as a first `/yt-clipper` run on a real lesson; the eval harness built to score that run became the clipper (studio). Ended with video 1 fully labeled, leftover eval list closed, product still uncommitted on `two-surface-refactor`.

## What changed
- **Committed this session:** `56fac83` — first session-log (mis-leveled; this file is the curate rewrite of that). HEAD of the *product* is still `9dd147d` (PR 2: extension capture).
- Working tree holds the whole two-surface + studio tree (`?? apps/studio/`, rewritten PRD, labels). Git cannot split “Fri–Sat uncommitted” from “Sunday.”
- Session-log skill symlinked: `~/.cursor/skills/session-log` → `~/.claude/skills/session-log`.
- Folded ledger written, not committed.

## Decisions
- Studio is the annotating workspace; the YouTube extension stays a frozen thin viewing client. They share the clip contract (`docs/clip-schema.md`), not code.
- Store: `runs/{id}.json` immutable ingest/model output; `labels.jsonl` append-only human events. Latest event per row identity wins; deletes are `unmiss` tombstones.
- Language: **marker** (run `markers[]`) vs **added clip** (miss/`unmiss`) vs **gold** (published description stamps). Stop “skill marker.”
- Eval channels stay distinct: `g` = stingy few-shot keep of a *marker*; `star` = personal bookmark; taxonomy without `g` = ordinary keep (not a skip); `x` = reject marker; blank + no taxonomy = unreviewed; delete/`unmiss` = remove an add. Same `x` *key* on an ADDED CLIP already deletes.
- Grid align: **exact start first**, then ≤2s. Earliest-cue-wins was lying about times.
- Copy-timestamps: never drop gold or adds; 2s fold; **add beats marker**; `g` still exports (so 20:46 and 21:18 both copy). Export-vs-eval exclusion of ballpark-`g` deferred.
- Studio ingest (URL) = cues/gaps/gold, **empty markers**. Skill still proposes markers. Video 2: Add video in the header unless you want another `/yt-clipper` pass.
- This log’s starting point is the first skill run (Fri 12:35), not the pre-Friday extension/PRD.

## Learning arc
- First skill run on `YYW4Q1Nivg8`: markers at 1:20 / 2:37 sat in the middle of playing. Could not judge them without seeing captions, `>>> GAP` lines, and the runbook on one surface. That sniff *is* the eval-harness ask.
- Asked for a disposable scoring loop (check keyword, rationale → runbook, 5 videos in a few hours) and, three minutes later, durable `labels.jsonl` “in case we want this in the product.” Then every “eval” request (captions on the grid, add-clip, gold column, `j`/`k`) was already the annotating IDE. Named at 1:30 — 42 minutes after the harness ask, still calling it eval.
- Two-surface named in your own words at 4:40: viewing (YouTube) and annotating (this dashboard) are two clients of one clipper. The dashboard is yt-marker v1; the extension-as-IDE was the wrong host.
- Split the work across models on purpose: Grok for speed-to-prototype the same afternoon; Fable to lock the instinct (promote `eval/` → studio, freeze extension, ingest, split the 1500-line script). Sunday Grok was not “come back to harden” — it was **use-as-design** on video 1.
- Using the tool designed the remaining product: `g` vs `star` vs `x`, follow vs pin, filler hide, inherit work/lane. Highest-value wobble: the time column is the caption the clip was *aligned onto*, not the clip’s stored start (1:18:50/`g` was marker@52 snapped onto “Okay.”).
- Eval channels must not collapse: taxonomy-without-`g` is a keep, not a blank; `g` is the few-shot positive (not optional chrome); useful ballpark ≠ perfect place (keep both, or `x` the hunt).

## Concepts touched
- [concept] eval-harness-becomes-the-product — solidifying — asked for a 5-video scoring UI; 1:30 named it as the tool; Sunday labeled inside it
- [concept] eval harness (fixture that holds the skill so you can score it) — emerging — used the word; mechanism sharpened this curate (input → capture → human score → durable write)
- [concept] hostile-host / two-surface — solidifying — named 4:40; Fable locked it into PRD + tree; not the founding prompt of this log
- [concept] skill as suggester not workflow — solidifying — fetch/gold moved into studio ingest; skill still proposes markers; video 2 does not have to go through `/yt-clipper`
- [concept] speed-model then structure-model then use-as-design — emerging — Grok Fri / Fable Fri–Sat / Grok Sun; remembered as “moved back to Grok to harden,” which the transcripts contradict
- [concept] eval channels vs product keep (g / x / taxonomy / star / delete) — solidifying — recipe written; almost collapsed to “just train on x”
- [concept] displayed-time vs stored identity — solidifying — 1:18:50/52/54 named after two fluent misreads; exact-first landed

## Coaching hooks
- **Harness that you keep using is the first store.** Durable labels “in case it becomes product” was the tell. Next time you stand up a scoring UI for a skill, assume you are scaffolding the workspace, not a throwaway table.
- **Displayed-time ≠ stored-time** (earliest neighbor wins): 1:18:50/`g` and 1:18:52/ADDED CLIP were the same two clips, twice. Next “I don’t see that stamp” / “why is this g’d,” dump store identity (`markerIndex` / miss start) before arguing the time column. Mechanism-before-badge: three captions + run file + events unstuck it; repeating “skill marker” did not.
- **Session-log chronology must start at the starting point.** First write of this file started at Sunday leftover nits; a week-later reader could not recover “eval dashboard was v1.” Your remembered 6-beat arc was the right *kind* of story, mis-leveled (started too late, beat 5 mixed Fable-harden with Sunday-use). Interrogate memory against transcripts before rewriting.
- **Heuristic that died in review:** “last sequential-number mention in a block.” Capture the death so a future pass doesn’t revive it from an old note.

## Next / open threads
- **Land the repo in splits** (not done): A product (two-surface + studio UI) as PR 3; B `runs/` + `labels.jsonl`; C `docs/sessions/`. Never `git add -A`. Never commit to `main`. Fetch/pull `main` first.
- **Video 2:** Add video in the studio header (empty markers) unless you want another skill pass.
- **Export vs eval:** 20:46 (`g`) and 21:18 (add) both copy. Decide later whether ballpark-`g` should be export-excluded.
- PRD next (unbuilt): clip `end`s, JSON export for media-scraper, suggest-markers as a studio action.
- Offer (not done): add a `## Session logs` one-liner to `AGENTS.md` pointing at `docs/sessions/` + `track:`.
- Skill `surface` allowlist has no grok value — extend the skill, or keep documenting the exception.

## Open questions / blockers
- Should `g` keep a row in copy-timestamps, or is `g` eval-only?
- None blocking annotation; eval leftover list is empty. Ledger: 64 markers (`g` 23 · `x` 24 · keep 14 · note 3 · blank 0), 21 live adds, 24 gold. (First log’s “14 blanks” were taxonomy-without-`g` keeps.)

## Chronology (the record)
- Fri 12:09–12:30 (door into the run, same sitting): captions have start not end; `yt-dlp` PATH vs Homebrew vs `python3 -m` — the fetch the skill needs.
- Fri 12:35: first `/yt-clipper` on `https://www.youtube.com/watch?v=YYW4Q1Nivg8`. Run stamp `YYW4Q1Nivg8-20260814-1248` (~12:48): 64 markers, 1464 cues, 27 gaps.
- Fri 12:42: 1:20 and 2:37 look arbitrary mid-playing. “Sniffing like an eval surface might help.” 12:44: where is the actual runbook?
- Fri 12:48: spin up a **quick eval web dashboard**; rationale field as close as possible to the runbook rule; goal 5 videos in a few hours. Flow: run skill → table (start, description, rationale, feedback) → `check` = good marker.
- Fri 12:51: store eval feedback durably “in case we want to turn this eval into a real part of the product.” → `eval/labels.jsonl`.
- Fri 13:03–13:05: `>>> GAP` is the fetch script, not a caption. **Add caption segments + timestamps in the dashboard** so captions + playbook rules + markers are inline (the 0:22 / GAP@1:20 “Heat. Heat.” sketch).
- Fri 13:09–13:11: formatting; keep YouTube native keys (←/→ seek).
- Fri 13:12–13:24: how to mark a *missed* clip from the transcript? Enter on caption → add-clip; refresh the marker panel.
- Fri 13:30: “Honestly could see this replacing large swaths of the actual tool.” Editable description; **keep the skill’s original label** for another eval loop.
- Fri 13:36: gold/description column as eval against manual tagging; **3-way time-aligned grid** (captions / skill markers / description stamps).
- Fri 13:48–14:08: video on top; `j`/`k`/Enter; gold-row visual; layout toggle (`f` then); apply-clip key; delete for adds; gold-inserted rows highlighted only when they add a row (overlap with a caption = no extra treatment).
- Fri 14:10–14:20: checkbox that spawned a second add-clip on an already-clipped caption → kill the checkbox; freeform feedback; positive feedback on generated markers too.
- Fri 14:20: click timestamp steals keys; iframe focus (`keepKeysOnPage` later).
- Fri 14:29–14:53: TAKE/CONCEPT independent of the clip. Taxonomy: tags (take, fingering, technique, star) + work (song|rendition) + lane (transcription, …). Chapter ≠ concept. Autocomplete; Tab+t/w/l; field order Work, Lane, Tags; Enter on existing → edit label. `kind` becomes legacy.
- Fri 14:58: `j` stuck on 3:19 — two rows share a start; selection must be **row identity**, not start time.
- Fri 15:43: “easiest path for Fable to audit/refactor.” Grok: the eval dashboard *is* the app; promote it; don’t wrap in Next or fold into the extension.
- Fri 16:40: **product breakthrough in your words** — “this might actually end up being the better surface for what I imagined yt-clipper to be (chrome extension in yt)… viewing surface (youtube) and annotating surface (this dashboard) might be 2 separate things.”
- Fri 16:44: media-scraper is a **separate repo**, downstream JSON export only. Skill vs in-app scrape still open. Ask for a split to-do.
- Fri 16:50: wrap chronology + findings as a **suggested path** for Claude → `docs/two-surface-handoff.md`.
- Fri 16:54 **this thread (Fable):** execute handoff Steps A–D (PRD, tree, freeze extension, promote `eval/` → `apps/studio/`).
- Fri 17:16: port from Grok to Fable for production — audit / red-team / harden, not a from-scratch rebuild. `eval/` is a husk.
- Fri 17:32–17:39: Fable extra-high overbaked for UX nits? Yes for chrome; no for keyboard/focus/state. **Yes: split the 1500-line inline script** → `ui/keys.js` one dispatcher, `ui/state.js` `S`, modules.
- Sat 15:48: Shift+j/k between populated marker rows; “skill” → feel “marker” is better (terminology lands Sunday).
- Sat 16:48–17:08: Esc out of tag field; `x` on tag chip; tab work→lane in composer.
- Sun 11:18 (Grok again, same composer): follow; inherit work/lane; Enter expands marker fields and submits.
- Sun 11:23–11:38: how to say “perfect skill marker”? Talk through tags vs fields. `g` = write `check` under the hood (few-shot), **not** a tag and **not** `star` (personal bookmark). `c`/chapter deprecated. Grid `s` / `g` / `x`. Visual eval chip.
- Sun 11:40–11:54: selected row centered; timeline ticks; star migration + visual; qualitative why on remove (“Heat heat” hallucinated caption); 0:00 as chapter not clip; YouTube chapters as a maybe; rogue tags on Tab; restore selection on refresh.
- Sun 11:59: Tab+w → why on existing markers.
- Sun 12:27–12:31: follow vs pin — follow on while watching fights editing (row runs away). Toggle; layout hotkey moves off `f`.
- Sun 12:39 then 12:58: pause-on-j reversed — browse keeps playing; **edit mode pauses**.
- Sun 12:43–12:54: filler captions (yeah/okay/right) are noise, not an AssemblyAI problem. Hide/skip backchannels; editable skip-word list; `h` toggle + mode chrome.
- Sun 13:15–13:41: `x` not delete as the reject/delete key; tags column between marker and work; `<`/`>` playback rate; follow-on `j`/`k` origin = playhead row then pin.
- Sun 14:04: first full marker-eval + clipping pass done. Ask: (1) do the annotations make a comprehensible eval stream? (2) copy timestamps back to YouTube description — never drop manuals; label matches manual where present.
- Sun 14:10–14:21: copy-timestamps metadata; over 5000 chars → work as section header; first section needs “Pennies from Heaven | Stan Getz”; `0:00 Start` under first header; `***` for star.
- Sun 14:22–14:24: taxonomy-without-`g` is an unlabeled **keep**, not a skip. Is `g` worth it vs just taxonomy? Yes: `g` is a note to future-you (few-shot exemplar); `star` is for you.
- Sun 14:28–14:36: cross-ref notes; sloppy ones rewritten; 29:09 not a grid row (caption-only) — note lives on 29:23.
- Sun 14:40–14:54: 1:18:50/52/54 confusion. Store: no clip at 50; marker[53] at 52 `g`; add at 54. Time column had snapped. Terminology: “skill marker” → “marker.” Align fix: `takeExact` then `takeNear`. Leftover adds: **delete** (`unmiss`), not `x`-as-verdict; `x` key on ADDED CLIP already deletes.
- Sun 14:58–15:04: 35:53/`x` (still hunting) + 36:39 keep; 0:22 unmiss; 38:55 `x` (chapter change). Aside: do not train only on `x` — `g` is few-shot. 20:46/`g` ballpark + 21:18 perfect; sequential-numbers = fingering, last-mention stripped; 29:23/`g` names 29:09, no add created.
- Sun 15:06–15:15: session-log skill import (symlink); first `/session-log` write (this file, then mis-leveled). Folded ledger asked so Claude can reverse-engineer marker + gold + added without the live grid.
- Sun 15:13–15:15: Fable refactor was **this** composer, not a missing Claude-app chat. Model flip is the picker (re-bills prefix).
- Sun 16:10: video 2 ingest is **studio** Add video (empty markers), not required skill run.
- Sun 16:14–16:16: land repo soon; model-switch cost; first log introspected as too app-specific / wrong starting point.
- Sun 16:27–16:34: remembered 6-beat arc interrogated against transcripts **before** rewriting. Starting point = first skill run. Skip pre-Friday product history. Curate this file.

## Worked corrections
- Claim: I stood up an eval, then later realized it was the product. → Correction: 13:30 was 42 minutes after the 12:48 harness ask, in the same Grok sitting, while still asking to preserve skill labels for another eval loop. → Principle: the instinct often arrives *inside* the “disposable” tool, not after a finished prototype.
- Claim: moved back to Grok and hardened through one full runthrough. → Correction: Fable (Fri 17:16–Sat) was the harden/restructure; Sunday Grok was labeling video 1, which designed the remaining UX. → Principle: speed-model / structure-model / use-as-design are three jobs; don’t merge the last two.
- Claim: 1:18:50 is a `g`-tagged manual clip. → Correction: no clip at 1:18:50; `g` is marker 1:18:52 parked on caption “Okay.” → Principle: **row time ≠ clip start** until exact match wins.
- Claim: ADDED CLIP on 1:18:52 means I added 1:18:52. → Correction: add stored at 1:18:54; same snap. → Principle: badge follows stored identity; time column follows the caption the clip was aligned onto.
- Claim: `x` is purely for markers, so leftover adds need a different op. → Correction: verdict `wrong` is markers-only; the `x` *key* on an add already `unmiss`es. → Principle: one key, two writes — check ADDED CLIP vs marker before you hit it.
- Claim: we should just train on `x`. → Correction: `g` is the few-shot positive; `x` is the negative; taxonomy without `g` is ordinary keep. → Principle: don’t collapse eval channels because one of them is also a hotkey.
- Claim: 14 blank markers remain. → Correction: those 14 had taxonomy and no `g` — they are keeps. True unreviewed = blank + no taxonomy. → Principle: missing few-shot label ≠ unreviewed.

## Banked artifacts

Eval harness (plain): a **harness** is the fixture that holds the thing under test so you can apply a known load and read a score — a test stand, not the motor. An **eval harness** for a skill is: known input (this video) → capture the skill’s output (the run) → human score (`check` / why / later `g`/`x`) → durable write (`labels.jsonl`) so the next run can compare. The Friday dashboard was that stand. Keeping the stand in daily use is how it became the product.

Eval verdicts (do not collapse):
- `g` / `check` / `check:` — few-shot exemplar of a *marker*. Stingy.
- `star` tag — personal bookmark, not eval.
- taxonomy (work/lane/tags) without `g` — ordinary keep.
- `x` / `wrong` / `wrong:` — reject this marker. Eval negative.
- delete / `unmiss` — remove an added clip. Not a marker verdict.
- blank feedback + no taxonomy — unreviewed.

Sequential-numbers rule (surviving; last-mention is dead):
> Spoken sequential finger numbers (e.g. 5 4 3 1, 2 1 3) mean a fingering clip. Tag fingering. Do not prefer the last mention in a block — that heuristic did not survive review.

Placement pairs on `YYW4Q1Nivg8-20260814-1248`:
- 20:46 marker `g` (ballpark) → 21:18 added “Double note fingering” (perfect).
- 29:23 marker `g` (ballpark) → better caption 29:09 “Maybe it’s a good hint”; no clip stored there.
- 35:53 marker `x` (still hunting) → 36:39 added “Line before the ending” (keep).

Copy-timestamps fold (`apps/studio/ui/export.js`): gold + adds never dropped; nearby ≤2s merge; RANK gold < miss < skill so an add steals time+label from a marker; `wrong` markers skipped; `g`/taxonomy markers kept.

Grid align (`buildRows` in `apps/studio/ui/grid.js`): exact start first, then ≤2s. MATCH is still 2.

Hotkeys (current): `j`/`k` rows · `J`/`K` marker rows · Enter add/edit · `s` star · `g` check · `x` reject/delete · Tab then `t`/`w`/`l`/`y` · `h` hide filler · `f` follow · `v` layout · `<`/`>` speed · space play.

Video 2 door: studio header **Add video** (URL → cues/gaps/gold, empty `markers[]`). Skill pass optional if you want proposed markers.
