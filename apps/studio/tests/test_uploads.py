#!/usr/bin/env python3
"""Uploads cache: authenticated merge, offline reads, and one worker."""
from __future__ import annotations

import contextlib
import io
import json
import pathlib
import stat
import sys
import tempfile
import threading
import time
import unittest
from datetime import datetime, timedelta, timezone
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import uploads  # noqa: E402


CANARY = {
    "id": uploads.CANARY_ID,
    "title": "Private lesson",
    "duration": 3883,
    "upload_date": "20260819",
}
PUBLIC = {
    "id": "dYT41doJw2I",
    "title": "Public lesson | with a pipe",
    "duration": None,
    "upload_date": None,
}


class UploadCacheTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.cache_path = self.root / "uploads.json"
        self.addCleanup(self._tmp.cleanup)

    def fake_ytdlp(self, rows=(), *, exit_code=0, stderr=""):
        path = self.root / f"fake-ytdlp-{len(list(self.root.glob('fake-ytdlp-*')))}"
        body = ["#!/usr/bin/env python3", "import json, sys"]
        for row in rows:
            body.append(f"print(json.dumps({row!r}))")
        if stderr:
            body.append(f"print({stderr!r}, file=sys.stderr)")
        body.append(f"raise SystemExit({exit_code})")
        path.write_text("\n".join(body) + "\n", encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)
        return str(path)

    def write_cache(self, items, *, authenticated=True, fetched_at=None):
        data = {
            "fetchedAt": fetched_at or datetime.now(timezone.utc).isoformat(),
            "channel": uploads.CHANNEL_ID,
            "authenticated": authenticated,
            "items": [uploads.normalize_item(item) for item in items],
        }
        uploads.write_cache_atomic(self.cache_path, data)
        return data

    def test_cold_fill_uses_json_lines_and_preserves_pipe_in_title(self):
        cache = uploads.UploadCache(
            self.cache_path,
            executable=self.fake_ytdlp([PUBLIC, CANARY]),
        )

        self.assertTrue(cache.refresh())

        stored = json.loads(self.cache_path.read_text(encoding="utf-8"))
        self.assertTrue(stored["authenticated"])
        self.assertEqual([item["id"] for item in stored["items"]], [PUBLIC["id"], CANARY["id"]])
        self.assertEqual(stored["items"][0]["title"], PUBLIC["title"])
        self.assertIsNone(stored["items"][0]["duration"])
        self.assertIsNone(stored["items"][0]["uploadDate"])

    def test_fetch_uses_the_shared_ingest_timeout(self):
        completed = mock.Mock(returncode=0, stdout=json.dumps(CANARY) + "\n", stderr="")
        with mock.patch.object(uploads.subprocess, "run", return_value=completed) as run:
            uploads.fetch_uploads("fake-yt-dlp")
        self.assertEqual(run.call_args.kwargs["timeout"], uploads.ingest.SUBPROCESS_TIMEOUT)

    def test_cold_public_only_fill_is_marked_unauthenticated(self):
        cache = uploads.UploadCache(
            self.cache_path,
            executable=self.fake_ytdlp([PUBLIC]),
        )

        self.assertTrue(cache.refresh())

        stored = json.loads(self.cache_path.read_text(encoding="utf-8"))
        self.assertFalse(stored["authenticated"])
        self.assertEqual([item["id"] for item in stored["items"]], [PUBLIC["id"]])

    def test_unauthenticated_refresh_updates_without_pruning(self):
        self.write_cache([CANARY], authenticated=True)
        changed_public = dict(PUBLIC, title="Updated public title")
        cache = uploads.UploadCache(
            self.cache_path,
            executable=self.fake_ytdlp([changed_public]),
        )

        self.assertTrue(cache.refresh())

        stored = json.loads(self.cache_path.read_text(encoding="utf-8"))
        self.assertFalse(stored["authenticated"])
        self.assertEqual([item["id"] for item in stored["items"]], [PUBLIC["id"], CANARY["id"]])
        self.assertEqual(stored["items"][0]["title"], "Updated public title")

    def test_authenticated_refresh_may_prune(self):
        stale = dict(PUBLIC, id="nWCc3xBSz-0", title="Deleted upload")
        self.write_cache([stale, CANARY])
        cache = uploads.UploadCache(
            self.cache_path,
            executable=self.fake_ytdlp([CANARY]),
        )

        self.assertTrue(cache.refresh())

        stored = json.loads(self.cache_path.read_text(encoding="utf-8"))
        self.assertEqual([item["id"] for item in stored["items"]], [CANARY["id"]])

    def test_refresh_recovers_valid_rows_from_malformed_cache(self):
        valid = uploads.normalize_item(CANARY)
        malformed = dict(valid, id="not-a-video-id")
        uploads.write_cache_atomic(self.cache_path, {
            "fetchedAt": datetime.now(timezone.utc).isoformat(),
            "channel": uploads.CHANNEL_ID,
            "authenticated": True,
            "items": [valid, malformed],
        })
        self.assertIsNone(uploads.read_cache(self.cache_path))
        cache = uploads.UploadCache(
            self.cache_path,
            executable=self.fake_ytdlp([PUBLIC]),
        )

        self.assertTrue(cache.refresh())

        stored = json.loads(self.cache_path.read_text(encoding="utf-8"))
        self.assertEqual(
            [item["id"] for item in stored["items"]],
            [PUBLIC["id"], CANARY["id"]],
        )

    def test_drastic_authenticated_shrink_merges_and_logs(self):
        previous = [CANARY] + [
            {
                "id": f"video{i:06d}",
                "title": f"Lesson {i}",
                "duration": 1000 + i,
                "upload_date": "20260820",
            }
            for i in range(9)
        ]
        self.write_cache(previous)
        cache = uploads.UploadCache(
            self.cache_path,
            executable=self.fake_ytdlp([CANARY]),
        )

        output = io.StringIO()
        with contextlib.redirect_stderr(output):
            self.assertTrue(cache.refresh())

        stored = json.loads(self.cache_path.read_text(encoding="utf-8"))
        self.assertTrue(stored["authenticated"])
        self.assertEqual(len(stored["items"]), 10)
        self.assertIn("drastic authenticated shrink (1 of 10)", output.getvalue())

    def test_failed_refresh_retains_cache_and_logs_once_per_episode(self):
        original = self.write_cache([CANARY])
        cache = uploads.UploadCache(
            self.cache_path,
            executable=self.fake_ytdlp(exit_code=1, stderr="offline"),
        )

        output = io.StringIO()
        with contextlib.redirect_stderr(output):
            self.assertFalse(cache.refresh())
            self.assertFalse(cache.refresh())

        self.assertEqual(json.loads(self.cache_path.read_text(encoding="utf-8")), original)
        self.assertEqual(output.getvalue().count("uploads refresh failed"), 1)

    def test_failed_atomic_replace_leaves_old_file_and_no_temp(self):
        original = self.write_cache([PUBLIC], authenticated=False)
        cache = uploads.UploadCache(
            self.cache_path,
            executable=self.fake_ytdlp([CANARY]),
        )

        with contextlib.redirect_stderr(io.StringIO()):
            with mock.patch.object(uploads.os, "replace", side_effect=OSError("interrupted")):
                self.assertFalse(cache.refresh())

        self.assertEqual(json.loads(self.cache_path.read_text(encoding="utf-8")), original)
        self.assertEqual(list(self.root.glob(".uploads.json.*.tmp")), [])

    def test_api_empty_shape_for_missing_and_invalid_cache(self):
        expected = {
            "channel": uploads.CHANNEL_ID,
            "items": [],
            "fetchedAt": None,
            "ageSeconds": None,
        }
        self.assertEqual(uploads.api_payload(self.cache_path), expected)
        self.cache_path.write_text("not json", encoding="utf-8")
        self.assertEqual(uploads.api_payload(self.cache_path), expected)

    def test_api_age_is_non_negative_and_uses_fetched_at(self):
        fetched = datetime(2026, 8, 21, 12, tzinfo=timezone.utc)
        self.write_cache([CANARY], fetched_at=fetched.isoformat())
        later = fetched + timedelta(seconds=125)
        self.assertEqual(uploads.api_payload(self.cache_path, later)["ageSeconds"], 125)
        self.assertEqual(uploads.api_payload(self.cache_path, fetched - timedelta(seconds=2))["ageSeconds"], 0)

    def test_second_refresh_is_deduped_while_first_is_running(self):
        entered = threading.Event()
        release = threading.Event()

        def blocking_fetch():
            entered.set()
            release.wait(1)
            return [uploads.normalize_item(CANARY)]

        cache = uploads.UploadCache(self.cache_path, fetcher=blocking_fetch)
        first = threading.Thread(target=cache.refresh)
        first.start()
        self.assertTrue(entered.wait(1))
        self.assertFalse(cache.refresh())
        release.set()
        first.join(1)
        self.assertFalse(first.is_alive())

    def test_start_returns_while_offline_refresh_is_blocked(self):
        entered = threading.Event()
        release = threading.Event()

        def offline_fetch():
            entered.set()
            release.wait(1)
            raise uploads.UploadsError("offline")

        cache = uploads.UploadCache(self.cache_path, fetcher=offline_fetch, interval=60)
        with contextlib.redirect_stderr(io.StringIO()):
            before = time.monotonic()
            cache.start()
            elapsed = time.monotonic() - before
            self.assertTrue(entered.wait(1))
            self.assertLess(elapsed, 0.1)
            self.assertEqual(cache.read_api()["items"], [])
            release.set()
            cache.stop()


if __name__ == "__main__":
    unittest.main(verbosity=2)
