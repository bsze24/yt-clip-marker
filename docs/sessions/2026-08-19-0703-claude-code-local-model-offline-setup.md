---
date: 2026-08-19
time: "07:03"
surface: claude-code-opus-5
project: yt-clip-marker
track: offline-capability
branch: local-video-mode
commit: 4b344d5c47c4997de4e5bd68c1bc2b7b4053b478
task: docs/coordination/CURRENT.md
---

# Session log — 2026-08-19 07:03 (claude-code-opus-5) — local-model-offline-setup

## Project context
- Brian boards an 18-hour flight today and wants to work the studio with no network:
  process transcripts 2–5 and polish UX. This session set up a local model to stand in
  for Claude. `CURRENT.md` at this commit still points at the PR 3/4/5 review; that thread
  is untouched here.
- A parallel session landed **PR 7 (`4b344d5`)** on this branch mid-conversation — local
  video mode, a `<video>` backend behind `player.js`'s existing interface plus a
  range-capable `/media/` route and `local.py`. It is not this session's work and has no
  log of its own. It closes the offline-player blocker named below.

## What changed
- **Nothing in the repo from this session.** All work was machine setup outside the tree.
- Installed: `ollama` (brew), `aider-chat` 0.86.2 (uv, pinned to Python 3.12).
- Pulled: `qwen3-coder:30b` (18 GB) and `qwen3:30b-a3b` (18 GB).
- Wrote `~/flight-local-llm.md` — offline cheatsheet, outside the repo, banked below.
- Landed in parallel, not by this session: `4b344d5` PR 7 local video mode.

## Decisions
- **Local model stack is ollama + `qwen3-coder:30b` for code, `qwen3:30b-a3b` for
  transcripts, driven by aider.** One serving stack, official Ollama tags, both fit RAM
  at 4-bit. Tooling choice, not a product `D-0xx`.
- **Skip Qwen3-Coder-Next.** Its 4-bit build is 48.5 GB and does not fit 48 GB unified
  memory; the 3-bit builds that do fit are not reliably better than a 30B at 4-bit, and
  running it would split the stack across llama.cpp.
- **Coder model for code, generalist for transcripts.** Segmenting a lesson is prose
  judgment, and coder post-training measurably degrades it.

## Learning arc
- Brian caught that I recommended Qwen3-Coder-Next and then downloaded the 30B without
  labelling the hedge. He was right — the action and the words disagreed. He caught the
  same class of thing a second time when a stale `llama-server` process was still alive
  after I said Next was skipped.
- "do i need next if we're going with coder" — consolidating rather than accumulating.
  The instinct to cut an option once a decision is made, instead of hoarding all three.
- The size error was mine and it drove a wrong recommendation: I quoted 28 GB for
  Qwen3-Coder-Next Q4_K_M from a search snippet. The real file is 48.5 GB. Verifying at
  the source (the HF file listing) inverted the recommendation.

## Concepts touched
- [concept] quantization-vs-parameter-count — emerging — surfaced only when Brian pushed on
  the contradiction; an 80B at 3-bit and a 30B at 4-bit land in the same place, and code
  suffers more from low-bit quantization than prose does.
- [concept] prebuilt-wheel-vs-source-build — emerging — aider install died compiling scipy
  for want of a Fortran compiler; pinning `--python 3.12` put it back on a version with
  prebuilt wheels. "It started compiling" is the signal.
- [concept] offline-blocker-inventory — emerging — the model was never the hard part.
  Enumerating what silently needs network (ingest, the YouTube iframe, package installs)
  before losing it is the actual work.

## Coaching hooks
- **Unlabelled hedge, 2x today.** I downloaded the safe model while recommending the
  ambitious one, and didn't say I was hedging. Brian read it as a contradiction both times,
  correctly. If an action diverges from the stated recommendation, name it in the same
  breath as the action.
- **Verify sizes at the source, not from a search snippet.** One wrong number produced a
  wrong recommendation that took three turns to unwind.
- Brian's questions were the fastest path to the real tradeoff. The "wait, why" questions
  were doing real work, not signalling confusion.

## Next / open threads
- **Transcripts 2–5 are still not ingested.** `runs/` holds only video 1
  (`YYW4Q1Nivg8-20260814-1248.json`). `ingest.py` needs YouTube. This is the one blocker
  that cannot be cleared offline and it is the subject of the planned flight work.
- **`apps/studio/media/` is empty.** PR 7 makes offline playback possible but requires
  `{videoId}.mp4` on disk. Without a pull, playback is still dead in the air.
- PR 7 (`4b344d5`) has no session log and is not reflected in `CURRENT.md`. Someone should
  reconcile it.
- Airplane-mode smoke test was never run end to end with the studio.

