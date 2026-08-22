#!/usr/bin/env python3
"""Clip Studio — the clipper's annotation workspace.

python3 apps/studio/server.py → http://127.0.0.1:8765
"""
from __future__ import annotations

import json
import os
import math
import re
import sys
import threading
import traceback
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

import ingest
import local
import uploads

APP_DIR = Path(__file__).resolve().parent
RUNS_DIR = APP_DIR / "runs"
UI_DIR = APP_DIR / "ui"
LABELS_PATH = APP_DIR / "labels.jsonl"
MEDIA_DIR = APP_DIR / "media"
UPLOADS_PATH = APP_DIR / "uploads.json"
PORT = 8765
UPLOADS_CACHE = uploads.UploadCache(UPLOADS_PATH)

# /media/ serves only bare filenames from MEDIA_DIR. No slashes and no "..",
# so a symlinked gigabyte file inside the directory is reachable while nothing
# outside it is. Files here are often symlinks — never resolve() before the
# check, or a legitimate link would read as an escape.
MEDIA_FILE = re.compile(r"^[A-Za-z0-9._-]+$")
MEDIA_TYPES = {
    ".mp4": "video/mp4", ".m4v": "video/mp4", ".mov": "video/quicktime",
    ".webm": "video/webm", ".mkv": "video/x-matroska",
    ".m4a": "audio/mp4", ".mp3": "audio/mpeg", ".ogg": "audio/ogg",
    ".oga": "audio/ogg", ".opus": "audio/ogg", ".wav": "audio/wav",
    ".flac": "audio/flac",
}
# Streamed in chunks so a 2 GB lesson never lands in memory.
STREAM_CHUNK = 256 * 1024

# /ui/ serves only bare .js/.css filenames — no dots in the stem, so no "..",
# no subdirectories, no traversal.
UI_FILE = re.compile(r"^[a-z0-9_-]+\.(js|css)$")
UI_TYPES = {".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8"}

# labels.jsonl is append-only and shared across request threads; a lock keeps
# two simultaneous saves from interleaving inside one JSONL line.
LABELS_LOCK = threading.Lock()


def append_event(event):
    ensure_dirs()
    line = json.dumps(event, ensure_ascii=False) + "\n"
    with LABELS_LOCK:
        with LABELS_PATH.open("a", encoding="utf-8") as fh:
            fh.write(line)


def finite_float(value):
    """float() that rejects NaN/inf — they would poison last-event-wins folds."""
    out = float(value)
    if not math.isfinite(out):
        raise ValueError("not finite")
    return out

SAFE_ID = re.compile(r"^[A-Za-z0-9._-]+$")
RULE_RE = re.compile(r"R-[A-Z0-9-]+")
TAG_RE = re.compile(r"^[a-z0-9][a-z0-9 _-]{0,39}$")


def normalize_tags(raw):
    if not isinstance(raw, list):
        return []
    seen = []
    for item in raw:
        if not isinstance(item, str):
            continue
        tag = " ".join(item.strip().lower().split())
        if not tag or not TAG_RE.match(tag) or tag in seen:
            continue
        seen.append(tag)
    return seen


def ensure_dirs():
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    if not LABELS_PATH.exists():
        LABELS_PATH.write_text("", encoding="utf-8")


def read_label_events():
    ensure_dirs()
    events = []
    try:
        raw = LABELS_PATH.read_text(encoding="utf-8")
    except OSError:
        return events
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def current_feedback_map(events=None):
    """runId -> {markerIndexStr: feedbackText}, last event wins."""
    by_run = {}
    for ev in read_label_events() if events is None else events:
        run_id = ev.get("runId")
        if not run_id:
            continue
        if ev.get("verdict") in ("miss", "relabel", "unmiss", "annotate"):
            continue
        idx = ev.get("markerIndex")
        if idx is None:
            continue
        by_run.setdefault(run_id, {})[str(idx)] = ev.get("feedback") or ""
    return by_run


