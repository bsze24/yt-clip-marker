#!/usr/bin/env python3
"""Build a studio run from a media file already on disk — no network.

Two callers matter:

  * a YouTube video downloaded ahead of time with yt-dlp, where the sidecar
    `.info.json` and `.json3`/`.vtt` subtitle files carry the same title,
    description and caption track the online ingest would have fetched;
  * a Zoom recording, which has a `.vtt` only when the meeting was cloud
    recorded with "Create audio transcript" on. Local Zoom recordings have no
    transcript, so a run with zero cues is a supported outcome, not a failure.

Run shape matches ingest.create_run so every reader downstream is unchanged,
plus two keys: `source: "local"` and `media` (the file name inside media/).
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path

import ingest
from ingest import IngestError

VIDEO_EXT = {".mp4", ".m4v", ".webm", ".mkv", ".mov"}
AUDIO_EXT = {".m4a", ".mp3", ".ogg", ".oga", ".wav", ".opus", ".flac"}
MEDIA_EXT = VIDEO_EXT | AUDIO_EXT

# Subtitle sidecars, best first. json3 keeps yt-dlp's exact cue starts; vtt and
# srt are the only thing Zoom and hand-made transcripts offer.
SUB_EXT = (".json3", ".vtt", ".srt")

CUE_ID_RE = re.compile(r"^\d+$")
VTT_TIME_RE = re.compile(
    r"(\d{1,3}):(\d{2}):(\d{2})[.,](\d{1,3})\s*-->\s*(\d{1,3}):(\d{2}):(\d{2})[.,](\d{1,3})"
)
VTT_SHORT_TIME_RE = re.compile(
    r"(\d{1,3}):(\d{2})[.,](\d{1,3})\s*-->\s*(\d{1,3}):(\d{2})[.,](\d{1,3})"
)
TAG_RE = re.compile(r"<[^>]*>")
UNSAFE_RE = re.compile(r"[^A-Za-z0-9._-]+")


def looks_like_media_path(s):
    """True when this string is a local file reference, not a YouTube URL/id.

    Checked before the YouTube parse so a path never gets sent to yt-dlp.
    """
    s = (s or "").strip()
    if not s:
        return False
    if s.lower().startswith(("http://", "https://", "www.")):
        return False
    if s.startswith(("/", "~", "./", "../")):
        return True
    return Path(s).suffix.lower() in MEDIA_EXT


def resolve_media(spec, media_dir):
    """A user-typed path or bare name -> an existing media file Path."""
    spec = (spec or "").strip().strip('"').strip("'")
    if not spec:
        raise IngestError("no media file given")
    media_dir = Path(media_dir)
    candidates = []
    expanded = Path(os.path.expanduser(spec))
    if expanded.is_absolute() or spec.startswith(("./", "../", "~")):
        candidates.append(expanded)
    else:
        candidates.append(media_dir / spec)
        candidates.append(expanded)
    for path in candidates:
        if path.is_file():
            return path
    raise IngestError(f"no file at {spec!r} (looked in {media_dir} and as a path)")


def stage_media(path, media_dir):
    """Make the file reachable under media/ and return its name there.

    A file outside media/ is symlinked rather than copied — these are gigabytes
    and the studio only ever reads them. One allowlisted directory keeps the
    /media/ route free of any path-traversal surface.
    """
    media_dir = Path(media_dir)
    media_dir.mkdir(parents=True, exist_ok=True)
    path = path.resolve()
    if path.parent == media_dir.resolve():
        return path.name
    name = safe_name(path.name)
    link = media_dir / name
    if link.exists() or link.is_symlink():
        if link.is_symlink() and Path(os.readlink(link)) == path:
            return name
        stem, ext = os.path.splitext(name)
        n = 2
        while (media_dir / f"{stem}-{n}{ext}").exists():
            n += 1
        name = f"{stem}-{n}{ext}"
        link = media_dir / name
    link.symlink_to(path)
    return name


def safe_name(name):
    """Filename reduced to the characters the /media/ route will serve."""
    stem, ext = os.path.splitext(name)
    stem = UNSAFE_RE.sub("-", stem).strip("-.") or "media"
    return stem[:80] + ext.lower()


def synthetic_video_id(path):
    """Stable id for a file with no YouTube identity, from its own name."""
    stem = UNSAFE_RE.sub("-", Path(path).stem).strip("-.")
    return (stem or "local")[:48]


def find_sidecars(path):
    """Subtitle / info-json / description files sharing this file's stem.

    yt-dlp writes `{id}.en.json3` and `{id}.info.json`; Zoom writes a bare
    `{name}.vtt`. Both are stem-prefix matches in the same directory.
    """
    path = Path(path)
    stem = path.stem
    subs, info, description = [], None, None
    for sibling in sorted(path.parent.iterdir()):
        if not sibling.is_file() or sibling.name == path.name:
            continue
        if not sibling.name.startswith(stem):
            continue
        rest = sibling.name[len(stem):]
        if sibling.name.endswith(".info.json"):
            info = sibling
        elif sibling.suffix == ".description":
            description = sibling
        elif sibling.suffix.lower() in SUB_EXT:
            # Rank: json3 over vtt over srt, English-tagged over anything else.
            rank = (SUB_EXT.index(sibling.suffix.lower()), 0 if ".en" in rest else 1)
            subs.append((rank, sibling))
    subs.sort(key=lambda item: item[0])
    return [s for _rank, s in subs], info, description


def parse_json3(text):
    data = json.loads(text)
    pairs = []
    for ev in data.get("events", []):
        segs = ev.get("segs")
        if not segs:
            continue
        line = "".join(seg.get("utf8", "") for seg in segs)
        if not line.strip():
            continue
        pairs.append((ev.get("tStartMs", 0) / 1000.0, " ".join(line.split())))
    return pairs


def _clock(*parts):
    if len(parts) == 4:
        h, m, s, frac = parts
        return int(h) * 3600 + int(m) * 60 + int(s) + int(frac.ljust(3, "0")) / 1000.0
    m, s, frac = parts
    return int(m) * 60 + int(s) + int(frac.ljust(3, "0")) / 1000.0


def parse_vtt(text):
    """WebVTT or SRT -> [(start_seconds, text)].

    Handles the three shapes that actually turn up: Zoom's cue-numbered VTT
    with `Speaker: line` bodies, yt-dlp's auto-caption VTT with inline
    `<00:00:01.000><c>` karaoke tags and rolling repeated lines, and SRT.
    Speaker names are kept — they are useful in a lesson grid.
    """
    pairs = []
    start = None
    body = []

    def flush():
        nonlocal start, body
        if start is not None:
            line = " ".join(" ".join(body).split())
            line = TAG_RE.sub("", line).strip()
            if line and (not pairs or pairs[-1][1] != line):
                pairs.append((start, line))
        start, body = None, []

    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line:
            flush()
            continue
        if line.upper().startswith("WEBVTT") or line.startswith(("NOTE", "STYLE", "REGION")):
            flush()
            continue
        match = VTT_TIME_RE.search(line) or VTT_SHORT_TIME_RE.search(line)
        if match:
            flush()
            groups = match.groups()
            start = _clock(*groups[: len(groups) // 2])
            continue
        if start is None and CUE_ID_RE.match(line):
            continue
        if start is not None:
            body.append(line)
    flush()
    return pairs


def read_cue_pairs(sub_path):
    text = Path(sub_path).read_text(encoding="utf-8", errors="replace")
    if Path(sub_path).suffix.lower() == ".json3":
        return parse_json3(text)
    return parse_vtt(text)


def create_local_run(spec, runs_dir, media_dir, gap_seconds=ingest.DEFAULT_GAP_SECONDS):
    """Ingest a file already on disk. Returns (run_id, run, notes)."""
    source_path = resolve_media(spec, media_dir)
    if source_path.suffix.lower() not in MEDIA_EXT:
        raise IngestError(
            f"{source_path.name}: not a media file "
            f"(want one of {', '.join(sorted(MEDIA_EXT))})"
        )
    notes = []
    subs, info_path, desc_path = find_sidecars(source_path)

    video_id = None
    title = None
    description = ""
    url = ""
    if info_path is not None:
        try:
            info = json.loads(info_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            info = {}
            notes.append(f"{info_path.name} unreadable — ignored")
        raw_id = info.get("id") or ""
        if ingest.VIDEO_ID_RE.match(raw_id):
            video_id = raw_id
            url = ingest.watch_url(raw_id)
        title = (info.get("title") or "").strip() or None
        description = info.get("description") or ""
    if not description and desc_path is not None:
        description = desc_path.read_text(encoding="utf-8", errors="replace")

    if video_id is None:
        video_id = synthetic_video_id(source_path)
    if not title:
        title = source_path.stem

    cues = []
    if subs:
        pairs = read_cue_pairs(subs[0])
        if pairs:
            cues = ingest.build_cues(pairs, gap_seconds)
            notes.append(f"captions from {subs[0].name} ({len(cues)} cues)")
        else:
            notes.append(f"{subs[0].name} parsed to zero cues")
    else:
        notes.append("no transcript sidecar found — grid starts empty, use n to mark")

    media_name = stage_media(source_path, media_dir)
    run = {
        "videoId": video_id,
        "url": url,
        "title": title,
        "createdAt": datetime.now().astimezone().isoformat(),
        "source": "local",
        "media": media_name,
        "markers": [],
        "cues": cues,
        "descriptionText": description,
        "extracted": ingest.parse_description_timestamps(description),
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
    return run_id, run, notes


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("usage: local.py <media-file-or-name> [gap_seconds]", file=sys.stderr)
        raise SystemExit(2)
    gap = float(sys.argv[2]) if len(sys.argv) > 2 else ingest.DEFAULT_GAP_SECONDS
    here = Path(__file__).resolve().parent
    try:
        rid, r, msgs = create_local_run(sys.argv[1], here / "runs", here / "media", gap)
    except IngestError as err:
        print(f"ERROR: {err}", file=sys.stderr)
        raise SystemExit(1)
    print(f"wrote run {rid}: {len(r['cues'])} cues, {len(r['extracted'])} extracted")
    for msg in msgs:
        print(f"  - {msg}")