## Open questions / blockers
- Whether the 30B is actually good enough for the studio's JS at agentic depth. Untested
  beyond a one-line generation.
- Unknown whether transcripts 2–5 have caption tracks at all; ingest fails without them.

## Chronology (the record)
- Brian opens with the flight and asks how to get a local model running, guessing a coder
  model is right.
- Machine audit: M4 Pro, 48 GB, 1.1 TB free. `llama.cpp` and `yt-dlp` already present via
  brew; no ollama, no LM Studio, no models.
- Repo audit turns up the real problem: `apps/studio/runs/` does not exist on `main`, and
  `player.js:56` loads the YouTube iframe API. Two network dependencies, neither about
  the model.
- Brian: 45 minutes, pick a model and download it. Then interrupts to ask for a range of
  options and a web search first.
- Searches surface Qwen3-Coder-Next as the 48 GB pick, GLM-4.7-Flash as a strong 30B-class
  alternative, Qwen3-Coder 30B-A3B as the safe consensus.
- I start the 19 GB `qwen3-coder:30b` pull as insurance while writing up the options —
  without labelling it as insurance.
- Brian: "wait why are you installing Qwen3-Coder 30B-A3B when you recommended Next?"
  Fair. I answer the inconsistency directly.
- Throughput measured at "71 MB/s" — wrong, it was reading ollama's preallocated sparse
  files. Real rate later measured at 48 MB/s.
- The Next download 404s on a bad quant tag. Fetching the actual HF file listing shows
  Q4_K_M is 48.5 GB, not the 28 GB the search snippet claimed. That kills the
  recommendation: on 48 GB, Next only fits at 3-bit.
- Brian: "getting mixed signals — can my machine handle next or is coder the better fit?"
  Straight answer given: take the 30B.
- Brian: "do i need next if we're going with coder?" No. Skipped.
- Brian spots that a `llama-server` process is still alive. It is — a zombie from the 404,
  downloading nothing. Killed it. He follows with "oh i see nm".
- `brew install uv && uv tool install aider-chat` fails building scipy from source for want
  of `g95`. Fixed with `--python 3.12`.
- Both models complete. Smoke test: `qwen3-coder:30b` returns a correct clamp one-liner in
  ~11 s including load.
- Wrote `~/flight-local-llm.md`.
- Restarted `ollama serve` with `OLLAMA_CONTEXT_LENGTH=65536`, flash attention on, KV cache
  at q8_0. Verified: 65536 context, 100% GPU, 21 GB resident, `/v1` endpoint answering.
- Brian: "so we are actually at pencils down on the local model" — yes. I flag the two
  remaining network-dependent items; he does not paste the URLs.
- Meanwhile, a parallel session commits PR 7 (`4b344d5`) — local video mode — at 07:03.
- Brian invokes `/session-log`.

## Banked artifacts

`~/flight-local-llm.md` lives outside the repo. Contents:

```
# Offline setup — yt-clip-marker

## Start the model server (do this first, every time)
OLLAMA_CONTEXT_LENGTH=65536 ollama serve

Default context is small and SILENTLY TRUNCATES transcripts.
If the model seems dumb about a transcript, this is why.

## Models
qwen3-coder:30b   -> code / UX polish   (~52 tok/s)
qwen3:30b-a3b     -> transcript segmentation, prose judgment

## Coding agent
cd ~/app-projects/yt-clip-marker
OPENAI_API_BASE=http://127.0.0.1:11434/v1 OPENAI_API_KEY=dummy \
  aider --model openai/qwen3-coder:30b --no-auto-commits

## Studio
cd ~/app-projects/yt-clip-marker/apps/studio && python3 server.py
Open http://127.0.0.1:8765

## KNOWN OFFLINE LIMITS
- YouTube iframe player will NOT load (ui/player.js:56 fetches youtube.com).
  Labeling is transcript-text-only unless you swap in a local <video>.
- ingest.py needs network. Cannot add new transcripts in the air.

## Battery
~3h of continuous generation. Use a smaller model or pause between prompts.
```

Note: the "KNOWN OFFLINE LIMITS" player line is now stale — PR 7 addresses it in code,
though `media/` is still empty.

Ingest command for transcripts 2–5, unrun:

```
cd ~/app-projects/yt-clip-marker/apps/studio && for u in URL2 URL3 URL4 URL5; do python3 ingest.py "$u"; done
```

**quantization** — shrinking a model by storing its numbers with fewer bits. 4-bit ("Q4")
halves the size of 8-bit at a small accuracy cost; 3-bit and below start visibly degrading
output. It is NOT the same as making the model smaller: parameter count is unchanged, only
the precision of each parameter. This is why an 80B at 3-bit and a 30B at 4-bit can be
comparable — the 80B knows more but expresses it more coarsely.
