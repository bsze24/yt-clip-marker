#!/usr/bin/env python3
"""Pull a YouTube video down for offline work: file, captions, metadata, run.

The offline path assumes yt-dlp is the door. This is that door as one command
instead of a memorised flag soup:

    python3 apps/studio/prefetch.py <url-or-id> [<url-or-id> ...]

For each video it downloads the media plus its `.json3` captions and
`.info.json` into `media/`, then makes sure a run exists for it. If a run for
that video id is already in `runs/` — because you ingested it online earlier —
nothing new is written: `resolve_run_media` in server.py matches the file to
that run by video id on every read, so the existing run simply starts playing
from disk. Only a video with no run yet gets one built.

Codec choice is the one non-obvious flag. Chrome seeks H.264/AAC in MP4 far
more reliably than the VP9 and AV1 streams yt-dlp otherwise prefers, and
seeking is the whole job here.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import ingest
import local
from ingest import IngestError

APP_DIR = Path(__file__).resolve().parent
RUNS_DIR = APP_DIR / "runs"
MEDIA_DIR = APP_DIR / "media"

FORMAT = "bv*[height<=1080][vcodec^=avc1]+ba[acodec^=mp4a]/b[ext=mp4]/b"
DOWNLOAD_TIMEOUT = 3600
SUBS_TIMEOUT = 300

# The two tracks a YouTube lesson actually carries: "English (Original)" and
# the auto-generated "English". A wildcard like `en.*` also matches
# auto-translated tracks (`en-de`, `en-en`), which are useless here and cost an
# extra request each — enough to earn a 429 that then fails the whole download.
SUB_LANGS = "en-orig,en"

# Which YouTube player client yt-dlp asks for the stream URLs. This is not a
# preference, it is a workaround with a shelf life: on 2026-08-19 the default
# choice (`android_vr`) returned URLs that answered 403 Forbidden for the media
# itself, while still listing every format. `web_embedded` offers the same full
# format list and its URLs work; `mweb` is a fallback that works but only ever
# offers 360p. Captions and metadata are unaffected — only stream downloads are.
#
# When this rots, re-derive it rather than guessing. For each candidate client:
#
#   yt-dlp --extractor-args "youtube:player_client=<client>" -F <url>
#
# and prefer the one that both lists high formats and actually downloads.
# Updating yt-dlp is the real fix; this constant is the stopgap.
PLAYER_CLIENTS = "web_embedded,mweb"


def run_cue_count(run_id, runs_dir):
    try:
        data = json.loads((runs_dir / f"{run_id}.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 0
    return len(data.get("cues") or [])


def existing_run_for(video_id, runs_dir):
    """Newest run id already covering this video, or None."""
    best = None
    for path in sorted(runs_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if data.get("videoId") == video_id:
            if best is None or path.stat().st_mtime > best[1]:
                best = (path.stem, path.stat().st_mtime)
    return best[0] if best else None


def caption_sidecars(video_id, media_dir):
    return sorted(media_dir.glob(f"{video_id}.*.json3")) + sorted(media_dir.glob(f"{video_id}.*.vtt"))


def downloaded_media(video_id, media_dir):
    for ext in (".mp4", ".m4v", ".mkv", ".webm", ".mov"):
        path = media_dir / f"{video_id}{ext}"
        if path.is_file():
            return path
    return None


def fetch(video_id, media_dir):
    """Download media + captions + info json. Returns the media file path."""
    cmd = [
        "yt-dlp",
        "-f", FORMAT,
        "--merge-output-format", "mp4",
        "--write-auto-subs", "--write-subs",
        "--sub-langs", SUB_LANGS,
        "--sub-format", "json3/vtt",
        "--write-info-json",
        "--no-playlist",
        "--extractor-args", f"youtube:player_client={PLAYER_CLIENTS}",
        "-o", str(media_dir / "%(id)s.%(ext)s"),
        ingest.watch_url(video_id),
    ]
    try:
        proc = subprocess.run(cmd, timeout=DOWNLOAD_TIMEOUT)
    except FileNotFoundError:
        raise IngestError("yt-dlp not found. Install it: pip install yt-dlp")
    except subprocess.TimeoutExpired:
        raise IngestError("yt-dlp timed out")
    # Judge success by what landed on disk, not by the exit code. yt-dlp exits
    # non-zero if any single subtitle track fails — a 429 on one redundant
    # track would otherwise throw away a video that downloaded fine.
    path = downloaded_media(video_id, media_dir)
    if path is None:
        raise IngestError(f"yt-dlp exited {proc.returncode} and left no media file")
    if proc.returncode != 0:
        print(f"  note: yt-dlp exited {proc.returncode}, but the media file landed")
    if not any(media_dir.glob(f"{video_id}*.json3")) and not any(media_dir.glob(f"{video_id}*.vtt")):
        print("  note: no caption track came down — this run will have zero cues,\n"
              "        mark with n at the playhead instead")
    return path


def fetch_subs(video_id, media_dir):
    """Captions and metadata only — no media. Cheap enough to retry freely.

    Split out from `fetch` because YouTube generates auto-captions well after a
    freshly uploaded video is watchable. Downloading the video is the expensive,
    once-only half; getting its transcript is the half you come back for.
    """
    cmd = [
        "yt-dlp", "--skip-download",
        "--write-auto-subs", "--write-subs",
        "--sub-langs", SUB_LANGS,
        "--sub-format", "json3/vtt",
        "--write-info-json",
        "--no-playlist",
        "--extractor-args", f"youtube:player_client={PLAYER_CLIENTS}",
        "-o", str(media_dir / "%(id)s.%(ext)s"),
        ingest.watch_url(video_id),
    ]
    try:
        subprocess.run(cmd, timeout=SUBS_TIMEOUT)
    except FileNotFoundError:
        raise IngestError("yt-dlp not found. Install it: pip install yt-dlp")
    except subprocess.TimeoutExpired:
        raise IngestError("yt-dlp timed out fetching captions")
    return caption_sidecars(video_id, media_dir)


def prefetch_one(spec, runs_dir, media_dir):
    video_id = ingest.parse_video_id(spec)
    if not video_id:
        raise IngestError(f"could not parse a video id from: {spec!r}")
    media_dir.mkdir(parents=True, exist_ok=True)
    runs_dir.mkdir(parents=True, exist_ok=True)

    path = downloaded_media(video_id, media_dir)
    if path is not None:
        print(f"  media already present: {path.name}")
    else:
        path = fetch(video_id, media_dir)
        print(f"  downloaded {path.name}")

    # A rerun must be able to pick up captions that appeared after the video
    # did. Without this the function short-circuits on the existing run and a
    # zero-cue run stays zero-cue forever, which is the wrong answer for a
    # freshly uploaded video — exactly the case reruns exist for.
    if not caption_sidecars(video_id, media_dir):
        print("  no captions on disk — checking whether YouTube has them yet")
        if fetch_subs(video_id, media_dir):
            print("  captions arrived")
        else:
            print("  still none. Rerun this later; the video download is already done.")

    known = existing_run_for(video_id, runs_dir)
    if known:
        known_cues = run_cue_count(known, runs_dir)
        if known_cues or not caption_sidecars(video_id, media_dir):
            print(f"  run {known} already exists ({known_cues} cues) — it will play from this file")
            return known, False
        # Captions landed after a zero-cue run was built. Runs are immutable
        # ingest output (D-002), so this writes a second one rather than editing
        # the first; both play from the same file. Say so, because label events
        # are keyed by run id and do not follow.
        print(f"  run {known} has 0 cues but captions now exist — writing a new run")
        print(f"    delete runs/{known}.json if you have not annotated it")

    run_id, run, notes = local.create_local_run(path, runs_dir, media_dir)
    print(f"  wrote run {run_id}: {len(run['cues'])} cues, {len(run['extracted'])} extracted")
    for note in notes:
        print(f"    - {note}")
    return run_id, True


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip().splitlines()[0], file=sys.stderr)
        print("usage: prefetch.py <url-or-id> [<url-or-id> ...]", file=sys.stderr)
        return 2
    if shutil.which("ffmpeg") is None:
        print("warning: ffmpeg not on PATH — yt-dlp cannot merge separate video and\n"
              "         audio streams, so it will fall back to a lower-quality\n"
              "         single-file format.", file=sys.stderr)
    failures = 0
    for spec in argv[1:]:
        print(spec)
        try:
            prefetch_one(spec, RUNS_DIR, MEDIA_DIR)
        except IngestError as err:
            print(f"  ERROR: {err}", file=sys.stderr)
            failures += 1
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