def load_additions(run_id, events=None):
    """Human-added misses for a run. Last event per start time wins."""
    by_start = {}
    for ev in read_label_events() if events is None else events:
        if ev.get("runId") != run_id:
            continue
        start = ev.get("start")
        if start is None:
            continue
        if ev.get("verdict") == "unmiss":
            by_start.pop(float(start), None)
            continue
        if ev.get("verdict") != "miss":
            continue
        by_start[float(start)] = {
            "start": float(start),
            "end": ev.get("end"),
            "kind": ev.get("kind") or None,
            "description": ev.get("description") or "",
            "why": ev.get("feedback") or "",
            "cueText": ev.get("cueText") or "",
            "gapBefore": ev.get("gapBefore"),
            "tags": normalize_tags(ev.get("tags")),
            "lane": ev.get("lane") or "",
            "work": ev.get("work") or "",
        }
    return sorted(by_start.values(), key=lambda m: m["start"])


def load_edits(run_id, events=None):
    """Human-edited labels for markers. Last relabel per index wins.
    The run JSON keeps the original description."""
    by_idx = {}
    for ev in read_label_events() if events is None else events:
        if ev.get("runId") != run_id:
            continue
        if ev.get("verdict") != "relabel":
            continue
        idx = ev.get("markerIndex")
        if idx is None:
            continue
        by_idx[str(idx)] = ev.get("description") or ""
    return by_idx


def load_sections(run_id, events=None):
    """Where the lesson's work changes, as [(start, work), ...] ascending.

    A work change is an event at a timestamp, stored once. It is not a property
    of a clip: on video 1 the work changes twice across 67 rows, and the old
    shape stored the string on all 67. One lesson covering two pieces is normal,
    so the answer is a section break, not a per-clip field.

    Lives here rather than on the run file because `runs/{id}.json` is immutable
    ingest output ([[D-002]]). Resolved on read, same as media ([[D-034]]).

    Latest event per `start` wins, so re-setting a break overwrites it and
    clearing its work removes it.
    """
    by_start = {}
    for ev in read_label_events() if events is None else events:
        if ev.get("runId") != run_id or ev.get("verdict") != "chapter":
            continue
        start = ev.get("start")
        start = 0.0 if start is None else float(start)
        work = (ev.get("work") or "").strip()
        lane = (ev.get("lane") or "").strip()
        if work or lane:
            by_start[start] = {"work": work, "lane": lane}
        else:
            by_start.pop(start, None)
    return [[at, v["work"], v["lane"]] for at, v in sorted(by_start.items())]


def section_at(sections, start):
    """The work and lane in effect at `start` — the latest break at or before it."""
    current = ("", "")
    for at, work, lane in sections:
        if at <= start:
            current = (work, lane)
        else:
            break
    return current


def append_section(run_id, run, payload):
    work = payload.get("work") if isinstance(payload.get("work"), str) else ""
    lane_in = payload.get("lane") if isinstance(payload.get("lane"), str) else ""
    try:
        start = float(payload.get("start") or 0)
    except (TypeError, ValueError):
        start = 0.0
    event = {
        "schemaVersion": 2,
        "recordedAt": datetime.now().astimezone().isoformat(),
        "runId": run_id,
        "videoId": run.get("videoId"),
        "videoUrl": run.get("url"),
        "videoTitle": run.get("title"),
        "markerIndex": None,
        "source": "human-chapter",
        "start": start,
        "end": None,
        "description": "",
        "tags": [],
        "lane": lane_in.strip(),
        "work": work.strip(),
        "feedback": "",
        "verdict": "chapter",
    }
    append_event(event)
    return load_sections(run_id)


def load_annotations(run_id, events=None):
    """tags / lane / work on markers. Last annotate per index wins."""
    by_idx = {}
    for ev in read_label_events() if events is None else events:
        if ev.get("runId") != run_id:
            continue
        if ev.get("verdict") != "annotate":
            continue
        idx = ev.get("markerIndex")
        if idx is None:
            continue
        by_idx[str(idx)] = {
            "tags": normalize_tags(ev.get("tags")),
            "lane": ev.get("lane") or "",
            "work": ev.get("work") or "",
        }
    return by_idx


def load_run(run_id):
    if not SAFE_ID.match(run_id):
        return None
    path = RUNS_DIR / f"{run_id}.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"}


def linked_youtube_id(run_id, events=None):
    """Latest append-only link value for a run, or ``None`` when never set.

    An explicit empty string is different from no event: it clears an immutable
    URL fallback. Invalid non-empty values are treated as a clear on reads; the
    writer rejects them, but a malformed hand-edited event must never authorize
    playback or deletion.
    """
    linked = None
    found = False
    for ev in read_label_events() if events is None else events:
        if (ev.get("runId") != run_id or ev.get("verdict") != "link"
                or "youtubeId" not in ev):
            continue
        found = True
        raw = ev.get("youtubeId")
        candidate = raw.strip() if isinstance(raw, str) else ""
        linked = candidate if ingest.VIDEO_ID_RE.fullmatch(candidate) else ""
    return linked if found else None


