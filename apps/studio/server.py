#!/usr/bin/env python3
"""Clip Studio — the clipper's annotation workspace.

python3 apps/studio/server.py → http://127.0.0.1:8765
"""
from __future__ import annotations

import json
import math
import re
import threading
import traceback
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import ingest

APP_DIR = Path(__file__).resolve().parent
RUNS_DIR = APP_DIR / "runs"
UI_DIR = APP_DIR / "ui"
LABELS_PATH = APP_DIR / "labels.jsonl"
PORT = 8765

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


def load_feedback(run_id):
    return current_feedback_map().get(run_id, {})


def verdict_for(text):
    stripped = (text or "").strip()
    lower = stripped.lower()
    if lower == "check" or lower.startswith("check:"):
        return "check"
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
        "schemaVersion": 1,
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
        "schemaVersion": 1,
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
        "schemaVersion": 1,
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
        "schemaVersion": 1,
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
        "schemaVersion": 1,
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
        checks = notes = 0
        for i, _m in enumerate(markers):
            v = verdict_for(fb.get(str(i), ""))
            if v == "check":
                checks += 1
            elif v == "note":
                notes += 1
        rows.append(
            {
                "id": run_id,
                "videoId": data.get("videoId") or "",
                "url": data.get("url") or "",
                "title": data.get("title") or run_id,
                "createdAt": data.get("createdAt") or "",
                "markerCount": len(markers),
                "missCount": len(load_additions(run_id)),
                "checkCount": checks,
                "noteCount": notes,
                "blankCount": max(0, len(markers) - checks - notes),
            }
        )
    return rows


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[studio] {self.address_string()} {fmt % args}")

    def handle_one_request(self):
        # A bug in a route handler should surface as a 500 JSON error, not a raw
        # traceback and a reset connection in the UI.
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
        self.wfile.write(data)

    def _json(self, code, obj):
        self._send(code, json.dumps(obj), "application/json; charset=utf-8")

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
                    "additions": load_additions(run_id),
                    "edits": load_edits(run_id),
                    "annotations": load_annotations(run_id),
                },
            )
            return
        self._json(404, {"error": "not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
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
        try:
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
            "goldCount": n,
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
        self._json(404, {"error": "not found"})


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
