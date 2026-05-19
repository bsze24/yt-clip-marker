# yt-clip-marker

Chrome extension for marking and exporting clip ranges from YouTube videos.

## Install for development

1. Clone this repo.
2. Open `chrome://extensions` in Chrome.
3. Enable **Developer mode** (toggle in the top-right corner).
4. Click **Load unpacked** and select the project folder.
5. Visit a YouTube watch page (e.g. `https://www.youtube.com/watch?v=...`).

A placeholder panel labeled "Clip Marker" should appear in the top-right of the page.

## Status

V1 in active development. See open PRs for current scope and progress.

## Troubleshooting

If the panel doesn't appear on a watch page, check `chrome://extensions` → click "Details" on the extension → "Site access" should be set to allow youtube.com. Reload the watch page after changing.