def effective_youtube_id(run_id, run, events=None):
    """The playable YouTube identity from a link event or immutable ingest data.

    A local Zoom run has a filename-derived ``videoId`` that must never be sent
    to the embed. A downloaded YouTube run can also say ``source: local``, so
    source and id shape are not sufficient either. The canonical watch URL is
    the evidence: accept only known YouTube hosts and a valid 11-character id.

    The latest link event wins, including an explicit empty string that clears
    the fallback. Otherwise the run's canonical watch URL is the evidence.
    """
    linked = linked_youtube_id(run_id, events)
    if linked is not None:
        return linked
    if not isinstance(run, dict):
        return ""
    raw = run.get("url")
    if not isinstance(raw, str) or not raw.strip():
        return ""
    try:
        parsed = urlparse(raw.strip())
    except ValueError:
        return ""
    host = (parsed.hostname or "").lower().rstrip(".")
    candidate = ""
    if host == "youtu.be":
        candidate = parsed.path.strip("/").split("/", 1)[0]
    elif host in YOUTUBE_HOSTS:
        if parsed.path.rstrip("/") == "/watch":
            candidate = (parse_qs(parsed.query).get("v") or [""])[0]
        else:
            parts = [part for part in parsed.path.split("/") if part]
            if len(parts) >= 2 and parts[0] in ("shorts", "embed", "live"):
                candidate = parts[1]
    return candidate if ingest.VIDEO_ID_RE.fullmatch(candidate or "") else ""


def run_warnings(run_id, run, events=None):
    """Nonfatal store faults that must stay visible while the run remains usable."""
    warnings = []
    if "gold" in run:
        message = f"run {run_id} has deprecated gold[]; rename gold[] → extracted[]"
        print(f"[studio] ERROR: {message}", file=sys.stderr)
        warnings.append({"code": "deprecated-run-key", "key": "gold", "message": message})
    # A run that names a media file but cannot find it. Worth saying out loud:
    # files in media/ are usually symlinks into wherever the recording actually
    # lives, so moving or renaming the source breaks one without touching
    # anything the studio owns. The old failure was silent — a black player and
    # no reason — and the fix is a one-line repoint, but only if you know that
    # is what happened. Annotations are unaffected either way; they are keyed by
    # run id in labels.jsonl, not by the file.
    youtube_id = effective_youtube_id(run_id, run, events)
    declared = run.get("media")
    if declared and resolve_run_media(run) is None and not youtube_id:
        message = (
            f"run {run_id} expects media/{declared}, which is missing or is a "
            f"broken symlink — captions and markers are intact, but it will not play. "
            f"Repoint it: ln -sf <new path> apps/studio/media/{declared}"
        )
        print(f"[studio] ERROR: {message}", file=sys.stderr)
        warnings.append({"code": "missing-media", "key": declared, "message": message})
    return warnings


def load_feedback(run_id):
    return current_feedback_map().get(run_id, {})


def append_link(run_id, run, payload):
    """Append a human YouTube link (or explicit clear) for one immutable run."""
    raw = payload.get("youtubeId")
    if not isinstance(raw, str):
        raise ValueError("youtubeId must be a string")
    youtube_id = raw.strip()
    if youtube_id and not ingest.VIDEO_ID_RE.fullmatch(youtube_id):
        raise ValueError("youtubeId must be an 11-character YouTube id or empty")
    append_event({
        "schemaVersion": 2,
        "recordedAt": datetime.now().astimezone().isoformat(),
        "runId": run_id,
        "videoId": run.get("videoId"),
        "videoUrl": run.get("url"),
        "videoTitle": run.get("title"),
        "verdict": "link",
        "youtubeId": youtube_id,
        "source": "human-link",
    })
    return youtube_id


def verdict_for(text):
    stripped = (text or "").strip()
    lower = stripped.lower()
    if lower == "check" or lower.startswith("check:"):
        return "check"
    if lower == "wrong" or lower.startswith("wrong:"):
        return "wrong"
    if stripped:
        return "note"
    return "blank"


