#!/usr/bin/env python3
"""Ingest a YouTube video into a studio run: caption track (with silence-gap
flags), title, description, and parsed description timestamps (extracted).

Shells out to yt-dlp (must be on PATH: pip install yt-dlp). Needs network
egress to YouTube. Ported from the yt-clipper skill's fetch_transcript.py and
attach_extracted.py so the skill runbook is no longer the only door to a run file.
"""
from __future__ import annotations

import glob
import json
import os
import re
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

# Talk cues sit ~2-15s apart; playing/demo takes ~20-60s+ apart. Inter-onset
# gaps at or above this threshold get a gapBefore flag on the following cue.
DEFAULT_GAP_SECONDS = 18.0
SUBPROCESS_TIMEOUT = 300

VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
STAMP_RE = re.compile(r"^(\d{1,2}:\d{2}(?::\d{2})?)\s+(.+)$")


class IngestError(RuntimeError):
    """User-reportable ingest failure (bad input, yt-dlp failure, no captions)."""


def parse_video_id(s):
    """Extract an 11-char YouTube video id from a URL or bare id, else None."""
    s = (s or "").strip()
    if VIDEO_ID_RE.match(s):
        return s
    m = re.search(r"(?:v=|/shorts/|youtu\.be/|/embed/|/live/)([A-Za-z0-9_-]{11})", s)
    return m.group(1) if m else None


def watch_url(video_id):
    return f"https://www.youtube.com/watch?v={video_id}"


def _run_ytdlp(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=SUBPROCESS_TIMEOUT)
    except FileNotFoundError:
        raise IngestError("yt-dlp not found. Install it: pip install yt-dlp")
    except subprocess.TimeoutExpired:
        raise IngestError("yt-dlp timed out — YouTube unreachable or very slow")


def fetch_captions(video_id):
    """Auto/manual caption track as [(start_seconds, text), ...] via json3."""
    with tempfile.TemporaryDirectory() as td:
        proc = _run_ytdlp([
            "yt-dlp", "--skip-download",
            "--write-auto-subs", "--write-subs",
            "--sub-langs", "en.*,en",
            "--sub-format", "json3",
            "-o", os.path.join(td, "%(id)s.%(ext)s"),
            watch_url(video_id),
        ])
        files = sorted(glob.glob(os.path.join(td, "*.json3")))
        if not files:
            tail = (proc.stderr or "").strip()[-500:]
            raise IngestError(
                f"no captions found (yt-dlp exit {proc.returncode}). {tail}"
            )
        with open(files[0], encoding="utf-8") as fh:
            data = json.load(fh)
    cues = []
    for ev in data.get("events", []):
        segs = ev.get("segs")
        if not segs:
            continue
        text = "".join(seg.get("utf8", "") for seg in segs)
        if not text.strip():
            continue
        cues.append((ev.get("tStartMs", 0) / 1000.0, " ".join(text.split())))
    if not cues:
        raise IngestError("caption track was empty")
    return cues


def build_cues(pairs, gap_seconds=DEFAULT_GAP_SECONDS):
    """[(start, text)] -> run `cues` entries with gapBefore flags.

    Gaps are inter-onset (next start minus previous start) because auto-caption
    durations are unreliable. Starts stored as whole seconds, matching the
    original fetch_transcript.py output that existing runs were built from.
    """
    cues = []
    prev = None
    for start, text in pairs:
        entry = {"start": int(start), "text": text}
        if prev is not None and (start - prev) >= gap_seconds:
            entry["gapBefore"] = int(start - prev)
        cues.append(entry)
        prev = start
    return cues


def fetch_title_and_description(video_id):
    """One yt-dlp call: first output line is the title, the rest is the description."""
    proc = _run_ytdlp([
        "yt-dlp", "--print", "title", "--print", "description",
        "--skip-download", watch_url(video_id),
    ])
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "yt-dlp failed").strip()[-500:]
        raise IngestError(f"could not fetch video metadata: {tail}")
    out = proc.stdout
    title, _, description = out.partition("\n")
    return title.strip(), description


def parse_description_timestamps(text):
    """`M:SS label` / `H:MM:SS label` lines from a description -> extracted entries."""
    marks = []
    for raw in (text or "").splitlines():
        match = STAMP_RE.match(raw.strip())
        if not match:
            continue
        parts = [int(p) for p in match.group(1).split(":")]
        seconds = parts[-1] + parts[-2] * 60 + (parts[-3] * 3600 if len(parts) == 3 else 0)
        marks.append({"start": float(seconds), "label": match.group(2).strip()})
    return marks


def extracted_markers(run):
    """Return description timestamps from the one supported data key."""
    extracted = run.get("extracted")
    return extracted if isinstance(extracted, list) else []


def create_run(url_or_id, runs_dir, gap_seconds=DEFAULT_GAP_SECONDS):
    """Ingest a video and write a run file with an empty markers array.

    Returns (run_id, run_dict). Raises IngestError on anything user-reportable.
    """
    video_id = parse_video_id(url_or_id)
    if not video_id:
        raise IngestError(f"could not parse a video id from: {url_or_id!r}")

    title, description = fetch_title_and_description(video_id)
    cues = build_cues(fetch_captions(video_id), gap_seconds)

    run = {
        "videoId": video_id,
        "url": watch_url(video_id),
        "title": title or video_id,
        "createdAt": datetime.now().astimezone().isoformat(),
        "markers": [],
        "cues": cues,
        "descriptionText": description,
        "extracted": parse_description_timestamps(description),
    }

    runs_dir = Path(runs_dir)
    runs_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    run_id = f"{video_id}-{stamp}"
    path = runs_dir / f"{run_id}.json"
    n = 2
    while path.exists():
        run_id = f"{video_id}-{stamp}-{n}"
        path = runs_dir / f"{run_id}.json"
        n += 1
    path.write_text(json.dumps(run, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return run_id, run


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("usage: ingest.py <youtube-url-or-id> [gap_seconds]", file=sys.stderr)
        raise SystemExit(2)
    gap = float(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_GAP_SECONDS
    try:
        rid, r = create_run(sys.argv[1], Path(__file__).resolve().parent / "runs", gap)
    except IngestError as err:
        print(f"ERROR: {err}", file=sys.stderr)
        raise SystemExit(1)
    print(f"wrote run {rid}: {len(r['cues'])} cues, {len(r['extracted'])} extracted")
