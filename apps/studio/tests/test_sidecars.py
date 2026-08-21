#!/usr/bin/env python3
"""Sidecar matching — the one place this project keeps getting wrong.

    python3 apps/studio/tests/test_sidecars.py

Stdlib `unittest` only, so this does not touch [[D-005]].

A **sidecar** is a file sitting beside the media that describes it: the
transcript, or a `.info.json` of metadata. Matching one to a video is most of
`local.py` and the source of every ingest bug so far — F18 (a bare prefix match
let `Lesson 1.mp4` adopt `Lesson 10.vtt`) and F20 (an exact sidecar losing to a
normalized Zoom base). Both were fixed and verified once, by hand, and nothing
stopped the next edit from undoing them.

The failure mode is what makes this worth a file: picking the WRONG neighbour is
silent. You get a full grid of a different lesson's captions, and if an
`.info.json` comes with it, that lesson's identity too. Picking nothing is loud —
an empty grid you notice immediately. So every case below asserts which of those
two happened, and the safe answer when in doubt is nothing.

[[D-037]] makes the `.` boundary a standing rule: every future stem variant
inherits it and owes a case here.
"""
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import local  # noqa: E402

VTT = "WEBVTT\n\n00:00:01.000 --> 00:00:02.000\n%s\n"


class SidecarMatching(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = pathlib.Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def write(self, name, body=None):
        path = self.dir / name
        path.write_text(VTT % body if body else "", encoding="utf-8")
        return path

    def picks(self, media):
        subs, info, _desc = local.find_sidecars(self.dir / media)
        text = ""
        if subs:
            pairs = local.read_cue_pairs(subs[0])
            text = pairs[0][1] if pairs else ""
        return (subs[0].name if subs else None), text, (info.name if info else None)

    # --- F18: a numbered neighbour must never be adopted -------------------
    def test_numbered_neighbour_is_not_a_sidecar(self):
        self.write("Lesson 1.mp4")
        self.write("Lesson 10.vtt", "NEIGHBOUR")
        self.assertEqual(self.picks("Lesson 1.mp4")[0], None)

    def test_numbered_neighbour_survives_a_stem_variant(self):
        """The variant strips `_640x360`, which is exactly how F18 could return."""
        self.write("Lesson 1_640x360.mp4")
        self.write("Lesson 10.vtt", "NEIGHBOUR")
        self.assertEqual(self.picks("Lesson 1_640x360.mp4")[0], None)

    def test_prefix_sibling_after_stripping(self):
        self.write("Solo_640x360.mp4")
        self.write("Solo10.vtt", "NEIGHBOUR")
        self.assertEqual(self.picks("Solo_640x360.mp4")[0], None)

    def test_space_suffix_is_not_a_boundary(self):
        self.write("Lesson 1.mp4")
        self.write("Lesson 1 backup.vtt", "BACKUP")
        self.assertEqual(self.picks("Lesson 1.mp4")[0], None)

    # --- the Zoom case the variants exist for ------------------------------
    def test_zoom_resolution_suffix(self):
        self.write("Talk_640x360.mp4")
        self.write("Talk.transcript.vtt", "ZOOM")
        self.assertEqual(self.picks("Talk_640x360.mp4")[1], "ZOOM")

    def test_zoom_variant_still_refuses_a_neighbour(self):
        self.write("Talk_640x360.mp4")
        self.write("Talk.transcript.vtt", "ZOOM")
        self.write("Talk2.vtt", "NEIGHBOUR")
        self.assertEqual(self.picks("Talk_640x360.mp4")[1], "ZOOM")

    def test_browser_duplicate_marker_and_resolution_together(self):
        self.write("Talk (1)_640x360.mp4")
        self.write("Talk.vtt", "BOTH SUFFIXES")
        self.assertEqual(self.picks("Talk (1)_640x360.mp4")[1], "BOTH SUFFIXES")

    def test_two_resolutions_share_one_transcript(self):
        """Same meeting exported twice. Both should find it — not a collision."""
        self.write("Dup_640x360.mp4")
        self.write("Dup_1920x1080.mp4")
        self.write("Dup.vtt", "SHARED")
        self.assertEqual(self.picks("Dup_640x360.mp4")[1], "SHARED")
        self.assertEqual(self.picks("Dup_1920x1080.mp4")[1], "SHARED")

    # --- F20: the exact stem outranks the normalized base ------------------
    def test_exact_stem_beats_normalized_base(self):
        self.write("Lecture_1920x1080.mp4")
        self.write("Lecture.vtt", "WRONG BASE")
        self.write("Lecture_1920x1080.vtt", "RIGHT EXACT")
        self.assertEqual(self.picks("Lecture_1920x1080.mp4")[1], "RIGHT EXACT")

    def test_exact_stem_beats_normalized_base_for_info_json(self):
        self.write("Lecture_1920x1080.mp4")
        (self.dir / "Lecture.info.json").write_text('{"id": "WRONGID"}', encoding="utf-8")
        (self.dir / "Lecture_1920x1080.info.json").write_text('{"id": "RIGHTID"}', encoding="utf-8")
        self.assertEqual(self.picks("Lecture_1920x1080.mp4")[2], "Lecture_1920x1080.info.json")

    # --- degenerate shapes should fail closed, never wide ------------------
    def test_empty_stem_after_stripping_matches_nothing(self):
        self.write("_640x360.mp4")
        self.write(".hidden.vtt", "HIDDEN")
        self.assertEqual(self.picks("_640x360.mp4")[0], None)

    def test_case_mismatch_fails_closed(self):
        """Documents current behaviour, and that the safe direction is nothing.

        `CASE.vtt` beside `Case_640x360.mp4` attaches nothing and the run reports
        'no transcript sidecar found', which is not strictly true — the file is
        right there. Loud and wrong beats silent and wrong, so this is the
        acceptable failure; change it only with a case for why.
        """
        self.write("Case_640x360.mp4")
        self.write("CASE.vtt", "CASE MISMATCH")
        self.assertEqual(self.picks("Case_640x360.mp4")[0], None)

    def test_no_sidecar_at_all(self):
        self.write("Alone.mp4")
        self.assertEqual(self.picks("Alone.mp4"), (None, "", None))


class TranscriptSource(unittest.TestCase):
    """The run has to say which file its grid came from."""

    def test_local_run_records_the_sidecar_it_used(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            src, runs, media = root / "src", root / "runs", root / "media"
            src.mkdir()
            (src / "Talk_640x360.mp4").write_text("", encoding="utf-8")
            (src / "Talk.transcript.vtt").write_text(VTT % "ZOOM", encoding="utf-8")
            _run_id, run, _notes = local.create_local_run(src / "Talk_640x360.mp4", runs, media)
            self.assertEqual(run["transcriptSource"], "Talk.transcript.vtt")

    def test_zero_cue_run_records_an_empty_source(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            src, runs, media = root / "src", root / "runs", root / "media"
            src.mkdir()
            (src / "Alone.mp4").write_text("", encoding="utf-8")
            _run_id, run, _notes = local.create_local_run(src / "Alone.mp4", runs, media)
            self.assertEqual(run["transcriptSource"], "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