def append_label(run_id, run, index, text):
    markers = run.get("markers") or []
    marker = markers[index] if 0 <= index < len(markers) else {}
    rationale = marker.get("rationale") or ""
    original = marker.get("description") or ""
    current_label = load_edits(run_id).get(str(index)) or original
    event = {
        "schemaVersion": 2,
        "recordedAt": datetime.now().astimezone().isoformat(),
        "runId": run_id,
        "videoId": run.get("videoId"),
        "videoUrl": run.get("url"),
        "videoTitle": run.get("title"),
        "markerIndex": index,
        "start": marker.get("start"),
        "end": marker.get("end"),
        "kind": marker.get("kind"),
        "originalDescription": original,
        "description": current_label,
        "rationale": rationale,
        "ruleIds": RULE_RE.findall(rationale),
        "feedback": text,
        "verdict": verdict_for(text),
    }
    append_event(event)
    return load_feedback(run_id)


def append_miss(run_id, run, payload):
    try:
        start = finite_float(payload.get("start"))
    except (TypeError, ValueError):
        raise ValueError("bad start")
    description = (payload.get("description") or "").strip()
    if not description:
        raise ValueError("description required")
    why = payload.get("why") if isinstance(payload.get("why"), str) else ""
    why = why.strip()
    tags = normalize_tags(payload.get("tags"))
    lane = payload.get("lane") if isinstance(payload.get("lane"), str) else ""
    work = payload.get("work") if isinstance(payload.get("work"), str) else ""
    lane = lane.strip()
    work = work.strip()
    kind = payload.get("kind")
    if kind not in ("TAKE", "CONCEPT"):
        kind = None
    event = {
        "schemaVersion": 2,
        "recordedAt": datetime.now().astimezone().isoformat(),
        "runId": run_id,
        "videoId": run.get("videoId"),
        "videoUrl": run.get("url"),
        "videoTitle": run.get("title"),
        "markerIndex": None,
        "source": "human-miss",
        "start": start,
        "end": None,
        "kind": kind,
        "tags": tags,
        "lane": lane,
        "work": work,
        "description": description,
        "rationale": f"MISS. {why}".strip() if why else "MISS.",
        "ruleIds": [],
        "feedback": why,
        "verdict": "miss",
        "cueText": payload.get("cueText") or "",
        "gapBefore": payload.get("gapBefore"),
    }
    append_event(event)
    return load_additions(run_id)


def append_unmiss(run_id, run, payload):
    try:
        start = finite_float(payload.get("start"))
    except (TypeError, ValueError):
        raise ValueError("bad start")
    existing = next((m for m in load_additions(run_id) if m["start"] == start), None)
    if existing is None:
        return load_additions(run_id)
    event = {
        "schemaVersion": 2,
        "recordedAt": datetime.now().astimezone().isoformat(),
        "runId": run_id,
        "videoId": run.get("videoId"),
        "videoUrl": run.get("url"),
        "videoTitle": run.get("title"),
        "markerIndex": None,
        "source": "human-unmiss",
        "start": start,
        "end": existing.get("end"),
        "kind": existing.get("kind"),
        "tags": existing.get("tags") or [],
        "lane": existing.get("lane") or "",
        "work": existing.get("work") or "",
        "description": existing.get("description") or "",
        "rationale": "UNMISS.",
        "ruleIds": [],
        "feedback": "",
        "verdict": "unmiss",
        "cueText": existing.get("cueText") or "",
        "gapBefore": existing.get("gapBefore"),
    }
    append_event(event)
    return load_additions(run_id)


def append_relabel(run_id, run, index, description):
    markers = run.get("markers") or []
    if not (0 <= index < len(markers)):
        raise ValueError("bad index")
    marker = markers[index]
    original = marker.get("description") or ""
    description = (description or "").strip()
    if not description:
        raise ValueError("description required")
    event = {
        "schemaVersion": 2,
        "recordedAt": datetime.now().astimezone().isoformat(),
        "runId": run_id,
        "videoId": run.get("videoId"),
        "videoUrl": run.get("url"),
        "videoTitle": run.get("title"),
        "markerIndex": index,
        "source": "human-relabel",
        "start": marker.get("start"),
        "end": marker.get("end"),
        "kind": marker.get("kind"),
        "originalDescription": original,
        "description": description,
        "rationale": marker.get("rationale") or "",
        "ruleIds": RULE_RE.findall(marker.get("rationale") or ""),
        "feedback": "",
        "verdict": "relabel",
    }
    append_event(event)
    return load_edits(run_id)


