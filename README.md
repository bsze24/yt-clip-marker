# yt-clip-marker

Clip-marking tool for long-form YouTube video (music lessons). One clipper, two surfaces:

- **Studio** (`apps/studio/`) — the workspace. Local web app with a time-aligned grid of captions, skill markers, added markers, and extracted markers; keyboard-first clip creation with a work / lane / tags taxonomy; in-app ingest from a YouTube URL.
- **Extension** (`apps/extension/`) — the viewing surface. Thin Chrome extension for coarse `[` / `]` capture while watching on youtube.com. Deliberately frozen at that scope.

Both speak the same clip record (`docs/clip-schema.md`). Product model and rationale: `docs/youtube-clip-marker-prd.md`. Active task, decisions, and roadmap for agents: `docs/coordination/`.

## Studio

```
python3 apps/studio/server.py
```

Open http://127.0.0.1:8765. Requires Python 3 and, for ingesting new videos, [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) on PATH (`pip install yt-dlp`).

- Paste a YouTube URL in the header to ingest it (caption track, silence-gap flags, description timestamps) and start annotating.
- `j`/`k` move rows · `Enter` add/edit clip · `Tab` then `t`/`w`/`l`/`y` edit tags/work/lane/why · `x` reject a skill marker or delete an added marker · `f` follow · `space` play/pause.
- Data lives in `apps/studio/runs/` (per-video ingest/model output) and `apps/studio/labels.jsonl` (append-only judgments). Commit them to back up your work.
- **Eval mode** (header toggle) reveals the skill-scoring chrome: per-marker check/note feedback and rationales.

## Extension

1. Open `chrome://extensions`, enable **Developer mode**.
2. Click **Load unpacked** and select the `apps/extension` folder.
3. On a YouTube watch page: `[` marks a start (5s backdate), `]` marks the end and offers an optional description. Marks are in-memory scratch — real annotation happens in the studio.

If the panel doesn't appear, check `chrome://extensions` → Details → Site access allows youtube.com, then reload the watch page.

## Status

Studio is the active surface; the extension is frozen at coarse capture. **PR 3** (the
two-surface product) merged to `main` on 2026-08-18. Still open: **PR 4** (video 1 store),
**PR 5** (session log), **PR 6** (superseded — see `docs/coordination/`). Live baton:
`docs/coordination/CURRENT.md`. Change history: `docs/prs/`.
