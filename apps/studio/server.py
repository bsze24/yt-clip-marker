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

APP_DIR = Path(__file__).resolve().parent
RUNS_DIR = APP_DIR / "runs"
UI_DIR = APP_DIR / "ui"
LABELS_PATH = APP_DIR / "labels.jsonl"
MEDIA_DIR = APP_DIR / "media"
PORT = 8765

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


def current_feedback_map():
    """runId -> {markerIndexStr: feedbackText}, last event wins."""
    by_run = {}
    for ev in read_label_events():
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


def load_additions(run_id):
    """Human-added misses for a run. Last event per start time wins."""
    by_start = {}
    for ev in read_label_events():
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


def load_edits(run_id):
    """Human-edited labels for markers. Last relabel per index wins.
    The run JSON keeps the original description."""
    by_idx = {}
    for ev in read_label_events():
        if ev.get("runId") != run_id:
            continue
        if ev.get("verdict") != "relabel":
            continue
        idx = ev.get("markerIndex")
        if idx is None:
            continue
        by_idx[str(idx)] = ev.get("description") or ""
    return by_idx


def load_run_work(run_id):
    """The lesson's work — piece and rendition — as one value for the whole run.

    It lives here rather than on the run file because `runs/{id}.json` is
    immutable ingest output ([[D-002]]), and it lives here rather than on every
    clip because it never varied per clip: across 193 annotated rows it changed
    5 times on one video and 0 on the other two, where the same string was
    stored 75 times. Resolved on read, same as media ([[D-034]]).

    A clip that carries its own `work` still wins — one lesson covering two
    pieces is normal, and video 1 does exactly that.
    """
    work = ""
    for ev in read_label_events():
        if ev.get("runId") != run_id or ev.get("verdict") != "chapter":
            continue
        work = (ev.get("work") or "").strip()
    return work


def append_run_work(run_id, run, payload):
    work = payload.get("work") if isinstance(payload.get("work"), str) else ""
    event = {
        "schemaVersion": 2,
        "recordedAt": datetime.now().astimezone().isoformat(),
        "runId": run_id,
        "videoId": run.get("videoId"),
        "videoUrl": run.get("url"),
        "videoTitle": run.get("title"),
        "markerIndex": None,
        "source": "human-chapter",
        "start": None,
        "end": None,
        "description": "",
        "tags": [],
        "lane": "",
        "work": work.strip(),
        "feedback": "",
        "verdict": "chapter",
    }
    append_event(event)
    return load_run_work(run_id)


def load_annotations(run_id):
    """tags / lane / work on markers. Last annotate per index wins."""
    by_idx = {}
    for ev in read_label_events():
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


def run_warnings(run_id, run):
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
    declared = run.get("media")
    if declared and resolve_run_media(run) is None:
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


def list_runs():
    ensure_dirs()
    fb_by_run = current_feedback_map()
    rows = []
    for path in sorted(RUNS_DIR.glob("*.json"), key=_mtime, reverse=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        run_id = path.stem
        markers = data.get("markers") or []
        fb = fb_by_run.get(run_id, {})
        annotations = load_annotations(run_id)
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
                "url": data.get("url") or "",
                "title": data.get("title") or run_id,
                "createdAt": data.get("createdAt") or "",
                "source": data.get("source") or "youtube",
                "hasMedia": bool(resolve_run_media(data)),
                "markerCount": len(markers),
                "missCount": len(load_additions(run_id)),
                "checkCount": checks,
                "wrongCount": wrongs,
                "noteCount": notes,
                "keepCount": keeps,
                "blankCount": max(0, len(markers) - checks - wrongs - notes - keeps),
            }
        )
    return rows


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
        if path == "/api/run":
            run_id = (parse_qs(parsed.query).get("id") or [""])[0]
            run = load_run(run_id)
            if run is None:
                self._json(404, {"error": "run not found"})
                return
            self._json(
                200,
                {
                    "id": run_id,
                    "run": run,
                    "feedback": load_feedback(run_id),
                    "runWork": load_run_work(run_id),
                    "additions": load_additions(run_id),
                    "edits": load_edits(run_id),
                    "annotations": load_annotations(run_id),
                    "warnings": run_warnings(run_id, run),
                    "media": resolve_run_media(run),
                },
            )
            return
        self._json(404, {"error": "not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
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
        if parsed.path == "/api/run-work":
            work = append_run_work(run_id, run, payload)
            self._json(200, {"ok": True, "runWork": work})
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
    print(f"clip studio → http://127.0.0.1:{PORT}")
    print(f"runs:    {RUNS_DIR}")
    print(f"labels:  {LABELS_PATH}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()