def append_annotate(run_id, run, index, payload):
    markers = run.get("markers") or []
    if not (0 <= index < len(markers)):
        raise ValueError("bad index")
    marker = markers[index]
    tags = normalize_tags(payload.get("tags"))
    lane = payload.get("lane") if isinstance(payload.get("lane"), str) else ""
    work = payload.get("work") if isinstance(payload.get("work"), str) else ""
    event = {
        "schemaVersion": 2,
        "recordedAt": datetime.now().astimezone().isoformat(),
        "runId": run_id,
        "videoId": run.get("videoId"),
        "videoUrl": run.get("url"),
        "videoTitle": run.get("title"),
        "markerIndex": index,
        "source": "human-annotate",
        "start": marker.get("start"),
        "end": marker.get("end"),
        "kind": marker.get("kind"),
        "description": marker.get("description") or "",
        "tags": tags,
        "lane": lane.strip(),
        "work": work.strip(),
        "rationale": marker.get("rationale") or "",
        "ruleIds": RULE_RE.findall(marker.get("rationale") or ""),
        "feedback": "",
        "verdict": "annotate",
    }
    append_event(event)
    return load_annotations(run_id)


def media_file(name):
    """MEDIA_DIR/name if that name is servable and present, else None."""
    if not name or not MEDIA_FILE.match(name):
        return None
    path = MEDIA_DIR / name
    if not path.is_file():
        return None
    if path.suffix.lower() not in MEDIA_TYPES:
        return None
    return path


def resolve_run_media(run):
    """Local playback source for a run, computed fresh on every read.

    Deliberately not written back into the run file: `runs/{id}.json` is
    immutable ingest output (D-002). A run gains offline playback the moment a
    matching file appears in media/ and loses it when the file goes away, with
    no history rewritten either way.

    Two doors. A local run names its file. A YouTube run is matched by video id,
    so downloading `{videoId}.mp4` into media/ is the whole attach step.
    """
    if not isinstance(run, dict):
        return None
    path = media_file(run.get("media") or "")
    if path is None:
        video_id = run.get("videoId") or ""
        if MEDIA_FILE.match(video_id or ""):
            for ext in MEDIA_TYPES:
                candidate = MEDIA_DIR / f"{video_id}{ext}"
                if candidate.is_file():
                    path = candidate
                    break
    if path is None:
        return None
    kind = "audio" if MEDIA_TYPES[path.suffix.lower()].startswith("audio/") else "video"
    return {
        "name": path.name,
        "url": "/media/" + quote(path.name),
        "kind": kind,
        "type": MEDIA_TYPES[path.suffix.lower()],
    }


def list_media():
    """Files in media/, newest first, flagged with whether a run points at one."""
    ensure_dirs()
    claimed = set()
    for path in RUNS_DIR.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        found = resolve_run_media(data)
        if found:
            claimed.add(found["name"])
    rows = []
    for path in sorted(MEDIA_DIR.iterdir(), key=_mtime, reverse=True):
        if not path.is_file() or path.suffix.lower() not in MEDIA_TYPES:
            continue
        rows.append({"name": path.name, "used": path.name in claimed})
    return rows


def _mtime(path):
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def cached_upload_titles():
    """YouTube id -> current cached title; an invalid cache joins nothing."""
    cached = uploads.read_cache(UPLOADS_PATH)
    if cached is None:
        return {}
    return {item["id"]: item["title"] for item in cached["items"]}


def display_title(run, youtube_id, titles):
    """The read-time lesson title. YouTube owns it when the cache can join."""
    return titles.get(youtube_id) or run.get("title") or ""


