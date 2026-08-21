#!/usr/bin/env python3
"""Effective YouTube identity and missing-media fallback behavior."""
import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import server  # noqa: E402


class EffectiveYoutubeId(unittest.TestCase):
    def test_canonical_watch_url(self):
        run = {
            "videoId": "local-filename-id",
            "url": "https://www.youtube.com/watch?v=Oa0wqetkNcg",
            "source": "local",
        }
        self.assertEqual(server.effective_youtube_id(run), "Oa0wqetkNcg")

    def test_supported_youtube_url_shapes(self):
        for url in (
            "https://youtu.be/Oa0wqetkNcg?t=10",
            "https://youtube.com/shorts/Oa0wqetkNcg",
            "https://m.youtube.com/live/Oa0wqetkNcg?feature=share",
        ):
            with self.subTest(url=url):
                self.assertEqual(server.effective_youtube_id({"url": url}), "Oa0wqetkNcg")

    def test_synthetic_id_without_url_is_not_a_fallback(self):
        run = {
            "videoId": "GMT20260730-155336_Recording_640x360-1",
            "url": "",
            "source": "local",
        }
        self.assertEqual(server.effective_youtube_id(run), "")

    def test_valid_shaped_video_id_without_url_is_not_a_fallback(self):
        run = {"videoId": "Oa0wqetkNcg", "url": "", "source": "local"}
        self.assertEqual(server.effective_youtube_id(run), "")

    def test_non_youtube_url_cannot_authorize_a_fallback(self):
        run = {"url": "https://example.com/watch?v=Oa0wqetkNcg"}
        self.assertEqual(server.effective_youtube_id(run), "")


class MissingMediaWarnings(unittest.TestCase):
    def test_missing_download_is_silent_when_watch_url_exists(self):
        run = {
            "videoId": "Oa0wqetkNcg",
            "url": "https://www.youtube.com/watch?v=Oa0wqetkNcg",
            "media": "Oa0wqetkNcg.mp4",
        }
        youtube_id = server.effective_youtube_id(run)
        with mock.patch.object(server, "resolve_run_media", return_value=None):
            self.assertEqual(server.run_warnings("download-run", run, youtube_id), [])

    def test_missing_local_media_warns_without_watch_url(self):
        run = {
            "videoId": "GMT20260730-155336_Recording_640x360-1",
            "url": "",
            "media": "GMT20260730.mp4",
        }
        with mock.patch.object(server, "resolve_run_media", return_value=None):
            with contextlib.redirect_stderr(io.StringIO()):
                warnings = server.run_warnings("zoom-run", run, "")
        self.assertEqual([warning["code"] for warning in warnings], ["missing-media"])


class ReadApiContract(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        root = pathlib.Path(self._tmp.name)
        self.runs = root / "runs"
        self.media = root / "media"
        self.labels = root / "labels.jsonl"
        self.patchers = [
            mock.patch.object(server, "RUNS_DIR", self.runs),
            mock.patch.object(server, "MEDIA_DIR", self.media),
            mock.patch.object(server, "LABELS_PATH", self.labels),
        ]
        for patcher in self.patchers:
            patcher.start()
            self.addCleanup(patcher.stop)
        server.ensure_dirs()

    def write_run(self, run_id, run):
        (self.runs / f"{run_id}.json").write_text(json.dumps(run), encoding="utf-8")

    def test_both_read_apis_expose_the_same_resolved_id(self):
        run_id = "Oa0wqetkNcg-20260819-0858"
        run = {
            "videoId": "Oa0wqetkNcg",
            "url": "https://www.youtube.com/watch?v=Oa0wqetkNcg",
            "title": "Lesson",
            "markers": [],
            "cues": [],
        }
        self.write_run(run_id, run)

        rows = server.list_runs()
        detail = server.run_payload(run_id, run)

        self.assertEqual(rows[0]["youtubeId"], "Oa0wqetkNcg")
        self.assertEqual(detail["youtubeId"], "Oa0wqetkNcg")

    def test_local_only_run_exposes_empty_id_and_warning(self):
        run_id = "GMT20260730-local"
        run = {
            "videoId": "GMT20260730-155336_Recording_640x360-1",
            "url": "",
            "title": "Zoom lesson",
            "media": "missing.mp4",
            "markers": [],
            "cues": [],
        }
        self.write_run(run_id, run)

        with contextlib.redirect_stderr(io.StringIO()):
            detail = server.run_payload(run_id, run)

        self.assertEqual(detail["youtubeId"], "")
        self.assertEqual([warning["code"] for warning in detail["warnings"]], ["missing-media"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
