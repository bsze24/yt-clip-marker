#!/usr/bin/env python3
"""Background cache of the channel's YouTube uploads.

The HTTP request path only reads ``uploads.json``.  yt-dlp always runs on this
module's one background worker, so starting or polling the Studio never waits
for YouTube.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path

import ingest

CHANNEL_ID = "UC5waNKHe9sqmnjPG78qyjRw"
UPLOADS_URL = "https://www.youtube.com/playlist?list=UU5waNKHe9sqmnjPG78qyjRw"
CANARY_ID = "Oa0wqetkNcg"
REFRESH_SECONDS = 30 * 60
VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


class UploadsError(RuntimeError):
    """A refresh failed without invalidating the last good cache."""


def _nullable_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value if value >= 0 else None


def _nullable_date(value):
    if isinstance(value, str) and re.fullmatch(r"\d{8}", value):
        return value
    return None


def normalize_item(raw):
    if not isinstance(raw, dict):
        raise UploadsError("yt-dlp returned a non-object upload")
    video_id = raw.get("id")
    if not isinstance(video_id, str) or not VIDEO_ID_RE.fullmatch(video_id):
        raise UploadsError("yt-dlp returned an upload without a valid video id")
    title = raw.get("title")
    if not isinstance(title, str) or not title.strip():
        title = video_id
    return {
        "id": video_id,
        "title": title.strip(),
        "duration": _nullable_number(raw.get("duration")),
        "uploadDate": _nullable_date(raw.get("upload_date")),
        "dateApproximate": True,
    }


def fetch_uploads(executable="yt-dlp"):
    """Fetch and parse one JSON object per upload from yt-dlp."""
    command = [
        executable,
        "--flat-playlist",
        "--skip-download",
        "--cookies-from-browser", "chrome",
        "--extractor-args", "youtubetab:approximate_date",
        "--print", "%(.{id,title,duration,upload_date})j",
        UPLOADS_URL,
    ]
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=ingest.SUBPROCESS_TIMEOUT,
        )
    except FileNotFoundError as err:
        raise UploadsError("yt-dlp not found") from err
    except subprocess.TimeoutExpired as err:
        raise UploadsError("yt-dlp timed out") from err
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "yt-dlp failed").strip()[-500:]
        raise UploadsError(detail)

    items = []
    by_id = {}
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        try:
            item = normalize_item(json.loads(line))
        except json.JSONDecodeError as err:
            raise UploadsError("yt-dlp returned invalid JSON") from err
        if item["id"] not in by_id:
            items.append(item)
        else:
            items[by_id[item["id"]]] = item
            continue
        by_id[item["id"]] = len(items) - 1
    if not items:
        raise UploadsError("yt-dlp returned no uploads")
    return items


def _aware_timestamp(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed


def _validated_cache(raw):
    if not isinstance(raw, dict) or raw.get("channel") != CHANNEL_ID:
        return None
    if _aware_timestamp(raw.get("fetchedAt")) is None:
        return None
    if not isinstance(raw.get("authenticated"), bool):
        return None
    items = raw.get("items")
    if not isinstance(items, list):
        return None
    try:
        normalized = [
            normalize_item({
                "id": item.get("id"),
                "title": item.get("title"),
                "duration": item.get("duration"),
                "upload_date": item.get("uploadDate"),
            })
            for item in items
            if isinstance(item, dict)
        ]
    except UploadsError:
        return None
    if len(normalized) != len(items):
        return None
    return {
        "fetchedAt": raw["fetchedAt"],
        "channel": CHANNEL_ID,
        "authenticated": raw["authenticated"],
        "items": normalized,
    }


def read_cache(path):
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    return _validated_cache(raw)


def empty_api_payload():
    return {
        "channel": CHANNEL_ID,
        "items": [],
        "fetchedAt": None,
        "ageSeconds": None,
    }


def api_payload(path, now=None):
    cached = read_cache(path)
    if cached is None:
        return empty_api_payload()
    now = now or datetime.now(timezone.utc)
    fetched_at = _aware_timestamp(cached["fetchedAt"])
    age = max(0, int((now - fetched_at.astimezone(timezone.utc)).total_seconds()))
    return {
        "channel": CHANNEL_ID,
        "items": cached["items"],
        "fetchedAt": cached["fetchedAt"],
        "ageSeconds": age,
    }


def merge_items(previous, fetched):
    """Update by id; prune only when this refresh proves Chrome auth works."""
    authenticated = any(item["id"] == CANARY_ID for item in fetched)
    if authenticated:
        return list(fetched), True

    merged = list(fetched)
    seen = {item["id"] for item in fetched}
    for item in previous:
        if item["id"] not in seen:
            merged.append(item)
    return merged, False


def write_cache_atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as fh:
            temp_path = Path(fh.name)
            json.dump(data, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(temp_path, path)
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass


class UploadCache:
    """One non-blocking refresh worker around an atomic cache file."""

    def __init__(self, path, *, executable="yt-dlp", interval=REFRESH_SECONDS,
                 fetcher=None):
        self.path = Path(path)
        self.executable = executable
        self.interval = interval
        self.fetcher = fetcher
        self._refresh_lock = threading.Lock()
        self._start_lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = None
        self._failure_logged = False

    def read_api(self, now=None):
        return api_payload(self.path, now)

    def refresh(self):
        if not self._refresh_lock.acquire(blocking=False):
            return False
        try:
            fetched = self.fetcher() if self.fetcher else fetch_uploads(self.executable)
            previous = read_cache(self.path)
            items, authenticated = merge_items(
                previous["items"] if previous else [],
                fetched,
            )
            data = {
                "fetchedAt": datetime.now(timezone.utc).isoformat(),
                "channel": CHANNEL_ID,
                "authenticated": authenticated,
                "items": items,
            }
            write_cache_atomic(self.path, data)
            self._failure_logged = False
            return True
        except Exception as err:
            if not self._failure_logged:
                print(f"[studio] uploads refresh failed; keeping cache: {err}", file=sys.stderr)
                self._failure_logged = True
            return False
        finally:
            self._refresh_lock.release()

    def _run(self):
        while not self._stop.is_set():
            self.refresh()
            self._stop.wait(self.interval)

    def start(self):
        """Start once and return immediately; network work stays on the thread."""
        with self._start_lock:
            if self._thread is not None and self._thread.is_alive():
                return self._thread
            self._stop.clear()
            self._thread = threading.Thread(
                target=self._run,
                name="studio-uploads-refresh",
                daemon=True,
            )
            self._thread.start()
            return self._thread

    def stop(self, timeout=1):
        """Test/support hook; production relies on the daemon process lifetime."""
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout)