def list_runs():
    ensure_dirs()
    events = read_label_events()
    fb_by_run = current_feedback_map(events)
    titles = cached_upload_titles()
    rows = []
    for path in sorted(RUNS_DIR.glob("*.json"), key=_mtime, reverse=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        run_id = path.stem
        youtube_id = effective_youtube_id(run_id, data, events)
        markers = data.get("markers") or []
        fb = fb_by_run.get(run_id, {})
        annotations = load_annotations(run_id, events)
        checks = wrongs = notes = keeps = 0
        for i, _m in enumerate(markers):
            v = verdict_for(fb.get(str(i), ""))
            if v == "check":
                checks += 1
            elif v == "wrong":
                wrongs += 1
            elif v == "note":
                notes += 1
            else:
                annotation = annotations.get(str(i), {})
                if annotation.get("tags") or annotation.get("lane") or annotation.get("work"):
                    keeps += 1
        rows.append(
            {
                "id": run_id,
                "videoId": data.get("videoId") or "",
                "youtubeId": youtube_id,
                "url": data.get("url") or "",
                "title": display_title(data, youtube_id, titles) or run_id,
                "runTitle": data.get("title") or run_id,
                "createdAt": data.get("createdAt") or "",
                "source": data.get("source") or "youtube",
                "hasMedia": bool(resolve_run_media(data)),
                "markerCount": len(markers),
                "missCount": len(load_additions(run_id, events)),
                "checkCount": checks,
                "wrongCount": wrongs,
                "noteCount": notes,
                "keepCount": keeps,
                "blankCount": max(0, len(markers) - checks - wrongs - notes - keeps),
            }
        )
    return rows


def run_payload(run_id, run):
    """Resolved `/api/run` response for one immutable run."""
    events = read_label_events()
    youtube_id = effective_youtube_id(run_id, run, events)
    return {
        "id": run_id,
        "youtubeId": youtube_id,
        "title": display_title(run, youtube_id, cached_upload_titles()) or run_id,
        "run": run,
        "feedback": current_feedback_map(events).get(run_id, {}),
        "sections": load_sections(run_id, events),
        "additions": load_additions(run_id, events),
        "edits": load_edits(run_id, events),
        "annotations": load_annotations(run_id, events),
        "warnings": run_warnings(run_id, run, events),
        "media": resolve_run_media(run),
    }


class Handler(BaseHTTPRequestHandler):
    # Keep-alive. Seeking a local video fires a burst of range requests, and
    # HTTP/1.0 would open a fresh connection for each one. Safe because every
    # response on every route sets Content-Length.
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        print(f"[studio] {self.address_string()} {fmt % args}")

    # True for the length of one HEAD request. Reset per request rather than in
    # a finally, so the 500 path in handle_one_request is still bodyless when a
    # HEAD is what failed. BaseHTTPRequestHandler reuses one instance across
    # every keep-alive request on a connection, which is why this must be reset
    # at the start of each rather than at the end of the last.
    _head_request = False

    def handle_one_request(self):
        # A bug in a route handler should surface as a 500 JSON error, not a raw
        # traceback and a reset connection in the UI.
        self._head_request = False
        try:
            super().handle_one_request()
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception:
            traceback.print_exc()
            try:
                self._json(500, {"error": "internal server error"})
            except Exception:
                pass

    def _send(self, code, body, content_type):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self._head_request:
            return
        self.wfile.write(data)

    def _json(self, code, obj):
        self._send(code, json.dumps(obj), "application/json; charset=utf-8")

    def _parse_range(self, header, size):
        """`Range: bytes=…` -> (start, end) inclusive, or None to send it whole.

        Raises ValueError when the range is syntactically fine but unsatisfiable,
        which is a 416. A header we don't understand is not an error — the spec
        says ignore it and send 200.
        """
        header = (header or "").strip()
        if not header.lower().startswith("bytes="):
            return None
        spec = header[6:].split(",")[0].strip()
        if "-" not in spec:
            return None
        first, _, last = spec.partition("-")
        try:
            if not first:
                # bytes=-N — the trailing N bytes.
                n = int(last)
                if n <= 0:
                    raise ValueError("empty suffix range")
                return max(0, size - n), size - 1
            start = int(first)
            end = int(last) if last else size - 1
        except ValueError:
            return None
        if start >= size or start > end:
            raise ValueError("unsatisfiable range")
        return start, min(end, size - 1)

    def _send_media(self, path):
        """Serve a media file with byte-range support.

        Chrome will happily *play* a 200 response, but it can only seek inside
        what it has already buffered — on an hour-long lesson that makes the
        timeline useless. 206 responses are what make seeking instant, so this
        route exists instead of reusing _send.
        """
        content_type = MEDIA_TYPES[path.suffix.lower()]
        try:
            size = path.stat().st_size
        except OSError:
            self._json(404, {"error": "not found"})
            return
        try:
            span = self._parse_range(self.headers.get("Range"), size)
        except ValueError:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{size}")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        if span is None:
            start, end = 0, size - 1
            code = 200
        else:
            start, end = span
            code = 206
        length = end - start + 1
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(length))
        if code == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self._head_request:
            return
        # Seeking aborts in-flight range requests constantly; a dropped client
        # is normal here, not a fault. handle_one_request swallows the reset.
        with path.open("rb") as fh:
            fh.seek(start)
            remaining = length
            while remaining > 0:
                chunk = fh.read(min(STREAM_CHUNK, remaining))
                if not chunk:
                    break
                self.wfile.write(chunk)
                remaining -= len(chunk)

    def _media_for_request(self, path):
        name = unquote(path[len("/media/"):])
        return media_file(name)

    def do_HEAD(self):
        # Same routing as GET, same status and Content-Length, no body. _send
        # and _send_media both stop at the flag, so every route answers a HEAD
        # correctly rather than only /media/.
        self._head_request = True
        self.do_GET()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/" or path == "/index.html":
            html = (APP_DIR / "index.html").read_text(encoding="utf-8")
            self._send(200, html, "text/html; charset=utf-8")
            return
        if path.startswith("/ui/"):
            name = path[len("/ui/"):]
            file_path = UI_DIR / name
            if not UI_FILE.match(name) or not file_path.is_file():
                self._json(404, {"error": "not found"})
                return
            body = file_path.read_text(encoding="utf-8")
            self._send(200, body, UI_TYPES[file_path.suffix])
            return
        if path.startswith("/media/"):
            found = self._media_for_request(path)
            if found is None:
                self._json(404, {"error": "not found"})
                return
            self._send_media(found)
            return
        if path == "/api/media":
            self._json(200, list_media())
            return
        if path == "/api/runs":
            self._json(200, list_runs())
            return
        if path == "/api/uploads":
            # Optional derived data: a missing or invalid cache is a successful
            # empty response, and this read never invokes yt-dlp.
            self._json(200, UPLOADS_CACHE.read_api())
            return
        if path == "/api/run":
            run_id = (parse_qs(parsed.query).get("id") or [""])[0]
            run = load_run(run_id)
            if run is None:
                self._json(404, {"error": "run not found"})
                return
            self._json(200, run_payload(run_id, run))
            return
        self._json(404, {"error": "not found"})

    def same_origin(self):
        """Reject a request a browser could make on another site's behalf.

        Binding to 127.0.0.1 is not an authorization boundary. Any page can
        submit a plain HTML form to a fixed localhost URL: it needs no CORS
        permission because it never reads the response, and the side effect
        lands anyway. Reproduced against /api/quit with
        `Origin: https://unrelated.example` — 200, and the server stopped.

        Two independent checks, because either alone has a gap:
        - `Origin` must match this request's own `Host` when present. Absent is
          allowed: curl and same-origin GETs omit it, and a cross-site *form*
          POST always sends it.
        - Content type must be JSON. The three form-encodable types are exactly
          the ones that skip a CORS preflight, so requiring JSON blocks the
          form shape even if a browser ever omits Origin.
        """
        origin = self.headers.get("Origin")
        if origin:
            host = (self.headers.get("Host") or "").strip()
            if urlparse(origin).netloc != host:
                return False
        ctype = (self.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        return ctype == "application/json"

    def do_POST(self):
        parsed = urlparse(self.path)
        # Both POST routes have side effects — /api/quit stops the server and
        # /api/ingest shells out to yt-dlp. PUT routes are unreachable from a
        # form, so the guard belongs here.
        if not self.same_origin():
            self._json(403, {"error": "cross-site request refused"})
            return
        if parsed.path == "/api/quit":
            # Quit for real. Under launchd, KeepAlive means simply exiting gets
            # us restarted a second later, so the agent has to be booted out
            # first — otherwise the button would appear to do nothing.
            self._json(200, {"ok": True, "quitting": True})
            try:
                self.wfile.flush()
            except OSError:
                pass
            threading.Thread(target=shutdown, daemon=True).start()
            return
        if parsed.path != "/api/ingest":
            self._json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length") or 0)
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json(400, {"error": "bad json"})
            return
        url = payload.get("url")
        if not isinstance(url, str) or not url.strip():
            self._json(400, {"error": "url required"})
            return
        try:
            gap = finite_float(payload.get("gapSeconds") or ingest.DEFAULT_GAP_SECONDS)
        except (TypeError, ValueError):
            self._json(400, {"error": "bad gapSeconds"})
            return
        if not (1.0 <= gap <= 600.0):
            self._json(400, {"error": "gapSeconds out of range (1-600)"})
            return
        # One input field, two doors. The local branch is tried first because a
        # path is unambiguous, while an 11-char stem could parse as a video id.
        # Local ingest never touches the network — that is the whole point.
        notes = []
        try:
            if local.looks_like_media_path(url):
                run_id, run, notes = local.create_local_run(url, RUNS_DIR, MEDIA_DIR, gap)
            else:
                run_id, run = ingest.create_run(url, RUNS_DIR, gap)
        except ingest.IngestError as err:
            self._json(502, {"error": str(err)})
            return
        n = len(ingest.extracted_markers(run))
        self._json(200, {
            "ok": True,
            "id": run_id,
            "cueCount": len(run["cues"]),
            "extractedCount": n,
            "source": run.get("source") or "youtube",
            "notes": notes,
        })

    def do_PUT(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length") or 0)
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json(400, {"error": "bad json"})
            return
        run_id = payload.get("runId") or ""
        run = load_run(run_id)
        if run is None or not SAFE_ID.match(run_id):
            self._json(404, {"error": "run not found"})
            return
        if parsed.path == "/api/feedback":
            try:
                index = int(payload.get("index"))
            except (TypeError, ValueError):
                self._json(400, {"error": "bad index"})
                return
            text = payload.get("text")
            if not isinstance(text, str):
                self._json(400, {"error": "text must be a string"})
                return
            fb = append_label(run_id, run, index, text)
            self._json(200, {"ok": True, "feedback": fb})
            return
        if parsed.path == "/api/miss":
            try:
                additions = append_miss(run_id, run, payload)
            except ValueError as err:
                self._json(400, {"error": str(err)})
                return
            self._json(200, {"ok": True, "additions": additions})
            return
        if parsed.path == "/api/unmiss":
            try:
                additions = append_unmiss(run_id, run, payload)
            except ValueError as err:
                self._json(400, {"error": str(err)})
                return
            self._json(200, {"ok": True, "additions": additions})
            return
        if parsed.path == "/api/relabel":
            try:
                index = int(payload.get("index"))
            except (TypeError, ValueError):
                self._json(400, {"error": "bad index"})
                return
            try:
                edits = append_relabel(run_id, run, index, payload.get("description"))
            except ValueError as err:
                self._json(400, {"error": str(err)})
                return
            self._json(200, {"ok": True, "edits": edits})
            return
        if parsed.path == "/api/annotate":
            try:
                index = int(payload.get("index"))
            except (TypeError, ValueError):
                self._json(400, {"error": "bad index"})
                return
            try:
                annotations = append_annotate(run_id, run, index, payload)
            except ValueError as err:
                self._json(400, {"error": str(err)})
                return
            self._json(200, {"ok": True, "annotations": annotations})
            return
        if parsed.path == "/api/section":
            sections = append_section(run_id, run, payload)
            self._json(200, {"ok": True, "sections": sections})
            return
        if parsed.path == "/api/link":
            try:
                youtube_id = append_link(run_id, run, payload)
            except ValueError as err:
                self._json(400, {"error": str(err)})
                return
            self._json(200, {"ok": True, "youtubeId": youtube_id})
            return
        self._json(404, {"error": "not found"})


def shutdown():
    """Stop, and stay stopped. Called on a thread so the HTTP reply lands first."""
    import subprocess
    import time
    time.sleep(0.2)
    label = "com.briansze.yt-clip-studio"
    try:
        subprocess.run(
            ["launchctl", "bootout", f"gui/{os.getuid()}/{label}"],
            capture_output=True, timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        pass  # not running under launchd, or launchctl missing — just exit
    os._exit(0)


def main():
    ensure_dirs()
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    # Don't let a slow in-flight ingest thread block Ctrl-C shutdown.
    server.daemon_threads = True
    UPLOADS_CACHE.start()
    print(f"clip studio → http://127.0.0.1:{PORT}")
    print(f"runs:    {RUNS_DIR}")
    print(f"labels:  {LABELS_PATH}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()
