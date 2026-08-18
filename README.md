# yt-clip-marker

Clip-marking tool for long-form YouTube video (music lessons). One clipper, two surfaces:

- **Studio** (`apps/studio/`) — the workspace. Local web app with a time-aligned grid of captions, markers, and published description timestamps; keyboard-first clip creation with a work / lane / tags taxonomy; in-app ingest from a YouTube URL.
- **Extension** (`apps/extension/`) — the viewing surface. Thin Chrome extension for coarse `[` / `]` capture while watching on youtube.com. Deliberately frozen at that scope.

Both speak the same clip record (`docs/clip-schema.md`). Product model and rationale: `docs/youtube-clip-marker-prd.md`.

## Studio

```
python3 apps/studio/server.py
```

Open http://127.0.0.1:8765. Requires Python 3 and, for ingesting new videos, [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) on PATH (`pip install yt-dlp`).

- Paste a YouTube URL in the header to ingest it (caption track, silence-gap flags, description timestamps) and start annotating.
- `j`/`k` move rows · `Enter` add/edit clip · `Tab` then `t`/`w`/`l`/`y` edit tags/work/lane/why · `x` reject a marker or delete an added clip · `f` follow · `space` play/pause.
- Data lives in `apps/studio/runs/` (per-video ingest/model output) and `apps/studio/labels.jsonl` (append-only judgments). Commit them to back up your work.
- **Eval mode** (header toggle) reveals the skill-scoring chrome: per-marker check/note feedback and rationales.

## Extension

1. Open `chrome://extensions`, enable **Developer mode**.
2. Click **Load unpacked** and select the `apps/extension` folder.
3. On a YouTube watch page: `[` marks a start (5s backdate), `]` marks the end and offers an optional description. Marks are in-memory scratch — real annotation happens in the studio.

If the panel doesn't appear, check `chrome://extensions` → Details → Site access allows youtube.com, then reload the watch page.

## Status

Two-surface refactor in progress. The studio is the active surface; the extension is frozen at coarse capture. See `docs/prs/` for change history.
