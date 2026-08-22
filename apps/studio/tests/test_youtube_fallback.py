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
        self.assertEqual(server.effective_youtube_id("run", run), "Oa0wqetkNcg")

    def test_supported_youtube_url_shapes(self):
        for url in (
            "https://youtu.be/Oa0wqetkNcg?t=10",
            "https://youtube.com/shorts/Oa0wqetkNcg",
            "https://m.youtube.com/live/Oa0wqetkNcg?feature=share",
        ):
            with self.subTest(url=url):
                self.assertEqual(server.effective_youtube_id("run", {"url": url}), "Oa0wqetkNcg")

    def test_synthetic_id_without_url_is_not_a_fallback(self):
        run = {
            "videoId": "GMT20260730-155336_Recording_640x360-1",
            "url": "",
            "source": "local",
        }
        self.assertEqual(server.effective_youtube_id("run", run), "")

    def test_valid_shaped_video_id_without_url_is_not_a_fallback(self):
        run = {"videoId": "Oa0wqetkNcg", "url": "", "source": "local"}
        self.assertEqual(server.effective_youtube_id("run", run), "")

    def test_non_youtube_url_cannot_authorize_a_fallback(self):
        run = {"url": "https://example.com/watch?v=Oa0wqetkNcg"}
        self.assertEqual(server.effective_youtube_id("run", run), "")


class MissingMediaWarnings(unittest.TestCase):
    def test_missing_download_is_silent_when_watch_url_exists(self):
        run = {
            "videoId": "Oa0wqetkNcg",
            "url": "https://www.youtube.com/watch?v=Oa0wqetkNcg",
            "media": "Oa0wqetkNcg.mp4",
        }
        with mock.patch.object(server, "resolve_run_media", return_value=None):
            self.assertEqual(server.run_warnings("download-run", run), [])

    def test_missing_local_media_warns_without_watch_url(self):
        run = {
            "videoId": "GMT20260730-155336_Recording_640x360-1",
            "url": "",
            "media": "GMT20260730.mp4",
        }
        with mock.patch.object(server, "resolve_run_media", return_value=None):
            with contextlib.redirect_stderr(io.StringIO()):
                warnings = server.run_warnings("zoom-run", run)
        self.assertEqual([warning["code"] for warning in warnings], ["missing-media"])


class ReadApiContract(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        root = pathlib.Path(self._tmp.name)
        self.runs = root / "runs"
        self.media = root / "media"
        self.labels = root / "labels.jsonl"
        self.uploads = root / "uploads.json"
        self.patchers = [
            mock.patch.object(server, "RUNS_DIR", self.runs),
            mock.patch.object(server, "MEDIA_DIR", self.media),
            mock.patch.object(server, "LABELS_PATH", self.labels),
            mock.patch.object(server, "UPLOADS_PATH", self.uploads),
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

    def test_link_event_overrides_url_and_empty_link_clears_it(self):
        run_id = "local-run"
        run = {"url": "https://www.youtube.com/watch?v=dYT41doJw2I"}

        server.append_link(run_id, {"youtubeId": "Oa0wqetkNcg"})
        self.assertEqual(server.effective_youtube_id(run_id, run), "Oa0wqetkNcg")
        event = server.read_label_events()[-1]
        self.assertEqual(event["schemaVersion"], 2)
        self.assertEqual(event["verdict"], "link")
        self.assertEqual(event["source"], "human-link")
        self.assertEqual(event["runId"], run_id)
        self.assertEqual(event["youtubeId"], "Oa0wqetkNcg")

        server.append_link(run_id, {"youtubeId": ""})
        self.assertEqual(server.effective_youtube_id(run_id, run), "")

    def test_link_event_suppresses_missing_media_warning_inside_resolver(self):
        run_id = "local-run"
        run = {"url": "", "media": "missing.mp4"}
        server.append_link(run_id, {"youtubeId": "Oa0wqetkNcg"})

        with mock.patch.object(server, "resolve_run_media", return_value=None):
            self.assertEqual(server.run_warnings(run_id, run), [])

    def test_invalid_link_is_refused_without_an_event(self):
        with self.assertRaisesRegex(ValueError, "11-character"):
            server.append_link("local-run", {"youtubeId": "too-short"})
        self.assertEqual(server.read_label_events(), [])

    def test_writing_link_leaves_sections_byte_identical(self):
        run_id = "local-run"
        run = {"videoId": "local", "url": "", "title": "Lesson"}
        server.append_section(run_id, run, {"start": 0, "work": "Pennies", "lane": "comping"})
        before = json.dumps(server.load_sections(run_id), separators=(",", ":"))

        server.append_link(run_id, {"youtubeId": "Oa0wqetkNcg"})

        after = json.dumps(server.load_sections(run_id), separators=(",", ":"))
        self.assertEqual(after, before)

    def test_writing_section_leaves_effective_id_unchanged(self):
        run_id = "local-run"
        run = {"videoId": "local", "url": "", "title": "Lesson"}
        server.append_link(run_id, {"youtubeId": "Oa0wqetkNcg"})
        before = server.effective_youtube_id(run_id, run)

        server.append_section(run_id, run, {"start": 0, "work": "Pennies", "lane": "comping"})

        self.assertEqual(server.effective_youtube_id(run_id, run), before)

    def test_cached_youtube_title_wins_on_both_read_apis(self):
        run_id = "local-run"
        run = {
            "videoId": "local",
            "url": "",
            "title": "Filename title",
            "markers": [],
            "cues": [],
        }
        self.write_run(run_id, run)
        server.append_link(run_id, {"youtubeId": "Oa0wqetkNcg"})
        server.uploads.write_cache_atomic(self.uploads, {
            "fetchedAt": "2026-08-22T00:00:00+00:00",
            "channel": server.uploads.CHANNEL_ID,
            "authenticated": True,
            "items": [server.uploads.normalize_item({
                "id": "Oa0wqetkNcg",
                "title": "YouTube title",
                "duration": 3883,
                "upload_date": "20260820",
            })],
        })

        self.assertEqual(server.list_runs()[0]["title"], "YouTube title")
        self.assertEqual(server.run_payload(run_id, run)["title"], "YouTube title")
        self.assertEqual(run["title"], "Filename title")

    def test_title_falls_back_to_immutable_run_when_cache_is_missing(self):
        run_id = "local-run"
        run = {
            "videoId": "local", "url": "", "title": "Filename title",
            "markers": [], "cues": [],
        }
        self.write_run(run_id, run)
        server.append_link(run_id, {"youtubeId": "Oa0wqetkNcg"})

        self.assertEqual(server.list_runs()[0]["title"], "Filename title")
        self.assertEqual(server.run_payload(run_id, run)["title"], "Filename title")

    def test_run_list_reads_label_log_once(self):
        for index in range(2):
            self.write_run(f"run-{index}", {
                "videoId": f"local-{index}", "url": "", "title": "Lesson",
                "markers": [], "cues": [],
            })
        with mock.patch.object(server, "read_label_events", wraps=server.read_label_events) as read:
            server.list_runs()
        self.assertEqual(read.call_count, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
